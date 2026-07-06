from dataclasses import asdict

from te_backend_upgrade.canonical import canonical_hash, make_evidence
from te_backend_upgrade.merkle_log import MerkleLog
from te_backend_upgrade.rekor_adapter import build_synthetic_rekor_payload


def test_append_receipts_are_monotonic():
    log = MerkleLog()
    receipts = [log.append(make_evidence(i)) for i in range(5)]
    assert [r.tree_size for r in receipts] == [1, 2, 3, 4, 5]
    assert [r.leaf_index for r in receipts] == [0, 1, 2, 3, 4]
    assert len({r.root_hash for r in receipts}) == 5


def test_inclusion_and_tamper_rejection():
    log = MerkleLog()
    objects = []
    for i in range(64):
        obj = make_evidence(i)
        log.append(obj)
        objects.append(obj)
    receipt = log.inclusion_receipt(17)
    assert MerkleLog.verify_receipt(objects[17], receipt)
    tampered = dict(objects[17])
    tampered["payload_hash"] = "bad"
    assert not MerkleLog.verify_receipt(tampered, receipt)


def test_receipt_binding_rejects_wrong_id():
    log = MerkleLog()
    obj = make_evidence(1)
    log.append(obj)
    receipt = asdict(log.inclusion_receipt(0))
    receipt["evidence_id"] = "wrong"
    assert not MerkleLog.verify_receipt(obj, receipt)


def test_canonicalisation_stable_under_key_order():
    assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})


def test_prefix_consistency_check():
    log = MerkleLog()
    for i in range(32):
        log.append(make_evidence(i))
    assert log.verify_consistency_by_prefix(16, log.roots_by_size[16])
    assert not log.verify_consistency_by_prefix(16, log.roots_by_size[17])


def test_rekor_payload_is_hash_commitment_only():
    obj = make_evidence(12, backend="A3_REKOR_ADAPTER")
    payload = build_synthetic_rekor_payload(obj)
    assert payload["kind"] == "hashedrekord"
    assert payload["spec"]["data"]["hash"]["algorithm"] == "sha256"
    assert "payload_hash" not in str(payload["spec"]["signature"])
