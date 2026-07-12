"""TE-HASH-1 length-prefixed, domain-separated SHA-256 operations."""

from __future__ import annotations

import hashlib
from typing import Any

from .canonical import canonicalise_te, unsigned_core, unsigned_receipt

HASH_ALGORITHM = "SHA-256"


def _as_bytes(value: str | bytes) -> bytes:
    return value if isinstance(value, bytes) else value.encode("utf-8")


def tuple_encode(*parts: str | bytes) -> bytes:
    output = bytearray()
    for part in parts:
        raw = _as_bytes(part)
        output.extend(len(raw).to_bytes(8, "big"))
        output.extend(raw)
    return bytes(output)


def domain_digest(domain: str, *parts: str | bytes) -> bytes:
    return hashlib.sha256(tuple_encode(domain, HASH_ALGORITHM, *parts)).digest()


def core_digest_bytes(core: dict[str, Any], *, envelope_profile: str) -> bytes:
    return domain_digest("TE-CMPB:core:v1", envelope_profile, canonicalise_te(unsigned_core(core)))


def core_digest_hex(core: dict[str, Any], *, envelope_profile: str) -> str:
    return core_digest_bytes(core, envelope_profile=envelope_profile).hex()


def core_signature_message(core_digest: bytes, *, algorithm: str, key_id: str) -> bytes:
    return tuple_encode("TE-CMPB:core-signature:v1", algorithm, key_id, core_digest)


def payload_commitment_bytes(
    payload: bytes,
    *,
    nonce: bytes,
    representation_profile: str,
    commitment_context: str,
) -> bytes:
    return domain_digest(
        "TE-CMPB:payload:v1",
        representation_profile,
        commitment_context,
        nonce,
        payload,
    )


def leaf_input_bytes(*, backend_id: str, log_id: str, core_digest_hex_value: str) -> bytes:
    return tuple_encode(
        "TE-CMPB:a2-leaf-input:v1",
        HASH_ALGORITHM,
        backend_id,
        log_id,
        bytes.fromhex(core_digest_hex_value),
    )


def proof_digest_bytes(proof: dict[str, Any]) -> bytes:
    return domain_digest("TE-CMPB:a2-proof:v1", canonicalise_te(proof))


def proof_digest_hex(proof: dict[str, Any]) -> str:
    return proof_digest_bytes(proof).hex()


def receipt_digest_bytes(receipt: dict[str, Any]) -> bytes:
    return domain_digest("TE-CMPB:a2-receipt:v1", canonicalise_te(unsigned_receipt(receipt)))


def receipt_digest_hex(receipt: dict[str, Any]) -> str:
    return receipt_digest_bytes(receipt).hex()


def receipt_signature_message(receipt_digest: bytes, *, algorithm: str, key_id: str) -> bytes:
    return tuple_encode("TE-CMPB:a2-receipt-signature:v1", algorithm, key_id, receipt_digest)
