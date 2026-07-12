from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from trustevidence.backends.a2_merkle import (
    LocalA2MerkleLog, RetainedCheckpoint, attach_receipt, consistency_path,
    inclusion_path, leaf_hash, merkle_tree_hash, verify_consistency,
    verify_envelope_receipt, verify_inclusion,
)
from trustevidence.envelope import build_signed_envelope
from trustevidence.testing import (
    FIXTURE_BACKEND_ID, FIXTURE_BACKEND_KEY_ID, FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID, fixture_backend_private_key, fixture_emitter_private_key,
)

ROOT = Path(__file__).resolve().parents[1]


def verify(envelope, *, checkpoint=None, consistency_proof=None):
    return verify_envelope_receipt(
        envelope,
        emitter_keys={FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
        receipt_keys={FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
        retained_checkpoint=checkpoint,
        consistency_proof=consistency_proof,
    )


def test_fixed_three_leaf_oracle_and_all_generated_paths_through_32():
    entries = [b"a", b"b", b"c"]
    assert merkle_tree_hash(entries).hex() == "36642e73c2540ab121e3a6bf9545b0a24982cd830eb13d3cd19de3ce6c021ec1"
    for size in range(1, 33):
        items = [f"leaf:{i}".encode() for i in range(size)]
        root = merkle_tree_hash(items)
        for index, item in enumerate(items):
            path = inclusion_path(items, index)
            assert verify_inclusion(leaf_hash(item), leaf_index=index, tree_size=size, siblings=path, root_hash=root)


def test_receipt_verifies_and_proof_path_mutation_rejects():
    event = json.loads((ROOT / "data_examples/personal_monitoring/access_event.json").read_text())
    envelope, digest = build_signed_envelope(event, emitted_at="2026-07-01T06:10:00.500Z", private_key=fixture_emitter_private_key())
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    log.append_core_digest(digest)
    log.append_core_digest(hashlib.sha256(b"other").hexdigest())
    receipt = log.issue_receipt(0, issued_at="2026-07-03T04:00:00.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
    complete = attach_receipt(envelope, receipt)
    assert verify(complete).accepted
    altered = deepcopy(complete)
    altered["backend_receipt"]["inclusion_proof"]["siblings"][0] = "00" * 32
    assert not verify(altered).accepted


def test_all_consistency_prefixes_through_48_and_length_changes():
    entries = [hashlib.sha256(f"entry:{index}".encode()).digest() for index in range(48)]
    for second in range(2, 49):
        second_root = merkle_tree_hash(entries[:second])
        for first in range(1, second):
            proof = consistency_path(entries, first, second)
            first_root = merkle_tree_hash(entries[:first])
            assert verify_consistency(first_size=first, second_size=second, first_root=first_root, second_root=second_root, hashes=proof)
            assert not verify_consistency(first_size=first, second_size=second, first_root=first_root, second_root=second_root, hashes=proof + [bytes(32)])


def test_larger_retained_checkpoint_requires_consistency_proof():
    event = json.loads((ROOT / "data_examples/personal_monitoring/access_event.json").read_text())
    envelope, digest = build_signed_envelope(event, emitted_at="2026-07-01T06:10:00.500Z", private_key=fixture_emitter_private_key())
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    log.append_core_digest(digest)
    for index in range(3):
        log.append_core_digest(hashlib.sha256(f"prefix:{index}".encode()).hexdigest())
    checkpoint = RetainedCheckpoint(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, log.tree_size, log.root_digest)
    for index in range(3):
        log.append_core_digest(hashlib.sha256(f"extension:{index}".encode()).hexdigest())
    receipt = log.issue_receipt(0, issued_at="2026-07-03T04:00:00.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
    complete = attach_receipt(envelope, receipt)
    assert "TE-E-CONSISTENCY-MISSING" in verify(complete, checkpoint=checkpoint).codes
    proof = log.issue_consistency_proof(checkpoint.tree_size)
    assert verify(complete, checkpoint=checkpoint, consistency_proof=proof).accepted
