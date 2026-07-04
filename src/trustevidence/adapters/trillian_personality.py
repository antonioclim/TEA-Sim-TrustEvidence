from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from trustevidence.adapters.common import now_z, signed_receipt
from trustevidence.canonical import b64url_encode, canon_te, core_hash, core_hash_b64
from trustevidence.schema import EnvelopeValidator


class TrillianEvidenceClient(Protocol):
    """Narrow client interface required by the TrustEvidence personality."""

    def queue_leaf(self, *, log_id: int, leaf_value: bytes) -> dict[str, Any]: ...
    def get_latest_signed_log_root(self, *, log_id: int) -> dict[str, Any]: ...
    def get_inclusion_proof_by_hash(self, *, log_id: int, leaf_hash: bytes, tree_size: int) -> dict[str, Any]: ...
    def get_consistency_proof(self, *, log_id: int, first_tree_size: int, second_tree_size: int) -> dict[str, Any]: ...


class GeneratedGrpcTrillianClient:
    """Adapter over Python gRPC stubs generated from upstream Trillian protos.

    The imports are intentionally delayed. Operators generate stubs under
    `src/trustevidence/trillian_generated/` using scripts/generate_trillian_stubs.sh.
    """

    def __init__(self, endpoint: str = "localhost:8090"):
        import grpc  # type: ignore
        from trustevidence.trillian_generated import trillian_log_api_pb2_grpc, trillian_pb2  # type: ignore
        self.grpc = grpc
        self.pb = trillian_pb2
        self.channel = grpc.insecure_channel(endpoint)
        self.stub = trillian_log_api_pb2_grpc.TrillianLogStub(self.channel)

    def queue_leaf(self, *, log_id: int, leaf_value: bytes) -> dict[str, Any]:
        req = self.pb.QueueLeafRequest(log_id=log_id, leaf=self.pb.LogLeaf(leaf_value=leaf_value))
        resp = self.stub.QueueLeaf(req)
        return {"queued": True, "raw": resp}

    def get_latest_signed_log_root(self, *, log_id: int) -> dict[str, Any]:
        req = self.pb.GetLatestSignedLogRootRequest(log_id=log_id)
        resp = self.stub.GetLatestSignedLogRoot(req)
        slr = resp.signed_log_root
        return {
            "tree_size": int(getattr(slr, "tree_size", 0)),
            "root_hash": bytes(getattr(slr, "root_hash", b"")),
            "timestamp_nanos": int(getattr(slr, "timestamp_nanos", 0)),
        }

    def get_inclusion_proof_by_hash(self, *, log_id: int, leaf_hash: bytes, tree_size: int) -> dict[str, Any]:
        req = self.pb.GetInclusionProofByHashRequest(log_id=log_id, leaf_hash=leaf_hash, tree_size=tree_size)
        resp = self.stub.GetInclusionProofByHash(req)
        return {"proof": resp.proof}

    def get_consistency_proof(self, *, log_id: int, first_tree_size: int, second_tree_size: int) -> dict[str, Any]:
        req = self.pb.GetConsistencyProofRequest(
            log_id=log_id, first_tree_size=first_tree_size, second_tree_size=second_tree_size
        )
        resp = self.stub.GetConsistencyProof(req)
        return {"proof": resp.proof}


@dataclass(slots=True)
class EvidenceTrillianPersonality:
    """TrustEvidence admission/canonicalisation personality above Trillian Log mode."""

    backend_id: str
    trillian_log_id: int
    signer: Any
    client: TrillianEvidenceClient
    alg_id: str = "sha256-te-v2"
    validator: EnvelopeValidator = EnvelopeValidator()

    @property
    def log_id(self) -> str:
        return f"trillian:{self.trillian_log_id}"

    def leaf_payload(self, envelope: dict[str, Any]) -> bytes:
        core = envelope["artefact_core"]
        return canon_te({
            "kind": "trustevidence-core-hash-v1",
            "alg_id": self.alg_id,
            "backend_id": self.backend_id,
            "log_id": self.log_id,
            "core_hash": core_hash_b64(core, self.alg_id),
        })

    def append(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.validator.validate(envelope)
        core = envelope["artefact_core"]
        leaf_value = self.leaf_payload(envelope)
        leaf_hash_value = core_hash({"emitter_signature": {"signature_value": "AA"}, "leaf_payload": b64url_encode(leaf_value)}, self.alg_id)
        self.client.queue_leaf(log_id=self.trillian_log_id, leaf_value=leaf_value)
        root = self.client.get_latest_signed_log_root(log_id=self.trillian_log_id)
        tree_size = int(root.get("tree_size") or 0)
        root_hash = root.get("root_hash") or b""
        if isinstance(root_hash, str):
            root_hash_b64 = root_hash
        else:
            root_hash_b64 = b64url_encode(root_hash or b"\x00" * 32)
        self.client.get_inclusion_proof_by_hash(
            log_id=self.trillian_log_id, leaf_hash=leaf_hash_value, tree_size=max(tree_size, 1)
        )
        receipt = {
            "backend_type": "trillian",
            "backend_id": self.backend_id,
            "log_id": self.log_id,
            "alg_id": self.alg_id,
            "core_hash": core_hash_b64(core, self.alg_id),
            "tree_size": max(tree_size, 1),
            "root_hash": root_hash_b64,
            "inclusion_proof_ref": f"urn:te:trillian:proof:{self.trillian_log_id}:{core_hash_b64(core, self.alg_id)}",
            "consistency_proof_ref": f"urn:te:trillian:consistency:{self.trillian_log_id}:latest",
            "issued_at": now_z(),
            "signer_id": self.signer.key_id,
        }
        out = dict(envelope)
        out["backend_receipt"] = signed_receipt(receipt, self.signer)
        return out
