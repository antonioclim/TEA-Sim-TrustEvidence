from dataclasses import dataclass
from .canonical import core_hash_b64
from .crypto import KeyRegistry
from .errors import *
from .schema import EnvelopeValidator
@dataclass(slots=True)
class VerifierState:
    backend_id: str; log_id: str; alg_id: str; tree_size: int; root_hash: str; retained: bool=True
class SemanticValidator:
    def __init__(self,*,accepted_backend_id=None,accepted_log_id=None,accepted_alg_id="sha256-te-v2",keys:KeyRegistry|None=None):
        self.schema=EnvelopeValidator(); self.accepted_backend_id=accepted_backend_id; self.accepted_log_id=accepted_log_id; self.accepted_alg_id=accepted_alg_id; self.keys=keys
    def validate_envelope(self,envelope,*,verify_signatures=False):
        self.schema.validate(envelope); core=envelope["artefact_core"]
        if verify_signatures and self.keys: self.keys.verify_emitter_core(core)
        receipt=envelope.get("backend_receipt")
        if receipt:
            if receipt["core_hash"] != core_hash_b64(core,receipt.get("alg_id",self.accepted_alg_id)): raise TrustEvidenceError(DOMAIN_TAG_MISMATCH,"receipt core_hash mismatch")
            if self.accepted_backend_id and receipt["backend_id"] != self.accepted_backend_id: raise TrustEvidenceError(WRONG_BACKEND_IDENTITY,"wrong backend")
            if self.accepted_log_id and receipt.get("log_id") != self.accepted_log_id: raise TrustEvidenceError(WRONG_LOG_IDENTITY,"wrong log")
            if receipt["backend_type"]=="hash-log":
                for f in ["log_id","tree_size","root_hash","leaf_index","inclusion_proof_ref"]:
                    if f not in receipt: raise TrustEvidenceError(UNAVAILABLE_PROOF,f"missing {f}")
            if receipt["backend_type"]=="central-audit" and ("root_hash" in receipt or "tree_size" in receipt): raise TrustEvidenceError(DOMAIN_TAG_MISMATCH,"central audit must not claim Merkle state")
            if verify_signatures and self.keys: self.keys.verify_backend_receipt(receipt)
        failure=core.get("failure")
        if failure and failure.get("failure_code")==PRE_BOUNDARY_NON_EMISSION and core.get("evidence_type")!="failure-artefact": raise TrustEvidenceError(PRE_BOUNDARY_NON_EMISSION,"pre-boundary non-emission requires failure artefact")
    def accept_checkpoint(self,receipt,state:VerifierState|None):
        if receipt.get("backend_id")!=self.accepted_backend_id: raise TrustEvidenceError(WRONG_BACKEND_IDENTITY,"wrong backend")
        if receipt.get("log_id")!=self.accepted_log_id: raise TrustEvidenceError(WRONG_LOG_IDENTITY,"wrong log")
        if receipt.get("alg_id")!=self.accepted_alg_id: raise TrustEvidenceError(DOMAIN_TAG_MISMATCH,"wrong alg")
        if state is None or not state.retained: raise TrustEvidenceError(VERIFIER_STATE_LOSS,"state loss")
        ts=int(receipt.get("tree_size",0)); root=receipt.get("root_hash","")
        if ts<state.tree_size: raise TrustEvidenceError(STALE_CHECKPOINT,"stale checkpoint")
        if ts==state.tree_size and root!=state.root_hash: raise TrustEvidenceError(FORK_EVIDENCE,"fork evidence")
        return VerifierState(receipt["backend_id"],receipt["log_id"],receipt["alg_id"],ts,root,True)
