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
    for path, key, value in _walk(portable):
        normal = key.lower().replace("-", "_")
        if normal in {
            "valuequantity", "valueinteger", "valuedecimal", "valuestring",
            "clinical_note", "diagnosis", "conclusion",
        }:
            forbidden_terms.append(path)

    audit_events = {
        entry["resource"]["id"]: entry["resource"]
        for entry in portable["entry"]
        if entry["resource"]["resourceType"] == "AuditEvent"
    }
    auth = audit_events["authorisation-decision-hie-001"]
    disclosure = audit_events["privacy-disclosure-source-hie-001"]
    auth_details = {
        item["type"]: item.get("valueString")
        for entity in auth.get("entity", [])
        for item in entity.get("detail", [])
    }

    report = {
        "status": "PASS",
        "case_id": "HIE-DISCLOSURE-001",
        "event_schema_accepted": event_result.accepted,
        "envelope_schema_accepted": envelope_result.accepted,
        "exact_binary_bytes_preserved": decoded == exact,
        "canonical_envelope_sha256": hashlib.sha256(exact).hexdigest(),
        "portable_resource_types": resource_types,
        "forbidden_portable_resource_types": forbidden_types,
        "forbidden_clinical_value_paths": forbidden_terms,
        "authorisation_decision_id": auth_details.get("authorisation-decision-id"),
        "policy_version": auth_details.get("policy-version"),
        "consent_reference_present": any(
            entity.get("what", {}).get("reference") == "Consent/consent-hie-001"
            for entity in auth.get("entity", [])
        ),
        "diagnostic_report_reference_present": any(
            entity.get("what", {}).get("reference")
            == "DiagnosticReport/diagnostic-report-hie-001/_history/2"
            for entity in disclosure.get("entity", [])
        ),
        "claim_boundary": {
            "clinical_payload": "excluded from portable bundle; present only in source fixture bundle",
            "patient_identity": "pseudonymous synthetic token",
            "fhir_validation": "reported separately by the official validator toolchain",
        },
    }
    failures = [
        key for key, value in {
            "event_schema_accepted": report["event_schema_accepted"],
            "envelope_schema_accepted": report["envelope_schema_accepted"],
            "exact_binary_bytes_preserved": report["exact_binary_bytes_preserved"],
            "no_forbidden_resource_types": not forbidden_types,
            "no_forbidden_clinical_value_paths": not forbidden_terms,
            "decision_id": report["authorisation_decision_id"] == "D-204",
            "policy_version": report["policy_version"] == "6",
            "consent_reference": report["consent_reference_present"],
            "diagnostic_report_reference": report["diagnostic_report_reference_present"],
        }.items() if not value
    ]
    if failures:
        report["status"] = "FAIL"
        report["failures"] = failures

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("HIE-FHIR-SEMANTIC: FAIL " + ", ".join(failures))
    print("HIE-FHIR-SEMANTIC: PASS")


if __name__ == "__main__":
    main()
