
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from typing import Any, Dict, List, Tuple

from .canonical import canonical_bytes, sha256_hex, validate_evidence_hash

ProofStep = Tuple[str, str, int, int]


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
    leaf_index: int
    tree_size: int
    root_hash: str
    proof: List[ProofStep]
    hash_alg: str = "SHA-256"
    tree_alg: str = "CT_STYLE_SHA256_V1"
    receipt_digest: str = ""

    def material(self) -> Dict[str, Any]:
        data = asdict(self)
        data.pop("receipt_digest", None)
        return data

    def compute_digest(self) -> str:
        material = json.dumps(self.material(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return sha256_hex(b"receipt\x00" + material)

    def with_digest(self) -> "Receipt":
        return replace(self, receipt_digest=self.compute_digest())

    def to_json_bytes(self) -> bytes:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
        tree_size = len(self.leaves)
        leaf_index = tree_size - 1
        self.roots_by_size[tree_size] = root
        proof = self.inclusion_proof(leaf_index)
        return Receipt("A2_MERKLE", obj["evidence_id"], leaf, leaf_index, tree_size, root, proof).with_digest()

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
        if key in self._range_root_cache:
            return self._range_root_cache[key]
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

    def inclusion_proof(self, index: int, tree_size: int | None = None) -> List[ProofStep]:
        tree_size = len(self.leaves) if tree_size is None else tree_size
        if index < 0 or index >= tree_size or tree_size > len(self.leaves):
            raise IndexError(index)

        def proof(start: int, end: int, idx: int) -> List[ProofStep]:
            span = end - start
            if span == 1:
                return []
            k = _largest_power_of_two_less_than(span)
            split = start + k
            if idx < split:
                return proof(start, split, idx) + [("right", self._root_range(split, end), split, end)]
            return proof(split, end, idx) + [("left", self._root_range(start, split), start, split)]

        return proof(0, tree_size, index)

    @staticmethod
    def verify_inclusion_at_index(leaf_hash: str, proof: List[ProofStep], leaf_index: int, tree_size: int, root_hash: str) -> bool:
        if leaf_index < 0 or tree_size <= 0 or leaf_index >= tree_size:
            return False

        def build(start: int, end: int, idx: int, pos: int) -> tuple[str, int] | None:
            span = end - start
            if span == 1:
                return leaf_hash, pos
            k = _largest_power_of_two_less_than(span)
            split = start + k
            if idx < split:
                left = build(start, split, idx, pos)
                if left is None:
                    return None
                left_hash, next_pos = left
                if next_pos >= len(proof) or proof[next_pos][0] != "right" or proof[next_pos][2] != split or proof[next_pos][3] != end:
                    return None
                return _node_hash(left_hash, proof[next_pos][1]), next_pos + 1
            right = build(split, end, idx, pos)
            if right is None:
                return None
            right_hash, next_pos = right
            if next_pos >= len(proof) or proof[next_pos][0] != "left" or proof[next_pos][2] != start or proof[next_pos][3] != split:
                return None
            return _node_hash(proof[next_pos][1], right_hash), next_pos + 1

        try:
            result = build(0, tree_size, leaf_index, 0)
        except Exception:
            return False
        return result is not None and result[1] == len(proof) and result[0] == root_hash

    @staticmethod
    def verify_receipt(obj: Dict[str, Any], receipt: Receipt, *, expected_tree_size: int | None = None) -> bool:
        try:
            leaf = _leaf_hash(obj)
        except ValueError:
            return False
        if receipt.backend != "A2_MERKLE":
            return False
        if receipt.hash_alg != "SHA-256" or receipt.tree_alg != "CT_STYLE_SHA256_V1":
            return False
        if receipt.evidence_id != obj.get("evidence_id"):
            return False
        if receipt.leaf_hash != leaf:
            return False
        if expected_tree_size is not None and receipt.tree_size != expected_tree_size:
            return False
        if receipt.compute_digest() != receipt.receipt_digest:
            return False
        return MerkleLog.verify_inclusion_at_index(receipt.leaf_hash, receipt.proof, receipt.leaf_index, receipt.tree_size, receipt.root_hash)

    def verify_consistency_by_prefix(self, old_size: int, old_root: str) -> bool:
        # Reference-implementation recomputation; not a compact RFC-style consistency proof.
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
