#!/usr/bin/env python3
"""Finite executable exploration of the declared verification boundary.

The model enumerates a small input alphabet and bounded sequence lengths.  It
is a systematic finite check, not a formal proof for unbounded logs or an
operational security assessment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from trustevidence.backends.a2_merkle import (  # noqa: E402
    LocalA2MerkleLog,
    RetainedCheckpoint,
    attach_receipt,
    consistency_path,
    inclusion_path,
    leaf_hash,
    merkle_tree_hash,
    node_hash,
    verify_consistency,
    verify_envelope_receipt,
    verify_inclusion,
)
from trustevidence.canonical import canonicalise_te  # noqa: E402
from trustevidence.crypto import sign_receipt  # noqa: E402
from trustevidence.envelope import build_signed_envelope  # noqa: E402
from trustevidence.hashing import proof_digest_hex  # noqa: E402
from trustevidence.testing import (  # noqa: E402
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

RUN_ID = "cmpb-bounded-checks-001"
DOMAIN = (0, 1, 2)
MAX_SEQUENCE_LENGTH = 5

PROPERTY_META = {
    "P1": ("append monotonicity", "Finite append transitions preserve earlier prefix roots and increment size by one."),
    "P2": ("inclusion soundness", "Generated inclusion paths reconstruct the bounded root; changed paths, roots, or indices reject for position-distinguished leaves."),
    "P3": ("tamper rejection", "Changed Merkle components and re-signed receipt metadata reject under the bounded controls."),
    "P4": ("canonicalisation determinism", "Finite admissible JSON objects canonicalise identically under key reordering and differently after an added semantic field."),
    "P5": ("receipt binding", "Signed receipt fields remain bound to the evidence core, expected backend identity, and inclusion path."),
    "P6": ("payload non-disclosure", "The public fixture contains a commitment but no nonce, raw payload, sample array, or physiological value field."),
    "P7": ("same-size fork comparison", "Verifier-visible same-size checkpoints with different roots are distinguished."),
    "P8": ("prefix consistency", "RFC-9162-shaped consistency paths verify valid bounded extensions and reject missing, altered, short, long, or mismatched proofs."),
}


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def iterative_root(entries: list[bytes]) -> bytes:
    """Independent stack-form root calculation."""

    if not entries:
        return hashlib.sha256(b"").digest()
    stack: list[bytes] = []
    for index, entry in enumerate(entries):
        stack.append(hashlib.sha256(b"\x00" + entry).digest())
        merge_count = 0
        value = index
        while value & 1:
            merge_count += 1
            value >>= 1
        for _ in range(merge_count):
            right = stack.pop()
            left = stack.pop()
            stack.append(hashlib.sha256(b"\x01" + left + right).digest())
    while len(stack) > 1:
        right = stack.pop()
        left = stack.pop()
        stack.append(hashlib.sha256(b"\x01" + left + right).digest())
    return stack[0]


def flip_bytes(value: bytes) -> bytes:
    raw = bytearray(value)
    raw[0] ^= 1
    return bytes(raw)


def flip_hex(value: str) -> str:
    return flip_bytes(bytes.fromhex(value)).hex()


def digest(label: bytes) -> str:
    return hashlib.sha256(b"te-cmpb-bounded-v1:" + label).hexdigest()


def contains_key(value: Any, names: set[str]) -> bool:
    if isinstance(value, dict):
        return bool(names & set(value)) or any(contains_key(item, names) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, names) for item in value)
    return False


def access_envelope() -> tuple[dict[str, Any], str]:
    event = json.loads((ROOT / "data_examples/personal_monitoring/access_event.json").read_text(encoding="utf-8"))
    return build_signed_envelope(
        event,
        emitted_at="2026-07-01T06:10:00.500Z",
        private_key=fixture_emitter_private_key(),
    )


def verify(envelope: dict[str, Any], *, checkpoint=None, consistency_proof=None):
    return verify_envelope_receipt(
        envelope,
        emitter_keys={FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
        receipt_keys={FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
        retained_checkpoint=checkpoint,
        consistency_proof=consistency_proof,
    )


def run(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    failures: list[dict[str, str]] = []
    counts = {property_id: 0 for property_id in PROPERTY_META}

    def check(property_id: str, case_id: str, condition: bool, detail: str) -> None:
        counts[property_id] += 1
        if not condition:
            failures.append({
                "property_id": property_id,
                "case_id": case_id,
                "detail": detail,
            })

    sequence_count = 0
    append_transition_count = 0
    inclusion_count = 0
    consistency_count = 0

    # Exhaustive sequence-state exploration.
    for length in range(MAX_SEQUENCE_LENGTH + 1):
        for sequence in itertools.product(DOMAIN, repeat=length):
            sequence_count += 1
            entries = [f"{position}:{value}".encode("ascii") for position, value in enumerate(sequence)]
            recursive = merkle_tree_hash(entries)
            check("P1", f"root-oracle:{sequence}", recursive == iterative_root(entries), "Recursive and stack roots differ")

            log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
            prior_roots = [log.root_digest]
            for position, entry in enumerate(entries):
                old_size = log.tree_size
                old_root = log.root_digest
                index = log.append_core_digest(digest(entry))
                append_transition_count += 1
                check("P1", f"append-index:{sequence}:{position}", index == old_size, "Append index is not prior tree size")
                check("P1", f"append-size:{sequence}:{position}", log.tree_size == old_size + 1, "Tree size did not increment by one")
                check("P1", f"prefix-stable:{sequence}:{position}", log.root_digest_at(old_size) == old_root, "Earlier prefix root changed")
                prior_roots.append(log.root_digest)
            for size, expected_root in enumerate(prior_roots):
                check("P1", f"prefix-recall:{sequence}:{size}", log.root_digest_at(size) == expected_root, "Stored prefix root is not reproducible")

            for index, entry in enumerate(entries):
                path = inclusion_path(entries, index)
                inclusion_count += 1
                check(
                    "P2",
                    f"include:{sequence}:{index}",
                    verify_inclusion(leaf_hash(entry), leaf_index=index, tree_size=length, siblings=path, root_hash=recursive),
                    "Valid inclusion path rejected",
                )
                check(
                    "P2",
                    f"wrong-root:{sequence}:{index}",
                    not verify_inclusion(leaf_hash(entry), leaf_index=index, tree_size=length, siblings=path, root_hash=flip_bytes(recursive)),
                    "Changed root accepted",
                )
                if length > 1:
                    wrong_index = (index + 1) % length
                    check(
                        "P2",
                        f"wrong-index:{sequence}:{index}",
                        not verify_inclusion(leaf_hash(entry), leaf_index=wrong_index, tree_size=length, siblings=path, root_hash=recursive),
                        "Changed index accepted for position-distinguished leaves",
                    )
                    mutated = list(path)
                    mutated[0] = flip_bytes(mutated[0])
                    check(
                        "P3",
                        f"include-mutation:{sequence}:{index}",
                        not verify_inclusion(leaf_hash(entry), leaf_index=index, tree_size=length, siblings=mutated, root_hash=recursive),
                        "Changed inclusion component accepted",
                    )

            for first in range(1, length):
                path = consistency_path(entries, first, length)
                first_root = merkle_tree_hash(entries[:first])
                consistency_count += 1
                valid = verify_consistency(
                    first_size=first,
                    second_size=length,
                    first_root=first_root,
                    second_root=recursive,
                    hashes=path,
                )
                check("P8", f"consistency:{sequence}:{first}", valid, "Valid consistency path rejected")
                check(
                    "P8",
                    f"consistency-missing:{sequence}:{first}",
                    not verify_consistency(first_size=first, second_size=length, first_root=first_root, second_root=recursive, hashes=[]),
                    "Missing consistency path accepted",
                )
                check(
                    "P8",
                    f"consistency-short:{sequence}:{first}",
                    not verify_consistency(first_size=first, second_size=length, first_root=first_root, second_root=recursive, hashes=path[:-1]),
                    "Short consistency path accepted",
                )
                check(
                    "P8",
                    f"consistency-long:{sequence}:{first}",
                    not verify_consistency(first_size=first, second_size=length, first_root=first_root, second_root=recursive, hashes=path + [bytes(32)]),
                    "Long consistency path accepted",
                )
                mutated = list(path)
                mutated[0] = flip_bytes(mutated[0])
                check(
                    "P8",
                    f"consistency-mutation:{sequence}:{first}",
                    not verify_consistency(first_size=first, second_size=length, first_root=first_root, second_root=recursive, hashes=mutated),
                    "Changed consistency component accepted",
                )
                check(
                    "P8",
                    f"consistency-old-root:{sequence}:{first}",
                    not verify_consistency(first_size=first, second_size=length, first_root=flip_bytes(first_root), second_root=recursive, hashes=path),
                    "Changed prior root accepted",
                )
                check(
                    "P8",
                    f"consistency-new-root:{sequence}:{first}",
                    not verify_consistency(first_size=first, second_size=length, first_root=first_root, second_root=flip_bytes(recursive), hashes=path),
                    "Changed current root accepted",
                )

            if length > 0:
                check(
                    "P8",
                    f"equal-size:{sequence}",
                    verify_consistency(first_size=length, second_size=length, first_root=recursive, second_root=recursive, hashes=[]),
                    "Equal-size equal-root check rejected",
                )
                check(
                    "P8",
                    f"equal-size-root-change:{sequence}",
                    not verify_consistency(first_size=length, second_size=length, first_root=recursive, second_root=flip_bytes(recursive), hashes=[]),
                    "Equal-size changed root accepted",
                )

    # Finite canonicalisation domain.
    canonical_object_count = 0
    scalar_values: tuple[Any, ...] = (None, False, True, -1, 0, 1, "a", "b")
    keys = ("a", "b", "c")
    for field_count in range(4):
        for selected_keys in itertools.combinations(keys, field_count):
            for values in itertools.product(scalar_values, repeat=field_count):
                obj = dict(zip(selected_keys, values, strict=True))
                reversed_obj = dict(reversed(list(obj.items())))
                canonical_object_count += 1
                check("P4", f"canonical-order:{selected_keys}:{values}", canonicalise_te(obj) == canonicalise_te(reversed_obj), "Key order changed canonical bytes")
                changed = dict(obj)
                changed["mutation_marker"] = "changed"
                check("P4", f"canonical-change:{selected_keys}:{values}", canonicalise_te(obj) != canonicalise_te(changed), "Added semantic field did not change canonical bytes")

    # Verifier-level receipt, consistency, rollback, and fork controls.
    envelope, core_digest = access_envelope()
    verifier_advances = 0
    for prefix_extra in range(4):
        log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
        log.append_core_digest(core_digest)
        for index in range(prefix_extra):
            log.append_core_digest(digest(f"prefix:{prefix_extra}:{index}".encode()))
        retained = RetainedCheckpoint(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, log.tree_size, log.root_digest)
        for extension in range(1, 5):
            extended = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
            for value in log.core_digests_at():
                extended.append_core_digest(value)
            for index in range(extension):
                extended.append_core_digest(digest(f"extension:{prefix_extra}:{extension}:{index}".encode()))
            receipt = extended.issue_receipt(0, issued_at="2026-07-03T05:00:00.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
            complete = attach_receipt(envelope, receipt)
            missing = verify(complete, checkpoint=retained)
            check("P8", f"verifier-missing:{prefix_extra}:{extension}", not missing.accepted and "TE-E-CONSISTENCY-MISSING" in missing.codes, "Verifier accepted larger checkpoint without proof")
            proof = extended.issue_consistency_proof(retained.tree_size)
            accepted = verify(complete, checkpoint=retained, consistency_proof=proof)
            verifier_advances += 1
            check("P8", f"verifier-valid:{prefix_extra}:{extension}", accepted.accepted, "Verifier rejected valid checkpoint extension")
            malformed = deepcopy(proof)
            malformed["hashes"][0] = flip_hex(malformed["hashes"][0])
            rejected = verify(complete, checkpoint=retained, consistency_proof=malformed)
            check("P8", f"verifier-mutated:{prefix_extra}:{extension}", not rejected.accepted and "TE-E-CONSISTENCY-PATH" in rejected.codes, "Verifier accepted changed consistency proof")

            changed_receipt = deepcopy(complete)
            changed_receipt["backend_receipt"]["root_digest"] = flip_hex(changed_receipt["backend_receipt"]["root_digest"])
            changed_receipt["backend_receipt"].pop("receipt_signature", None)
            signature, _ = sign_receipt(changed_receipt["backend_receipt"], private_key=fixture_backend_private_key(), key_id=FIXTURE_BACKEND_KEY_ID)
            changed_receipt["backend_receipt"]["receipt_signature"] = signature
            changed_result = verify(changed_receipt)
            check("P5", f"receipt-root:{prefix_extra}:{extension}", not changed_result.accepted and "TE-E-PROOF-PATH" in changed_result.codes, "Re-signed changed root accepted")

    # Same-size verifier-visible fork pairs over a finite alphabet.
    fork_pair_count = 0
    for common_length in range(1, 4):
        common = [f"common:{index}".encode() for index in range(common_length)]
        for suffix_length in range(1, MAX_SEQUENCE_LENGTH - common_length + 1):
            suffixes = list(itertools.product(DOMAIN, repeat=suffix_length))
            for left_suffix, right_suffix in itertools.combinations(suffixes, 2):
                left_entries = common + [f"left:{index}:{value}".encode() for index, value in enumerate(left_suffix)]
                right_entries = common + [f"right:{index}:{value}".encode() for index, value in enumerate(right_suffix)]
                fork_pair_count += 1
                check("P7", f"fork:{common_length}:{left_suffix}:{right_suffix}", merkle_tree_hash(left_entries) != merkle_tree_hash(right_entries), "Distinct bounded same-size histories produced the same observed root")

    # Public evidence-only verification and syntactic non-disclosure.
    one = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    one.append_core_digest(core_digest)
    receipt = one.issue_receipt(0, issued_at="2026-07-03T05:30:00.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
    public = attach_receipt(envelope, receipt)
    check("P5", "public-receipt-valid", verify(public).accepted, "Unmodified public receipt rejected")
    check("P6", "public-no-withheld-fields", not contains_key(public, {"nonce", "payload", "raw_payload", "samples", "glucose_value", "physiological_value"}), "Public envelope contains withheld payload material")

    # Explicit capability observation: duplicate leaf bytes do not prove uniqueness.
    duplicates = [b"duplicate", b"duplicate"]
    duplicate_cross_index = verify_inclusion(
        leaf_hash(duplicates[0]),
        leaf_index=1,
        tree_size=2,
        siblings=inclusion_path(duplicates, 0),
        root_hash=merkle_tree_hash(duplicates),
    )
    observations = [{
        "observation_id": "LIM-DUPLICATE-LEAF-001",
        "observed": str(duplicate_cross_index).lower(),
        "interpretation": "With identical leaf material in a symmetric two-leaf tree, inclusion alone does not establish occurrence uniqueness; the application relies on signed index metadata and unique evidence identifiers.",
        "public_claim_boundary": "Do not claim that a Merkle proof demonstrates that identical evidence material occurs only once.",
    }]

    failure_by_property = {property_id: 0 for property_id in PROPERTY_META}
    for failure in failures:
        failure_by_property[failure["property_id"]] += 1

    summary_rows = []
    for property_id, (name, scope) in PROPERTY_META.items():
        summary_rows.append({
            "run_id": RUN_ID,
            "property_id": property_id,
            "property_name": name,
            "checks_executed": counts[property_id],
            "failures": failure_by_property[property_id],
            "status": "PASS" if failure_by_property[property_id] == 0 else "FAIL",
            "bounded_scope": scope,
        })

    with (output / "bounded_model_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)
    with (output / "bounded_model_failures.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["property_id", "case_id", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(failures)
    with (output / "bounded_model_observations.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(observations[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(observations)

    facts = {
        "run_id": RUN_ID,
        "domain": list(DOMAIN),
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "sequences_checked": sequence_count,
        "append_transitions_checked": append_transition_count,
        "inclusion_proofs_checked": inclusion_count,
        "consistency_proofs_checked": consistency_count,
        "canonical_objects_checked": canonical_object_count,
        "verifier_checkpoint_advances_checked": verifier_advances,
        "same_size_fork_pairs_checked": fork_pair_count,
        "checks_executed": sum(counts.values()),
        "failures": len(failures),
        "duplicate_leaf_index_ambiguity_observed": duplicate_cross_index,
        "claim_boundary": "finite executable exploration only; no unbounded theorem, mechanised proof, operational key-compromise model, gossip, witnessing, or global non-equivocation result",
    }
    dump_json(output / "bounded_model_summary.json", facts)
    print(json.dumps(facts, sort_keys=True))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results_expected/cmpb_reference/property_checks",
    )
    args = parser.parse_args()
    return run(args.output_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
