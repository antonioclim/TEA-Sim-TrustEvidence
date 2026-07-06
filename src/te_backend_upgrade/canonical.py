
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

CANONICAL_HASH_FIELD = "canonical_hash"

def canonical_bytes(obj: Dict[str, Any], *, exclude_hash_field: bool = True) -> bytes:
    material = dict(obj)
    if exclude_hash_field:
        material.pop(CANONICAL_HASH_FIELD, None)
    return json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_hash(obj: Dict[str, Any]) -> str:
    return sha256_hex(canonical_bytes(obj, exclude_hash_field=True))

def validate_evidence_hash(obj: Dict[str, Any]) -> bool:
    return obj.get(CANONICAL_HASH_FIELD) == canonical_hash(obj)

def make_evidence(i: int, *, policy_version: str = "policy-v1") -> Dict[str, Any]:
    obj: Dict[str, Any] = {
        "evidence_id": f"te-{i:08d}",
        "subject_ref_token": f"subject-{i % 17:02d}",
        "actor_role": ["clinician", "researcher", "patient", "auditor"][i % 4],
        "consent_state": ["grant", "revoke", "emergency", "unknown"][i % 4],
        "policy_version": policy_version,
        "payload_hash": sha256_hex(f"payload-{i}".encode("utf-8")),
        "event_time": f"2026-07-{(i % 28) + 1:02d}T12:{i % 60:02d}:00Z",
        "backend_type": "A2_MERKLE",
    }
    obj[CANONICAL_HASH_FIELD] = canonical_hash(obj)
    return obj
