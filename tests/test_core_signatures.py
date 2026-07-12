from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from trustevidence.crypto import verify_evidence_core_signature
from trustevidence.envelope import build_signed_envelope
from trustevidence.testing import FIXTURE_EMITTER_KEY_ID, fixture_emitter_private_key

ROOT = Path(__file__).resolve().parents[1]


def build():
    event = json.loads((ROOT / "data_examples/personal_monitoring/access_event.json").read_text())
    return build_signed_envelope(event, emitted_at="2026-07-01T06:10:00.500Z", private_key=fixture_emitter_private_key())[0]


def test_fixture_core_signature_verifies():
    envelope = build()
    result = verify_evidence_core_signature(
        envelope["evidence_core"],
        {FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
    )
    assert result.accepted


def test_core_mutation_breaks_signature():
    envelope = build()
    altered = deepcopy(envelope["evidence_core"])
    altered["purpose_code"] = "research"
    result = verify_evidence_core_signature(altered, {FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()})
    assert not result.accepted
    assert result.code == "TE-E-CORE-SIGNATURE"


def test_unknown_key_identifier_is_rejected():
    envelope = build()
    result = verify_evidence_core_signature(envelope["evidence_core"], {})
    assert not result.accepted
