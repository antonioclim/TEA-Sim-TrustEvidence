from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import httpx
from cryptography.hazmat.primitives import serialization

from trustevidence.adapters.common import b64_to_hex, hex_to_b64, now_z, signed_receipt
from trustevidence.canonical import core_hash_b64
from trustevidence.errors import UNAVAILABLE_PROOF, TrustEvidenceError


def _public_key_pem_b64(pair: Any) -> str:
    public_key = pair.public_key
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return base64.b64encode(pem).decode("ascii")


def _pick_entry(response_json: Any) -> tuple[str, dict[str, Any]]:
    if isinstance(response_json, dict) and len(response_json) == 1:
        uuid, entry = next(iter(response_json.items()))
        if isinstance(entry, dict):
            return str(uuid), entry
    if isinstance(response_json, dict):
        uuid = str(response_json.get("uuid") or response_json.get("entryUUID") or response_json.get("logID") or "unknown")
        return uuid, response_json
    raise TrustEvidenceError(UNAVAILABLE_PROOF, "unexpected Rekor response shape")


@dataclass(slots=True)
class RekorClientAdapter:
    """Rekor v1 REST adapter for TrustEvidence evidence hashes.

    The adapter submits a hashedrekord-style proposed entry containing the
    TrustEvidence core hash and normalises the returned transparency-log
    information into the v2.0.0 backend receipt shape.
    """

    base_url: str
    backend_id: str
    signer: Any
    alg_id: str = "sha256-te-v2"
    timeout_s: float = 20.0

    @property
    def log_id(self) -> str:
        return self.base_url.rstrip("/")

    def proposed_entry(self, envelope: dict[str, Any]) -> dict[str, Any]:
        core = envelope["artefact_core"]
        sig = core.get("emitter_signature", {})
        signature = sig.get("signature_value", "")
        return {
            "apiVersion": "0.0.1",
            "kind": "hashedrekord",
            "spec": {
                "data": {"hash": {"algorithm": "sha256", "value": b64_to_hex(core_hash_b64(core, self.alg_id))}},
                "signature": {
                    "content": signature,
                    "publicKey": {"content": _public_key_pem_b64(self.signer)},
                },
            },
        }

    def append(self, envelope: dict[str, Any]) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/api/v1/log/entries"
        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(url, json=self.proposed_entry(envelope))
            if response.status_code not in (200, 201, 409):
                raise TrustEvidenceError(UNAVAILABLE_PROOF, f"Rekor append failed: {response.status_code} {response.text}")
            uuid, entry = _pick_entry(response.json())
        verification = entry.get("verification", {}) if isinstance(entry, dict) else {}
        proof = verification.get("inclusionProof", {}) if isinstance(verification, dict) else {}
        root_hash = proof.get("rootHash") or proof.get("root_hash") or entry.get("rootHash") or entry.get("root_hash")
        if root_hash and all(c in "0123456789abcdefABCDEF" for c in str(root_hash).removeprefix("0x")):
            root_hash = hex_to_b64(str(root_hash))
        tree_size = int(proof.get("treeSize") or proof.get("tree_size") or entry.get("treeSize") or 0)
        leaf_index = int(entry.get("logIndex") or proof.get("logIndex") or 0)
        receipt = {
            "backend_type": "rekor",
            "backend_id": self.backend_id,
            "log_id": self.log_id,
            "alg_id": self.alg_id,
            "core_hash": core_hash_b64(envelope["artefact_core"], self.alg_id),
            "tree_size": tree_size,
            "leaf_index": leaf_index,
            "inclusion_proof_ref": f"urn:te:rekor:entry:{uuid}",
            "issued_at": now_z(),
            "signer_id": self.signer.key_id,
        }
        if root_hash:
            receipt["root_hash"] = root_hash
        if verification.get("signedEntryTimestamp"):
            receipt["witness_ref"] = f"urn:te:rekor:set:{uuid}"
        out = dict(envelope)
        out["backend_receipt"] = signed_receipt(receipt, self.signer)
        return out
