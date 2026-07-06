import hashlib
from dataclasses import dataclass, field
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from .canonical import b64url_decode,b64url_encode,core_signature_input,receipt_signature_input
from .errors import UNAUTHORISED_SIGNER, TrustEvidenceError
@dataclass(slots=True)
class DeterministicEd25519KeyPair:
    key_id: str; private_key: Ed25519PrivateKey
    @classmethod
    def from_label(cls,key_id,label): return cls(key_id,Ed25519PrivateKey.from_private_bytes(hashlib.sha256(label.encode()).digest()))
    @property
    def public_key(self): return self.private_key.public_key()
    def sign(self,data: bytes) -> str: return b64url_encode(self.private_key.sign(data))
@dataclass
class KeyRegistry:
    emitter_keys: dict[str,Ed25519PublicKey]=field(default_factory=dict); backend_keys: dict[str,Ed25519PublicKey]=field(default_factory=dict)
    def register_emitter(self,pair): self.emitter_keys[pair.key_id]=pair.public_key
    def register_backend(self,pair): self.backend_keys[pair.key_id]=pair.public_key
    def verify_emitter_core(self,core):
        sig=core.get("emitter_signature",{}); key=self.emitter_keys.get(sig.get("key_id"))
        if key is None: raise TrustEvidenceError(UNAUTHORISED_SIGNER,"unknown emitter key")
        try: key.verify(b64url_decode(sig["signature_value"]),core_signature_input(core))
        except (InvalidSignature,KeyError,ValueError) as exc: raise TrustEvidenceError(UNAUTHORISED_SIGNER,"emitter signature failed") from exc
    def verify_backend_receipt(self,receipt):
        sig=receipt.get("receipt_signature",{}); key=self.backend_keys.get(sig.get("key_id"))
        if key is None: raise TrustEvidenceError(UNAUTHORISED_SIGNER,"unknown backend key")
        try: key.verify(b64url_decode(sig["signature_value"]),receipt_signature_input(receipt))
        except (InvalidSignature,KeyError,ValueError) as exc: raise TrustEvidenceError(UNAUTHORISED_SIGNER,"backend signature failed") from exc
def sign_core(core,pair):
    core=dict(core); sig=dict(core.get("emitter_signature",{})); sig.setdefault("alg_id","ed25519"); sig["key_id"]=pair.key_id; sig["signature_value"]="AA"; core["emitter_signature"]=sig; sig["signature_value"]=pair.sign(core_signature_input(core)); core["emitter_signature"]=sig; return core
def sign_receipt(receipt,pair):
    receipt=dict(receipt); sig=dict(receipt.get("receipt_signature",{})); sig.setdefault("alg_id","ed25519"); sig["key_id"]=pair.key_id; sig["signature_value"]="AA"; receipt["receipt_signature"]=sig; sig["signature_value"]=pair.sign(receipt_signature_input(receipt)); receipt["receipt_signature"]=sig; return receipt
