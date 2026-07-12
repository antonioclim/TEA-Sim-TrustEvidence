"""Hypothesis checks for canonicalisation and evidence-only verification."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from hypothesis import HealthCheck, given, settings, strategies as st

from trustevidence.backends.a2_merkle import LocalA2MerkleLog, attach_receipt, verify_envelope_receipt
from trustevidence.canonical import canonicalise_te
from trustevidence.crypto import commit_payload, verify_payload_commitment
from trustevidence.envelope import build_signed_envelope
from trustevidence.testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data_examples" / "personal_monitoring"

PROP = settings(
    max_examples=100,
    deadline=None,
    database=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)

_ascii = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_:/.",
    min_size=0,
    max_size=16,
)
_key = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
    min_size=1,
    max_size=10,
).filter(lambda value: value != "__property_mutation__")
_scalar = st.one_of(st.none(), st.booleans(), st.integers(min_value=-(10**9), max_value=10**9), _ascii)
_json_value = st.recursive(
    _scalar,
    lambda child: st.lists(child, min_size=0, max_size=4)
    | st.dictionaries(_key, child, min_size=0, max_size=4),
    max_leaves=14,
)
_json_object = st.dictionaries(_key, _json_value, min_size=0, max_size=6)


def _reverse_mappings(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _reverse_mappings(item) for key, item in reversed(list(value.items()))}
    if isinstance(value, list):
        return [_reverse_mappings(item) for item in value]
    return value


def _contains_key(value: Any, prohibited: set[str]) -> bool:
    if isinstance(value, dict):
        return bool(prohibited & set(value)) or any(_contains_key(item, prohibited) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, prohibited) for item in value)
    return False


@PROP
@given(value=_json_object)
def test_canonicalisation_is_deterministic_under_recursive_key_reordering(value: dict[str, Any]) -> None:
    reordered = _reverse_mappings(deepcopy(value))
    assert canonicalise_te(value) == canonicalise_te(reordered)
    mutated = deepcopy(value)
    mutated["__property_mutation__"] = "changed"
    assert canonicalise_te(value) != canonicalise_te(mutated)


@PROP
@given(
    payload=st.binary(min_size=0, max_size=128),
    nonce=st.binary(min_size=16, max_size=32),
)
def test_payload_commitment_binds_withheld_material_but_evidence_verification_needs_neither(
    payload: bytes, nonce: bytes
) -> None:
    representation = "application/fhir+json-rfc8785-v1"
    context = "cgm-day-object"
    commitment = commit_payload(
        payload,
        nonce=nonce,
        representation_profile=representation,
        commitment_context=context,
    )
    assert verify_payload_commitment(
        commitment,
        payload,
        nonce=nonce,
        representation_profile=representation,
        commitment_context=context,
    )
    assert not verify_payload_commitment(
        commitment,
        payload + b"x",
        nonce=nonce,
        representation_profile=representation,
        commitment_context=context,
    )

    event = json.loads((EXAMPLES / "cgm_monitoring_object_registration.json").read_text(encoding="utf-8"))
    event["object_contexts"][0]["payload_binding"]["commitment"] = commitment
    envelope, digest = build_signed_envelope(
        event,
        emitted_at="2026-07-01T06:00:00.500Z",
        private_key=fixture_emitter_private_key(),
    )
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    log.append_core_digest(digest)
    receipt = log.issue_receipt(
        0,
        issued_at="2026-07-03T03:00:00.000Z",
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    public_envelope = attach_receipt(envelope, receipt)

    # The evidence-only verifier receives no payload or nonce arguments.
    result = verify_envelope_receipt(
        public_envelope,
        emitter_keys={FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
        receipt_keys={FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
    )
    assert result.accepted, result.issues
    assert not _contains_key(
        public_envelope,
        {"nonce", "payload", "raw_payload", "samples", "glucose_value", "physiological_value"},
    )
