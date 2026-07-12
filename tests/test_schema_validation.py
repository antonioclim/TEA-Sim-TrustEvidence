from __future__ import annotations

import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from trustevidence.envelope import build_signed_envelope
from trustevidence.schema import load_schema
from trustevidence.testing import fixture_emitter_private_key
from trustevidence.validators import validate_envelope, validate_monitoring_event

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data_examples" / "personal_monitoring"
RESULTS = ROOT / "results_expected" / "cmpb_reference"
EMITTED = {
    "access_event.json": "2026-07-01T06:10:00.500Z",
    "aggregation_event.json": "2026-07-01T23:59:59.500Z",
    "cgm_monitoring_object_registration.json": "2026-07-01T06:00:00.500Z",
    "consent_grant_event.json": "2026-07-01T07:00:00.500Z",
    "consent_revocation_event.json": "2026-07-02T07:00:00.500Z",
    "disclosure_event.json": "2026-07-01T10:00:00.500Z",
    "failure_event.json": "2026-07-01T11:00:00.500Z",
    "provenance_transform_event.json": "2026-07-01T09:00:00.500Z",
    "wearable_monitoring_object_registration.json": "2026-07-01T06:05:00.500Z",
}


def test_packaged_schemas_are_valid_draft_2020_12():
    for name in ("monitoring_event", "trust_evidence_envelope", "curation_result"):
        Draft202012Validator.check_schema(load_schema(name))


def test_nine_synthetic_inputs_cover_seven_event_classes_and_validate():
    event_types = set()
    for name in sorted(EMITTED):
        event = json.loads((EXAMPLES / name).read_text(encoding="utf-8"))
        result = validate_monitoring_event(event)
        assert result.accepted, (name, result.issues)
        envelope, _ = build_signed_envelope(
            event,
            emitted_at=EMITTED[name],
            private_key=fixture_emitter_private_key(),
        )
        checked = validate_envelope(envelope)
        assert checked.accepted, (name, checked.issues)
        event_types.add(event["event_type"])
    assert len(event_types) == 7


def test_reference_validation_matrix_has_no_unexpected_outcome():
    rows = list(csv.DictReader((RESULTS / "schema_validation_summary.csv").open(newline="", encoding="utf-8")))
    assert len(rows) == 53
    assert all(row["passed"] == "true" for row in rows)
    negatives = [row for row in rows if row["case_class"] == "negative-control"]
    assert len(negatives) == 34
    assert all(row["observed_outcome"] == "rejected" for row in negatives)


def test_all_required_or_conditional_deletions_rejected():
    rows = list(csv.DictReader((RESULTS / "field_deletion_results.csv").open(newline="", encoding="utf-8")))
    assert len(rows) == 185
    assert all(row["passed"] == "true" and row["observed_outcome"] == "rejected" for row in rows)
