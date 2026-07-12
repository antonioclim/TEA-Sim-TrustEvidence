from __future__ import annotations

import json
from pathlib import Path

from trustevidence.backends.a2_merkle import LocalA2MerkleLog, attach_receipt, verify_envelope_receipt
from trustevidence.envelope import build_signed_envelope
from trustevidence.harness.workload import iter_synthetic_events, load_event_templates, sample_indices
from trustevidence.testing import (
    FIXTURE_BACKEND_ID, FIXTURE_BACKEND_KEY_ID, FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID, fixture_backend_private_key, fixture_emitter_private_key,
)
from trustevidence.validators import validate_envelope

ROOT = Path(__file__).resolve().parents[1]


def test_small_integrated_passage():
    templates = load_event_templates(ROOT / "data_examples/personal_monitoring")
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    sampled = set(sample_indices(16, 8))
    envelopes = {}
    for index, _, event, emitted in iter_synthetic_events(templates, descriptor_id="W16", repetition=1, tree_size=16):
        envelope, digest = build_signed_envelope(event, emitted_at=emitted, private_key=fixture_emitter_private_key())
        assert validate_envelope(envelope).accepted
        assert log.append_core_digest(digest) == index
        if index in sampled:
            envelopes[index] = envelope
    assert log.tree_size == 16
    for index in sorted(sampled):
        receipt = log.issue_receipt(index, issued_at="2026-07-03T04:00:00.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
        result = verify_envelope_receipt(
            attach_receipt(envelopes[index], receipt),
            emitter_keys={FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
            receipt_keys={FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
            expected_backend_id=FIXTURE_BACKEND_ID,
            expected_log_id=FIXTURE_LOG_ID,
        )
        assert result.accepted
