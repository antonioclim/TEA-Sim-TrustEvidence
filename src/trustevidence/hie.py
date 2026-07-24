"""Route C healthcare-information-exchange profile and verifier.

The HIE profile is intentionally separate from the v2.1 personal-monitoring
profile. It reuses the project's deterministic canonicalisation, Ed25519 test
fixtures and local A2 Merkle implementation without claiming SCITT or COSE
Receipt conformance.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .backends.a2_merkle import (
    LocalA2MerkleLog,
    RetainedCheckpoint,
    VerificationIssue,
    VerificationResult,
    attach_receipt,
    leaf_hash,
    verify_consistency,
    verify_inclusion,
)
from .canonical import normalise_timestamp_ms
from .crypto import b64url_decode, b64url_encode, verify_receipt_signature
from .hashing import (
    core_digest_bytes,
    core_digest_hex,
    core_signature_message,
    leaf_input_bytes,
    proof_digest_hex,
)
from .hie_validation import validate_hie_disclosure_event, validate_hie_envelope
from .testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

HIE_INPUT_VERSION = "1.0.0"
HIE_ENVELOPE_VERSION = "1.0.0"
HIE_ENVELOPE_PROFILE = "TE-HIE-Envelope-1"
HIE_MINIMISATION_PROFILE = "TE-HIE-Min-1"
HIE_TOKENISATION_PROFILE = "TE-Token-Pseudonymous-1"
HIE_COMMITMENT_CONTEXT = "diagnostic-report-source-v1"
HIE_REPRESENTATION_PROFILE = "application/fhir+json-rfc8785-v1"

_EVIDENCE_NAMESPACE = uuid.UUID("c36e61e2-a960-5d55-8b5c-a34480b12311")


def _add(issues: list[VerificationIssue], code: str, detail: str) -> None:
    if code not in {item.code for item in issues}:
        issues.append(VerificationIssue(code, detail))


def _normalise_facts(value: dict[str, Any]) -> dict[str, Any]:
    facts = deepcopy(value)
    for key in ("effective_at", "activity_started_at", "activity_ended_at"):
        if key in facts:
            facts[key] = normalise_timestamp_ms(facts[key])
    return facts


def _sign_hie_core(
    core: dict[str, Any],
    *,
    private_key: Ed25519PrivateKey,
    key_id: str,
) -> tuple[dict[str, str], str]:
    if core.get("emitter", {}).get("key_id") != key_id:
        raise ValueError("Emitter key identifier differs from the signing key identifier")
    digest = core_digest_bytes(core, envelope_profile=HIE_ENVELOPE_PROFILE)
    message = core_signature_message(digest, algorithm="Ed25519", key_id=key_id)
    return {
        "algorithm": "Ed25519",
        "key_id": key_id,
        "signature": b64url_encode(private_key.sign(message)),
    }, digest.hex()


def verify_hie_core_signature(
    core: dict[str, Any],
    key_registry: Mapping[str, Ed25519PublicKey],
) -> tuple[bool, str, str]:
    signature = core.get("emitter_signature")
    if not isinstance(signature, dict):
        return False, "TE-E-CORE-SIGNATURE", "Emitter signature is absent"
    if signature.get("algorithm") != "Ed25519":
        return False, "TE-E-CORE-SIGNATURE", "Unsupported emitter signature algorithm"
    key_id = signature.get("key_id")
    if key_id != core.get("emitter", {}).get("key_id"):
        return False, "TE-E-CORE-SIGNATURE", "Emitter and signature key identifiers differ"
    public_key = key_registry.get(str(key_id))
    if public_key is None:
        return False, "TE-E-CORE-SIGNATURE", "Emitter key identifier is not registered"
    try:
        digest = core_digest_bytes(core, envelope_profile=HIE_ENVELOPE_PROFILE)
        message = core_signature_message(digest, algorithm="Ed25519", key_id=str(key_id))
        raw = b64url_decode(str(signature.get("signature", "")))
        if len(raw) != 64:
            raise ValueError("Ed25519 signature length")
        public_key.verify(raw, message)
    except (InvalidSignature, ValueError, TypeError):
        return False, "TE-E-CORE-SIGNATURE", "Emitter signature verification failed"
    return True, "PASS", "Emitter signature verified"


def build_hie_signed_envelope(
    event: dict[str, Any],
    *,
    emitted_at: str,
    private_key: Ed25519PrivateKey,
) -> tuple[dict[str, Any], str]:
    validation = validate_hie_disclosure_event(event)
    if not validation.accepted:
        details = "; ".join(f"{item.code} {item.path}: {item.message}" for item in validation.issues)
        raise ValueError(f"HIE disclosure event is invalid: {details}")

    source = event["source_boundary"]
    core: dict[str, Any] = {
        "evidence_id": f"urn:uuid:{uuid.uuid5(_EVIDENCE_NAMESPACE, event['source_event_id'])}",
        "event_id": event["source_event_id"],
        "event_type": event["event_type"],
        "occurred_at": normalise_timestamp_ms(event["occurred_at"]),
        "emitted_at": normalise_timestamp_ms(emitted_at),
        "time_source": deepcopy(source["time_source"]),
        "emitter": {
            "emitter_id": source["source_id"],
            "role_code": source["source_role_code"],
            "organisation_ref_token": source["organisation_ref_token"],
            "key_id": source["key_id"],
        },
        "subject_context": deepcopy(event["subject_context"]),
        "objects": deepcopy(event["object_contexts"]),
        "purpose_code": event["purpose_code"],
        "outcome": deepcopy(event["outcome"]),
        "privacy_profile": deepcopy(event["privacy_profile"]),
        "event_facts": _normalise_facts(event["event_facts"]),
        "actor": deepcopy(event["actor_context"]),
        "policy_binding": deepcopy(event["policy_context"]["policy_binding"]),
        "consent_binding": deepcopy(event["policy_context"]["consent_binding"]),
    }
    signature, digest = _sign_hie_core(core, private_key=private_key, key_id=source["key_id"])
    core["emitter_signature"] = signature
    envelope = {
        "envelope_version": HIE_ENVELOPE_VERSION,
        "profile": HIE_ENVELOPE_PROFILE,
        "evidence_core": core,
    }
    envelope_validation = validate_hie_envelope(envelope)
    if not envelope_validation.accepted:
        details = "; ".join(f"{item.code} {item.path}: {item.message}" for item in envelope_validation.issues)
        raise ValueError(f"Constructed HIE envelope is invalid: {details}")
    return envelope, digest


def build_hie_fixture_envelope(event: dict[str, Any], *, emitted_at: str) -> dict[str, Any]:
    envelope, _ = build_hie_signed_envelope(
        event,
        emitted_at=emitted_at,
        private_key=fixture_emitter_private_key(),
    )
    return envelope


def attach_hie_fixture_receipt(
    envelope: dict[str, Any],
    *,
    issued_at: str | None = None,
) -> tuple[dict[str, Any], RetainedCheckpoint]:
    validation = validate_hie_envelope(envelope)
    if not validation.accepted:
        raise ValueError("Cannot receipt an invalid HIE envelope")
    digest = core_digest_hex(envelope["evidence_core"], envelope_profile=HIE_ENVELOPE_PROFILE)
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    index = log.append_core_digest(digest)
    if issued_at is None:
        emitted = datetime.fromisoformat(envelope["evidence_core"]["emitted_at"].replace("Z", "+00:00"))
        issued_at = (emitted + timedelta(seconds=1)).astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    receipt = log.issue_receipt(
        index,
        issued_at=issued_at,
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    checkpoint = RetainedCheckpoint(
        backend_id=log.backend_id,
        log_id=log.log_id,
        tree_size=log.tree_size,
        root_digest=log.root_digest,
    )
    return attach_receipt(envelope, receipt), checkpoint


def _verify_hie_consistency(
    proof: Mapping[str, Any],
    *,
    retained: RetainedCheckpoint,
    backend_id: str,
    log_id: str,
    current_size: int,
    current_root: str,
) -> tuple[VerificationIssue, ...]:
    issues: list[VerificationIssue] = []
    if proof.get("profile") != "TE-A2-Consistency-1":
        _add(issues, "TE-E-CONSISTENCY-STRUCTURE", "Unsupported consistency-proof profile")
    if proof.get("backend_id") != backend_id or proof.get("log_id") != log_id:
        _add(issues, "TE-E-CONSISTENCY-IDENTITY", "Consistency proof belongs to another backend/log")
    if proof.get("first_size") != retained.tree_size or proof.get("second_size") != current_size:
        _add(issues, "TE-E-CONSISTENCY-SIZE", "Consistency-proof sizes do not match retained state")
    if proof.get("first_root") != retained.root_digest or proof.get("second_root") != current_root:
        _add(issues, "TE-E-CONSISTENCY-ROOT", "Consistency-proof roots do not match retained state")
    try:
        hashes = [bytes.fromhex(str(item)) for item in proof.get("hashes", [])]
    except (TypeError, ValueError):
        hashes = []
        _add(issues, "TE-E-CONSISTENCY-STRUCTURE", "Consistency proof contains invalid hashes")
    if not issues:
        try:
            accepted = verify_consistency(
                first_size=retained.tree_size,
                second_size=current_size,
                first_root=bytes.fromhex(retained.root_digest),
                second_root=bytes.fromhex(current_root),
                hashes=hashes,
            )
        except (TypeError, ValueError):
            accepted = False
        if not accepted:
            _add(issues, "TE-E-CONSISTENCY-PATH", "Consistency path does not prove append-only extension")
    return tuple(issues)


def verify_hie_envelope_receipt(
    envelope: dict[str, Any],
    *,
    emitter_keys: Mapping[str, Ed25519PublicKey],
    receipt_keys: Mapping[str, Ed25519PublicKey],
    expected_backend_id: str | None = None,
    expected_log_id: str | None = None,
    retained_checkpoint: RetainedCheckpoint | None = None,
    consistency_proof: Mapping[str, Any] | None = None,
) -> VerificationResult:
    issues: list[VerificationIssue] = []
    validation = validate_hie_envelope(envelope)
    if not validation.accepted:
        for item in validation.issues:
            _add(issues, item.code, item.message)
        return VerificationResult(False, tuple(issues))

    core = envelope["evidence_core"]
    receipt = envelope.get("backend_receipt")
    if not isinstance(receipt, dict):
        return VerificationResult(
            False,
            (VerificationIssue("TE-E-RECEIPT-MISSING", "Envelope has no backend receipt"),),
        )

    core_ok, core_code, core_detail = verify_hie_core_signature(core, emitter_keys)
    if not core_ok:
        _add(issues, core_code, core_detail)
    receipt_check = verify_receipt_signature(receipt, receipt_keys)
    if not receipt_check.accepted:
        _add(issues, receipt_check.code, receipt_check.detail)

    if expected_backend_id is not None and receipt.get("backend_id") != expected_backend_id:
        _add(issues, "TE-E-BACKEND-IDENTITY", "Receipt backend identifier differs from expected")
    if expected_log_id is not None and receipt.get("log_id") != expected_log_id:
        _add(issues, "TE-E-LOG-IDENTITY", "Receipt log identifier differs from expected")

    computed_core = core_digest_hex(core, envelope_profile=HIE_ENVELOPE_PROFILE)
    if receipt.get("core_digest") != computed_core:
        _add(issues, "TE-E-RECEIPT-BINDING", "Receipt core digest does not match the signed HIE core")

    try:
        expected_leaf_input = leaf_input_bytes(
            backend_id=str(receipt.get("backend_id")),
            log_id=str(receipt.get("log_id")),
            core_digest_hex_value=str(receipt.get("core_digest")),
        )
        expected_leaf = leaf_hash(expected_leaf_input).hex()
    except (TypeError, ValueError):
        expected_leaf = ""
    if receipt.get("leaf_hash") != expected_leaf:
        _add(issues, "TE-E-LEAF-BINDING", "Leaf hash does not bind backend, log and HIE core digest")

    proof = receipt.get("inclusion_proof")
    if not isinstance(proof, dict):
        _add(issues, "TE-E-PROOF-STRUCTURE", "Inclusion proof is absent")
    else:
        if receipt.get("leaf_index") != proof.get("leaf_index"):
            _add(issues, "TE-E-PROOF-INDEX", "Receipt and proof leaf indices differ")
        if receipt.get("tree_size") != proof.get("tree_size"):
            _add(issues, "TE-E-PROOF-SIZE", "Receipt and proof tree sizes differ")
        try:
            observed_proof_digest = proof_digest_hex(proof)
        except Exception:
            observed_proof_digest = ""
        if receipt.get("inclusion_proof_digest") != observed_proof_digest:
            _add(issues, "TE-E-PROOF-DIGEST", "Proof digest does not match proof material")
        try:
            siblings = [bytes.fromhex(str(item)) for item in proof.get("siblings", [])]
            inclusion_ok = verify_inclusion(
                bytes.fromhex(str(receipt.get("leaf_hash"))),
                leaf_index=int(receipt.get("leaf_index")),
                tree_size=int(receipt.get("tree_size")),
                siblings=siblings,
                root_hash=bytes.fromhex(str(receipt.get("root_digest"))),
            )
        except (TypeError, ValueError):
            inclusion_ok = False
        if not inclusion_ok:
            _add(issues, "TE-E-PROOF-PATH", "Inclusion path does not reconstruct the signed root")

    if retained_checkpoint is not None:
        if (
            receipt.get("backend_id") != retained_checkpoint.backend_id
            or receipt.get("log_id") != retained_checkpoint.log_id
        ):
            _add(issues, "TE-E-CHECKPOINT-IDENTITY", "Retained checkpoint belongs to another backend/log")
        else:
            try:
                new_size = int(receipt.get("tree_size"))
            except (TypeError, ValueError):
                new_size = -1
            current_root = str(receipt.get("root_digest"))
            if new_size < retained_checkpoint.tree_size:
                _add(issues, "TE-E-CHECKPOINT-ROLLBACK", "Receipt tree size is smaller than retained state")
            elif new_size == retained_checkpoint.tree_size:
                if current_root != retained_checkpoint.root_digest:
                    _add(issues, "TE-E-CHECKPOINT-FORK", "Same-size root differs from retained state")
            elif consistency_proof is None:
                _add(issues, "TE-E-CONSISTENCY-MISSING", "Larger-tree receipt requires a consistency proof")
            else:
                for issue in _verify_hie_consistency(
                    consistency_proof,
                    retained=retained_checkpoint,
                    backend_id=str(receipt.get("backend_id")),
                    log_id=str(receipt.get("log_id")),
                    current_size=new_size,
                    current_root=current_root,
                ):
                    _add(issues, issue.code, issue.detail)

    return VerificationResult(not issues, tuple(issues))


def verification_report(result: VerificationResult) -> dict[str, Any]:
    return {
        "accepted": result.accepted,
        "primary_code": result.primary_code,
        "issues": [asdict(item) for item in result.issues],
        "profile": HIE_ENVELOPE_PROFILE,
        "claim_boundary": {
            "issuer_signature": "authenticates the declared core under the fixture key assumptions",
            "payload_commitment": "binds withheld bytes and nonce; it is not encryption",
            "inclusion": "proves membership in the declared local tree state",
            "completeness": "not established",
            "clinical_truth": "not established",
        },
    }
