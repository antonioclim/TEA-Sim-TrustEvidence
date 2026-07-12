"""Hypothesis checks for the local A2 Merkle and retained-state model.

These tests explore generated finite examples.  They are executable property
checks, not a mathematical or mechanised formal proof.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from hypothesis import HealthCheck, given, settings, strategies as st

from trustevidence.backends.a2_merkle import (
    LocalA2MerkleLog,
    RetainedCheckpoint,
    attach_receipt,
    consistency_path,
    inclusion_path,
    leaf_hash,
    merkle_tree_hash,
    verify_consistency,
    verify_envelope_receipt,
    verify_inclusion,
)
from trustevidence.crypto import sign_receipt
from trustevidence.envelope import build_signed_envelope
from trustevidence.hashing import proof_digest_hex
from trustevidence.testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data_examples" / "personal_monitoring"

PROP = settings(
    max_examples=80,
    deadline=None,
    database=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)


def _digest(value: bytes) -> str:
    return hashlib.sha256(b"te-cmpb-property-v1:" + value).hexdigest()


def _flip_hex(value: str) -> str:
    raw = bytearray.fromhex(value)
    raw[0] ^= 1
    return raw.hex()


def _access_envelope() -> tuple[dict, str]:
    event = json.loads((EXAMPLES / "access_event.json").read_text(encoding="utf-8"))
    return build_signed_envelope(
        event,
        emitted_at="2026-07-01T06:10:00.500Z",
        private_key=fixture_emitter_private_key(),
    )


def _verify(envelope: dict, *, checkpoint=None, consistency_proof=None):
    return verify_envelope_receipt(
        envelope,
        emitter_keys={FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
        receipt_keys={FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
        retained_checkpoint=checkpoint,
        consistency_proof=consistency_proof,
    )


@PROP
@given(values=st.lists(st.binary(min_size=0, max_size=24), min_size=2, max_size=48))
def test_append_monotonicity_and_prefix_roots(values: list[bytes]) -> None:
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    prefix_roots: list[str] = []
    for expected_index, value in enumerate(values):
        previous_size = log.tree_size
        previous_root = log.root_digest
        observed_index = log.append_core_digest(_digest(expected_index.to_bytes(2, "big") + value))
        assert observed_index == expected_index
        assert log.tree_size == previous_size + 1
        assert log.root_digest_at(previous_size) == previous_root
        prefix_roots.append(log.root_digest)
    for size, root in enumerate(prefix_roots, start=1):
        assert log.root_digest_at(size) == root


@PROP
@given(
    entries=st.lists(st.binary(min_size=0, max_size=24), min_size=2, max_size=64),
    raw_index=st.integers(min_value=0, max_value=10_000),
    raw_component=st.integers(min_value=0, max_value=10_000),
)
def test_inclusion_soundness_and_path_mutation_rejection(
    entries: list[bytes], raw_index: int, raw_component: int
) -> None:
    # Prefix each generated value with its position so the test concerns
    # index binding rather than the distinct issue of duplicate leaf material.
    positioned = [position.to_bytes(4, "big") + value for position, value in enumerate(entries)]
    index = raw_index % len(positioned)
    root = merkle_tree_hash(positioned)
    path = inclusion_path(positioned, index)
    assert verify_inclusion(
        leaf_hash(positioned[index]),
        leaf_index=index,
        tree_size=len(entries),
        siblings=path,
        root_hash=root,
    )
    assert not verify_inclusion(
        leaf_hash(positioned[index]),
        leaf_index=(index + 1) % len(positioned),
        tree_size=len(positioned),
        siblings=path,
        root_hash=root,
    )
    mutated = list(path)
    component = raw_component % len(mutated)
    changed = bytearray(mutated[component])
    changed[0] ^= 1
    mutated[component] = bytes(changed)
    assert not verify_inclusion(
        leaf_hash(positioned[index]),
        leaf_index=index,
        tree_size=len(positioned),
        siblings=mutated,
        root_hash=root,
    )
    wrong_root = bytearray(root)
    wrong_root[0] ^= 1
    assert not verify_inclusion(
        leaf_hash(positioned[index]),
        leaf_index=index,
        tree_size=len(positioned),
        siblings=path,
        root_hash=bytes(wrong_root),
    )


@PROP
@given(
    entries=st.lists(st.binary(min_size=0, max_size=24), min_size=2, max_size=64),
    raw_first=st.integers(min_value=1, max_value=10_000),
    raw_component=st.integers(min_value=0, max_value=10_000),
)
def test_consistency_soundness_and_mutation_rejection(
    entries: list[bytes], raw_first: int, raw_component: int
) -> None:
    first = 1 + (raw_first % (len(entries) - 1))
    second = len(entries)
    path = consistency_path(entries, first, second)
    first_root = merkle_tree_hash(entries[:first])
    second_root = merkle_tree_hash(entries)
    assert verify_consistency(
        first_size=first,
        second_size=second,
        first_root=first_root,
        second_root=second_root,
        hashes=path,
    )
    assert not verify_consistency(
        first_size=first,
        second_size=second,
        first_root=first_root,
        second_root=second_root,
        hashes=[],
    )
    assert not verify_consistency(
        first_size=first,
        second_size=second,
        first_root=first_root,
        second_root=second_root,
        hashes=path + [bytes(32)],
    )
    mutated = list(path)
    component = raw_component % len(mutated)
    changed = bytearray(mutated[component])
    changed[-1] ^= 1
    mutated[component] = bytes(changed)
    assert not verify_consistency(
        first_size=first,
        second_size=second,
        first_root=first_root,
        second_root=second_root,
        hashes=mutated,
    )


@PROP
@given(
    extras=st.lists(st.binary(min_size=0, max_size=24), min_size=1, max_size=24),
    mutation=st.sampled_from(["root", "proof", "leaf-index", "tree-size", "core-digest"]),
)
def test_receipt_binding_rejects_resigned_coherent_looking_mutations(
    extras: list[bytes], mutation: str
) -> None:
    envelope, core_digest = _access_envelope()
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    log.append_core_digest(core_digest)
    for position, value in enumerate(extras, start=1):
        log.append_core_digest(_digest(position.to_bytes(2, "big") + value))
    receipt = log.issue_receipt(
        0,
        issued_at="2026-07-03T02:00:00.000Z",
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    complete = attach_receipt(envelope, receipt)
    assert _verify(complete).accepted

    candidate = deepcopy(complete)
    changed_receipt = candidate["backend_receipt"]
    if mutation == "root":
        changed_receipt["root_digest"] = _flip_hex(changed_receipt["root_digest"])
    elif mutation == "proof":
        changed_receipt["inclusion_proof"]["siblings"][0] = _flip_hex(
            changed_receipt["inclusion_proof"]["siblings"][0]
        )
        changed_receipt["inclusion_proof_digest"] = proof_digest_hex(changed_receipt["inclusion_proof"])
    elif mutation == "leaf-index":
        changed_receipt["leaf_index"] = 1
        changed_receipt["inclusion_proof"]["leaf_index"] = 1
        changed_receipt["inclusion_proof_digest"] = proof_digest_hex(changed_receipt["inclusion_proof"])
    elif mutation == "tree-size":
        changed_receipt["tree_size"] += 1
        changed_receipt["inclusion_proof"]["tree_size"] += 1
        changed_receipt["inclusion_proof_digest"] = proof_digest_hex(changed_receipt["inclusion_proof"])
    else:
        changed_receipt["core_digest"] = _flip_hex(changed_receipt["core_digest"])

    changed_receipt.pop("receipt_signature", None)
    signature, _ = sign_receipt(
        changed_receipt,
        private_key=fixture_backend_private_key(),
        key_id=FIXTURE_BACKEND_KEY_ID,
    )
    changed_receipt["receipt_signature"] = signature
    assert not _verify(candidate).accepted


@PROP
@given(
    common=st.lists(st.binary(min_size=0, max_size=16), min_size=0, max_size=10),
    suffix_len=st.integers(min_value=1, max_value=8),
)
def test_same_size_root_comparison_detects_verifier_visible_fork(
    common: list[bytes], suffix_len: int
) -> None:
    envelope, core_digest = _access_envelope()
    left = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    right = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    left.append_core_digest(core_digest)
    right.append_core_digest(core_digest)
    for position, value in enumerate(common, start=1):
        digest = _digest(position.to_bytes(2, "big") + value)
        left.append_core_digest(digest)
        right.append_core_digest(digest)
    for position in range(suffix_len):
        left.append_core_digest(_digest(b"left:" + position.to_bytes(2, "big")))
        right.append_core_digest(_digest(b"right:" + position.to_bytes(2, "big")))
    assert left.tree_size == right.tree_size
    assert left.root_digest != right.root_digest

    retained = RetainedCheckpoint(
        FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, left.tree_size, left.root_digest
    )
    receipt = right.issue_receipt(
        0,
        issued_at="2026-07-03T02:00:01.000Z",
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    result = _verify(attach_receipt(envelope, receipt), checkpoint=retained)
    assert not result.accepted
    assert "TE-E-CHECKPOINT-FORK" in result.codes


@PROP
@given(
    prefix_extra=st.lists(st.binary(min_size=0, max_size=16), min_size=0, max_size=8),
    extension=st.lists(st.binary(min_size=0, max_size=16), min_size=1, max_size=8),
)
def test_larger_checkpoint_requires_and_accepts_valid_consistency_proof(
    prefix_extra: list[bytes], extension: list[bytes]
) -> None:
    envelope, core_digest = _access_envelope()
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    log.append_core_digest(core_digest)
    for position, value in enumerate(prefix_extra, start=1):
        log.append_core_digest(_digest(b"p" + position.to_bytes(2, "big") + value))
    retained = RetainedCheckpoint(
        FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, log.tree_size, log.root_digest
    )
    for position, value in enumerate(extension, start=1):
        log.append_core_digest(_digest(b"e" + position.to_bytes(2, "big") + value))
    receipt = log.issue_receipt(
        0,
        issued_at="2026-07-03T02:00:02.000Z",
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    complete = attach_receipt(envelope, receipt)
    missing = _verify(complete, checkpoint=retained)
    assert not missing.accepted
    assert "TE-E-CONSISTENCY-MISSING" in missing.codes

    proof = log.issue_consistency_proof(retained.tree_size)
    accepted = _verify(complete, checkpoint=retained, consistency_proof=proof)
    assert accepted.accepted, accepted.issues

    malformed = deepcopy(proof)
    malformed["hashes"][0] = _flip_hex(malformed["hashes"][0])
    rejected = _verify(complete, checkpoint=retained, consistency_proof=malformed)
    assert not rejected.accepted
    assert "TE-E-CONSISTENCY-PATH" in rejected.codes
