from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, Dict, List, Tuple

from .canonical import canonical_bytes, sha256_hex, validate_evidence_hash

ProofStep = Tuple[str, str]  # (side, sibling_hash_hex), ordered from leaf to root


def _leaf_hash(obj: Dict[str, Any]) -> str:
    if not validate_evidence_hash(obj):
        raise ValueError(f"canonical_hash does not bind evidence object {obj.get('evidence_id')}")
    return sha256_hex(b"\x00" + canonical_bytes(obj, exclude_hash_field=True))


def _node_hash(left_hex: str, right_hex: str) -> str:
    return sha256_hex(b"\x01" + bytes.fromhex(left_hex) + bytes.fromhex(right_hex))


def _largest_power_of_two_less_than(n: int) -> int:
    if n <= 1:
        raise ValueError("n must be > 1")
    return 1 << ((n - 1).bit_length() - 1)


def merkle_root_from_leaves(leaves: List[str]) -> str:
    """Certificate-Transparency-style Merkle tree hash."""
    if not leaves:
        return sha256_hex(b"empty")
    if len(leaves) == 1:
        return leaves[0]
    k = _largest_power_of_two_less_than(len(leaves))
    return _node_hash(merkle_root_from_leaves(leaves[:k]), merkle_root_from_leaves(leaves[k:]))


@dataclass(frozen=True)
class Receipt:
    backend: str
    evidence_id: str
    leaf_hash: str
    tree_size: int
    root_hash: str
    hash_alg: str = "SHA-256"
    tree_alg: str = "CT_STYLE_SHA256_V1"

    def to_json_bytes(self) -> bytes:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")


class MerkleLog:
    def __init__(self) -> None:
        self.objects: List[Dict[str, Any]] = []
        self.leaves: List[str] = []
        self.roots_by_size: Dict[int, str] = {0: merkle_root_from_leaves([])}
        self._frontier: List[str | None] = []
        self._range_root_cache: Dict[Tuple[int, int], str] = {}

    def append(self, obj: Dict[str, Any]) -> Receipt:
        leaf = _leaf_hash(obj)
        self.objects.append(dict(obj))
        self.leaves.append(leaf)
        self._range_root_cache.clear()
        self._append_frontier(leaf, len(self.leaves) - 1)
        root = self.root_hash()
        size = len(self.leaves)
        self.roots_by_size[size] = root
        return Receipt("A2_MERKLE", obj["evidence_id"], leaf, size, root)

    def _append_frontier(self, leaf: str, zero_based_index: int) -> None:
        h = leaf
        level = 0
        index = zero_based_index
        while index & 1:
            left = self._frontier[level]
            if left is None:
                raise RuntimeError("frontier invariant violated")
            h = _node_hash(left, h)
            self._frontier[level] = None
            index >>= 1
            level += 1
        while len(self._frontier) <= level:
            self._frontier.append(None)
        self._frontier[level] = h

    def root_hash(self) -> str:
        if not self.leaves:
            return merkle_root_from_leaves([])
        root: str | None = None
        # For CT-style roots, binary-decomposition peaks must be combined from
        # the smallest rightmost subtree upwards so that size 7 becomes
        # node(root[0:4], node(root[4:6], leaf[6])).
        for level in range(0, len(self._frontier)):
            node = self._frontier[level]
            if node is None:
                continue
            root = node if root is None else _node_hash(node, root)
        if root is None:
            raise RuntimeError("frontier has no nodes for non-empty tree")
        return root

    def _root_range(self, start: int, end: int) -> str:
        key = (start, end)
        cached = self._range_root_cache.get(key)
        if cached is not None:
            return cached
        span = end - start
        if span <= 0:
            raise ValueError("empty range is not a valid non-empty subtree")
        if span == 1:
            val = self.leaves[start]
        else:
            k = _largest_power_of_two_less_than(span)
            val = _node_hash(self._root_range(start, start + k), self._root_range(start + k, end))
        self._range_root_cache[key] = val
        return val

    def inclusion_proof(self, index: int) -> List[ProofStep]:
        if index < 0 or index >= len(self.leaves):
            raise IndexError(index)

        def proof(start: int, end: int, idx: int) -> List[ProofStep]:
            span = end - start
            if span == 1:
                return []
            k = _largest_power_of_two_less_than(span)
            split = start + k
            if idx < split:
                return proof(start, split, idx) + [("right", self._root_range(split, end))]
            return proof(split, end, idx) + [("left", self._root_range(start, split))]

        return proof(0, len(self.leaves), index)

    @staticmethod
    def verify_inclusion(obj: Dict[str, Any], proof: List[ProofStep], root_hash: str) -> bool:
        try:
            cur = _leaf_hash(obj)
        except ValueError:
            return False
        for side, sibling in proof:
            if side == "left":
                cur = _node_hash(sibling, cur)
            elif side == "right":
                cur = _node_hash(cur, sibling)
            else:
                return False
        return cur == root_hash

    def verify_consistency_by_prefix(self, old_size: int, old_root: str) -> bool:
        # Reference-implementation check, not a compact RFC-style consistency proof.
        if old_size < 0 or old_size > len(self.leaves):
            return False
        return merkle_root_from_leaves(self.leaves[:old_size]) == old_root

    def receipt_size_bytes(self, receipt: Receipt) -> int:
        return len(receipt.to_json_bytes())

    def proof_size_bytes(self, proof: List[ProofStep]) -> int:
        return len(json.dumps(proof, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    def approximate_storage_bytes(self) -> int:
        object_bytes = sum(len(canonical_bytes(o, exclude_hash_field=False)) for o in self.objects)
        leaf_bytes = len(self.leaves) * 32
        root_checkpoint_bytes = len(self.roots_by_size) * 32
        return object_bytes + leaf_bytes + root_checkpoint_bytes
