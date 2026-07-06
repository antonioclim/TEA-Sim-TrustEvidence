from __future__ import annotations

import datetime
import hashlib
import json
import uuid
from typing import Any, Dict

CANONICAL_HASH_FIELD = "canonical_hash"


def evidence_for_hash(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Return the evidence material used for canonical hashing.

    The stored canonical_hash field is deliberately excluded. This avoids a
    self-referential digest and makes receipt binding deterministic.
    """
    return {k: v for k, v in obj.items() if k != CANONICAL_HASH_FIELD}


def canonical_bytes(obj: Dict[str, Any], *, exclude_hash_field: bool = True) -> bytes:
    material = evidence_for_hash(obj) if exclude_hash_field else obj
    return json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(obj: Dict[str, Any]) -> str:
    return sha256_hex(canonical_bytes(obj, exclude_hash_field=True))


def make_evidence(i: int, policy: str = "policy-v1", backend: str = "A2_MERKLE") -> Dict[str, Any]:
    payload_hash = sha256_hex(f"payload-{i}".encode("utf-8"))
    obj: Dict[str, Any] = {
        "evidence_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"trustevidence-{i}")),
        "evidence_type": "access_attestation" if i % 3 else "integrity_anchor",
        "subject_ref_token": f"subj-{i % 100:04d}",
        "payload_hash": payload_hash,
        "policy_version": policy,
        "consent_state": "active" if i % 17 else "revoked",
        "actor_role": "clinician" if i % 2 else "service",
        "organisation_ref": f"org-{i % 5}",
        "backend_type": backend,
        "created_at": (
            datetime.datetime(2026, 7, 2, tzinfo=datetime.timezone.utc)
            + datetime.timedelta(seconds=i)
        ).isoformat(),
    }
    obj[CANONICAL_HASH_FIELD] = canonical_hash(obj)
    return obj


def validate_evidence_hash(obj: Dict[str, Any]) -> bool:
    return obj.get(CANONICAL_HASH_FIELD) == canonical_hash(obj)
