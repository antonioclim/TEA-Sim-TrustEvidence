#!/usr/bin/env python3
"""Execute signed-core, receipt-binding, Merkle-path and commitment controls."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from trustevidence.backends.a2_merkle import (
    LocalA2MerkleLog,
    RetainedCheckpoint,
    attach_receipt,
    verify_envelope_receipt,
)
from trustevidence.crypto import (
    b64url_decode,
    b64url_encode,
    commit_payload,
    sign_receipt,
    verify_payload_commitment,
)
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
DEFAULT_OUTPUT = ROOT / "results_expected" / "cmpb_reference"
RUN_ID = "cmpb-mutation-consistency-001"
EMITTED_AT = {
    "access_event.json": "2026-07-01T06:10:00.500Z",
    "aggregation_event.json": "2026-07-01T23:59:59.500Z",
    "cgm_monitoring_object_registration.json": "2026-07-01T06:00:00.500Z",
    "consent_grant_event.json": "2026-07-01T07:00:00.500Z",
    "consent_revocation_event.json": "2026-07-02T07:00:00.500Z",
    "disclosure_event.json": "2026-07-01T10:00:00.500Z",
    "failure_event.json": "2026-07-01T11:00:00.500Z",
    "provenance_transform_event.json": "2026-07-01T09:00:00.500Z",
    "wearable_monitoring_object_registration.json": "2026-07-01T06:05:00.500Z",
}


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def flip_hex(value: str) -> str:
    raw = bytearray.fromhex(value)
    raw[0] ^= 0x01
    return raw.hex()


def flip_signature(value: str) -> str:
    raw = bytearray(b64url_decode(value))
    raw[0] ^= 0x01
    return b64url_encode(bytes(raw))


def public_contains_key(value: Any, prohibited: str) -> bool:
    if isinstance(value, dict):
        return prohibited in value or any(public_contains_key(item, prohibited) for item in value.values())
    if isinstance(value, list):
        return any(public_contains_key(item, prohibited) for item in value)
    return False


def build_reference() -> tuple[dict[str, dict[str, Any]], list[str], LocalA2MerkleLog]:
    emitter_key = fixture_emitter_private_key()
    envelopes: dict[str, dict[str, Any]] = {}
    digests: list[str] = []
    for filename in sorted(EMITTED_AT):
        event = json.loads((EXAMPLES / filename).read_text(encoding="utf-8"))
        envelope, core_digest = build_signed_envelope(
            event,
            emitted_at=EMITTED_AT[filename],
            private_key=emitter_key,
        )
        envelopes[filename] = envelope
        digests.append(core_digest)
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    for core_digest in digests:
        log.append_core_digest(core_digest)
    return envelopes, digests, log


def issue_all(
    envelopes: dict[str, dict[str, Any]], log: LocalA2MerkleLog
) -> dict[str, dict[str, Any]]:
    backend_key = fixture_backend_private_key()
    result: dict[str, dict[str, Any]] = {}
    for index, filename in enumerate(sorted(envelopes)):
        receipt = log.issue_receipt(
            index,
            issued_at=f"2026-07-03T00:00:{index:02d}.000Z",
            private_key=backend_key,
            signer_key_id=FIXTURE_BACKEND_KEY_ID,
        )
        result[filename] = attach_receipt(envelopes[filename], receipt)
    return result


def verifier(
    envelope: dict[str, Any],
    *,
    checkpoint: RetainedCheckpoint | None = None,
    consistency_proof: dict[str, Any] | None = None,
):
    return verify_envelope_receipt(
        envelope,
        emitter_keys={FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
        receipt_keys={FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
        retained_checkpoint=checkpoint,
        consistency_proof=consistency_proof,
    )


def result_row(
    case_id: str,
    case_class: str,
    mutation_class: str,
    target_path: str,
    signing_state: str,
    expected_outcome: str,
    observed_outcome: str,
    observed_codes: tuple[str, ...] | list[str],
    expected_code: str,
    passed: bool,
    notes: str,
) -> dict[str, Any]:
    codes = tuple(observed_codes)
    return {
        "run_id": RUN_ID,
        "case_id": case_id,
        "case_class": case_class,
        "mutation_class": mutation_class,
        "target_path": target_path,
        "signing_state": signing_state,
        "expected_outcome": expected_outcome,
        "observed_outcome": observed_outcome,
        "expected_error_code_or_pass": expected_code,
        "primary_error_code": "PASS" if not codes else codes[0],
        "observed_error_codes": ";".join(codes),
        "passed": str(passed).lower(),
        "notes": notes,
    }


def verify_row(
    case_id: str,
    case_class: str,
    mutation_class: str,
    target_path: str,
    signing_state: str,
    candidate: dict[str, Any],
    *,
    expected_outcome: str = "rejected",
    expected_code: str,
    checkpoint: RetainedCheckpoint | None = None,
    consistency_proof: dict[str, Any] | None = None,
    notes: str,
) -> dict[str, Any]:
    observed = verifier(candidate, checkpoint=checkpoint, consistency_proof=consistency_proof)
    observed_outcome = "accepted" if observed.accepted else "rejected"
    code_ok = expected_code == "PASS" if observed.accepted else expected_code in observed.codes
    passed = observed_outcome == expected_outcome and code_ok
    return result_row(
        case_id, case_class, mutation_class, target_path, signing_state,
        expected_outcome, observed_outcome, observed.codes, expected_code, passed, notes,
    )


def mutate_copy(source: dict[str, Any], mutation: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    candidate = deepcopy(source)
    mutation(candidate)
    return candidate


def resign(candidate: dict[str, Any], *, recompute_proof_digest: bool = False) -> None:
    receipt = candidate["backend_receipt"]
    if recompute_proof_digest:
        receipt["inclusion_proof_digest"] = proof_digest_hex(receipt["inclusion_proof"])
    receipt.pop("receipt_signature", None)
    signature, _ = sign_receipt(
        receipt,
        private_key=fixture_backend_private_key(),
        key_id=FIXTURE_BACKEND_KEY_ID,
    )
    receipt["receipt_signature"] = signature


def run(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    signed, digests, log = build_reference()
    complete = issue_all(signed, log)
    rows: list[dict[str, Any]] = []

    # Persist all positive signed-core and receipt examples.
    for filename in sorted(complete):
        dump_json(output / "signed_envelopes" / filename, complete[filename])
        rows.append(verify_row(
            f"POS-{filename.removesuffix('.json').upper().replace('_', '-')}",
            "positive-receipt", "none", "$", "valid-signatures",
            complete[filename], expected_outcome="accepted", expected_code="PASS",
            notes="Signed evidence core and final-tree inclusion receipt",
        ))

    baseline = complete["access_event.json"]
    receipt_path = "$.backend_receipt"

    # Core mutations retain schema-valid shapes where possible and do not re-sign.
    core_mutations: list[tuple[str, str, str, Callable[[dict[str, Any]], None], str, str]] = [
        ("MUT-CORE-001", "actor", "$.evidence_core.actor.actor_ref_token", lambda x: x["evidence_core"]["actor"].__setitem__("actor_ref_token", "urn:te:actor-token:reader-service-002"), "TE-E-CORE-SIGNATURE", "Actor token mutation"),
        ("MUT-CORE-002", "role", "$.evidence_core.actor.role_code", lambda x: x["evidence_core"]["actor"].__setitem__("role_code", "curation-service"), "TE-E-CORE-SIGNATURE", "Actor role mutation using another admitted code"),
        ("MUT-CORE-003", "object-role", "$.evidence_core.objects[0].object_role", lambda x: x["evidence_core"]["objects"][0].__setitem__("object_role", "source"), "TE-E-OBJECT-ROLE", "Object-role mutation violates the access-event target invariant"),
        ("MUT-CORE-004", "subject-reference", "$.evidence_core.subject_context and objects[*]", lambda x: (x["evidence_core"]["subject_context"].__setitem__("subject_ref_token", "urn:te:subject-token:fixture-002"), [obj.__setitem__("subject_ref_token", "urn:te:subject-token:fixture-002") for obj in x["evidence_core"]["objects"]]), "TE-E-CORE-SIGNATURE", "Coherent subject-token mutation remains structurally valid but breaks the signed core"),
        ("MUT-CORE-005", "consent-state", "$.evidence_core.consent_binding.consent_state", lambda x: x["evidence_core"]["consent_binding"].__setitem__("consent_state", "revoked"), "TE-E-CORE-SIGNATURE", "Admitted consent-state mutation"),
        ("MUT-CORE-006", "policy-version", "$.evidence_core.policy_binding.policy_version", lambda x: x["evidence_core"]["policy_binding"].__setitem__("policy_version", "2026-08"), "TE-E-CORE-SIGNATURE", "Policy-version mutation"),
        ("MUT-CORE-007", "timestamp", "$.evidence_core.occurred_at", lambda x: x["evidence_core"].__setitem__("occurred_at", "2026-07-01T06:10:00.001Z"), "TE-E-CORE-SIGNATURE", "Millisecond timestamp mutation within the admitted temporal ordering"),
        ("MUT-CORE-008", "payload-reference", "$.evidence_core.objects[0].object_ref_token", lambda x: x["evidence_core"]["objects"][0].__setitem__("object_ref_token", "urn:te:object-token:cgm-day-002"), "TE-E-CORE-SIGNATURE", "Payload-reference token mutation"),
        ("MUT-CORE-009", "emitter-signature", "$.evidence_core.emitter_signature.signature", lambda x: x["evidence_core"]["emitter_signature"].__setitem__("signature", flip_signature(x["evidence_core"]["emitter_signature"]["signature"])), "TE-E-CORE-SIGNATURE", "One-bit Ed25519 signature mutation"),
        ("MUT-CORE-010", "unknown-emitter-key", "$.evidence_core.emitter.key_id and emitter_signature.key_id", lambda x: (x["evidence_core"]["emitter"].__setitem__("key_id", "urn:te:key:fixture-emitter-unknown"), x["evidence_core"]["emitter_signature"].__setitem__("key_id", "urn:te:key:fixture-emitter-unknown")), "TE-E-CORE-SIGNATURE", "Unknown emitter key identifier is rejected by the explicit verifier registry"),
    ]
    for case_id, mutation_class, target, mutation, expected_code, note in core_mutations:
        candidate = mutate_copy(baseline, mutation)
        rows.append(verify_row(case_id, "core-mutation", mutation_class, target, "stale-core-signature", candidate, expected_code=expected_code, notes=note))

    # Receipt and proof mutations, initially without access to the backend signing key.
    receipt_mutations: list[tuple[str, str, str, Callable[[dict[str, Any]], None], str, str]] = [
        ("MUT-RCP-001", "evidence-hash", f"{receipt_path}.core_digest", lambda x: x["backend_receipt"].__setitem__("core_digest", flip_hex(x["backend_receipt"]["core_digest"])), "TE-E-RECEIPT-SIGNATURE", "Core-digest mutation"),
        ("MUT-RCP-002", "leaf-hash", f"{receipt_path}.leaf_hash", lambda x: x["backend_receipt"].__setitem__("leaf_hash", flip_hex(x["backend_receipt"]["leaf_hash"])), "TE-E-RECEIPT-SIGNATURE", "Leaf-hash mutation"),
        ("MUT-RCP-003", "proof-path", f"{receipt_path}.inclusion_proof.siblings[0]", lambda x: x["backend_receipt"]["inclusion_proof"]["siblings"].__setitem__(0, flip_hex(x["backend_receipt"]["inclusion_proof"]["siblings"][0])), "TE-E-RECEIPT-SIGNATURE", "One-bit proof-sibling mutation"),
        ("MUT-RCP-004", "proof-path-order", f"{receipt_path}.inclusion_proof.siblings", lambda x: x["backend_receipt"]["inclusion_proof"].__setitem__("siblings", list(reversed(x["backend_receipt"]["inclusion_proof"]["siblings"]))), "TE-E-RECEIPT-SIGNATURE", "Proof-path order reversal"),
        ("MUT-RCP-005", "proof-path-missing", f"{receipt_path}.inclusion_proof.siblings", lambda x: x["backend_receipt"]["inclusion_proof"]["siblings"].pop(), "TE-E-RECEIPT-SIGNATURE", "Proof sibling deletion"),
        ("MUT-RCP-006", "proof-path-extra", f"{receipt_path}.inclusion_proof.siblings", lambda x: x["backend_receipt"]["inclusion_proof"]["siblings"].append(x["backend_receipt"]["inclusion_proof"]["siblings"][0]), "TE-E-RECEIPT-SIGNATURE", "Extra proof sibling"),
        ("MUT-RCP-007", "root", f"{receipt_path}.root_digest", lambda x: x["backend_receipt"].__setitem__("root_digest", flip_hex(x["backend_receipt"]["root_digest"])), "TE-E-RECEIPT-SIGNATURE", "Signed root mutation"),
        ("MUT-RCP-008", "tree-size-receipt-only", f"{receipt_path}.tree_size", lambda x: x["backend_receipt"].__setitem__("tree_size", x["backend_receipt"]["tree_size"] + 1), "TE-E-PROOF-SIZE", "Receipt/proof tree-size mismatch"),
        ("MUT-RCP-009", "tree-size", f"{receipt_path}.tree_size and inclusion_proof.tree_size", lambda x: (x["backend_receipt"].__setitem__("tree_size", x["backend_receipt"]["tree_size"] + 1), x["backend_receipt"]["inclusion_proof"].__setitem__("tree_size", x["backend_receipt"]["inclusion_proof"]["tree_size"] + 1)), "TE-E-RECEIPT-SIGNATURE", "Coherent field mutation still breaks signed receipt"),
        ("MUT-RCP-010", "leaf-index-receipt-only", f"{receipt_path}.leaf_index", lambda x: x["backend_receipt"].__setitem__("leaf_index", 1), "TE-E-PROOF-INDEX", "Receipt/proof leaf-index mismatch"),
        ("MUT-RCP-011", "leaf-index", f"{receipt_path}.leaf_index and inclusion_proof.leaf_index", lambda x: (x["backend_receipt"].__setitem__("leaf_index", 1), x["backend_receipt"]["inclusion_proof"].__setitem__("leaf_index", 1)), "TE-E-RECEIPT-SIGNATURE", "Coherent field mutation still breaks signed receipt"),
        ("MUT-RCP-012", "proof-digest", f"{receipt_path}.inclusion_proof_digest", lambda x: x["backend_receipt"].__setitem__("inclusion_proof_digest", flip_hex(x["backend_receipt"]["inclusion_proof_digest"])), "TE-E-RECEIPT-SIGNATURE", "Proof-digest mutation"),
        ("MUT-RCP-013", "backend-type", f"{receipt_path}.backend_type", lambda x: x["backend_receipt"].__setitem__("backend_type", "external-ledger"), "TE-E-SCHEMA-VALUE", "Backend-type discriminator mutation"),
        ("MUT-RCP-014", "backend-identifier", f"{receipt_path}.backend_id", lambda x: x["backend_receipt"].__setitem__("backend_id", "urn:te:backend:other-reference"), "TE-E-RECEIPT-SIGNATURE", "Backend identifier mutation"),
        ("MUT-RCP-015", "log-identifier", f"{receipt_path}.log_id", lambda x: x["backend_receipt"].__setitem__("log_id", "urn:te:log:other-reference"), "TE-E-RECEIPT-SIGNATURE", "Log identifier mutation"),
        ("MUT-RCP-016", "signer-identifier", f"{receipt_path}.signer_key_id", lambda x: x["backend_receipt"].__setitem__("signer_key_id", "urn:te:key:fixture-backend-v2"), "TE-E-RECEIPT-SIGNATURE", "Signer identifier mutation"),
        ("MUT-RCP-017", "receipt-signature", f"{receipt_path}.receipt_signature.signature", lambda x: x["backend_receipt"]["receipt_signature"].__setitem__("signature", flip_signature(x["backend_receipt"]["receipt_signature"]["signature"])), "TE-E-RECEIPT-SIGNATURE", "One-bit receipt-signature mutation"),
        ("MUT-RCP-018", "receipt-time", f"{receipt_path}.issued_at", lambda x: x["backend_receipt"].__setitem__("issued_at", "2026-07-03T00:00:00.001Z"), "TE-E-RECEIPT-SIGNATURE", "Receipt timestamp mutation"),
        ("MUT-RCP-019", "unknown-receipt-key", f"{receipt_path}.signer_key_id and receipt_signature.key_id", lambda x: (x["backend_receipt"].__setitem__("signer_key_id", "urn:te:key:fixture-backend-unknown"), x["backend_receipt"]["receipt_signature"].__setitem__("key_id", "urn:te:key:fixture-backend-unknown")), "TE-E-RECEIPT-SIGNATURE", "Unknown receipt key identifier is rejected by the explicit verifier registry"),
    ]
    for case_id, mutation_class, target, mutation, expected_code, note in receipt_mutations:
        candidate = mutate_copy(baseline, mutation)
        rows.append(verify_row(case_id, "receipt-mutation", mutation_class, target, "stale-receipt-signature", candidate, expected_code=expected_code, notes=note))

    # Re-signed malformed receipts exercise checks that are independent of stale signatures.
    resigned_cases: list[tuple[str, str, str, Callable[[dict[str, Any]], None], bool, str, str]] = [
        ("MUT-RSIG-001", "evidence-hash", f"{receipt_path}.core_digest", lambda x: x["backend_receipt"].__setitem__("core_digest", flip_hex(x["backend_receipt"]["core_digest"])), False, "TE-E-RECEIPT-BINDING", "Re-signed receipt cannot bind a different core digest"),
        ("MUT-RSIG-002", "proof-path", f"{receipt_path}.inclusion_proof.siblings[0]", lambda x: x["backend_receipt"]["inclusion_proof"]["siblings"].__setitem__(0, flip_hex(x["backend_receipt"]["inclusion_proof"]["siblings"][0])), True, "TE-E-PROOF-PATH", "Proof digest and receipt signature are recomputed, but the path fails root reconstruction"),
        ("MUT-RSIG-003", "root", f"{receipt_path}.root_digest", lambda x: x["backend_receipt"].__setitem__("root_digest", flip_hex(x["backend_receipt"]["root_digest"])), False, "TE-E-PROOF-PATH", "Re-signed altered root remains inconsistent with the proof"),
        ("MUT-RSIG-004", "backend-identifier", f"{receipt_path}.backend_id", lambda x: x["backend_receipt"].__setitem__("backend_id", "urn:te:backend:other-reference"), False, "TE-E-BACKEND-IDENTITY", "Expected backend identity is checked independently of receipt signature"),
        ("MUT-RSIG-005", "proof-digest", f"{receipt_path}.inclusion_proof_digest", lambda x: x["backend_receipt"].__setitem__("inclusion_proof_digest", flip_hex(x["backend_receipt"]["inclusion_proof_digest"])), False, "TE-E-PROOF-DIGEST", "Re-signed false proof digest is recomputed by the verifier"),
    ]
    for case_id, mutation_class, target, mutation, recompute, expected_code, note in resigned_cases:
        candidate = mutate_copy(baseline, mutation)
        resign(candidate, recompute_proof_digest=recompute)
        rows.append(verify_row(case_id, "re-signed-malformed-receipt", mutation_class, target, "receipt-re-signed-with-test-key", candidate, expected_code=expected_code, notes=note))

    # Retained-checkpoint controls.  These compare valid, independently signed receipts.
    retained = RetainedCheckpoint(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, log.tree_size, log.root_digest)

    prefix = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    for value in digests[:8]:
        prefix.append_core_digest(value)
    rollback_receipt = prefix.issue_receipt(0, issued_at="2026-07-03T01:00:00.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
    rollback_env = attach_receipt(signed["access_event.json"], rollback_receipt)
    rows.append(verify_row("CHK-001", "checkpoint-control", "rollback", "$.backend_receipt.tree_size", "valid-signatures", rollback_env, expected_code="TE-E-CHECKPOINT-ROLLBACK", checkpoint=retained, notes="A valid smaller-tree receipt is rejected against retained larger state"))

    divergent = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    for index, value in enumerate(digests):
        divergent.append_core_digest(value if index != 1 else hashlib.sha256(b"te-cmpb-divergent-sibling-v1").hexdigest())
    divergent_receipt = divergent.issue_receipt(0, issued_at="2026-07-03T01:00:01.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
    divergent_env = attach_receipt(signed["access_event.json"], divergent_receipt)
    rows.append(verify_row("CHK-002", "checkpoint-control", "same-size-divergence", "$.backend_receipt.root_digest", "valid-signatures", divergent_env, expected_code="TE-E-CHECKPOINT-FORK", checkpoint=retained, notes="A valid same-size receipt with another root is rejected against retained state"))

    larger = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    for value in digests + [hashlib.sha256(b"te-cmpb-tenth-entry-v1").hexdigest()]:
        larger.append_core_digest(value)
    larger_receipt = larger.issue_receipt(0, issued_at="2026-07-03T01:00:02.000Z", private_key=fixture_backend_private_key(), signer_key_id=FIXTURE_BACKEND_KEY_ID)
    larger_env = attach_receipt(signed["access_event.json"], larger_receipt)
    consistency = larger.issue_consistency_proof(log.tree_size)
    rows.append(verify_row(
        "CONS-001", "consistency-control", "missing-consistency-proof",
        "$consistency_proof", "valid-signatures", larger_env,
        expected_code="TE-E-CONSISTENCY-MISSING", checkpoint=retained,
        notes="A larger signed checkpoint is rejected when no prefix-extension proof is supplied",
    ))
    rows.append(verify_row(
        "CONS-002", "consistency-control", "valid-consistency-proof",
        "$consistency_proof", "valid-signatures", larger_env,
        expected_outcome="accepted", expected_code="PASS", checkpoint=retained,
        consistency_proof=consistency,
        notes="A valid consistency proof establishes local append-only extension from retained state",
    ))
    mutated_consistency = deepcopy(consistency)
    mutated_consistency["hashes"][0] = flip_hex(mutated_consistency["hashes"][0])
    rows.append(verify_row(
        "CONS-003", "consistency-control", "consistency-path-mutation",
        "$consistency_proof.hashes[0]", "valid-signatures", larger_env,
        expected_code="TE-E-CONSISTENCY-PATH", checkpoint=retained,
        consistency_proof=mutated_consistency,
        notes="A one-bit consistency-path mutation fails prefix-extension reconstruction",
    ))
    wrong_root_consistency = deepcopy(consistency)
    wrong_root_consistency["first_root"] = flip_hex(wrong_root_consistency["first_root"])
    rows.append(verify_row(
        "CONS-004", "consistency-control", "consistency-root-mismatch",
        "$consistency_proof.first_root", "valid-signatures", larger_env,
        expected_code="TE-E-CONSISTENCY-ROOT", checkpoint=retained,
        consistency_proof=wrong_root_consistency,
        notes="A proof declaring another retained root is rejected before path evaluation",
    ))
    wrong_size_consistency = deepcopy(consistency)
    wrong_size_consistency["first_size"] -= 1
    rows.append(verify_row(
        "CONS-005", "consistency-control", "consistency-size-mismatch",
        "$consistency_proof.first_size", "valid-signatures", larger_env,
        expected_code="TE-E-CONSISTENCY-SIZE", checkpoint=retained,
        consistency_proof=wrong_size_consistency,
        notes="A proof declaring another retained tree size is rejected",
    ))

    foreign = RetainedCheckpoint("urn:te:backend:other-reference", FIXTURE_LOG_ID, log.tree_size, log.root_digest)
    rows.append(verify_row("CHK-003", "checkpoint-control", "checkpoint-identity", "$retained_checkpoint.backend_id", "valid-signatures", baseline, expected_code="TE-E-CHECKPOINT-IDENTITY", checkpoint=foreign, notes="Verifier refuses retained state from another backend/log identity"))

    # Authorised-side payload commitment controls; the nonce never enters an envelope.
    payload = b'{"fixture_id":"synthetic-cgm-object-001","value_domain":"withheld"}'
    nonce = hashlib.sha256(b"TEA-Sim authorised nonce test fixture").digest()[:16]
    representation = "application/fhir+json-rfc8785-v1"
    context = "cgm-day-object"
    expected_commitment = commit_payload(payload, nonce=nonce, representation_profile=representation, commitment_context=context)
    fixture_event = json.loads((EXAMPLES / "cgm_monitoring_object_registration.json").read_text(encoding="utf-8"))
    declared_commitment = fixture_event["object_contexts"][0]["payload_binding"]["commitment"]

    commitment_cases = [
        ("COMMIT-001", "accepted", verify_payload_commitment(declared_commitment, payload, nonce=nonce, representation_profile=representation, commitment_context=context), "PASS", "Declared synthetic fixture commitment matches authorised payload and nonce"),
        ("COMMIT-002", "rejected", verify_payload_commitment(declared_commitment, payload + b" ", nonce=nonce, representation_profile=representation, commitment_context=context), "TE-E-PAYLOAD-COMMITMENT", "Changed payload is rejected"),
        ("COMMIT-003", "rejected", verify_payload_commitment(declared_commitment, payload, nonce=bytes([nonce[0] ^ 1]) + nonce[1:], representation_profile=representation, commitment_context=context), "TE-E-PAYLOAD-COMMITMENT", "Changed nonce is rejected"),
        ("COMMIT-004", "rejected", verify_payload_commitment(declared_commitment, payload, nonce=nonce, representation_profile=representation, commitment_context="other-context"), "TE-E-PAYLOAD-COMMITMENT", "Changed commitment context is rejected"),
    ]
    for case_id, expected_outcome, check, code, note in commitment_cases:
        observed_outcome = "accepted" if check else "rejected"
        rows.append(result_row(case_id, "payload-commitment-control", "payload-commitment", "$authorised_side", "not-applicable", expected_outcome, observed_outcome, () if check else (code,), "PASS" if expected_outcome == "accepted" else code, observed_outcome == expected_outcome, note))

    try:
        commit_payload(payload, nonce=b"too-short", representation_profile=representation, commitment_context=context)
        short_rejected = False
    except ValueError:
        short_rejected = True
    rows.append(result_row("COMMIT-005", "payload-commitment-control", "nonce-length", "$authorised_side.nonce", "not-applicable", "rejected", "rejected" if short_rejected else "accepted", ("TE-E-PAYLOAD-COMMITMENT",) if short_rejected else (), "TE-E-PAYLOAD-COMMITMENT", short_rejected, "Nonce shorter than 128 bits is rejected"))

    nonce_exposed = any(public_contains_key(envelope, "nonce") for envelope in complete.values())
    rows.append(result_row("COMMIT-006", "payload-commitment-control", "public-nonce-disclosure", "$.signed_envelopes[*]", "not-applicable", "absent", "present" if nonce_exposed else "absent", ("TE-E-MIN-PAYLOAD",) if nonce_exposed else (), "PASS", not nonce_exposed, "No public envelope contains a nonce property"))

    rows.sort(key=lambda item: item["case_id"])
    write_csv(output / "mutation_test_results.csv", rows)
    manifest = {
        "run_id": RUN_ID,
        "software_version": "2.1.0",
        "tree_size": log.tree_size,
        "root_digest": log.root_digest,
        "positive_receipts": sum(item["case_class"] == "positive-receipt" for item in rows),
        "mutation_controls": sum("mutation" in item["case_class"] or item["case_class"] == "re-signed-malformed-receipt" for item in rows),
        "checkpoint_controls": sum(item["case_class"] == "checkpoint-control" for item in rows),
        "consistency_controls": sum(item["case_class"] == "consistency-control" for item in rows),
        "commitment_controls": sum(item["case_class"] == "payload-commitment-control" for item in rows),
        "limitation_observations": sum(item["case_class"] == "limitation-observation" for item in rows),
        "case_count": len(rows),
        "passed_count": sum(item["passed"] == "true" for item in rows),
        "failed_count": sum(item["passed"] != "true" for item in rows),
        "fixture_commitment_matches": declared_commitment == expected_commitment,
        "claim_boundary": "local deterministic test keys, signed-core and receipt binding, inclusion reconstruction, controlled mutation rejection, retained-state rollback/same-size comparison, and RFC-9162-shaped local consistency verification; no gossip, witnessing, cross-verifier split-view detection, or global non-equivocation",
    }
    dump_json(output / "mutation_test_run.json", manifest)
    return 0 if manifest["failed_count"] == 0 and manifest["fixture_commitment_matches"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return run(args.output_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
