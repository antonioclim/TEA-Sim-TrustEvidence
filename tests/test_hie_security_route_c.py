"""Route C HIE security and retained-state regression tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from experiments.run_hie_security_mutations import build_results
from trustevidence.backends.a2_merkle import LocalA2MerkleLog, RetainedCheckpoint, attach_receipt
from trustevidence.hashing import core_digest_hex
from trustevidence.hie import HIE_ENVELOPE_PROFILE
from trustevidence.hie_state import RetainedHIEVerifier
from trustevidence.testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data_examples" / "hie_disclosure"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _keys():
    return (
        {FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
        {FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
    )


def _log(values: list[str]) -> LocalA2MerkleLog:
    log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    for value in values:
        log.append_core_digest(value)
    return log


def _envelope(log: LocalA2MerkleLog, signed: dict, issued_at: str) -> dict:
    receipt = log.issue_receipt(
        0,
        issued_at=issued_at,
        private_key=fixture_backend_private_key(),
        signer_key_id=FIXTURE_BACKEND_KEY_ID,
    )
    return attach_receipt(signed, receipt)


def test_c4_deterministic_result_contract_has_no_false_accepts() -> None:
    outputs = build_results()
    summary = json.loads(outputs["hie_security_mutation_run.json"])
    assert summary["case_count"] >= 60
    assert summary["failed_count"] == 0
    assert summary["false_accept_count"] == 0
    assert summary["false_reject_count"] == 0
    assert summary["state_nonadvancement_failure_count"] == 0
    assert summary["limitation_acceptance_count"] >= 6
    assert "LIM-BACKEND-002" in summary["limitation_acceptance_case_ids"]
    assert summary["portable_nonce_exposed"] is False
    assert summary["declared_clinical_source_marker_exposed"] is False


def test_c4_result_generation_is_byte_deterministic() -> None:
    first = build_results()
    second = build_results()
    assert first == second


def test_stateful_verifier_rejects_without_advancing_then_accepts_extension() -> None:
    signed = _json(CASE / "signed_envelope.json")
    core = core_digest_hex(signed["evidence_core"], envelope_profile=HIE_ENVELOPE_PROFILE)
    prefix_values = [core, hashlib.sha256(b"c4-prefix-1").hexdigest(), hashlib.sha256(b"c4-prefix-2").hexdigest()]
    prefix = _log(prefix_values)
    checkpoint = RetainedCheckpoint(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, prefix.tree_size, prefix.root_digest)
    state = RetainedHIEVerifier(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, checkpoint)
    before = state.snapshot()

    extension_values = prefix_values + [hashlib.sha256(b"c4-extension-3").hexdigest()]
    extension = _log(extension_values)
    candidate = _envelope(extension, signed, "2026-07-15T12:00:00.000Z")
    emitter_keys, receipt_keys = _keys()

    missing = state.verify_and_update(
        candidate,
        emitter_keys=emitter_keys,
        receipt_keys=receipt_keys,
    )
    assert not missing.accepted
    assert "TE-E-CONSISTENCY-MISSING" in missing.codes
    assert state.snapshot() == before

    proof = extension.issue_consistency_proof(prefix.tree_size)
    accepted = state.verify_and_update(
        candidate,
        emitter_keys=emitter_keys,
        receipt_keys=receipt_keys,
        consistency_proof=proof,
    )
    assert accepted.accepted
    assert state.checkpoint is not None
    assert state.checkpoint.tree_size == extension.tree_size
    assert state.checkpoint.root_digest == extension.root_digest


def test_stateful_verifier_does_not_implement_duplicate_replay_rejection() -> None:
    signed = _json(CASE / "signed_envelope.json")
    core = core_digest_hex(signed["evidence_core"], envelope_profile=HIE_ENVELOPE_PROFILE)
    log = _log([core, hashlib.sha256(b"c4-replay").hexdigest()])
    candidate = _envelope(log, signed, "2026-07-15T12:00:01.000Z")
    checkpoint = RetainedCheckpoint(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, log.tree_size, log.root_digest)
    state = RetainedHIEVerifier(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID, checkpoint)
    emitter_keys, receipt_keys = _keys()
    before = state.snapshot()
    result = state.verify_and_update(candidate, emitter_keys=emitter_keys, receipt_keys=receipt_keys)
    assert result.accepted
    assert state.snapshot() == before
