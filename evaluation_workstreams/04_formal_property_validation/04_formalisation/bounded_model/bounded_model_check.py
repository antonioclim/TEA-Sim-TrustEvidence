
from __future__ import annotations

from dataclasses import replace
import csv, itertools, json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from te_backend_upgrade.canonical import CANONICAL_HASH_FIELD, canonical_hash, make_evidence
from te_backend_upgrade.merkle_log import MerkleLog, merkle_root_from_leaves

DOMAIN = [0, 1, 2]
MAX_LEN = 4
failures = []
counters = {
    "sequences_checked": 0,
    "inclusion_receipts_checked": 0,
    "tamper_rejections_checked": 0,
    "prefix_roots_checked": 0,
    "fork_pairs_checked": 0,
    "failures": 0,
}


def check(condition: bool, label: str) -> None:
    if not condition:
        failures.append(label)

for length in range(MAX_LEN + 1):
    for seq in itertools.product(DOMAIN, repeat=length):
        counters["sequences_checked"] += 1
        log = MerkleLog()
        objects = []
        receipts = []
        for pos, val in enumerate(seq):
            obj = make_evidence(val + pos * 100)
            objects.append(obj)
            receipts.append(log.append(obj))
        check(log.root_hash() == merkle_root_from_leaves(log.leaves), f"root-mismatch:{seq}")
        for i, obj in enumerate(objects):
            counters["inclusion_receipts_checked"] += 1
            check(MerkleLog.verify_receipt(obj, receipts[i], expected_tree_size=i + 1), f"receipt-fail:{seq}:{i}")
            tampered = dict(obj)
            tampered["payload_hash"] = "tampered"
            counters["tamper_rejections_checked"] += 1
            check(not MerkleLog.verify_receipt(tampered, receipts[i], expected_tree_size=i + 1), f"tamper-accepted:{seq}:{i}")
            redigested = replace(receipts[i], leaf_index=receipts[i].leaf_index + 1, tree_size=receipts[i].tree_size + 1).with_digest()
            counters["tamper_rejections_checked"] += 1
            check(not MerkleLog.verify_receipt(obj, redigested, expected_tree_size=redigested.tree_size), f"metadata-accepted:{seq}:{i}")
        for prefix in range(length + 1):
            counters["prefix_roots_checked"] += 1
            root = merkle_root_from_leaves(log.leaves[:prefix])
            check(log.verify_consistency_by_prefix(prefix, root), f"prefix-fail:{seq}:{prefix}")
            wrong = root[:-1] + ("0" if root[-1] != "0" else "1")
            check(not log.verify_consistency_by_prefix(prefix, wrong), f"wrong-prefix-accepted:{seq}:{prefix}")

for prefix_len in range(MAX_LEN):
    common = [make_evidence(i) for i in range(prefix_len)]
    left = MerkleLog()
    right = MerkleLog()
    for obj in common:
        left.append(obj); right.append(dict(obj))
    checkpoint = left.root_hash()
    for suffix_len in range(1, MAX_LEN - prefix_len + 1):
        l2 = MerkleLog(); r2 = MerkleLog()
        for obj in common:
            l2.append(obj); r2.append(dict(obj))
        for j in range(suffix_len):
            l2.append(make_evidence(1_000 + prefix_len * 10 + j))
            r2.append(make_evidence(2_000 + prefix_len * 10 + j))
        counters["fork_pairs_checked"] += 1
        check(len(l2.leaves) == len(r2.leaves), "fork-size")
        check(l2.root_hash() != r2.root_hash(), f"fork-undetected:{prefix_len}:{suffix_len}")
        check(l2.verify_consistency_by_prefix(prefix_len, checkpoint), f"left-prefix:{prefix_len}:{suffix_len}")
        check(r2.verify_consistency_by_prefix(prefix_len, checkpoint), f"right-prefix:{prefix_len}:{suffix_len}")

counters["failures"] = len(failures)
out = Path("04_formalisation/bounded_model")
with (out / "bounded_model_summary.json").open("w", encoding="utf-8") as f:
    json.dump({"domain": DOMAIN, "max_len": MAX_LEN, "counters": counters, "failures": failures}, f, indent=2)
with (out / "bounded_model_summary.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["metric", "value"]); [w.writerow([k, v]) for k, v in counters.items()]
with (out / "bounded_model_failures.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["failure"]); [w.writerow([x]) for x in failures]
print(json.dumps(counters, sort_keys=True))
if failures:
    raise SystemExit(1)
