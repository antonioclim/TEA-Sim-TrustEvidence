from __future__ import annotations

import datetime as _dt
import hashlib
import json
import uuid
from typing import Any, Mapping


def canonical_bytes(obj: Mapping[str, Any]) -> bytes:
    """Return deterministic UTF-8 canonical JSON bytes for the reference implementation.

    This is a stable experimental canonicalisation routine for synthetic evidence
    objects. It is not presented as an RFC 8785 implementation.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(obj: Mapping[str, Any]) -> str:
    return sha256_hex(canonical_bytes(obj))


def evidence_without_self_hash(i: int, policy: str = "policy-v1", backend: str = "A2_MERKLE") -> dict[str, Any]:
    payload_hash = sha256_hex(f"synthetic-payload-{i}".encode("utf-8"))
    created = _dt.datetime(2026, 7, 2, tzinfo=_dt.timezone.utc) + _dt.timedelta(seconds=i)
    return {
        "evidence_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"trustevidence-backend-evaluation workstream-{backend}-{i}")),
        "evidence_type": "integrity_anchor" if i % 3 == 0 else "access_attestation",
        "subject_ref_token": f"subj-{i % 1000:04d}",
        "payload_hash": payload_hash,
        "policy_version": policy,
        "consent_state": "revoked" if i % 17 == 0 else "active",
        "actor_role": "service" if i % 2 == 0 else "clinician",
        "organisation_ref": f"org-{i % 7}",
        "backend_type": backend,
        "created_at": created.isoformat(),
    }


def make_evidence(i: int, policy: str = "policy-v1", backend: str = "A2_MERKLE") -> dict[str, Any]:
    obj = evidence_without_self_hash(i=i, policy=policy, backend=backend)
    obj["canonical_hash"] = canonical_hash(obj)
    return obj
