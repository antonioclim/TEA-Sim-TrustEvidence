from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from te_backend_upgrade.canonical import make_evidence
from te_backend_upgrade.merkle_log import MerkleLog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="benchmark_outputs/tamper_detection_results.csv")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    log = MerkleLog()
    objects = []
    for i in range(256):
        obj = make_evidence(i, backend="A2_MERKLE")
        log.append(obj)
        objects.append(obj)
    target_index = 77
    target = objects[target_index]
    receipt = log.inclusion_receipt(target_index)

    cases = []
    cases.append({"case_id": "T1", "property": "valid_inclusion_receipt", "expected": True, "observed": MerkleLog.verify_receipt(target, receipt)})

    tampered_payload = dict(target)
    tampered_payload["payload_hash"] = "0" * 64
    cases.append({"case_id": "T2", "property": "payload_tamper_rejection", "expected": False, "observed": MerkleLog.verify_receipt(tampered_payload, receipt)})

    rec_bad_root = asdict(receipt)
    rec_bad_root["root_hash"] = "f" * 64
    cases.append({"case_id": "T3", "property": "root_tamper_rejection", "expected": False, "observed": MerkleLog.verify_receipt(target, rec_bad_root)})

    rec_bad_proof = asdict(receipt)
    rec_bad_proof["proof"] = list(rec_bad_proof["proof"])
    side, sibling = rec_bad_proof["proof"][0]
    rec_bad_proof["proof"][0] = (side, "e" * 64)
    cases.append({"case_id": "T4", "property": "proof_tamper_rejection", "expected": False, "observed": MerkleLog.verify_receipt(target, rec_bad_proof)})

    rec_bad_id = asdict(receipt)
    rec_bad_id["evidence_id"] = "wrong-evidence-id"
    cases.append({"case_id": "T5", "property": "receipt_binding_rejection", "expected": False, "observed": MerkleLog.verify_receipt(target, rec_bad_id)})

    cases.append({"case_id": "T6", "property": "prefix_consistency_valid", "expected": True, "observed": log.verify_consistency_by_prefix(128, log.roots_by_size[128])})
    cases.append({"case_id": "T7", "property": "prefix_consistency_wrong_root_rejected", "expected": False, "observed": log.verify_consistency_by_prefix(128, log.roots_by_size[129])})

    for c in cases:
        c["status"] = "pass" if c["expected"] == c["observed"] else "fail"
        c["interpretation"] = "local reference property/tamper check"

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "property", "expected", "observed", "status", "interpretation"])
        writer.writeheader()
        writer.writerows(cases)
    failed = [c for c in cases if c["status"] != "pass"]
    print(f"wrote {out}; failed={len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
