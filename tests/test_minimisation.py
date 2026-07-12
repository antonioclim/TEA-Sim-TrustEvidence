from __future__ import annotations

import json
from pathlib import Path

from trustevidence.validators import validate_monitoring_event

ROOT = Path(__file__).resolve().parents[1]
NEG = ROOT / "tests/fixtures/negative"


def test_payload_leakage_controls_reject():
    for name in ("payload_leakage_direct.json", "payload_leakage_nested.json"):
        result = validate_monitoring_event(json.loads((NEG / name).read_text()))
        assert not result.accepted
        assert result.primary_code == "TE-E-MIN-PAYLOAD"


def test_direct_identifier_control_rejects():
    result = validate_monitoring_event(json.loads((NEG / "direct_identifier.json").read_text()))
    assert not result.accepted
    assert result.primary_code == "TE-E-MIN-IDENTIFIER"


def test_public_examples_contain_no_raw_value_or_nonce_keys():
    prohibited = {"glucose_value", "samples", "valueQuantity", "nonce", "patient_name", "email"}
    for path in (ROOT / "data_examples/personal_monitoring").glob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert all(f'"{key}"' not in text for key in prohibited)


def test_uuid_urn_is_not_misclassified_as_phone_identifier():
    from trustevidence.validators import _leakage_issues

    value = {"evidence_id": "urn:uuid:da300e85-7928-5288-9133-34a615ace607"}
    assert _leakage_issues(value) == []
