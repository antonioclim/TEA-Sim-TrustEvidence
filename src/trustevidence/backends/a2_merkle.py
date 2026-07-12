"""Local TE-A2 receipt and Merkle verification model.

The binary tree, inclusion path, and consistency path are shaped by the
algorithms in RFC 9162.  TE leaf inputs, receipt fields, signatures, and
application semantics are project-specific; this module is not a Certificate
Transparency protocol implementation.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from ..crypto import sign_receipt, verify_evidence_core_signature, verify_receipt_signature
from ..hashing import core_digest_hex, leaf_input_bytes, proof_digest_hex, receipt_digest_hex
from ..profiles import ENVELOPE_PROFILE, HASH_PROFILE, RECEIPT_PROFILE
from ..validators import validate_envelope

TREE_PROFILE = "TE-A2-Binary-Merkle-1"
PROOF_PROFILE = "TE-A2-Inclusion-1"
CONSISTENCY_PROFILE = "TE-A2-Consistency-1"
BACKEND_TYPE = "local-a2-merkle"


def leaf_hash(leaf_input: bytes) -> bytes:
    """Return the RFC-9162-shaped leaf hash for project-specific leaf input."""

    return hashlib.sha256(b"\x00" + leaf_input).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    """Return the RFC-9162-shaped internal-node hash."""

    return hashlib.sha256(b"\x01" + left + right).digest()


def _largest_power_of_two_less_than(value: int) -> int:
    if value <= 1:
        raise ValueError("value must exceed one")
    return 1 << ((value - 1).bit_length() - 1)


def merkle_tree_hash(entries: Sequence[bytes]) -> bytes:
    """Compute the recursive Merkle Tree Hash over ordered leaf inputs."""

    if not entries:
        return hashlib.sha256(b"").digest()
    if len(entries) == 1:
        return leaf_hash(entries[0])
    split = _largest_power_of_two_less_than(len(entries))
    return node_hash(merkle_tree_hash(entries[:split]), merkle_tree_hash(entries[split:]))


def inclusion_path(entries: Sequence[bytes], leaf_index: int) -> list[bytes]:
    """Generate the shortest inclusion path for ``leaf_index``."""

    size = len(entries)
    if size <= 0 or not 0 <= leaf_index < size:
        raise ValueError("leaf_index must be within a non-empty tree")
    if size == 1:
        return []
    split = _largest_power_of_two_less_than(size)
    if leaf_index < split:
        return inclusion_path(entries[:split], leaf_index) + [merkle_tree_hash(entries[split:])]
    return inclusion_path(entries[split:], leaf_index - split) + [merkle_tree_hash(entries[:split])]


def verify_inclusion(
    leaf_hash_value: bytes,
    *,
    leaf_index: int,
    tree_size: int,
    siblings: Sequence[bytes],
    root_hash: bytes,
) -> bool:
    """Verify an index- and tree-size-bound inclusion path."""

    if len(leaf_hash_value) != 32 or len(root_hash) != 32:
        return False
    if tree_size <= 0 or leaf_index < 0 or leaf_index >= tree_size:
        return False
    fn = leaf_index
    sn = tree_size - 1
    running = leaf_hash_value
    for sibling in siblings:
        if len(sibling) != 32 or sn == 0:
            return False
        if (fn & 1) == 1 or fn == sn:
            running = node_hash(sibling, running)
            if (fn & 1) == 0:
                while fn != 0 and (fn & 1) == 0:
                    fn >>= 1
                    sn >>= 1
        else:
            running = node_hash(running, sibling)
        fn >>= 1
        sn >>= 1
    return sn == 0 and running == root_hash


def _consistency_subproof(entries: Sequence[bytes], first_size: int, complete: bool) -> list[bytes]:
    """Recursive RFC-9162-shaped SUBPROOF helper."""

    second_size = len(entries)
    if first_size <= 0 or first_size > second_size:
        raise ValueError("first_size must be within the non-empty second tree")
    if first_size == second_size:
        return [] if complete else [merkle_tree_hash(entries)]
    split = _largest_power_of_two_less_than(second_size)
    if first_size <= split:
        return _consistency_subproof(entries[:split], first_size, complete) + [
            merkle_tree_hash(entries[split:])
        ]
    return _consistency_subproof(entries[split:], first_size - split, False) + [
        merkle_tree_hash(entries[:split])
    ]


def consistency_path(
    entries: Sequence[bytes], first_size: int, second_size: int | None = None
) -> list[bytes]:
    """Generate a minimal consistency path for ``0 < first_size <= second_size``.

    Equal-size trees have an empty path.  Empty-tree consistency is intentionally
    not represented by this profile because retained operational checkpoints are
    required to describe a non-empty tree.
    """

    second = len(entries) if second_size is None else second_size
    if second <= 0 or second > len(entries):
        raise ValueError("second_size must identify a non-empty available prefix")
    if first_size <= 0 or first_size > second:
        raise ValueError("first_size must satisfy 0 < first_size <= second_size")
    if first_size == second:
        return []
    return _consistency_subproof(entries[:second], first_size, True)


def verify_consistency(
    *,
    first_size: int,
    second_size: int,
    first_root: bytes,
    second_root: bytes,
    hashes: Sequence[bytes],
) -> bool:
    """Verify that the second tree extends the first tree.

    This implements the RFC-9162-shaped consistency algorithm over this
    project's leaf and node hash definitions.  It does not establish that two
    isolated verifiers were shown the same signed checkpoint.
    """

    if len(first_root) != 32 or len(second_root) != 32:
        return False
    if first_size <= 0 or second_size <= 0 or first_size > second_size:
        return False
    if any(len(item) != 32 for item in hashes):
        return False
    if first_size == second_size:
        return not hashes and first_root == second_root
    if not hashes:
        return False

    work = list(hashes)
    if first_size & (first_size - 1) == 0:
        work.insert(0, first_root)

    fn = first_size - 1
    sn = second_size - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1

    first_running = work[0]
    second_running = work[0]
    for component in work[1:]:
        if sn == 0:
            return False
        if (fn & 1) == 1 or fn == sn:
            first_running = node_hash(component, first_running)
            second_running = node_hash(component, second_running)
            if (fn & 1) == 0:
                while fn != 0 and (fn & 1) == 0:
                    fn >>= 1
                    sn >>= 1
        else:
            second_running = node_hash(second_running, component)
        fn >>= 1
        sn >>= 1

    return sn == 0 and first_running == first_root and second_running == second_root


@dataclass(frozen=True, slots=True)
class RetainedCheckpoint:
    backend_id: str
    log_id: str
    tree_size: int
    root_digest: str


@dataclass(frozen=True, slots=True)
class VerificationIssue:
    code: str
    detail: str


@dataclass(frozen=True, slots=True)
class VerificationResult:
    accepted: bool
    issues: tuple[VerificationIssue, ...]

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)

    @property
    def primary_code(self) -> str:
        return "PASS" if self.accepted else self.issues[0].code


class LocalA2MerkleLog:
    """In-memory deterministic reference log for synthetic experiments."""

    def __init__(self, *, backend_id: str, log_id: str) -> None:
        self.backend_id = backend_id
        self.log_id = log_id
        self._core_digests: list[str] = []
        self._leaf_inputs: list[bytes] = []
        # Range hashes are immutable once their leaf interval exists.  Retaining
        # them avoids recursively re-hashing the same completed subtrees for
        # every sampled receipt in a workload run, without changing tree bytes.
        self._subtree_hash_cache: dict[tuple[int, int], bytes] = {}

    @property
    def tree_size(self) -> int:
        return len(self._leaf_inputs)

    def _range_hash(self, start: int, end: int) -> bytes:
        """Return the Merkle hash for ``[start, end)`` with immutable caching."""

        if start < 0 or end < start or end > self.tree_size:
            raise ValueError("hash range is outside the available log")
        key = (start, end)
        cached = self._subtree_hash_cache.get(key)
        if cached is not None:
            return cached
        size = end - start
        if size == 0:
            value = hashlib.sha256(b"").digest()
        elif size == 1:
            value = leaf_hash(self._leaf_inputs[start])
        else:
            split = _largest_power_of_two_less_than(size)
            value = node_hash(
                self._range_hash(start, start + split),
                self._range_hash(start + split, end),
            )
        self._subtree_hash_cache[key] = value
        return value

    def _cached_inclusion_path(self, start: int, end: int, leaf_index: int) -> list[bytes]:
        """Generate the shortest path using the same RFC-9162-shaped recursion."""

        size = end - start
        if size <= 0 or not start <= leaf_index < end:
            raise ValueError("leaf_index must be within a non-empty range")
        if size == 1:
            return []
        split = _largest_power_of_two_less_than(size)
        boundary = start + split
        if leaf_index < boundary:
            return self._cached_inclusion_path(start, boundary, leaf_index) + [
                self._range_hash(boundary, end)
            ]
        return self._cached_inclusion_path(boundary, end, leaf_index) + [
            self._range_hash(start, boundary)
        ]

    @property
    def root_digest(self) -> str:
        return self._range_hash(0, self.tree_size).hex()

    def root_digest_at(self, tree_size: int) -> str:
        if tree_size < 0 or tree_size > self.tree_size:
            raise ValueError("tree_size is outside the available log prefix")
        return self._range_hash(0, tree_size).hex()

    def core_digests_at(self, tree_size: int | None = None) -> tuple[str, ...]:
        """Return an immutable copy of the available core-digest prefix."""

        size = self.tree_size if tree_size is None else tree_size
        if size < 0 or size > self.tree_size:
            raise ValueError("tree_size is outside the available log prefix")
        return tuple(self._core_digests[:size])

    def append_core_digest(self, digest_hex: str) -> int:
        if len(digest_hex) != 64 or digest_hex.lower() != digest_hex:
            raise ValueError("core digest must be a 32-byte lower-case hexadecimal value")
        int(digest_hex, 16)
        index = len(self._leaf_inputs)
        self._core_digests.append(digest_hex)
        self._leaf_inputs.append(
            leaf_input_bytes(backend_id=self.backend_id, log_id=self.log_id, core_digest_hex_value=digest_hex)
        )
        return index

    def issue_receipt(
        self,
        leaf_index: int,
        *,
        issued_at: str,
        private_key: Ed25519PrivateKey,
        signer_key_id: str,
    ) -> dict[str, Any]:
        if not 0 <= leaf_index < self.tree_size:
            raise ValueError("leaf index is outside the current tree")
        proof = {
            "profile": PROOF_PROFILE,
            "leaf_index": leaf_index,
            "tree_size": self.tree_size,
            "siblings": [
                value.hex()
                for value in self._cached_inclusion_path(0, self.tree_size, leaf_index)
            ],
        }
        leaf = leaf_hash(self._leaf_inputs[leaf_index]).hex()
        receipt: dict[str, Any] = {
            "profile": RECEIPT_PROFILE,
            "backend_type": BACKEND_TYPE,
            "backend_id": self.backend_id,
            "log_id": self.log_id,
            "hash_profile": HASH_PROFILE,
            "tree_profile": TREE_PROFILE,
            "core_digest": self._core_digests[leaf_index],
            "leaf_hash": leaf,
            "leaf_index": leaf_index,
            "tree_size": self.tree_size,
            "root_digest": self.root_digest,
            "inclusion_proof": proof,
            "inclusion_proof_digest": proof_digest_hex(proof),
            "issued_at": issued_at,
            "signer_key_id": signer_key_id,
        }
        signature, _ = sign_receipt(receipt, private_key=private_key, key_id=signer_key_id)
        receipt["receipt_signature"] = signature
        return receipt

    def issue_consistency_proof(
        self, first_size: int, second_size: int | None = None
    ) -> dict[str, Any]:
        second = self.tree_size if second_size is None else second_size
        hashes = consistency_path(self._leaf_inputs, first_size, second)
        return {
            "profile": CONSISTENCY_PROFILE,
            "backend_id": self.backend_id,
            "log_id": self.log_id,
            "first_size": first_size,
            "second_size": second,
            "first_root": self.root_digest_at(first_size),
            "second_root": self.root_digest_at(second),
            "hashes": [item.hex() for item in hashes],
        }


def attach_receipt(envelope: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(envelope)
    result["backend_receipt"] = deepcopy(receipt)
    return result


def receipt_fingerprint(receipt: dict[str, Any]) -> str:
    return receipt_digest_hex(receipt)


def _add(issues: list[VerificationIssue], code: str, detail: str) -> None:
    if code not in {issue.code for issue in issues}:
        issues.append(VerificationIssue(code, detail))


def _verify_consistency_object(
    proof: Mapping[str, Any],
    *,
    retained_checkpoint: RetainedCheckpoint,
    current_backend_id: str,
    current_log_id: str,
    current_size: int,
    current_root: str,
) -> tuple[VerificationIssue, ...]:
    issues: list[VerificationIssue] = []
    if proof.get("profile") != CONSISTENCY_PROFILE:
        _add(issues, "TE-E-CONSISTENCY-STRUCTURE", "Unsupported consistency-proof profile")
    if proof.get("backend_id") != current_backend_id or proof.get("log_id") != current_log_id:
        _add(issues, "TE-E-CONSISTENCY-IDENTITY", "Consistency proof belongs to another backend/log")
    if proof.get("first_size") != retained_checkpoint.tree_size or proof.get("second_size") != current_size:
        _add(issues, "TE-E-CONSISTENCY-SIZE", "Consistency-proof sizes do not match retained and current checkpoints")
    if proof.get("first_root") != retained_checkpoint.root_digest or proof.get("second_root") != current_root:
        _add(issues, "TE-E-CONSISTENCY-ROOT", "Consistency-proof roots do not match retained and current checkpoints")

    hashes_value = proof.get("hashes")
    parsed: list[bytes] = []
    if not isinstance(hashes_value, list):
        _add(issues, "TE-E-CONSISTENCY-STRUCTURE", "Consistency proof hashes must be an array")
    else:
        try:
            parsed = [bytes.fromhex(str(item)) for item in hashes_value]
        except (TypeError, ValueError):
            _add(issues, "TE-E-CONSISTENCY-STRUCTURE", "Consistency proof contains a non-hexadecimal hash")

    if not issues:
        try:
            accepted = verify_consistency(
                first_size=retained_checkpoint.tree_size,
                second_size=current_size,
                first_root=bytes.fromhex(retained_checkpoint.root_digest),
                second_root=bytes.fromhex(current_root),
                hashes=parsed,
            )
        except (TypeError, ValueError):
            accepted = False
        if not accepted:
            _add(issues, "TE-E-CONSISTENCY-PATH", "Consistency path does not prove append-only extension")
    return tuple(issues)


def verify_envelope_receipt(
    envelope: dict[str, Any],
    *,
    emitter_keys: Mapping[str, Ed25519PublicKey],
    receipt_keys: Mapping[str, Ed25519PublicKey],
    expected_backend_id: str | None = None,
    expected_log_id: str | None = None,
    retained_checkpoint: RetainedCheckpoint | None = None,
    consistency_proof: Mapping[str, Any] | None = None,
) -> VerificationResult:
    """Verify schema, signatures, receipt bindings, and optional retained state.

    When a supplied receipt advances beyond a retained non-empty checkpoint, a
    valid consistency proof is required.  This closes local prefix-extension
    verification but does not provide gossip, witnessing, or global
    non-equivocation between isolated verifiers.
    """

    issues: list[VerificationIssue] = []
    structural = validate_envelope(envelope)
    if not structural.accepted:
        for item in structural.issues:
            _add(issues, item.code, item.message)
        return VerificationResult(False, tuple(issues))

    core = envelope["evidence_core"]
    receipt = envelope.get("backend_receipt")
    if not isinstance(receipt, dict):
        return VerificationResult(False, (VerificationIssue("TE-E-RECEIPT-MISSING", "Envelope has no backend receipt"),))

    core_check = verify_evidence_core_signature(core, emitter_keys)
    if not core_check.accepted:
        _add(issues, core_check.code, core_check.detail)

    receipt_check = verify_receipt_signature(receipt, receipt_keys)
    if not receipt_check.accepted:
        _add(issues, receipt_check.code, receipt_check.detail)

    if expected_backend_id is not None and receipt.get("backend_id") != expected_backend_id:
        _add(issues, "TE-E-BACKEND-IDENTITY", "Receipt backend identifier differs from expected")
    if expected_log_id is not None and receipt.get("log_id") != expected_log_id:
        _add(issues, "TE-E-LOG-IDENTITY", "Receipt log identifier differs from expected")

    computed_core = core_digest_hex(core, envelope_profile=ENVELOPE_PROFILE)
    if receipt.get("core_digest") != computed_core:
        _add(issues, "TE-E-RECEIPT-BINDING", "Receipt core digest does not match the signed core")

    try:
        expected_leaf_input = leaf_input_bytes(
            backend_id=str(receipt.get("backend_id")),
            log_id=str(receipt.get("log_id")),
            core_digest_hex_value=str(receipt.get("core_digest")),
        )
        expected_leaf = leaf_hash(expected_leaf_input).hex()
    except (ValueError, TypeError):
        expected_leaf = ""
    if receipt.get("leaf_hash") != expected_leaf:
        _add(issues, "TE-E-LEAF-BINDING", "Leaf hash does not bind backend, log and core digest")

    proof = receipt.get("inclusion_proof")
    if not isinstance(proof, dict):
        _add(issues, "TE-E-PROOF-STRUCTURE", "Inclusion proof is absent")
    else:
        if receipt.get("leaf_index") != proof.get("leaf_index"):
            _add(issues, "TE-E-PROOF-INDEX", "Receipt and proof leaf indices differ")
        if receipt.get("tree_size") != proof.get("tree_size"):
            _add(issues, "TE-E-PROOF-SIZE", "Receipt and proof tree sizes differ")
        try:
            observed_proof_digest = proof_digest_hex(proof)
        except Exception:
            observed_proof_digest = ""
        if receipt.get("inclusion_proof_digest") != observed_proof_digest:
            _add(issues, "TE-E-PROOF-DIGEST", "Proof digest does not match proof material")
        try:
            siblings = [bytes.fromhex(item) for item in proof.get("siblings", [])]
            inclusion_ok = verify_inclusion(
                bytes.fromhex(str(receipt.get("leaf_hash"))),
                leaf_index=int(receipt.get("leaf_index")),
                tree_size=int(receipt.get("tree_size")),
                siblings=siblings,
                root_hash=bytes.fromhex(str(receipt.get("root_digest"))),
            )
        except (ValueError, TypeError):
            inclusion_ok = False
        if not inclusion_ok:
            _add(issues, "TE-E-PROOF-PATH", "Inclusion path does not reconstruct the signed root")

    if retained_checkpoint is not None:
        if receipt.get("backend_id") != retained_checkpoint.backend_id or receipt.get("log_id") != retained_checkpoint.log_id:
            _add(issues, "TE-E-CHECKPOINT-IDENTITY", "Retained checkpoint belongs to another backend/log")
        else:
            new_size = int(receipt.get("tree_size"))
            current_root = str(receipt.get("root_digest"))
            if new_size < retained_checkpoint.tree_size:
                _add(issues, "TE-E-CHECKPOINT-ROLLBACK", "Receipt tree size is smaller than retained state")
            elif new_size == retained_checkpoint.tree_size:
                if current_root != retained_checkpoint.root_digest:
                    _add(issues, "TE-E-CHECKPOINT-FORK", "Same-size root differs from retained state")
            else:
                if consistency_proof is None:
                    _add(issues, "TE-E-CONSISTENCY-MISSING", "Larger-tree receipt requires a consistency proof")
                else:
                    for issue in _verify_consistency_object(
                        consistency_proof,
                        retained_checkpoint=retained_checkpoint,
                        current_backend_id=str(receipt.get("backend_id")),
                        current_log_id=str(receipt.get("log_id")),
                        current_size=new_size,
                        current_root=current_root,
                    ):
                        _add(issues, issue.code, issue.detail)

    return VerificationResult(not issues, tuple(issues))
