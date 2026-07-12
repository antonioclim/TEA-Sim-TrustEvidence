"""Ed25519 signatures and nonce-based payload commitments."""

from __future__ import annotations

import base64
import hmac
from dataclasses import dataclass
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .hashing import (
    core_digest_bytes,
    core_signature_message,
    payload_commitment_bytes,
    receipt_digest_bytes,
    receipt_signature_message,
)
from .profiles import ENVELOPE_PROFILE


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    if not isinstance(value, str):
        raise ValueError("base64url value must be a string")
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


@dataclass(frozen=True, slots=True)
class SignatureCheck:
    accepted: bool
    code: str
    detail: str


def sign_evidence_core(
    core: dict[str, Any], *, private_key: Ed25519PrivateKey, key_id: str
) -> tuple[dict[str, str], str]:
    emitter_key_id = core.get("emitter", {}).get("key_id") if isinstance(core.get("emitter"), dict) else None
    if emitter_key_id != key_id:
        raise ValueError("Emitter key identifier differs from the signing key identifier")
    digest = core_digest_bytes(core, envelope_profile=ENVELOPE_PROFILE)
    message = core_signature_message(digest, algorithm="Ed25519", key_id=key_id)
    return {
        "algorithm": "Ed25519",
        "key_id": key_id,
        "signature": b64url_encode(private_key.sign(message)),
    }, digest.hex()


def verify_evidence_core_signature(
    core: dict[str, Any], key_registry: Mapping[str, Ed25519PublicKey]
) -> SignatureCheck:
    signature = core.get("emitter_signature")
    if not isinstance(signature, dict):
        return SignatureCheck(False, "TE-E-CORE-SIGNATURE", "Emitter signature is absent")
    if signature.get("algorithm") != "Ed25519":
        return SignatureCheck(False, "TE-E-CORE-SIGNATURE", "Unsupported emitter signature algorithm")
    key_id = signature.get("key_id")
    emitter_key_id = core.get("emitter", {}).get("key_id") if isinstance(core.get("emitter"), dict) else None
    if key_id != emitter_key_id:
        return SignatureCheck(False, "TE-E-CORE-SIGNATURE", "Emitter and signature key identifiers differ")
    public_key = key_registry.get(str(key_id))
    if public_key is None:
        return SignatureCheck(False, "TE-E-CORE-SIGNATURE", "Emitter key identifier is not registered")
    try:
        digest = core_digest_bytes(core, envelope_profile=ENVELOPE_PROFILE)
        message = core_signature_message(digest, algorithm="Ed25519", key_id=str(key_id))
        raw = b64url_decode(str(signature.get("signature", "")))
        if len(raw) != 64:
            raise ValueError("Ed25519 signature length")
        public_key.verify(raw, message)
    except (InvalidSignature, ValueError, TypeError):
        return SignatureCheck(False, "TE-E-CORE-SIGNATURE", "Emitter signature verification failed")
    return SignatureCheck(True, "PASS", "Emitter signature verified")


def sign_receipt(
    receipt_without_signature: dict[str, Any], *, private_key: Ed25519PrivateKey, key_id: str
) -> tuple[dict[str, str], str]:
    if receipt_without_signature.get("signer_key_id") != key_id:
        raise ValueError("Receipt signer identifier differs from the signing key identifier")
    digest = receipt_digest_bytes(receipt_without_signature)
    message = receipt_signature_message(digest, algorithm="Ed25519", key_id=key_id)
    return {
        "algorithm": "Ed25519",
        "key_id": key_id,
        "signature": b64url_encode(private_key.sign(message)),
    }, digest.hex()


def verify_receipt_signature(
    receipt: dict[str, Any], key_registry: Mapping[str, Ed25519PublicKey]
) -> SignatureCheck:
    signature = receipt.get("receipt_signature")
    if not isinstance(signature, dict):
        return SignatureCheck(False, "TE-E-RECEIPT-SIGNATURE", "Receipt signature is absent")
    if signature.get("algorithm") != "Ed25519":
        return SignatureCheck(False, "TE-E-RECEIPT-SIGNATURE", "Unsupported receipt signature algorithm")
    key_id = signature.get("key_id")
    if key_id != receipt.get("signer_key_id"):
        return SignatureCheck(False, "TE-E-RECEIPT-SIGNATURE", "Receipt signer identifiers differ")
    public_key = key_registry.get(str(key_id))
    if public_key is None:
        return SignatureCheck(False, "TE-E-RECEIPT-SIGNATURE", "Receipt key identifier is not registered")
    try:
        digest = receipt_digest_bytes(receipt)
        message = receipt_signature_message(digest, algorithm="Ed25519", key_id=str(key_id))
        raw = b64url_decode(str(signature.get("signature", "")))
        if len(raw) != 64:
            raise ValueError("Ed25519 signature length")
        public_key.verify(raw, message)
    except (InvalidSignature, ValueError, TypeError):
        return SignatureCheck(False, "TE-E-RECEIPT-SIGNATURE", "Receipt signature verification failed")
    return SignatureCheck(True, "PASS", "Receipt signature verified")


def commit_payload(
    payload: bytes,
    *,
    nonce: bytes,
    representation_profile: str,
    commitment_context: str,
) -> str:
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if not isinstance(nonce, bytes) or len(nonce) < 16:
        raise ValueError("Payload commitment nonce must contain at least 128 bits")
    representation_profile.encode("ascii")
    commitment_context.encode("ascii")
    return payload_commitment_bytes(
        payload,
        nonce=nonce,
        representation_profile=representation_profile,
        commitment_context=commitment_context,
    ).hex()


def verify_payload_commitment(
    expected_hex: str,
    payload: bytes,
    *,
    nonce: bytes,
    representation_profile: str,
    commitment_context: str,
) -> bool:
    actual = commit_payload(
        payload,
        nonce=nonce,
        representation_profile=representation_profile,
        commitment_context=commitment_context,
    )
    return hmac.compare_digest(actual, expected_hex)
