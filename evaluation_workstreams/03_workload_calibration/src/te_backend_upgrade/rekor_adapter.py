from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .canonical import canonical_hash, validate_evidence_hash


def export_rekor_artifact(obj: Dict[str, Any], out_dir: Path) -> Path:
    """Export a synthetic hash-commitment envelope suitable for a local Rekor attempt.

    This does not submit to Rekor and must not be interpreted as A3 execution.
    """
    if not validate_evidence_hash(obj):
        raise ValueError("canonical_hash does not bind evidence object")
    out_dir.mkdir(parents=True, exist_ok=True)
    commitment = {
        "evidence_id": obj["evidence_id"],
        "canonical_hash": canonical_hash(obj),
        "payload_hash": obj["payload_hash"],
        "policy_version": obj["policy_version"],
        "backend_type": "A3_REKOR_LOCAL_CANDIDATE",
        "submission_status": "not_submitted_adapter_only",
    }
    path = out_dir / f"{obj['evidence_id']}.json"
    path.write_text(json.dumps(commitment, sort_keys=True, indent=2), encoding="utf-8")
    return path
