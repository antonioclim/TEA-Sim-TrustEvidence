#!/usr/bin/env python3
"""Apply the documented C4 protocol amendment exactly once.

This one-time migration preserves the original failed hosted artifact in
`C4_PROTOCOL_DEVIATION.md` and changes only the expectation registry for the
falsified authorised-backend tree-size case. It does not weaken the verifier.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "experiments" / "run_hie_security_mutations.py"

OLD_TUPLE = '''        (
            "RSIG-005",
            "tree-size",
            "$.backend_receipt.tree_size and inclusion_proof.tree_size",
            lambda x: (
                x["backend_receipt"].__setitem__(
                    "tree_size", x["backend_receipt"]["tree_size"] + 1
                ),
                x["backend_receipt"]["inclusion_proof"].__setitem__(
                    "tree_size", x["backend_receipt"]["inclusion_proof"]["tree_size"] + 1
                ),
            ),
            True,
            "TE-E-PROOF-PATH",
            "Coherently relabelled tree size fails path verification",
        ),
'''

NEW_TUPLE = '''        (
            "LIM-BACKEND-002",
            "validly-signed-alternative-tree-size",
            "$.backend_receipt.tree_size and inclusion_proof.tree_size",
            lambda x: (
                x["backend_receipt"].__setitem__(
                    "tree_size", x["backend_receipt"]["tree_size"] + 1
                ),
                x["backend_receipt"]["inclusion_proof"].__setitem__(
                    "tree_size", x["backend_receipt"]["inclusion_proof"]["tree_size"] + 1
                ),
            ),
            True,
            "PASS",
            "An authorised backend can sign an alternative internally admissible tree-size statement; the receipt does not prove actual log population or completeness",
        ),
'''

OLD_LOOP = '''        candidate = mutate_copy(multi, mutation)
        resign_receipt(candidate, recompute_proof_digest=recompute)
        record_verification(
            rows,
            evidence,
            case_id=case_id,
            case_class="re-signed-malformed-receipt",
            mutation_class=mutation_class,
            target_path=target,
            signing_state="receipt-re-signed-with-authorised-test-key",
            candidate=candidate,
            expected_outcome="rejected",
            expected_code=expected_code,
            notes=notes,
        )
'''

NEW_LOOP = '''        candidate = mutate_copy(multi, mutation)
        resign_receipt(candidate, recompute_proof_digest=recompute)
        authorised_backend_limitation = case_id == "LIM-BACKEND-002"
        record_verification(
            rows,
            evidence,
            case_id=case_id,
            case_class=(
                "limitation-observation"
                if authorised_backend_limitation
                else "re-signed-malformed-receipt"
            ),
            mutation_class=mutation_class,
            target_path=target,
            signing_state="receipt-re-signed-with-authorised-test-key",
            candidate=candidate,
            expected_outcome=(
                "accepted" if authorised_backend_limitation else "rejected"
            ),
            expected_code=("PASS" if authorised_backend_limitation else expected_code),
            notes=notes,
        )
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"C4-PROTOCOL-AMENDMENT: FAIL ({label} matches={count})")
    return text.replace(old, new, 1)


def main() -> int:
    text = RUNNER.read_text(encoding="utf-8")
    if "LIM-BACKEND-002" in text and OLD_TUPLE not in text:
        print("C4-PROTOCOL-AMENDMENT: ALREADY APPLIED")
        return 0
    text = replace_once(text, OLD_TUPLE, NEW_TUPLE, "case tuple")
    text = replace_once(text, OLD_LOOP, NEW_LOOP, "execution loop")
    RUNNER.write_text(text, encoding="utf-8", newline="\n")
    print("C4-PROTOCOL-AMENDMENT: APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
