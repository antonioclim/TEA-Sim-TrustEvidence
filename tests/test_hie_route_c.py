"""Route C HIE disclosure case tests."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from experiments.build_hie_hero_case import (
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


def _json(outputs: dict[Path, bytes], path: Path):
    return json.loads(outputs[path])


def test_hie_hero_case_builds_and_validates() -> None:
    outputs = build_outputs()
    event = _json(outputs, DEFAULT_OUTPUT / "hie_disclosure_event.json")
    envelope = _json(outputs, DEFAULT_OUTPUT / "signed_envelope_with_receipt.json")
    assert validate_hie_disclosure_event(event).accepted
    assert validate_hie_envelope(envelope).accepted
    assert envelope["profile"] == HIE_ENVELOPE_PROFILE
    assert envelope["evidence_core"]["consent_binding"]["consent_version"] == "3"
    assert envelope["evidence_core"]["policy_binding"]["policy_version"] == "6"
    decision = [item for item in envelope["evidence_core"]["objects"] if item["object_role"] == "decision"]
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


def test_portable_bundle_preserves_exact_envelope_bytes_without_clinical_payload() -> None:
    outputs = build_outputs()
    portable = _json(outputs, FHIR_RESOURCES / "Bundle-portable-evidence-bundle-hie-001.json")
    binary = _json(outputs, FHIR_RESOURCES / "Binary-trustevidence-envelope-hie-001.json")
    exact = outputs[DEFAULT_OUTPUT / "signed_envelope_with_receipt.canonical.json"]
    assert base64.b64decode(binary["data"]) == exact
    resource_types = [entry["resource"]["resourceType"] for entry in portable["entry"]]
    assert "DiagnosticReport" not in resource_types
    assert "Observation" not in resource_types
    assert resource_types.count("AuditEvent") == 2
    assert "Binary" in resource_types
    assert "Provenance" in resource_types


def test_declared_negative_hie_events_are_rejected() -> None:
    outputs = build_outputs()
    missing_decision = _json(outputs, DEFAULT_OUTPUT / "negative" / "hie_event_missing_decision.json")
    payload_leakage = _json(outputs, DEFAULT_OUTPUT / "negative" / "hie_event_payload_leakage.json")
    assert not validate_hie_disclosure_event(missing_decision).accepted
    leakage = validate_hie_disclosure_event(payload_leakage)
    assert not leakage.accepted
    assert "TE-E-MIN-PAYLOAD" in leakage.codes
