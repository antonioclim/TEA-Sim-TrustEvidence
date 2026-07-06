
from __future__ import annotations

from dataclasses import replace
import json
from typing import Any, Dict

import pytest
pytest.importorskip("hypothesis", reason="optional dependency required for expanded property tests")
from hypothesis import HealthCheck, given, settings, strategies as st

from te_backend_upgrade.canonical import (
    CANONICAL_HASH_FIELD,
    canonical_bytes,
    canonical_hash,
    make_evidence,
    validate_evidence_hash,
)
from te_backend_upgrade.merkle_log import MerkleLog, _leaf_hash, merkle_root_from_leaves

PROP_SETTINGS = settings(max_examples=30, deadline=None, database=None, suppress_health_check=[HealthCheck.too_slow])

json_scalar = st.one_of(st.none(), st.booleans(), st.integers(min_value=-10**5, max_value=10**5), st.text(min_size=0, max_size=16))
json_value = st.recursive(
    json_scalar,
    lambda c: st.lists(c, min_size=0, max_size=3) | st.dictionaries(st.text(min_size=1, max_size=10), c, min_size=0, max_size=3),
    max_leaves=8,
)
json_object = st.dictionaries(
    st.text(min_size=1, max_size=10).filter(lambda s: s != CANONICAL_HASH_FIELD),
    json_value,
    min_size=0,
    max_size=3,
)


def build_log(size: int, *, offset: int = 0):
    log = MerkleLog()
    objects = []
    receipts = []
    for i in range(size):
        obj = make_evidence(offset + i)
        receipt = log.append(obj)
        objects.append(obj)
        receipts.append(receipt)
    return log, objects, receipts


def redigest(receipt, **changes):
    return replace(receipt, **changes).with_digest()


@given(size=st.integers(min_value=1, max_value=32))
@PROP_SETTINGS
def test_p1_append_monotonicity(size: int) -> None:
    log = MerkleLog()
    previous_root = log.root_hash()
    for i in range(size):
        obj = make_evidence(i)
        receipt = log.append(obj)
        assert receipt.leaf_index == i
        assert receipt.tree_size == i + 1
        assert receipt.root_hash == log.root_hash()
        assert log.roots_by_size[i + 1] == receipt.root_hash
        assert log.verify_consistency_by_prefix(i, previous_root)
        assert MerkleLog.verify_receipt(obj, receipt, expected_tree_size=i + 1)
        previous_root = receipt.root_hash


@given(size=st.integers(min_value=1, max_value=32), raw_index=st.integers(min_value=0, max_value=4096))
@PROP_SETTINGS
def test_p2_inclusion_soundness(size: int, raw_index: int) -> None:
    log, objects, receipts = build_log(size)
    index = raw_index % size
    # Receipt roots are append-time roots, so verify the receipt against its own checkpoint.
    assert MerkleLog.verify_receipt(objects[index], receipts[index], expected_tree_size=index + 1)
    assert log.root_hash() == merkle_root_from_leaves(log.leaves)
    if size > 1:
        assert not MerkleLog.verify_receipt(objects[(index + 1) % size], receipts[index], expected_tree_size=index + 1)


@given(size=st.integers(min_value=1, max_value=32), raw_index=st.integers(min_value=0, max_value=4096), field=st.sampled_from(["payload_hash", "policy_version", "consent_state", "actor_role", "subject_ref_token"]))
@PROP_SETTINGS
def test_p3_tamper_rejection(size: int, raw_index: int, field: str) -> None:
    _, objects, receipts = build_log(size)
    index = raw_index % size
    obj = objects[index]
    receipt = receipts[index]
    tampered = dict(obj)
    tampered[field] = f"tampered-{field}"
    assert not validate_evidence_hash(tampered)
    assert not MerkleLog.verify_receipt(tampered, receipt, expected_tree_size=receipt.tree_size)
    rebased = dict(tampered)
    rebased[CANONICAL_HASH_FIELD] = canonical_hash(rebased)
    assert validate_evidence_hash(rebased)
    assert not MerkleLog.verify_receipt(rebased, receipt, expected_tree_size=receipt.tree_size)


