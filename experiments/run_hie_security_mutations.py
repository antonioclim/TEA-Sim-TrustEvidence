#!/usr/bin/env python3
"""Execute the Route C HIE security, mutation and retained-state programme.

The programme is deterministic and uses synthetic fixtures plus deterministic
TEST-ONLY Ed25519 keys. It tests the exact project profile; it is not a
penetration test, clinical validation, formal proof, SCITT implementation or
production-security assessment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from trustevidence.backends.a2_merkle import (
    LocalA2MerkleLog,
    RetainedCheckpoint,
    attach_receipt,
)
from trustevidence.crypto import (
    b64url_decode,
    b64url_encode,
    sign_receipt,
    verify_payload_commitment,
)
from trustevidence.hashing import (
    core_digest_bytes,
    core_digest_hex,
    core_signature_message,
    proof_digest_hex,
)
from trustevidence.hie import (
    HIE_COMMITMENT_CONTEXT,
    HIE_ENVELOPE_PROFILE,
    HIE_REPRESENTATION_PROFILE,
    verify_hie_envelope_receipt,
)
from trustevidence.hie_state import RetainedHIEVerifier
from trustevidence.testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID,
    deterministic_test_private_key,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data_examples" / "hie_disclosure"
FHIR = ROOT / "standards" / "fhir_ig" / "input" / "resources"
DEFAULT_OUTPUT = ROOT / "results_expected" / "cmpb_reference" / "c4_hie_security"
RUN_ID = "route-c-hie-security-001"
SOFTWARE_STATUS = "working-branch-pre-v2.2.0"

Row = dict[str, Any]
Mutation = Callable[[dict[str, Any]], None]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def stable_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(stable_json_bytes(value)).hexdigest()


def flip_hex(value: str) -> str:
    raw = bytearray.fromhex(value)
    if not raw:
        raise ValueError("cannot flip an empty hexadecimal value")
    raw[0] ^= 1
    return raw.hex()


def flip_signature(value: str) -> str:
    raw = bytearray(b64url_decode(value))
    if not raw:
        raise ValueError("cannot flip an empty signature")
    raw[0] ^= 1
    return b64url_encode(bytes(raw))


def mutate_copy(source: dict[str, Any], mutation: Mutation) -> dict[str, Any]:
    candidate = deepcopy(source)
    mutation(candidate)
    return candidate


def correct_emitter_keys() -> dict[str, Ed25519PublicKey]:
    return {FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()}


def correct_receipt_keys() -> dict[str, Ed25519PublicKey]:
    return {FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()}


def verify_candidate(
    candidate: dict[str, Any],
    *,
    emitter_keys: Mapping[str, Ed25519PublicKey] | None = None,
    receipt_keys: Mapping[str, Ed25519PublicKey] | None = None,
    checkpoint: RetainedCheckpoint | None = None,
    consistency_proof: Mapping[str, Any] | None = None,
):
    return verify_hie_envelope_receipt(
        candidate,
        emitter_keys=emitter_keys or correct_emitter_keys(),
        receipt_keys=receipt_keys or correct_receipt_keys(),
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
        retained_checkpoint=checkpoint,
        consistency_proof=consistency_proof,
    )


def result_row(
    *,
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
) -> Row:
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


def record_verification(
    rows: list[Row],
    evidence: list[dict[str, Any]],
    *,
    case_id: str,
    case_class: str,
    mutation_class: str,
    target_path: str,
    signing_state: str,
    candidate: dict[str, Any],
    expected_outcome: str,
    expected_code: str,
    notes: str,
    emitter_keys: Mapping[str, Ed25519PublicKey] | None = None,
    receipt_keys: Mapping[str, Ed25519PublicKey] | None = None,
    checkpoint: RetainedCheckpoint | None = None,
    consistency_proof: Mapping[str, Any] | None = None,
) -> None:
    result = verify_candidate(
        candidate,
        emitter_keys=emitter_keys,
        receipt_keys=receipt_keys,
        checkpoint=checkpoint,
        consistency_proof=consistency_proof,
    )
    observed = "accepted" if result.accepted else "rejected"
    code_ok = expected_code == "PASS" if result.accepted else expected_code in result.codes
    passed = observed == expected_outcome and code_ok
    rows.append(
        result_row(
            case_id=case_id,
            case_class=case_class,
            mutation_class=mutation_class,
            target_path=target_path,
            signing_state=signing_state,
            expected_outcome=expected_outcome,
            observed_outcome=observed,
            observed_codes=result.codes,
            expected_code=expected_code,
            passed=passed,
            notes=notes,
        )
    )
    evidence.append(
        {
            "case_id": case_id,
            "candidate_sha256": digest_value(candidate),
            "consistency_proof_sha256": (
                digest_value(consistency_proof) if consistency_proof is not None else None
            ),
            "observed_outcome": observed,
            "observed_codes": list(result.codes),
            "expected_outcome": expected_outcome,
            "expected_code": expected_code,
            "passed": passed,
        }
    )


def record_boolean(
    rows: list[Row],
    evidence: list[dict[str, Any]],
    *,
    case_id: str,
    case_class: str,
    mutation_class: str,
    target_path: str,
    expected_outcome: str,
    observed_check: bool,
    notes: str,
) -> None:
    observed = "accepted" if observed_check else "rejected"
    expected_code = "PASS" if expected_outcome == "accepted" else "TE-E-PAYLOAD-COMMITMENT"
    codes = () if observed_check else ("TE-E-PAYLOAD-COMMITMENT",)
    passed = observed == expected_outcome
    rows.append(
        result_row(
            case_id=case_id,
            case_class=case_class,
            mutation_class=mutation_class,
            target_path=target_path,
            signing_state="not-applicable",
            expected_outcome=expected_outcome,
            observed_outcome=observed,
            observed_codes=codes,
            expected_code=expected_code,
            passed=passed,
            notes=notes,
        )
    )
    evidence.append(
        {
            "case_id": case_id,
            "observed_outcome": observed,
            "observed_codes": list(codes),
            "expected_outcome": expected_outcome,
            "expected_code": expected_code,
            "passed": passed,
        }
    )


def resign_hie_core(candidate: dict[str, Any]) -> None:
    core = candidate["evidence_core"]
    core.pop("emitter_signature", None)
    key_id = str(core["emitter"]["key_id"])
    digest = core_digest_bytes(core, envelope_profile=HIE_ENVELOPE_PROFILE)
    message = core_signature_message(digest, algorithm="Ed25519", key_id=key_id)
    core["emitter_signature"] = {
        "algorithm": "Ed25519",
        "key_id": key_id,
        "signature": b64url_encode(fixture_emitter_private_key().sign(message)),
    }


def resign_receipt(candidate: dict[str, Any], *, recompute_proof_digest: bool = False) -> None:
    receipt = candidate["backend_receipt"]
    if recompute_proof_digest:
        receipt["inclusion_proof_digest"] = proof_digest_hex(receipt["inclusion_proof"])
    receipt.pop("receipt_signature", None)
    signature, _ = sign_receipt(
        receipt,
        private_key=fixture_backend_private_key(),
        key_id=str(receipt["signer_key_id"]),
    )
    receipt["receipt_signature"] = signature


def fresh_receipt_for_core(candidate: dict[str, Any], *, dummy_count: int = 0) -> dict[str, Any]:
    result = deepcopy(candidate)
    result.pop("backend_receipt", None)
    core_digest = core_digest_hex(result["evidence_core"], envelope_profile=HIE_ENVELOPE_PROFILE)
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    log.append_core_digest(core_digest)
    for index in range(dummy_count):
        log.append_core_digest(hashlib.sha256(f"route-c-c4-fresh-{index}".encode()).hexdigest())
    receipt = log.issue_receipt(
        0,
        issued_at="2026-07-15T10:00:00.000Z",
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    return attach_receipt(result, receipt)


def build_log(digests: list[str]) -> LocalA2MerkleLog:
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    for value in digests:
        log.append_core_digest(value)
    return log


def issue_for_baseline(
    signed_without_receipt: dict[str, Any],
    log: LocalA2MerkleLog,
    *,
    issued_at: str,
) -> dict[str, Any]:
    receipt = log.issue_receipt(
        0,
        issued_at=issued_at,
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    return attach_receipt(signed_without_receipt, receipt)


def snapshot_dict(value: tuple[str, str, int, str] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "backend_id": value[0],
        "log_id": value[1],
        "tree_size": value[2],
        "root_digest": value[3],
    }


def record_state_case(
    rows: list[Row],
    evidence: list[dict[str, Any]],
    verifier_state: RetainedHIEVerifier,
    *,
    case_id: str,
    mutation_class: str,
    candidate: dict[str, Any],
    expected_outcome: str,
    expected_code: str,
    expected_state_change: bool,
    notes: str,
    consistency_proof: Mapping[str, Any] | None = None,
    case_class: str = "checkpoint-state-control",
) -> None:
    before = verifier_state.snapshot()
    result = verifier_state.verify_and_update(
        candidate,
        emitter_keys=correct_emitter_keys(),
        receipt_keys=correct_receipt_keys(),
        consistency_proof=consistency_proof,
    )
    after = verifier_state.snapshot()
    observed = "accepted" if result.accepted else "rejected"
    changed = before != after
    code_ok = expected_code == "PASS" if result.accepted else expected_code in result.codes
    passed = observed == expected_outcome and code_ok and changed == expected_state_change
    rows.append(
        result_row(
            case_id=case_id,
            case_class=case_class,
            mutation_class=mutation_class,
            target_path="$retained_checkpoint",
            signing_state="valid-signatures",
            expected_outcome=expected_outcome,
            observed_outcome=observed,
            observed_codes=result.codes,
            expected_code=expected_code,
            passed=passed,
            notes=f"{notes}; state_changed={str(changed).lower()}",
        )
    )
    evidence.append(
        {
            "case_id": case_id,
            "candidate_sha256": digest_value(candidate),
            "consistency_proof_sha256": (
                digest_value(consistency_proof) if consistency_proof is not None else None
            ),
            "checkpoint_before": snapshot_dict(before),
            "checkpoint_after": snapshot_dict(after),
            "state_changed": changed,
            "expected_state_change": expected_state_change,
            "observed_outcome": observed,
            "observed_codes": list(result.codes),
            "expected_outcome": expected_outcome,
            "expected_code": expected_code,
            "passed": passed,
        }
    )


def build_results() -> dict[str, bytes]:
    baseline = load_json(CASE / "signed_envelope_with_receipt.json")
    signed = load_json(CASE / "signed_envelope.json")
    event = load_json(CASE / "hie_disclosure_event.json")
    source_canonical = (CASE / "source" / "source_clinical_bundle.canonical.json").read_bytes()
    source_pretty = (CASE / "source" / "source_clinical_bundle.json").read_bytes()
    nonce = bytes.fromhex(
        (CASE / "private_test_material" / "payload_commitment_nonce.hex").read_text().strip()
    )
    portable_bundle = load_json(FHIR / "Bundle-portable-evidence-bundle-hie-001.json")

    rows: list[Row] = []
    evidence: list[dict[str, Any]] = []

    record_verification(
        rows,
        evidence,
        case_id="POS-HIE-001",
        case_class="positive-control",
        mutation_class="none",
        target_path="$",
        signing_state="valid-signatures",
        candidate=baseline,
        expected_outcome="accepted",
        expected_code="PASS",
        notes="Retained single-leaf HIE envelope and receipt",
    )

    baseline_core_digest = core_digest_hex(
        signed["evidence_core"], envelope_profile=HIE_ENVELOPE_PROFILE
    )
    multi_digests = [baseline_core_digest] + [
        hashlib.sha256(f"route-c-c4-multi-{index}".encode()).hexdigest()
        for index in range(1, 6)
    ]
    multi_log = build_log(multi_digests)
    multi = issue_for_baseline(signed, multi_log, issued_at="2026-07-15T10:01:00.000Z")
    record_verification(
        rows,
        evidence,
        case_id="POS-HIE-002",
        case_class="positive-control",
        mutation_class="multi-leaf-receipt",
        target_path="$.backend_receipt.inclusion_proof",
        signing_state="valid-signatures",
        candidate=multi,
        expected_outcome="accepted",
        expected_code="PASS",
        notes="Six-leaf reference tree provides a non-empty inclusion path",
    )

    core_mutations: list[tuple[str, str, str, Mutation, str, str]] = [
        (
            "CORE-001",
            "actor-token",
            "$.evidence_core.actor.actor_ref_token",
            lambda x: x["evidence_core"]["actor"].__setitem__(
                "actor_ref_token", "urn:te:actor-token:substituted-reader"
            ),
            "TE-E-CORE-SIGNATURE",
            "Actor-token substitution with stale issuer signature",
        ),
        (
            "CORE-002",
            "actor-organisation",
            "$.evidence_core.actor.organisation_ref_token",
            lambda x: x["evidence_core"]["actor"].__setitem__(
                "organisation_ref_token", "urn:te:org-token:hospital-a"
            ),
            "TE-E-CORE-SIGNATURE",
            "Actor organisation substitution",
        ),
        (
            "CORE-003",
            "actor-role",
            "$.evidence_core.actor.role_code",
            lambda x: x["evidence_core"]["actor"].__setitem__(
                "role_code", "disclosure-service"
            ),
            "TE-E-CORE-SIGNATURE",
            "Admitted role-code substitution",
        ),
        (
            "CORE-004",
            "emitter-organisation",
            "$.evidence_core.emitter.organisation_ref_token",
            lambda x: x["evidence_core"]["emitter"].__setitem__(
                "organisation_ref_token", "urn:te:org-token:hospital-b"
            ),
            "TE-E-CORE-SIGNATURE",
            "Emitter organisation substitution",
        ),
        (
            "CORE-005",
            "consent-version",
            "$.evidence_core.consent_binding and objects[consent]",
            lambda x: (
                x["evidence_core"]["consent_binding"].__setitem__("consent_version", "4"),
                [
                    obj.__setitem__("resource_version_token", "4")
                    for obj in x["evidence_core"]["objects"]
                    if obj["object_role"] == "consent"
                ],
            ),
            "TE-E-CORE-SIGNATURE",
            "Coherent Consent-version substitution",
        ),
        (
            "CORE-006",
            "consent-state",
            "$.evidence_core.consent_binding.consent_state",
            lambda x: x["evidence_core"]["consent_binding"].__setitem__(
                "consent_state", "revoked"
            ),
            "TE-E-CONSENT-STATE",
            "HIE profile rejects a non-active Consent state before signature interpretation",
        ),
        (
            "CORE-007",
            "policy-version",
            "$.evidence_core.policy_binding and objects[policy]",
            lambda x: (
                x["evidence_core"]["policy_binding"].__setitem__("policy_version", "7"),
                [
                    obj.__setitem__("resource_version_token", "7")
                    for obj in x["evidence_core"]["objects"]
                    if obj["object_role"] == "policy"
                ],
            ),
            "TE-E-CORE-SIGNATURE",
            "Coherent policy-version substitution",
        ),
        (
            "CORE-008",
            "policy-digest",
            "$.evidence_core.policy_binding.policy_digest",
            lambda x: x["evidence_core"]["policy_binding"].__setitem__(
                "policy_digest", flip_hex(x["evidence_core"]["policy_binding"]["policy_digest"])
            ),
            "TE-E-CORE-SIGNATURE",
            "Policy digest substitution",
        ),
        (
            "CORE-009",
            "decision-reference",
            "$.evidence_core.objects[decision].object_ref_token",
            lambda x: [
                obj.__setitem__("object_ref_token", "urn:te:decision:D-205")
                for obj in x["evidence_core"]["objects"]
                if obj["object_role"] == "decision"
            ],
            "TE-E-CORE-SIGNATURE",
            "Authorisation-decision substitution",
        ),
        (
            "CORE-010",
            "outcome-reason",
            "$.evidence_core.outcome.reason_code",
            lambda x: x["evidence_core"]["outcome"].__setitem__(
                "reason_code", "policy-permit"
            ),
            "TE-E-CORE-SIGNATURE",
            "Outcome-reason substitution",
        ),
        (
            "CORE-011",
            "resource-reference-version",
            "$.evidence_core.objects[target]",
            lambda x: [
                (
                    obj.__setitem__(
                        "object_ref_token",
                        "urn:te:fhir-token:diagnostic-report-hie-001-v3",
                    ),
                    obj.__setitem__("resource_version_token", "3"),
                )
                for obj in x["evidence_core"]["objects"]
                if obj["object_role"] == "target"
            ],
            "TE-E-CORE-SIGNATURE",
            "DiagnosticReport reference and version substitution",
        ),
        (
            "CORE-012",
            "provenance-reference",
            "$.evidence_core.objects[provenance].object_ref_token",
            lambda x: [
                obj.__setitem__("object_ref_token", "urn:te:provenance-token:hie-002")
                for obj in x["evidence_core"]["objects"]
                if obj["object_role"] == "provenance"
            ],
            "TE-E-CORE-SIGNATURE",
            "Provenance reference substitution",
        ),
        (
            "CORE-013",
            "recipient-organisation",
            "$.evidence_core.event_facts.recipient_ref_token",
            lambda x: x["evidence_core"]["event_facts"].__setitem__(
                "recipient_ref_token", "urn:te:org-token:hospital-c"
            ),
            "TE-E-SCHEMA-VALUE",
            "Frozen hero-case recipient substitution is rejected semantically",
        ),
        (
            "CORE-014",
            "purpose",
            "$.evidence_core.purpose_code",
            lambda x: x["evidence_core"].__setitem__("purpose_code", "research"),
            "TE-E-SCHEMA-VALUE",
            "Frozen hero-case purpose substitution is rejected structurally",
        ),
        (
            "CORE-015",
            "unknown-critical-field",
            "$.evidence_core.critical_extension",
            lambda x: x["evidence_core"].__setitem__(
                "critical_extension", {"must_understand": True}
            ),
            "TE-E-SCHEMA-ADDITIONAL",
            "Closed schema rejects an unknown critical field",
        ),
        (
            "CORE-016",
            "issuer-signature-bytes",
            "$.evidence_core.emitter_signature.signature",
            lambda x: x["evidence_core"]["emitter_signature"].__setitem__(
                "signature",
                flip_signature(x["evidence_core"]["emitter_signature"]["signature"]),
            ),
            "TE-E-CORE-SIGNATURE",
            "One-bit issuer-signature mutation",
        ),
        (
            "CORE-017",
            "unknown-issuer-key",
            "$.evidence_core.emitter.key_id",
            lambda x: (
                x["evidence_core"]["emitter"].__setitem__(
                    "key_id", "urn:te:key:fixture-emitter-unknown"
                ),
                x["evidence_core"]["emitter_signature"].__setitem__(
                    "key_id", "urn:te:key:fixture-emitter-unknown"
                ),
            ),
            "TE-E-CORE-SIGNATURE",
            "Unknown issuer key identifier",
        ),
        (
            "CORE-018",
            "missing-issuer-signature",
            "$.evidence_core.emitter_signature",
            lambda x: x["evidence_core"].pop("emitter_signature"),
            "TE-E-SCHEMA-REQUIRED",
            "Required issuer signature removed",
        ),
    ]
    for case_id, mutation_class, target, mutation, expected_code, notes in core_mutations:
        record_verification(
            rows,
            evidence,
            case_id=case_id,
            case_class="signed-core-mutation",
            mutation_class=mutation_class,
            target_path=target,
            signing_state="stale-issuer-signature",
            candidate=mutate_copy(baseline, mutation),
            expected_outcome="rejected",
            expected_code=expected_code,
            notes=notes,
        )

    wrong_emitter_public = deterministic_test_private_key("c4-wrong-emitter").public_key()
    record_verification(
        rows,
        evidence,
        case_id="CORE-019",
        case_class="trust-registry-control",
        mutation_class="wrong-issuer-key-material",
        target_path="$emitter_key_registry",
        signing_state="valid-signature-wrong-verification-key",
        candidate=baseline,
        emitter_keys={FIXTURE_EMITTER_KEY_ID: wrong_emitter_public},
        expected_outcome="rejected",
        expected_code="TE-E-CORE-SIGNATURE",
        notes="Correct key identifier mapped to unrelated public-key material",
    )

    limitation_mutations: list[tuple[str, str, Mutation, str]] = [
        (
            "LIM-ISSUER-001",
            "authorised-actor-substitution",
            lambda x: (
                x["evidence_core"]["actor"].__setitem__(
                    "actor_ref_token", "urn:te:actor-token:issuer-asserted-alternative"
                ),
                x["evidence_core"]["actor"].__setitem__(
                    "organisation_ref_token", "urn:te:org-token:hospital-a"
                ),
            ),
            "An authorised/compromised issuer can sign a different schema-valid actor assertion",
        ),
        (
            "LIM-ISSUER-002",
            "authorised-consent-version",
            lambda x: (
                x["evidence_core"]["consent_binding"].__setitem__("consent_version", "4"),
                [
                    obj.__setitem__("resource_version_token", "4")
                    for obj in x["evidence_core"]["objects"]
                    if obj["object_role"] == "consent"
                ],
            ),
            "A valid signature does not independently establish the truth of the asserted Consent version",
        ),
        (
            "LIM-ISSUER-003",
            "authorised-policy-version",
            lambda x: (
                x["evidence_core"]["policy_binding"].__setitem__("policy_version", "7"),
                [
                    obj.__setitem__("resource_version_token", "7")
                    for obj in x["evidence_core"]["objects"]
                    if obj["object_role"] == "policy"
                ],
            ),
            "A valid signature does not independently establish policy truth",
        ),
    ]
    for case_id, mutation_class, mutation, notes in limitation_mutations:
        candidate = mutate_copy(baseline, mutation)
        candidate.pop("backend_receipt", None)
        resign_hie_core(candidate)
        candidate = fresh_receipt_for_core(candidate, dummy_count=2)
        record_verification(
            rows,
            evidence,
            case_id=case_id,
            case_class="limitation-observation",
            mutation_class=mutation_class,
            target_path="$.evidence_core",
            signing_state="core-and-receipt-validly-reissued-with-test-keys",
            candidate=candidate,
            expected_outcome="accepted",
            expected_code="PASS",
            notes=notes,
        )

    receipt_mutations: list[tuple[str, str, str, Mutation, str, str]] = [
        (
            "RCP-001",
            "core-digest",
            "$.backend_receipt.core_digest",
            lambda x: x["backend_receipt"].__setitem__(
                "core_digest", flip_hex(x["backend_receipt"]["core_digest"])
            ),
            "TE-E-RECEIPT-SIGNATURE",
            "Stale receipt signature after core-digest mutation",
        ),
        (
            "RCP-002",
            "leaf-hash",
            "$.backend_receipt.leaf_hash",
            lambda x: x["backend_receipt"].__setitem__(
                "leaf_hash", flip_hex(x["backend_receipt"]["leaf_hash"])
            ),
            "TE-E-RECEIPT-SIGNATURE",
            "Stale receipt signature after leaf-hash mutation",
        ),
        (
            "RCP-003",
            "proof-sibling",
            "$.backend_receipt.inclusion_proof.siblings[0]",
            lambda x: x["backend_receipt"]["inclusion_proof"]["siblings"].__setitem__(
                0, flip_hex(x["backend_receipt"]["inclusion_proof"]["siblings"][0])
            ),
            "TE-E-RECEIPT-SIGNATURE",
            "Stale receipt signature after proof mutation",
        ),
        (
            "RCP-004",
            "root",
            "$.backend_receipt.root_digest",
            lambda x: x["backend_receipt"].__setitem__(
                "root_digest", flip_hex(x["backend_receipt"]["root_digest"])
            ),
            "TE-E-RECEIPT-SIGNATURE",
            "Stale receipt signature after root mutation",
        ),
        (
            "RCP-005",
            "leaf-index-receipt-only",
            "$.backend_receipt.leaf_index",
            lambda x: x["backend_receipt"].__setitem__("leaf_index", 1),
            "TE-E-PROOF-INDEX",
            "Receipt/proof leaf-index mismatch",
        ),
        (
            "RCP-006",
            "tree-size-receipt-only",
            "$.backend_receipt.tree_size",
            lambda x: x["backend_receipt"].__setitem__(
                "tree_size", x["backend_receipt"]["tree_size"] + 1
            ),
            "TE-E-PROOF-SIZE",
            "Receipt/proof tree-size mismatch",
        ),
        (
            "RCP-007",
            "proof-digest",
            "$.backend_receipt.inclusion_proof_digest",
            lambda x: x["backend_receipt"].__setitem__(
                "inclusion_proof_digest",
                flip_hex(x["backend_receipt"]["inclusion_proof_digest"]),
            ),
            "TE-E-PROOF-DIGEST",
            "Proof-digest mismatch is detected independently",
        ),
        (
            "RCP-008",
            "backend-identifier",
            "$.backend_receipt.backend_id",
            lambda x: x["backend_receipt"].__setitem__(
                "backend_id", "urn:te:backend:other-reference"
            ),
            "TE-E-BACKEND-IDENTITY",
            "Expected backend identifier is pinned by verifier policy",
        ),
        (
            "RCP-009",
            "log-identifier",
            "$.backend_receipt.log_id",
            lambda x: x["backend_receipt"].__setitem__(
                "log_id", "urn:te:log:other-reference"
            ),
            "TE-E-LOG-IDENTITY",
            "Expected log identifier is pinned by verifier policy",
        ),
        (
            "RCP-010",
            "signer-identifier",
            "$.backend_receipt.signer_key_id",
            lambda x: x["backend_receipt"].__setitem__(
                "signer_key_id", "urn:te:key:fixture-backend-unknown"
            ),
            "TE-E-RECEIPT-SIGNATURE",
            "Signer identifier substitution",
        ),
        (
            "RCP-011",
            "receipt-signature-bytes",
            "$.backend_receipt.receipt_signature.signature",
            lambda x: x["backend_receipt"]["receipt_signature"].__setitem__(
                "signature",
                flip_signature(x["backend_receipt"]["receipt_signature"]["signature"]),
            ),
            "TE-E-RECEIPT-SIGNATURE",
            "One-bit receipt-signature mutation",
        ),
        (
            "RCP-012",
            "unknown-critical-field",
            "$.backend_receipt.critical_extension",
            lambda x: x["backend_receipt"].__setitem__(
                "critical_extension", {"must_understand": True}
            ),
            "TE-E-SCHEMA-ADDITIONAL",
            "Closed receipt schema rejects an unknown critical field",
        ),
    ]
    for case_id, mutation_class, target, mutation, expected_code, notes in receipt_mutations:
        record_verification(
            rows,
            evidence,
            case_id=case_id,
            case_class="receipt-mutation",
            mutation_class=mutation_class,
            target_path=target,
            signing_state="stale-receipt-signature",
            candidate=mutate_copy(multi, mutation),
            expected_outcome="rejected",
            expected_code=expected_code,
            notes=notes,
        )

    resigned_receipt_cases: list[
        tuple[str, str, str, Mutation, bool, str, str]
    ] = [
        (
            "RSIG-001",
            "core-digest",
            "$.backend_receipt.core_digest",
            lambda x: x["backend_receipt"].__setitem__(
                "core_digest", flip_hex(x["backend_receipt"]["core_digest"])
            ),
            False,
            "TE-E-RECEIPT-BINDING",
            "Backend re-signing cannot bind a receipt to another evidence core",
        ),
        (
            "RSIG-002",
            "proof-sibling",
            "$.backend_receipt.inclusion_proof.siblings[0]",
            lambda x: x["backend_receipt"]["inclusion_proof"]["siblings"].__setitem__(
                0, flip_hex(x["backend_receipt"]["inclusion_proof"]["siblings"][0])
            ),
            True,
            "TE-E-PROOF-PATH",
            "Recomputed proof digest and receipt signature do not repair an invalid Merkle path",
        ),
        (
            "RSIG-003",
            "root",
            "$.backend_receipt.root_digest",
            lambda x: x["backend_receipt"].__setitem__(
                "root_digest", flip_hex(x["backend_receipt"]["root_digest"])
            ),
            False,
            "TE-E-PROOF-PATH",
            "Re-signed altered root fails inclusion reconstruction",
        ),
        (
            "RSIG-004",
            "leaf-index",
            "$.backend_receipt.leaf_index and inclusion_proof.leaf_index",
            lambda x: (
                x["backend_receipt"].__setitem__("leaf_index", 1),
                x["backend_receipt"]["inclusion_proof"].__setitem__("leaf_index", 1),
            ),
            True,
            "TE-E-PROOF-PATH",
            "Coherently relabelled leaf index fails path verification",
        ),
        (
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
        (
            "RSIG-006",
            "proof-digest",
            "$.backend_receipt.inclusion_proof_digest",
            lambda x: x["backend_receipt"].__setitem__(
                "inclusion_proof_digest",
                flip_hex(x["backend_receipt"]["inclusion_proof_digest"]),
            ),
            False,
            "TE-E-PROOF-DIGEST",
            "Verifier recomputes the proof digest after receipt re-signing",
        ),
        (
            "RSIG-007",
            "backend-identifier",
            "$.backend_receipt.backend_id",
            lambda x: x["backend_receipt"].__setitem__(
                "backend_id", "urn:te:backend:other-reference"
            ),
            False,
            "TE-E-BACKEND-IDENTITY",
            "Expected backend identity is independent of signature validity",
        ),
        (
            "RSIG-008",
            "log-identifier",
            "$.backend_receipt.log_id",
            lambda x: x["backend_receipt"].__setitem__(
                "log_id", "urn:te:log:other-reference"
            ),
            False,
            "TE-E-LOG-IDENTITY",
            "Expected log identity is independent of signature validity",
        ),
    ]
    for (
        case_id,
        mutation_class,
        target,
        mutation,
        recompute,
        expected_code,
        notes,
    ) in resigned_receipt_cases:
        candidate = mutate_copy(multi, mutation)
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

    wrong_backend_public = deterministic_test_private_key("c4-wrong-backend").public_key()
    record_verification(
        rows,
        evidence,
        case_id="RSIG-009",
        case_class="trust-registry-control",
        mutation_class="wrong-backend-key-material",
        target_path="$receipt_key_registry",
        signing_state="valid-signature-wrong-verification-key",
        candidate=multi,
        receipt_keys={FIXTURE_BACKEND_KEY_ID: wrong_backend_public},
        expected_outcome="rejected",
        expected_code="TE-E-RECEIPT-SIGNATURE",
        notes="Correct backend key identifier mapped to unrelated public-key material",
    )

    replay_core = deepcopy(baseline)
    replay_core.pop("backend_receipt", None)
    replay_core["evidence_core"]["outcome"]["reason_code"] = "policy-permit"
    resign_hie_core(replay_core)
    replay_core["backend_receipt"] = deepcopy(baseline["backend_receipt"])
    record_verification(
        rows,
        evidence,
        case_id="RPL-001",
        case_class="receipt-replay-control",
        mutation_class="receipt-replayed-for-other-core",
        target_path="$.backend_receipt",
        signing_state="valid-new-core-signature-stale-receipt",
        candidate=replay_core,
        expected_outcome="rejected",
        expected_code="TE-E-RECEIPT-BINDING",
        notes="A receipt from one signed core cannot be attached to another validly signed core",
    )

    prefix_digests = [baseline_core_digest] + [
        hashlib.sha256(f"route-c-c4-prefix-{index}".encode()).hexdigest()
        for index in range(1, 3)
    ]
    prefix_log = build_log(prefix_digests)
    prefix_env = issue_for_baseline(signed, prefix_log, issued_at="2026-07-15T10:02:00.000Z")
    prefix_checkpoint = RetainedCheckpoint(
        FIXTURE_BACKEND_ID,
        FIXTURE_LOG_ID,
        prefix_log.tree_size,
        prefix_log.root_digest,
    )
    state = RetainedHIEVerifier(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, prefix_checkpoint)

    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-001",
        mutation_class="same-checkpoint-confirmation",
        candidate=prefix_env,
        expected_outcome="accepted",
        expected_code="PASS",
        expected_state_change=False,
        notes="A valid same-size receipt confirms but does not advance retained state",
    )

    rollback_log = build_log(prefix_digests[:2])
    rollback_env = issue_for_baseline(
        signed, rollback_log, issued_at="2026-07-15T10:02:01.000Z"
    )
    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-002",
        mutation_class="rollback",
        candidate=rollback_env,
        expected_outcome="rejected",
        expected_code="TE-E-CHECKPOINT-ROLLBACK",
        expected_state_change=False,
        notes="A valid smaller-tree receipt is rejected and retained state is unchanged",
    )

    fork_digests = [baseline_core_digest] + [
        hashlib.sha256(f"route-c-c4-fork-{index}".encode()).hexdigest()
        for index in range(1, 3)
    ]
    fork_log = build_log(fork_digests)
    fork_env = issue_for_baseline(signed, fork_log, issued_at="2026-07-15T10:02:02.000Z")
    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-003",
        mutation_class="same-size-fork",
        candidate=fork_env,
        expected_outcome="rejected",
        expected_code="TE-E-CHECKPOINT-FORK",
        expected_state_change=False,
        notes="A valid same-size alternative root is rejected against retained state",
    )

    record_verification(
        rows,
        evidence,
        case_id="LIM-BACKEND-001",
        case_class="limitation-observation",
        mutation_class="stateless-split-view",
        target_path="$retained_checkpoint",
        signing_state="valid-backend-signature-no-retained-state",
        candidate=fork_env,
        expected_outcome="accepted",
        expected_code="PASS",
        notes="Without retained state or external witnessing a coherent alternative tree is not distinguishable",
    )

    extension_digests = prefix_digests + [
        hashlib.sha256(f"route-c-c4-extension-{index}".encode()).hexdigest()
        for index in range(3, 5)
    ]
    extension_log = build_log(extension_digests)
    extension_env = issue_for_baseline(
        signed, extension_log, issued_at="2026-07-15T10:02:03.000Z"
    )
    consistency = extension_log.issue_consistency_proof(prefix_log.tree_size)

    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-004",
        mutation_class="missing-consistency-proof",
        candidate=extension_env,
        expected_outcome="rejected",
        expected_code="TE-E-CONSISTENCY-MISSING",
        expected_state_change=False,
        notes="A larger-tree receipt cannot advance state without a consistency proof",
    )

    bad_path = deepcopy(consistency)
    bad_path["hashes"][0] = flip_hex(bad_path["hashes"][0])
    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-005",
        mutation_class="consistency-path",
        candidate=extension_env,
        expected_outcome="rejected",
        expected_code="TE-E-CONSISTENCY-PATH",
        expected_state_change=False,
        consistency_proof=bad_path,
        notes="Mutated consistency path is rejected without checkpoint advancement",
    )

    bad_root = deepcopy(consistency)
    bad_root["first_root"] = flip_hex(bad_root["first_root"])
    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-006",
        mutation_class="consistency-root",
        candidate=extension_env,
        expected_outcome="rejected",
        expected_code="TE-E-CONSISTENCY-ROOT",
        expected_state_change=False,
        consistency_proof=bad_root,
        notes="Consistency proof naming another retained root is rejected",
    )

    bad_size = deepcopy(consistency)
    bad_size["first_size"] -= 1
    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-007",
        mutation_class="consistency-size",
        candidate=extension_env,
        expected_outcome="rejected",
        expected_code="TE-E-CONSISTENCY-SIZE",
        expected_state_change=False,
        consistency_proof=bad_size,
        notes="Consistency proof naming another retained size is rejected",
    )

    bad_identity = deepcopy(consistency)
    bad_identity["backend_id"] = "urn:te:backend:other-reference"
    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-008",
        mutation_class="consistency-identity",
        candidate=extension_env,
        expected_outcome="rejected",
        expected_code="TE-E-CONSISTENCY-IDENTITY",
        expected_state_change=False,
        consistency_proof=bad_identity,
        notes="Consistency proof from another backend identity is rejected",
    )

    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-009",
        mutation_class="valid-prefix-extension",
        candidate=extension_env,
        expected_outcome="accepted",
        expected_code="PASS",
        expected_state_change=True,
        consistency_proof=consistency,
        notes="A valid proof advances retained state from size three to size five",
    )

    record_state_case(
        rows,
        evidence,
        state,
        case_id="STATE-010",
        mutation_class="post-advance-old-receipt",
        candidate=prefix_env,
        expected_outcome="rejected",
        expected_code="TE-E-CHECKPOINT-ROLLBACK",
        expected_state_change=False,
        notes="After valid advancement an older valid receipt is rejected without rollback",
    )

    record_state_case(
        rows,
        evidence,
        state,
        case_id="LIM-REPLAY-001",
        mutation_class="exact-receipt-replay",
        candidate=extension_env,
        expected_outcome="accepted",
        expected_code="PASS",
        expected_state_change=False,
        notes="Exact same-state replay is accepted; freshness and duplicate suppression are higher-layer controls",
        case_class="limitation-observation",
    )

    target = next(item for item in event["object_contexts"] if item["object_role"] == "target")
    binding = target["payload_binding"]
    declared_commitment = str(binding["commitment"])

    record_boolean(
        rows,
        evidence,
        case_id="COMMIT-001",
        case_class="payload-commitment-control",
        mutation_class="positive-candidate",
        target_path="$authorised_source_bytes",
        expected_outcome="accepted",
        observed_check=verify_payload_commitment(
            declared_commitment,
            source_canonical,
            nonce=nonce,
            representation_profile=HIE_REPRESENTATION_PROFILE,
            commitment_context=HIE_COMMITMENT_CONTEXT,
        ),
        notes="Exact canonical source bytes and deterministic test nonce reproduce the declared commitment",
    )
    record_boolean(
        rows,
        evidence,
        case_id="COMMIT-002",
        case_class="payload-commitment-control",
        mutation_class="payload-byte",
        target_path="$authorised_source_bytes",
        expected_outcome="rejected",
        observed_check=verify_payload_commitment(
            declared_commitment,
            source_canonical + b" ",
            nonce=nonce,
            representation_profile=HIE_REPRESENTATION_PROFILE,
            commitment_context=HIE_COMMITMENT_CONTEXT,
        ),
        notes="One added payload byte changes the commitment",
    )
    record_boolean(
        rows,
        evidence,
        case_id="COMMIT-003",
        case_class="payload-commitment-control",
        mutation_class="representation-bytes",
        target_path="$authorised_source_serialisation",
        expected_outcome="rejected",
        observed_check=verify_payload_commitment(
            declared_commitment,
            source_pretty,
            nonce=nonce,
            representation_profile=HIE_REPRESENTATION_PROFILE,
            commitment_context=HIE_COMMITMENT_CONTEXT,
        ),
        notes="A different JSON serialisation of the source is not interchangeable with the committed canonical bytes",
    )
    changed_nonce = bytes([nonce[0] ^ 1]) + nonce[1:]
    record_boolean(
        rows,
        evidence,
        case_id="COMMIT-004",
        case_class="payload-commitment-control",
        mutation_class="nonce",
        target_path="$authorised_nonce",
        expected_outcome="rejected",
        observed_check=verify_payload_commitment(
            declared_commitment,
            source_canonical,
            nonce=changed_nonce,
            representation_profile=HIE_REPRESENTATION_PROFILE,
            commitment_context=HIE_COMMITMENT_CONTEXT,
        ),
        notes="Changed nonce is rejected",
    )
    record_boolean(
        rows,
        evidence,
        case_id="COMMIT-005",
        case_class="payload-commitment-control",
        mutation_class="representation-profile",
        target_path="$commitment.representation_profile",
        expected_outcome="rejected",
        observed_check=verify_payload_commitment(
            declared_commitment,
            source_canonical,
            nonce=nonce,
            representation_profile="application/fhir+json-other-v1",
            commitment_context=HIE_COMMITMENT_CONTEXT,
        ),
        notes="Representation-profile substitution changes the framed commitment",
    )
    record_boolean(
        rows,
        evidence,
        case_id="COMMIT-006",
        case_class="payload-commitment-control",
        mutation_class="commitment-context",
        target_path="$commitment.commitment_context",
        expected_outcome="rejected",
        observed_check=verify_payload_commitment(
            declared_commitment,
            source_canonical,
            nonce=nonce,
            representation_profile=HIE_REPRESENTATION_PROFILE,
            commitment_context="other-source-context",
        ),
        notes="Commitment-context substitution changes the framed commitment",
    )

    try:
        verify_payload_commitment(
            declared_commitment,
            source_canonical,
            nonce=b"short",
            representation_profile=HIE_REPRESENTATION_PROFILE,
            commitment_context=HIE_COMMITMENT_CONTEXT,
        )
        short_nonce_rejected = False
    except ValueError:
        short_nonce_rejected = True
    rows.append(
        result_row(
            case_id="COMMIT-007",
            case_class="payload-commitment-control",
            mutation_class="short-nonce",
            target_path="$authorised_nonce",
            signing_state="not-applicable",
            expected_outcome="rejected",
            observed_outcome="rejected" if short_nonce_rejected else "accepted",
            observed_codes=("TE-E-PAYLOAD-COMMITMENT",) if short_nonce_rejected else (),
            expected_code="TE-E-PAYLOAD-COMMITMENT",
            passed=short_nonce_rejected,
            notes="Nonce shorter than 128 bits raises a validation error",
        )
    )
    evidence.append(
        {
            "case_id": "COMMIT-007",
            "observed_outcome": "rejected" if short_nonce_rejected else "accepted",
            "observed_codes": ["TE-E-PAYLOAD-COMMITMENT"] if short_nonce_rejected else [],
            "expected_outcome": "rejected",
            "expected_code": "TE-E-PAYLOAD-COMMITMENT",
            "passed": short_nonce_rejected,
        }
    )

    public_values = [baseline, portable_bundle]

    def contains_nonce(value: Any) -> bool:
        if isinstance(value, dict):
            return "nonce" in value or any(contains_nonce(item) for item in value.values())
        if isinstance(value, list):
            return any(contains_nonce(item) for item in value)
        if isinstance(value, str):
            return nonce.hex() in value.lower()
        return False

    nonce_exposed = any(contains_nonce(value) for value in public_values)
    rows.append(
        result_row(
            case_id="COMMIT-008",
            case_class="payload-custody-control",
            mutation_class="portable-nonce-disclosure",
            target_path="$.signed_envelope and $.portable_bundle",
            signing_state="not-applicable",
            expected_outcome="absent",
            observed_outcome="present" if nonce_exposed else "absent",
            observed_codes=("TE-E-MIN-PAYLOAD",) if nonce_exposed else (),
            expected_code="PASS",
            passed=not nonce_exposed,
            notes="The deterministic test nonce is absent from portable artefacts but retained separately for reproducibility",
        )
    )
    evidence.append(
        {
            "case_id": "COMMIT-008",
            "observed_outcome": "present" if nonce_exposed else "absent",
            "observed_codes": ["TE-E-MIN-PAYLOAD"] if nonce_exposed else [],
            "expected_outcome": "absent",
            "expected_code": "PASS",
            "passed": not nonce_exposed,
        }
    )

    portable_text = stable_json_bytes(public_values)
    source_markers = [b'"valueQuantity"', b'"conclusion"', b"Synthetic results within"]
    marker_present = any(marker in portable_text for marker in source_markers)
    rows.append(
        result_row(
            case_id="COMMIT-009",
            case_class="payload-custody-control",
            mutation_class="clinical-source-marker-disclosure",
            target_path="$.signed_envelope and $.portable_bundle",
            signing_state="not-applicable",
            expected_outcome="absent",
            observed_outcome="present" if marker_present else "absent",
            observed_codes=("TE-E-MIN-PAYLOAD",) if marker_present else (),
            expected_code="PASS",
            passed=not marker_present,
            notes="Declared source-clinical markers are absent from the inspected portable artefacts",
        )
    )
    evidence.append(
        {
            "case_id": "COMMIT-009",
            "observed_outcome": "present" if marker_present else "absent",
            "observed_codes": ["TE-E-MIN-PAYLOAD"] if marker_present else [],
            "expected_outcome": "absent",
            "expected_code": "PASS",
            "passed": not marker_present,
        }
    )

    rows.sort(key=lambda row: row["case_id"])
    evidence.sort(key=lambda row: row["case_id"])

    expected_rejections = [row for row in rows if row["expected_outcome"] == "rejected"]
    false_accepts = [
        row["case_id"] for row in expected_rejections if row["observed_outcome"] != "rejected"
    ]
    expected_acceptances = [row for row in rows if row["expected_outcome"] == "accepted"]
    false_rejects = [
        row["case_id"] for row in expected_acceptances if row["observed_outcome"] != "accepted"
    ]
    failed_rows = [row["case_id"] for row in rows if row["passed"] != "true"]
    state_rows = [item for item in evidence if item["case_id"].startswith("STATE-")]
    state_nonadvancement_failures = [
        item["case_id"]
        for item in state_rows
        if item.get("observed_outcome") == "rejected" and item.get("state_changed")
    ]
    limitation_acceptances = [
        row["case_id"]
        for row in rows
        if row["case_class"] == "limitation-observation"
        and row["observed_outcome"] == "accepted"
    ]

    summary = {
        "run_id": RUN_ID,
        "software_status": SOFTWARE_STATUS,
        "case_count": len(rows),
        "passed_count": len(rows) - len(failed_rows),
        "failed_count": len(failed_rows),
        "failed_case_ids": failed_rows,
        "expected_rejection_count": len(expected_rejections),
        "observed_rejection_count": sum(
            row["observed_outcome"] == "rejected" for row in expected_rejections
        ),
        "false_accept_count": len(false_accepts),
        "false_accept_case_ids": false_accepts,
        "expected_acceptance_count": len(expected_acceptances),
        "false_reject_count": len(false_rejects),
        "false_reject_case_ids": false_rejects,
        "limitation_acceptance_count": len(limitation_acceptances),
        "limitation_acceptance_case_ids": limitation_acceptances,
        "state_rejection_count": sum(
            item.get("observed_outcome") == "rejected" for item in state_rows
        ),
        "state_nonadvancement_failure_count": len(state_nonadvancement_failures),
        "state_nonadvancement_failure_case_ids": state_nonadvancement_failures,
        "final_retained_checkpoint": snapshot_dict(state.snapshot()),
        "portable_nonce_exposed": nonce_exposed,
        "declared_clinical_source_marker_exposed": marker_present,
        "claim_boundary": {
            "issuer_signature": "detects unauthorised changes under the declared key registry; it does not prove identity, consent truth, policy truth or clinical truth",
            "payload_commitment": "binds exact candidate bytes, framing and nonce; it is not encryption or confidentiality",
            "receipt_signature": "authenticates the project receipt under the declared backend key registry; it does not prove completeness",
            "inclusion": "establishes membership in the declared local tree state for the supplied path",
            "retained_checkpoint": "detects rollback and verifier-visible same-size forks and requires a valid prefix-extension proof before local state advances",
            "replay": "exact same-state replay is accepted; freshness and duplicate suppression are outside the bounded verifier",
            "non_equivocation": "not established without retained state, gossip, witnessing or another cross-verifier comparison mechanism",
            "transport_encryption": "not implemented or evaluated by this local reference pipeline",
            "at_rest_encryption": "not implemented or evaluated by this local reference pipeline",
        },
    }

    output: dict[str, bytes] = {}
    if rows:
        import io

        handle = io.StringIO(newline="")
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        output["hie_security_mutation_results.csv"] = handle.getvalue().encode("utf-8")
    output["hie_security_mutation_run.json"] = (
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    output["hie_security_case_evidence.jsonl"] = b"".join(
        stable_json_bytes(item) for item in evidence
    )
    return output


def run(output_dir: Path, *, check: bool) -> int:
    expected = build_results()
    if check:
        failures: list[str] = []
        for name, content in expected.items():
            path = output_dir / name
            if not path.is_file():
                failures.append(f"missing retained output: {name}")
            elif path.read_bytes() != content:
                failures.append(f"retained output differs: {name}")
        unexpected = sorted(
            path.name
            for path in output_dir.glob("*")
            if path.is_file() and path.name not in expected and path.name != "README.md"
        )
        if unexpected:
            failures.append("unexpected retained outputs: " + ", ".join(unexpected))
        if failures:
            print("C4-HIE-SECURITY: FAIL")
            print("\n".join(failures))
            return 1
        summary = json.loads(expected["hie_security_mutation_run.json"])
        print(
            "C4-HIE-SECURITY: PASS "
            f"({summary['case_count']} cases; {summary['expected_rejection_count']} expected rejections; "
            f"{summary['false_accept_count']} false accepts; "
            f"{summary['state_nonadvancement_failure_count']} state non-advancement failures)"
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in expected.items():
        (output_dir / name).write_bytes(content)
    summary = json.loads(expected["hie_security_mutation_run.json"])
    print(
        "C4-HIE-SECURITY: WROTE "
        f"{summary['case_count']} cases with {summary['false_accept_count']} false accepts"
    )
    return 0 if summary["failed_count"] == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return run(args.output_dir.resolve(), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
