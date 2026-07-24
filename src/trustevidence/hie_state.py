"""Stateful retained-checkpoint handling for the bounded Route C HIE verifier.

The underlying receipt verifier is deliberately pure.  This wrapper advances a
local retained checkpoint only after a complete verification succeeds.  It does
not provide persistence, gossip, external witnessing, replay prevention or
global non-equivocation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .backends.a2_merkle import RetainedCheckpoint, VerificationResult
from .hie import verify_hie_envelope_receipt


@dataclass(slots=True)
class RetainedHIEVerifier:
    """Hold one local checkpoint and advance it only on accepted evidence."""

    expected_backend_id: str
    expected_log_id: str
    checkpoint: RetainedCheckpoint | None = None

    def snapshot(self) -> tuple[str, str, int, str] | None:
        value = self.checkpoint
        if value is None:
            return None
        return (value.backend_id, value.log_id, value.tree_size, value.root_digest)

    def verify_and_update(
        self,
        envelope: dict[str, Any],
        *,
        emitter_keys: Mapping[str, Ed25519PublicKey],
        receipt_keys: Mapping[str, Ed25519PublicKey],
        consistency_proof: Mapping[str, Any] | None = None,
    ) -> VerificationResult:
        """Verify and conditionally retain the receipt checkpoint.

        Rejected evidence never changes ``checkpoint``.  An accepted receipt
        establishes the initial checkpoint, confirms the same checkpoint, or
        advances it after the underlying verifier has accepted the supplied
        consistency proof.
        """

        result = verify_hie_envelope_receipt(
            envelope,
            emitter_keys=emitter_keys,
            receipt_keys=receipt_keys,
            expected_backend_id=self.expected_backend_id,
            expected_log_id=self.expected_log_id,
            retained_checkpoint=self.checkpoint,
            consistency_proof=consistency_proof,
        )
        if not result.accepted:
            return result

        receipt = envelope["backend_receipt"]
        self.checkpoint = RetainedCheckpoint(
            backend_id=str(receipt["backend_id"]),
            log_id=str(receipt["log_id"]),
            tree_size=int(receipt["tree_size"]),
            root_digest=str(receipt["root_digest"]),
        )
        return result
