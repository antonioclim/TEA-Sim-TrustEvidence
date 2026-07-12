from __future__ import annotations

import json
from pathlib import Path

from trustevidence.validators import validate_monitoring_event

ROOT = Path(__file__).resolve().parents[1]
NEG = ROOT / "tests/fixtures/negative"


def check(name: str, code: str):
    result = validate_monitoring_event(json.loads((NEG / name).read_text()))
    assert not result.accepted
    assert result.primary_code == code, (name, result.issues)


def test_event_semantic_controls():
    check("aggregation_negative_count.json", "TE-E-AGGREGATION-COUNT")
    check("failure_missing_code.json", "TE-E-SCHEMA-BRANCH")
    check("inconsistent_subject_reference.json", "TE-E-SUBJECT-CONSISTENCY")
    check("invalid_consent_transition.json", "TE-E-CONSENT-STATE")
    check("malformed_timestamp.json", "TE-E-TIMESTAMP-FORMAT")
    check("missing_actor_access.json", "TE-E-SCHEMA-BRANCH")
    check("missing_policy_access.json", "TE-E-SCHEMA-BRANCH")
    check("provenance_missing_input.json", "TE-E-OBJECT-ROLE")