@given(obj=json_object)
@PROP_SETTINGS
def test_p4_canonicalisation_determinism(obj: Dict[str, Any]) -> None:
    round_tripped = json.loads(json.dumps(obj, ensure_ascii=False))
    reversed_items = dict(reversed(list(round_tripped.items())))
    assert canonical_bytes(round_tripped) == canonical_bytes(reversed_items)
    assert canonical_hash(round_tripped) == canonical_hash(reversed_items)
    with_hash = dict(round_tripped)
    with_hash[CANONICAL_HASH_FIELD] = "ignored-for-material-hash"
    assert canonical_hash(with_hash) == canonical_hash(round_tripped)


@given(size=st.integers(min_value=1, max_value=32), raw_index=st.integers(min_value=0, max_value=4096))
@PROP_SETTINGS
def test_p5_receipt_binding(size: int, raw_index: int) -> None:
    _, objects, receipts = build_log(size)
    index = raw_index % size
    obj = objects[index]
    receipt = receipts[index]
    assert MerkleLog.verify_receipt(obj, receipt, expected_tree_size=receipt.tree_size)
    assert receipt.leaf_hash == _leaf_hash(obj)

    # Single-field metadata mutations fail through digest mismatch.
    assert not MerkleLog.verify_receipt(obj, replace(receipt, evidence_id="wrong"), expected_tree_size=receipt.tree_size)
    assert not MerkleLog.verify_receipt(obj, replace(receipt, leaf_hash="0" * 64), expected_tree_size=receipt.tree_size)
    assert not MerkleLog.verify_receipt(obj, replace(receipt, leaf_index=receipt.leaf_index + 1), expected_tree_size=receipt.tree_size)
    assert not MerkleLog.verify_receipt(obj, replace(receipt, tree_size=receipt.tree_size + 1), expected_tree_size=receipt.tree_size)
    assert not MerkleLog.verify_receipt(obj, replace(receipt, root_hash="f" * 64), expected_tree_size=receipt.tree_size)

    # Re-digested coherent-looking index/size mutations still fail because the proof is checked against index and size.
    assert not MerkleLog.verify_receipt(obj, redigest(receipt, leaf_index=receipt.leaf_index + 1, tree_size=receipt.tree_size + 1), expected_tree_size=receipt.tree_size + 1)
    
    mutated_proof = [] if receipt.proof else [("right", "0" * 64)]
    assert not MerkleLog.verify_receipt(obj, redigest(receipt, proof=mutated_proof), expected_tree_size=receipt.tree_size)


@given(total_size=st.integers(min_value=1, max_value=32), raw_prefix=st.integers(min_value=0, max_value=4096))
@PROP_SETTINGS
def test_p6_prefix_consistency(total_size: int, raw_prefix: int) -> None:
    log, _, _ = build_log(total_size)
    prefix_size = raw_prefix % (total_size + 1)
    true_root = merkle_root_from_leaves(log.leaves[:prefix_size])
    assert log.verify_consistency_by_prefix(prefix_size, true_root)
    false_root = true_root[:-1] + ("0" if true_root[-1] != "0" else "1")
    assert not log.verify_consistency_by_prefix(prefix_size, false_root)
    assert not log.verify_consistency_by_prefix(total_size + 1, true_root)
    assert not log.verify_consistency_by_prefix(-1, true_root)


@given(common_prefix=st.integers(min_value=0, max_value=16), suffix_len=st.integers(min_value=1, max_value=8))
@PROP_SETTINGS
def test_p7_same_size_root_comparison_detects_forks(common_prefix: int, suffix_len: int) -> None:
    left = MerkleLog()
    right = MerkleLog()
    for i in range(common_prefix):
        left.append(make_evidence(i))
        right.append(make_evidence(i))
    checkpoint = left.root_hash()
    assert right.root_hash() == checkpoint
    for j in range(suffix_len):
        left.append(make_evidence(common_prefix + j))
        right.append(make_evidence(1_000_000 + common_prefix + j))
    assert len(left.leaves) == len(right.leaves)
    assert left.root_hash() != right.root_hash()
    assert left.verify_consistency_by_prefix(common_prefix, checkpoint)
    assert right.verify_consistency_by_prefix(common_prefix, checkpoint)


@given(size=st.integers(min_value=0, max_value=64))
@PROP_SETTINGS
def test_root_frontier_matches_recursive_reference(size: int) -> None:
    log, _, _ = build_log(size)
    assert log.root_hash() == merkle_root_from_leaves(log.leaves)
