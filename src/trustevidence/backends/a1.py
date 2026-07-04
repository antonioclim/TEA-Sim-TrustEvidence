from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol
from trustevidence.canonical import core_hash_b64
from trustevidence.crypto import sign_receipt
from trustevidence.errors import DUPLICATE_EMISSION, TrustEvidenceError
class A1AppendReceiptBackend(Protocol):
    def append(self,envelope:dict[str,Any])->dict[str,Any]: ...
def now_z(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
@dataclass
class InMemoryA1AppendBackend:
    backend_id: str; signer: object; alg_id: str="sha256-te-v2"; rows:list=field(default_factory=list); event_ids:set=field(default_factory=set)
    def append(self,envelope):
        core=envelope["artefact_core"]; ev=core["event_id"]
        if ev in self.event_ids: raise TrustEvidenceError(DUPLICATE_EMISSION,"duplicate event_id")
        receipt={"backend_type":"central-audit","backend_id":self.backend_id,"alg_id":self.alg_id,"core_hash":core_hash_b64(core,self.alg_id),"issued_at":now_z(),"signer_id":self.signer.key_id,"receipt_signature":{"alg_id":"ed25519","key_id":self.signer.key_id,"signature_value":"AA"}}
        receipt=sign_receipt(receipt,self.signer); self.rows.append({"sequence_id":len(self.rows)+1,"event_id":ev,"core_hash":receipt["core_hash"]}); self.event_ids.add(ev); out=dict(envelope); out["backend_receipt"]=receipt; return out
class PostgresA1Backend:
    def __init__(self,dsn,backend_id,signer,alg_id="sha256-te-v2"):
        try: import psycopg
        except ImportError as exc: raise RuntimeError("psycopg required for PostgresA1Backend") from exc
        self.psycopg=psycopg; self.dsn=dsn; self.backend_id=backend_id; self.signer=signer; self.alg_id=alg_id
    def append(self,envelope): # pragma: no cover
        core=envelope["artefact_core"]; receipt={"backend_type":"central-audit","backend_id":self.backend_id,"alg_id":self.alg_id,"core_hash":core_hash_b64(core,self.alg_id),"issued_at":now_z(),"signer_id":self.signer.key_id,"receipt_signature":{"alg_id":"ed25519","key_id":self.signer.key_id,"signature_value":"AA"}}
        receipt=sign_receipt(receipt,self.signer)
        with self.psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur: cur.execute("insert into trustevidence_a1_audit_log (artefact_id,event_id,core_hash_b64,envelope_json,receipt_json) values (%s,%s,%s,%s::jsonb,%s::jsonb)",(core["artefact_id"],core["event_id"],receipt["core_hash"],self.psycopg.types.json.Jsonb(envelope),self.psycopg.types.json.Jsonb(receipt)))
        out=dict(envelope); out["backend_receipt"]=receipt; return out
