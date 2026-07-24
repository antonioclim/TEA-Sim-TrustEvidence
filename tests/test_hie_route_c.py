"""Route C HIE disclosure case tests."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from experiments.run_hie_hero_case import (
    DEFAULT_OUTPUT,
    FHIR_RESOURCES,
    HIE_COMMITMENT_CONTEXT,
    HIE_REPRESENTATION_PROFILE,
    NONCE,
    build_outputs,
)
from trustevidence.crypto import verify_payload_commitment
from trustevidence.hie import HIE_ENVELOPE_PROFILE
from trustevidence.hie_validation import validate_hie_disclosure_event, validate_hie_envelope

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REFERENCE = "DiagnosticReport/diagnostic-report-hie-001/_history/2"
SOURCE_IDENTIFIER_SYSTEM = "urn:trustevidence:identifier:source-resource"


def _json(outputs: dict[Path, bytes], path: Path):
    return json.loads(outputs[path])


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_hie_hero_case_builds_and_validates() -> None:
    outputs = build_outputs()
    event = _json(outputs, DEFAULT_OUTPUT / "hie_disclosure_event.json")
    envelope = _json(outputs, DEFAULT_OUTPUT / "signed_envelope_with_receipt.json")
    assert validate_hie_disclosure_event(event).accepted
    assert validate_hie_envelope(envelope).accepted
    assert envelope["profile"] == HIE_ENVELOPE_PROFILE
    assert envelope["evidence_core"]["consent_binding"]["consent_version"] == "3"
    assert envelope["evidence_core"]["policy_binding"]["policy_version"] == "6"
    decision = [
        item for item in envelope["evidence_core"]["objects"]
        if item["object_role"] == "decision"
    ]
    assert decision[0]["object_ref_token"] == "urn:te:decision:D-204"


def test_hie_payload_commitment_binds_withheld_source_bundle() -> None:
    outputs = build_outputs()
    event = _json(outputs, DEFAULT_OUTPUT / "hie_disclosure_event.json")
    source = outputs[DEFAULT_OUTPUT / "source" / "source_clinical_bundle.canonical.json"]
    target = [item for item in event["object_contexts"] if item["object_role"] == "target"][0]
    binding = target["payload_binding"]
    assert verify_payload_commitment(
        binding["commitment"],
        source,
        nonce=NONCE,
        representation_profile=HIE_REPRESENTATION_PROFILE,
        commitment_context=HIE_COMMITMENT_CONTEXT,
    )
    assert b'"valueQuantity"' in source
    assert b'"value":140' in source
    assert b'"value":4' in source
    assert b'"value":1' in source


def test_portable_bundle_preserves_exact_envelope_bytes_without_clinical_payload() -> None:
    outputs = build_outputs()
    portable = _json(
        outputs, FHIR_RESOURCES / "Bundle-portable-evidence-bundle-hie-001.json"
    )
    binary = _json(
        outputs, FHIR_RESOURCES / "Binary-trustevidence-envelope-hie-001.json"
    )
    document = _json(
        outputs,
        FHIR_RESOURCES / "DocumentReference-trustevidence-document-hie-001.json",
    )
    exact = outputs[DEFAULT_OUTPUT / "signed_envelope_with_receipt.canonical.json"]
    assert base64.b64decode(binary["data"]) == exact
    assert binary["contentType"] == "application/json"
    assert document["content"][0]["attachment"]["contentType"] == "application/json"
    resource_types = [entry["resource"]["resourceType"] for entry in portable["entry"]]
    assert "DiagnosticReport" not in resource_types
    assert "Observation" not in resource_types
    assert resource_types.count("AuditEvent") == 2
    assert "Binary" in resource_types
    assert "Provenance" in resource_types


def test_source_custody_uses_versioned_identifier_not_dangling_reference() -> None:
    outputs = build_outputs()
    portable = _json(
        outputs, FHIR_RESOURCES / "Bundle-portable-evidence-bundle-hie-001.json"
    )
    source_identifiers = []
    dangling = []
    for item in _walk(portable):
        if item.get("reference") == SOURCE_REFERENCE:
            dangling.append(item)
        identifier = item.get("identifier")
        if (
            item.get("type") == "DiagnosticReport"
            and isinstance(identifier, dict)
            and identifier.get("system") == SOURCE_IDENTIFIER_SYSTEM
            and identifier.get("value") == SOURCE_REFERENCE
        ):
            source_identifiers.append(item)
    assert not dangling
    assert len(source_identifiers) == 3


def test_fixture_devices_do_not_use_undefined_type_codesystem() -> None:
    outputs = build_outputs()
    for resource_id in ("evidence-service-a", "authorisation-service-a"):
        device = _json(outputs, FHIR_RESOURCES / f"Device-{resource_id}.json")
        assert "type" not in device


def test_declared_negative_hie_events_are_rejected() -> None:
    outputs = build_outputs()
    missing_decision = _json(
        outputs, DEFAULT_OUTPUT / "negative" / "hie_event_missing_decision.json"
    )
    payload_leakage = _json(
        outputs, DEFAULT_OUTPUT / "negative" / "hie_event_payload_leakage.json"
    )
    assert not validate_hie_disclosure_event(missing_decision).accepted
    leakage = validate_hie_disclosure_event(payload_leakage)
    assert not leakage.accepted
    assert "TE-E-MIN-PAYLOAD" in leakage.codes


def test_negative_portable_bundle_contains_the_deliberate_observation() -> None:
    outputs = build_outputs()
    negative = _json(
        outputs,
        ROOT
        / "standards"
        / "fhir_ig"
        / "negative"
        / "Bundle-portable-evidence-with-clinical-payload.json",
    )
    resource_types = [entry["resource"]["resourceType"] for entry in negative["entry"]]
    assert resource_types[-1] == "Observation"
