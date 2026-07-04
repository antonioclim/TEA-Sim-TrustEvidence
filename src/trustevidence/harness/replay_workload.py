from __future__ import annotations

import argparse
import json
from pathlib import Path

from trustevidence.adapters.fabric import FabricCliAdapter
from trustevidence.adapters.rekor import RekorClientAdapter
from trustevidence.adapters.trillian_personality import EvidenceTrillianPersonality
from trustevidence.backends.a1 import InMemoryA1AppendBackend
from trustevidence.backends.a2_merkle import A2MerkleLog
from trustevidence.crypto import DeterministicEd25519KeyPair
from trustevidence.harness.workload import envelope_from_row, load_jsonl, summarise_receipt


class _FakeTrillianClient:
    def __init__(self):
        self.count = 0
    def queue_leaf(self, *, log_id: int, leaf_value: bytes):
        self.count += 1
        return {"queued": True}
    def get_latest_signed_log_root(self, *, log_id: int):
        return {"tree_size": self.count, "root_hash": bytes([self.count % 256]) * 32}
    def get_inclusion_proof_by_hash(self, *, log_id: int, leaf_hash: bytes, tree_size: int):
        return {"proof": []}
    def get_consistency_proof(self, *, log_id: int, first_tree_size: int, second_tree_size: int):
        return {"proof": []}


def replay_local(rows):
    emitter = DeterministicEd25519KeyPair.from_label("urn:te:key:emitter:external", "external-emitter")
    backend_signer = DeterministicEd25519KeyPair.from_label("urn:te:key:backend:external", "external-backend")
    a1 = InMemoryA1AppendBackend("urn:te:backend:a1:external", backend_signer)
    a2 = A2MerkleLog("urn:te:backend:a2:external", "urn:te:log:a2:external", backend_signer)
    trillian_fake = EvidenceTrillianPersonality("urn:te:backend:trillian:dry", 8675309, backend_signer, _FakeTrillianClient())
    out = []
    for row in rows:
        env = envelope_from_row(row, emitter)
        for name, backend in [("a1", a1), ("a2", a2), ("trillian-dry", trillian_fake)]:
            emitted = backend.append(env)
            out.append({"event_id": row["event_id"], "backend": name, "receipt": summarise_receipt(emitted)})
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Replay a TrustEvidence AuditEvent smoke workload")
    parser.add_argument("--workload", required=True)
    parser.add_argument("--mode", choices=["local", "external"], default="local")
    parser.add_argument("--results", default="results/external_smoke_receipts.jsonl")
    args = parser.parse_args(argv)
    rows = load_jsonl(args.workload)
    if args.mode == "external":
        raise SystemExit("external mode requires Docker-composed services; run make smoke after make up on operator hardware")
    results = replay_local(rows)
    path = Path(args.results)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"replayed_events={len(rows)}")
    print(f"receipt_rows={len(results)}")
    print(f"results={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
