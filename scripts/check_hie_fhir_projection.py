#!/usr/bin/env python3
"""Semantic and privacy checks for the generated Route C FHIR projection."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from trustevidence.hie_validation import validate_hie_disclosure_event, validate_hie_envelope

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data_examples" / "hie_disclosure"
FHIR = ROOT / "standards" / "fhir_ig" / "input" / "resources"

FORBIDDEN_PORTABLE_TYPES = {"Observation", "DiagnosticReport"}
FORBIDDEN_CLINICAL_KEYS = {
    "valuequantity",
    "valueinteger",
    "valuedecimal",
    "clinical_note",
    "diagnosis",
    "diagnostic_payload",
    "raw_payload",
    "conclusion",
}
SOURCE_REFERENCE = "DiagnosticReport/diagnostic-report-hie-001/_history/2"
SOURCE_IDENTIFIER_SYSTEM = "urn:trustevidence:identifier:source-resource"


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield f"{path}.{key}", key, child
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _is_source_identifier(reference: Any) -> bool:
    if not isinstance(reference, dict):
        return False
    identifier = reference.get("identifier")
    return (
        reference.get("type") == "DiagnosticReport"
        and isinstance(identifier, dict)
        and identifier.get("system") == SOURCE_IDENTIFIER_SYSTEM
        and identifier.get("value") == SOURCE_REFERENCE
        and "reference" not in reference
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    event = _load(CASE / "hie_disclosure_event.json")
    envelope = _load(CASE / "signed_envelope_with_receipt.json")
    portable = _load(FHIR / "Bundle-portable-evidence-bundle-hie-001.json")
    binary = _load(FHIR / "Binary-trustevidence-envelope-hie-001.json")
    exact = (CASE / "signed_envelope_with_receipt.canonical.json").read_bytes()

    event_result = validate_hie_disclosure_event(event)
    envelope_result = validate_hie_envelope(envelope)
    decoded = base64.b64decode(binary["data"], validate=True)
    resource_types = [entry["resource"]["resourceType"] for entry in portable["entry"]]
    forbidden_types = sorted(FORBIDDEN_PORTABLE_TYPES.intersection(resource_types))

    forbidden_terms = []
    unresolved_local_source_references = []
    for path, key, value in _walk(portable):
        normal = key.lower().replace("-", "_")
        if normal in FORBIDDEN_CLINICAL_KEYS:
            forbidden_terms.append(path)
        if key == "reference" and value == SOURCE_REFERENCE:
            unresolved_local_source_references.append(path)

    resources = {
        entry["resource"]["resourceType"] + "/" + entry["resource"]["id"]: entry["resource"]
        for entry in portable["entry"]
    }
    audit_events = {
        entry["resource"]["id"]: entry["resource"]
        for entry in portable["entry"]
        if entry["resource"]["resourceType"] == "AuditEvent"
    }
    auth = audit_events["authorisation-decision-hie-001"]
    disclosure = audit_events["privacy-disclosure-source-hie-001"]
    provenance = resources["Provenance/evidence-provenance-hie-001"]
    consent = resources["Consent/consent-hie-001"]
    document = resources["DocumentReference/trustevidence-document-hie-001"]
    auth_details = {
        item["type"]: item.get("valueString")
        for entity in auth.get("entity", [])
        for item in entity.get("detail", [])
    }

    disclosure_source = any(
        _is_source_identifier(entity.get("what"))
        for entity in disclosure.get("entity", [])
    )
    provenance_source = any(
        _is_source_identifier(entity.get("what"))
        for entity in provenance.get("entity", [])
    )
    consent_source = any(
        _is_source_identifier(item.get("reference"))
        for item in consent.get("provision", {}).get("data", [])
    )

    report = {
        "status": "PASS",
        "case_id": "HIE-DISCLOSURE-001",
        "event_schema_accepted": event_result.accepted,
        "envelope_schema_accepted": envelope_result.accepted,
        "exact_binary_bytes_preserved": decoded == exact,
        "binary_content_type": binary.get("contentType"),
        "document_content_type": document.get("content", [{}])[0]
        .get("attachment", {})
        .get("contentType"),
        "canonical_envelope_sha256": hashlib.sha256(exact).hexdigest(),
        "portable_resource_types": resource_types,
        "forbidden_portable_resource_types": forbidden_types,
        "forbidden_clinical_value_paths": forbidden_terms,
        "unresolved_local_source_reference_paths": unresolved_local_source_references,
        "authorisation_decision_id": auth_details.get("authorisation-decision-id"),
        "policy_version": auth_details.get("policy-version"),
        "consent_reference_present": any(
            entity.get("what", {}).get("reference") == "Consent/consent-hie-001"
            for entity in auth.get("entity", [])
        ),
        "diagnostic_report_identifier_present": disclosure_source,
        "provenance_source_identifier_present": provenance_source,
        "consent_source_identifier_present": consent_source,
        "claim_boundary": {
            "clinical_payload": "excluded from portable bundle; present only in source fixture bundle",
            "patient_identity": "pseudonymous synthetic token",
            "source_resource": "identified by type plus versioned identifier; not copied into the portable bundle",
            "fhir_validation": "reported separately by the official validator toolchain",
            "audit_detail_valueString": "permitted for non-clinical decision, version and digest details",
        },
    }
    failures = [
        key
        for key, value in {
            "event_schema_accepted": report["event_schema_accepted"],
            "envelope_schema_accepted": report["envelope_schema_accepted"],
            "exact_binary_bytes_preserved": report["exact_binary_bytes_preserved"],
            "standard_binary_content_type": report["binary_content_type"] == "application/json",
            "standard_document_content_type": report["document_content_type"] == "application/json",
            "no_forbidden_resource_types": not forbidden_types,
            "no_forbidden_clinical_value_paths": not forbidden_terms,
            "no_unresolved_local_source_references": not unresolved_local_source_references,
            "decision_id": report["authorisation_decision_id"] == "D-204",
            "policy_version": report["policy_version"] == "6",
            "consent_reference": report["consent_reference_present"],
            "diagnostic_report_identifier": report["diagnostic_report_identifier_present"],
            "provenance_source_identifier": report["provenance_source_identifier_present"],
            "consent_source_identifier": report["consent_source_identifier_present"],
        }.items()
        if not value
    ]
    if failures:
        report["status"] = "FAIL"
        report["failures"] = failures

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if failures:
        raise SystemExit("HIE-FHIR-SEMANTIC: FAIL " + ", ".join(failures))
    print("HIE-FHIR-SEMANTIC: PASS")


if __name__ == "__main__":
    main()
