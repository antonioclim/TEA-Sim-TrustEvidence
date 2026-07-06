from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Literal

from .canonical import canonical_bytes, sha256_hex

ProofSide = Literal["left", "right"]
ProofStep = tuple[ProofSide, str]


def _node_hash(left_hex: str, right_hex: str) -> str:
    return sha256_hex(b"node:" + bytes.fromhex(left_hex) + bytes.fromhex(right_hex))


def _leaf_hash(obj: dict[str, Any]) -> str:
    return sha256_hex(b"leaf:" + canonical_bytes(obj))


def _root_from_leaves(leaves: list[str]) -> str:
    if not leaves:
        return sha256_hex(b"empty")
    level = leaves[:]
    while len(level) > 1:
        nxt: list[str] = []
        for i in range(0, len(level), 2):
            left = level[i]
            if i + 1 < len(level):
                nxt.append(_node_hash(left, level[i + 1]))
            else:
                nxt.append(left)
        level = nxt
    return level[0]


def _levels_from_leaves(leaves: list[str]) -> list[list[str]]:
    if not leaves:
        return [[sha256_hex(b"empty")]]
    levels = [leaves[:]]
    while len(levels[-1]) > 1:
        current = levels[-1]
        nxt: list[str] = []
        for i in range(0, len(current), 2):
            left = current[i]
            if i + 1 < len(current):
                nxt.append(_node_hash(left, current[i + 1]))
            else:
                nxt.append(left)
        levels.append(nxt)
    return levels


@dataclass(frozen=True)
class AppendReceipt:
    backend: str
    evidence_id: str
    leaf_index: int
    leaf_hash: str
    tree_size: int
    root_hash: str
    hash_alg: str = "SHA-256"
    canonicalisation: str = "json.dumps(sort_keys=True,separators=(',',':'))"


@dataclass(frozen=True)
class InclusionReceipt:
    backend: str
    evidence_id: str
    leaf_index: int
    leaf_hash: str
    tree_size: int
    root_hash: str
    proof: list[ProofStep]
    hash_alg: str = "SHA-256"


class MerkleLog:
    """Pure-Python append-only Merkle reference implementation.

    The class is intentionally simple and inspectable. It provides append receipts,
    inclusion proofs and a prefix-consistency check by recomputing the historical
    prefix root. The prefix check is not a compact RFC-style consistency proof.
    """

    def __init__(self) -> None:
        self.objects: list[dict[str, Any]] = []
        self.leaves: list[str] = []
        self.roots_by_size: dict[int, str] = {0: _root_from_leaves([])}
        self._frontier: list[tuple[int, int, str]] = []  # start, size, hash

    def _frontier_root(self) -> str:
        if not self._frontier:
            return _root_from_leaves([])
        # Peaks must be bagged from right to left to match the carried-odd
        # tree produced by _levels_from_leaves. A left fold diverges for
        # non-power-of-two tree sizes such as 7 or 1000.
        cur = self._frontier[-1][2]
        for _, _, h in reversed(self._frontier[:-1]):
            cur = _node_hash(h, cur)
        return cur

    def append(self, obj: dict[str, Any]) -> AppendReceipt:
        leaf = _leaf_hash(obj)
        self.objects.append(obj)
        self.leaves.append(leaf)
        start = len(self.leaves) - 1
        self._frontier.append((start, 1, leaf))
        while len(self._frontier) >= 2 and self._frontier[-1][1] == self._frontier[-2][1]:
            right = self._frontier.pop()
            left = self._frontier.pop()
            self._frontier.append((left[0], left[1] + right[1], _node_hash(left[2], right[2])))
        size = len(self.leaves)
        root = self._frontier_root()
        self.roots_by_size[size] = root
        return AppendReceipt("A2_MERKLE", str(obj["evidence_id"]), size - 1, leaf, size, root)

    def root_hash(self) -> str:
        return self.roots_by_size[len(self.leaves)]

    def storage_bytes(self) -> int:
        # Deterministic serialised footprint approximation for local comparison.
        import json

        return len(json.dumps({"objects": self.objects, "leaves": self.leaves}, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    def inclusion_proof(self, index: int) -> list[ProofStep]:
        if index < 0 or index >= len(self.leaves):
            raise IndexError(index)
        proof: list[ProofStep] = []
        idx = index
        levels = _levels_from_leaves(self.leaves)
        for level in levels[:-1]:
            if idx % 2 == 0:
                sibling = idx + 1
                if sibling < len(level):
                    proof.append(("right", level[sibling]))
            else:
                sibling = idx - 1
                proof.append(("left", level[sibling]))
            idx //= 2
        return proof

    def inclusion_receipt(self, index: int) -> InclusionReceipt:
        obj = self.objects[index]
        return InclusionReceipt(
            backend="A2_MERKLE",
            evidence_id=str(obj["evidence_id"]),
            leaf_index=index,
            leaf_hash=self.leaves[index],
            tree_size=len(self.leaves),
            root_hash=self.root_hash(),
            proof=self.inclusion_proof(index),
        )

    @staticmethod
    def verify_inclusion(obj: dict[str, Any], proof: Iterable[ProofStep], root_hash: str) -> bool:
        cur = _leaf_hash(obj)
        for side, sibling_hex in proof:
            cur = _node_hash(sibling_hex, cur) if side == "left" else _node_hash(cur, sibling_hex)
        return cur == root_hash

    @staticmethod
    def verify_receipt(obj: dict[str, Any], receipt: InclusionReceipt | dict[str, Any]) -> bool:
        rec = asdict(receipt) if isinstance(receipt, InclusionReceipt) else receipt
        if str(obj.get("evidence_id")) != rec.get("evidence_id"):
            return False
        if _leaf_hash(obj) != rec.get("leaf_hash"):
            return False
        return MerkleLog.verify_inclusion(obj, rec.get("proof", []), str(rec.get("root_hash")))

    def verify_consistency_by_prefix(self, old_size: int, old_root: str) -> bool:
        if old_size < 0 or old_size > len(self.leaves):
            return False
        return _root_from_leaves(self.leaves[:old_size]) == old_root
