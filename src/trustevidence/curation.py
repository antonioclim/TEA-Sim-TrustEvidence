"""Curation path from MonitoringEvent metadata to an inspectable evidence envelope."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import __version__
from .envelope import build_fixture_envelope
from .profiles import (
    CANONICALISATION_PROFILE, ENVELOPE_PROFILE, HASH_PROFILE, MINIMISATION_PROFILE,
    RECEIPT_PROFILE, RESULT_PROFILE, SOFTWARE_RELEASE_LABEL,
)
from .hashing import core_digest_hex
from .validators import ValidationResult, validate_envelope, validate_monitoring_event


@dataclass(frozen=True, slots=True)
class CurationOutput:
    envelope: dict[str, Any] | None
    result: dict[str, Any]
    validation: ValidationResult


def _profile_versions() -> dict[str, str]:
    return {
        "envelope": ENVELOPE_PROFILE,
        "minimisation": MINIMISATION_PROFILE,
        "canonicalisation": CANONICALISATION_PROFILE,
        "hash": HASH_PROFILE,
        "receipt": RECEIPT_PROFILE,
        "curation_result": RESULT_PROFILE,
    }


def _result_base(event: dict[str, Any], run_id: str) -> dict[str, Any]:
    return {
        "result_version": "1.0.0",
        "profile": RESULT_PROFILE,
        "run_id": run_id,
        "method_version": SOFTWARE_RELEASE_LABEL,
        "profile_versions": _profile_versions(),
        "input_event_id": event.get("source_event_id", "urn:te:event:unavailable"),
        "event_type": event.get("event_type", "failure-event"),
        "software_version": __version__,
        "schema_versions": {
            "monitoring_event": "1.0.0",
            "trust_evidence_envelope": "2.1.0",
            "curation_result": "1.0.0",
        },
        "output_paths": [],
        "deterministic_fields": ["event-type", "input-event-id", "outcome", "stages"],
        "non_deterministic_fields": [],
    }


def curate_monitoring_event(event: dict[str, Any], *, run_id: str, emitted_at: str) -> CurationOutput:
    result = _result_base(event, run_id)
    input_validation = validate_monitoring_event(event)
    if not input_validation.accepted:
        issue = input_validation.issues[0]
        result.update({
            "stages": [
                {"stage": "detect", "status": "pass"},
                {"stage": "select", "status": "fail", "error_code": issue.code},
            ],
            "outcome": "rejected",
            "failed_stage": "select",
            "error_code": issue.code,
        })
        return CurationOutput(None, result, input_validation)

    envelope = build_fixture_envelope(event, emitted_at=emitted_at)
    envelope_validation = validate_envelope(envelope)
    if not envelope_validation.accepted:
        issue = envelope_validation.issues[0]
        result.update({
            "stages": [
                {"stage": "detect", "status": "pass"},
                {"stage": "select", "status": "pass"},
                {"stage": "normalise", "status": "pass"},
                {"stage": "minimise", "status": "pass"},
                {"stage": "validate", "status": "fail", "error_code": issue.code},
            ],
            "outcome": "rejected",
            "failed_stage": "validate",
            "error_code": issue.code,
        })
        return CurationOutput(None, result, envelope_validation)

    result.update({
        "stages": [
            {"stage": "detect", "status": "pass"},
            {"stage": "select", "status": "pass"},
            {"stage": "normalise", "status": "pass"},
            {"stage": "minimise", "status": "pass"},
            {"stage": "validate", "status": "pass"},
            {"stage": "canonicalise", "status": "pass"},
            {"stage": "sign", "status": "pass"},
            {"stage": "append", "status": "deferred", "detail_code": "TE-DEFERRED-RECEIPT-LAYER"},
            {"stage": "verify", "status": "deferred", "detail_code": "TE-DEFERRED-RECEIPT-LAYER"},
            {"stage": "preserve", "status": "deferred", "detail_code": "TE-DEFERRED-ARCHIVE-LAYER"},
        ],
        "outcome": "accepted",
        "evidence_core_digest": core_digest_hex(envelope["evidence_core"], envelope_profile=ENVELOPE_PROFILE),
        "deterministic_fields": ["event-type", "input-event-id", "outcome", "stages", "evidence-core-digest"],
        "output_paths": [f"results_expected/cmpb_reference/generated_envelopes/{run_id}.json"],
    })
    return CurationOutput(envelope, result, envelope_validation)
