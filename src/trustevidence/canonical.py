import base64, copy, hashlib, json
from typing import Any
from .errors import CANONICAL_SERIALISATION, TrustEvidenceError
def b64url_encode(data: bytes) -> str: return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")
def b64url_decode(text: str) -> bytes: return base64.urlsafe_b64decode((text + "="*((4-len(text)%4)%4)).encode("ascii"))
def canon_te(obj: Any) -> bytes:
    try: return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")
    except (TypeError,ValueError) as exc: raise TrustEvidenceError(CANONICAL_SERIALISATION,str(exc)) from exc
def _strip(obj: dict, path: list[str]) -> dict:
    x=copy.deepcopy(obj); cur=x
    for p in path[:-1]:
        if not isinstance(cur,dict) or p not in cur: return x
        cur=cur[p]
    if isinstance(cur,dict): cur.pop(path[-1],None)
    return x
def core_signature_input(core: dict) -> bytes: return canon_te(_strip(core,["emitter_signature","signature_value"]))
def receipt_signature_input(receipt: dict) -> bytes: return canon_te(_strip(receipt,["receipt_signature","signature_value"]))
def tuple_encode(*parts) -> bytes:
    out=bytearray()
    for p in parts:
        if isinstance(p,bytes): raw=p
        elif isinstance(p,str): raw=p.encode()
        elif isinstance(p,int) and p>=0: raw=str(p).encode("ascii")
        else: raw=canon_te(p)
        out.extend(len(raw).to_bytes(8,"big")); out.extend(raw)
    return bytes(out)
def te_hash(tag: str,*parts) -> bytes: return hashlib.sha256(tuple_encode(tag,*parts)).digest()
def core_hash(core: dict, alg_id="sha256-te-v2") -> bytes: return te_hash("TE-v2:artefact-core",alg_id,core_signature_input(core))
def core_hash_b64(core: dict, alg_id="sha256-te-v2") -> str: return b64url_encode(core_hash(core,alg_id))
def payload_commitment(payload: bytes, context: str, alg_id="sha256-te-v2") -> bytes: return te_hash("TE-v2:payload",alg_id,context,payload)
def leaf_hash(core_hash_bytes: bytes, backend_id: str, log_id: str, alg_id="sha256-te-v2") -> bytes: return te_hash("TE-v2:leaf",alg_id,backend_id,log_id,core_hash_bytes)
def node_hash(left: bytes,right: bytes,backend_id: str,log_id: str,alg_id="sha256-te-v2") -> bytes: return te_hash("TE-v2:node",alg_id,backend_id,log_id,left,right)
def checkpoint_hash(backend_id: str,log_id: str,tree_size: int,root_hash: bytes,issued_at: str,alg_id="sha256-te-v2") -> bytes: return te_hash("TE-v2:checkpoint",alg_id,backend_id,log_id,tree_size,root_hash,issued_at)
