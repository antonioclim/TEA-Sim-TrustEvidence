from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from trustevidence.canonical import b64url_decode,b64url_encode,core_hash,leaf_hash,node_hash
from trustevidence.crypto import sign_receipt
from trustevidence.errors import DOMAIN_TAG_MISMATCH, ROLLBACK_DETECTED, TrustEvidenceError
from trustevidence.proof_store import InMemoryProofStore
def now_z(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def lpot(n):
    if n<=1: raise ValueError("n must be >1")
    k=1
    while k*2<n: k*=2
    return k
@dataclass
class A2MerkleLog:
    backend_id: str; log_id: str; signer: object; proof_store: InMemoryProofStore=field(default_factory=InMemoryProofStore); alg_id: str="sha256-te-v2"; _leaves:list[bytes]=field(default_factory=list)
    @property
    def tree_size(self): return len(self._leaves)
    def _root(self,leaves):
        n=len(leaves)
        if n==0: return b"\x00"*32
        if n==1: return leaves[0]
        k=lpot(n); return node_hash(self._root(leaves[:k]),self._root(leaves[k:]),self.backend_id,self.log_id,self.alg_id)
    def root_hash(self,size=None): return self._root(self._leaves if size is None else self._leaves[:size])
    def append(self,envelope):
        core=envelope["artefact_core"]; old=self.tree_size; ch=core_hash(core,self.alg_id); self._leaves.append(leaf_hash(ch,self.backend_id,self.log_id,self.alg_id)); new=self.tree_size; root=self.root_hash(); inc_ref=self.proof_store.put("inclusion",self.inclusion_proof(new-1,new)); cons_ref=None
        if old>0: cons_ref=self.proof_store.put("consistency",self.consistency_proof(old,new))
        receipt={"backend_type":"hash-log","backend_id":self.backend_id,"log_id":self.log_id,"alg_id":self.alg_id,"core_hash":b64url_encode(ch),"tree_size":new,"root_hash":b64url_encode(root),"leaf_index":new-1,"inclusion_proof_ref":inc_ref,"issued_at":now_z(),"signer_id":self.signer.key_id,"receipt_signature":{"alg_id":"ed25519","key_id":self.signer.key_id,"signature_value":"AA"}}
        if cons_ref: receipt["consistency_proof_ref"]=cons_ref
        receipt=sign_receipt(receipt,self.signer); out=dict(envelope); out["backend_receipt"]=receipt; return out
    def _path(self,leaves,index,out):
        if len(leaves)==1: return leaves[0]
        k=lpot(len(leaves))
        if index<k:
            cur=self._path(leaves[:k],index,out); sib=self._root(leaves[k:]); out.append({"side":"right","hash":b64url_encode(sib)}); return node_hash(cur,sib,self.backend_id,self.log_id,self.alg_id)
        sib=self._root(leaves[:k]); cur=self._path(leaves[k:],index-k,out); out.append({"side":"left","hash":b64url_encode(sib)}); return node_hash(sib,cur,self.backend_id,self.log_id,self.alg_id)
    def inclusion_proof(self,index,tree_size=None):
        leaves=self._leaves if tree_size is None else self._leaves[:tree_size]; out=[]; self._path(leaves,index,out); return {"proof_type":"te-v2-inclusion","backend_id":self.backend_id,"log_id":self.log_id,"alg_id":self.alg_id,"leaf_index":index,"tree_size":len(leaves),"path":out}
    def verify_inclusion(self,core_hash_b64,root_hash_b64,proof):
        if proof.get("backend_id")!=self.backend_id or proof.get("log_id")!=self.log_id or proof.get("alg_id")!=self.alg_id: raise TrustEvidenceError(DOMAIN_TAG_MISMATCH,"proof identity mismatch")
        cur=leaf_hash(b64url_decode(core_hash_b64),self.backend_id,self.log_id,self.alg_id)
        for p in proof["path"]:
            sib=b64url_decode(p["hash"]); cur=node_hash(sib,cur,self.backend_id,self.log_id,self.alg_id) if p["side"]=="left" else node_hash(cur,sib,self.backend_id,self.log_id,self.alg_id)
        return cur==b64url_decode(root_hash_b64)
    def _subproof(self,leaves,m,complete):
        n=len(leaves)
        if m==n: return [] if complete else [self._root(leaves)]
        k=lpot(n)
        return self._subproof(leaves[:k],m,complete)+[self._root(leaves[k:])] if m<=k else self._subproof(leaves[k:],m-k,False)+[self._root(leaves[:k])]
    def consistency_proof(self,old_size,new_size=None):
        new_size=self.tree_size if new_size is None else new_size; path=[] if old_size in (0,new_size) else [b64url_encode(x) for x in self._subproof(self._leaves[:new_size],old_size,True)]; return {"proof_type":"te-v2-consistency","backend_id":self.backend_id,"log_id":self.log_id,"alg_id":self.alg_id,"old_size":old_size,"new_size":new_size,"path":path}
    def verify_consistency(self,old_size,new_size,old_root_b64,new_root_b64,proof):
        if proof.get("backend_id")!=self.backend_id or proof.get("log_id")!=self.log_id or proof.get("alg_id")!=self.alg_id: raise TrustEvidenceError(DOMAIN_TAG_MISMATCH,"proof identity mismatch")
        if old_size!=proof.get("old_size") or new_size!=proof.get("new_size"): raise TrustEvidenceError(ROLLBACK_DETECTED,"size mismatch")
        old_root=b64url_decode(old_root_b64); new_root=b64url_decode(new_root_b64); path=[b64url_decode(x) for x in proof.get("path",[])]
        if old_size==0: return True
        if old_size==new_size: return old_root==new_root and not path
        fn=old_size-1; sn=new_size-1
        while fn&1: fn>>=1; sn>>=1
        work=list(path)
        if fn==0: fr=old_root; sr=old_root
        else:
            if not work: return False
            fr=work.pop(0); sr=fr
        for comp in work:
            if sn==0: return False
            if (fn&1) or (fn==sn):
                fr=node_hash(comp,fr,self.backend_id,self.log_id,self.alg_id); sr=node_hash(comp,sr,self.backend_id,self.log_id,self.alg_id)
                while (fn&1)==0 and fn!=0: fn>>=1; sn>>=1
            else: sr=node_hash(sr,comp,self.backend_id,self.log_id,self.alg_id)
            fn>>=1; sn>>=1
        return fr==old_root and sr==new_root
