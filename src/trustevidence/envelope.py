"""Construction of TE-JCS-1 signed evidence envelopes."""

from __future__ import annotations

import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .canonical import normalise_timestamp_ms
from .crypto import sign_evidence_core
from .profiles import ENVELOPE_PROFILE, ENVELOPE_VERSION
from .testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

_EVIDENCE_NAMESPACE = uuid.UUID("2b5ac94d-6b44-5a48-a8a7-7d07db5c412d")


def _normalise_facts(value: dict[str, Any]) -> dict[str, Any]:
    facts = deepcopy(value)
    for key in ("effective_at", "activity_started_at", "activity_ended_at", "window_start", "window_end"):
        if key in facts:
            facts[key] = normalise_timestamp_ms(facts[key])
    for period_name in ("capture_period", "summary_period"):
        if period_name in facts:
            facts[period_name] = {
                "start": normalise_timestamp_ms(facts[period_name]["start"]),
                "end": normalise_timestamp_ms(facts[period_name]["end"]),
            }
    return facts


def build_signed_envelope(
    event: dict[str, Any],
    *,
    emitted_at: str,
    private_key: Ed25519PrivateKey,
) -> tuple[dict[str, Any], str]:
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
            "key_id": source["key_id"],
        },
        "subject_context": deepcopy(event["subject_context"]),
        "objects": deepcopy(event["object_contexts"]),
        "purpose_code": event["purpose_code"],
        "outcome": deepcopy(event["outcome"]),
        "privacy_profile": deepcopy(event["privacy_profile"]),
        "event_facts": _normalise_facts(event["event_facts"]),
    }
    if source.get("organisation_ref_token"):
        core["emitter"]["organisation_ref_token"] = source["organisation_ref_token"]
    if event.get("actor_context"):
        core["actor"] = deepcopy(event["actor_context"])
    if event.get("policy_context"):
        policy = event["policy_context"]
        if policy.get("policy_binding"):
            core["policy_binding"] = deepcopy(policy["policy_binding"])
        if policy.get("consent_binding"):
            core["consent_binding"] = deepcopy(policy["consent_binding"])

    signature, digest = sign_evidence_core(core, private_key=private_key, key_id=source["key_id"])
    core["emitter_signature"] = signature
    return {
        "envelope_version": ENVELOPE_VERSION,
        "profile": ENVELOPE_PROFILE,
        "evidence_core": core,
    }, digest


def build_fixture_envelope(event: dict[str, Any], *, emitted_at: str) -> dict[str, Any]:
    envelope, _ = build_signed_envelope(
        event,
        emitted_at=emitted_at,
        private_key=fixture_emitter_private_key(),
    )
    return envelope


def attach_structural_receipt(envelope: dict[str, Any]) -> dict[str, Any]:
    """Compatibility name for a complete one-leaf deterministic test receipt."""

    from .backends.a2_merkle import LocalA2MerkleLog, attach_receipt
    from .hashing import core_digest_hex

    digest = core_digest_hex(envelope["evidence_core"], envelope_profile=ENVELOPE_PROFILE)
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    index = log.append_core_digest(digest)
    emitted = datetime.fromisoformat(envelope["evidence_core"]["emitted_at"].replace("Z", "+00:00"))
    issued_at = (emitted + timedelta(seconds=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    receipt = log.issue_receipt(
        index,
        issued_at=issued_at,
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    return attach_receipt(envelope, receipt)
