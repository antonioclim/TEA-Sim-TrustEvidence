from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from trustevidence.canonical import b64url_decode, b64url_encode, canon_te, core_hash, core_hash_b64
from trustevidence.crypto import sign_receipt


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def envelope_digest_b64(envelope: dict[str, Any]) -> str:
    return b64url_encode(hashlib.sha256(canon_te(envelope)).digest())


def b64_to_hex(value: str) -> str:
    return b64url_decode(value).hex()


def hex_to_b64(value: str) -> str:
    value = value.removeprefix("0x")
    if len(value) % 2:
        value = "0" + value
    return b64url_encode(bytes.fromhex(value))


def signed_receipt(receipt: dict[str, Any], signer: Any) -> dict[str, Any]:
    receipt = dict(receipt)
    receipt.setdefault(
        "receipt_signature",
        {"alg_id": "ed25519", "key_id": signer.key_id, "signature_value": "AA"},
    )
    receipt.setdefault("signer_id", signer.key_id)
    return sign_receipt(receipt, signer)


@dataclass(slots=True)
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    def run(self, args: list[str], *, timeout: int = 60) -> CommandResult: ...
