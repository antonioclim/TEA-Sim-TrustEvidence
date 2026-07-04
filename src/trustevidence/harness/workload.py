from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from trustevidence.crypto import sign_core
from trustevidence.envelope import minimal_core


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            row = json.loads(line)
            row.setdefault("line_no", line_no)
            rows.append(row)
    return rows


def audit_event_resource(row: dict[str, Any]) -> dict[str, Any]:
    """Return a minimal AuditEvent resource for stack smoke testing only.

    Exact BALP/IG conformance requires full SUSHI and IG Publisher validation.
    """
    return {
        "resourceType": "AuditEvent",
        "type": {"system": "http://terminology.hl7.org/CodeSystem/audit-event-type", "code": "rest"},
        "action": row.get("action", "R"),
        "recorded": row.get("occurred_at", "2026-07-03T12:00:00Z"),
        "agent": [{"type": {"text": row.get("actor_role", "clinician")}, "who": {"display": row.get("actor", "actor")}}],
        "source": {"observer": {"display": row.get("source", "External smoke harness")}},
        "entity": [{"what": {"display": row.get("subject_token", "subject")}}],
    }


def envelope_from_row(row: dict[str, Any], pair: Any) -> dict[str, Any]:
    core = minimal_core(row["event_id"], row["artefact_id"], key_id=pair.key_id)
    core["occurred_at"] = row.get("occurred_at", core["occurred_at"])
    core["emitted_at"] = row.get("emitted_at", core["emitted_at"])
    core["event_action"] = row.get("event_action", "read")
    core["subject_ref"]["token"] = row.get("subject_token", core["subject_ref"]["token"])
    core["emitter"]["organisation_ref"] = row.get("organisation_ref", core["emitter"]["organisation_ref"])
    core["semantic_binding"] = {
        "fhir_release_hint": "draft-r4",
        "resource_class": "AuditEvent",
        "resource_ref_token": row.get("resource_ref_token", "auditevent_tok"),
        "binding_purpose": "audit",
    }
    return {"envelope_version": "2.0.0-draft", "artefact_core": sign_core(core, pair)}


def summarise_receipt(envelope: dict[str, Any]) -> dict[str, Any]:
    receipt = envelope.get("backend_receipt", {})
    keys = [
        "backend_type", "backend_id", "log_id", "core_hash", "tree_size", "leaf_index",
        "inclusion_proof_ref", "consistency_proof_ref", "finality_ref", "witness_ref",
    ]
    return {k: receipt[k] for k in keys if k in receipt}
