import json
from pathlib import Path
import pytest
from trustevidence.canonical import canon_te,core_hash,te_hash,tuple_encode,b64url_encode
from trustevidence.envelope import signed_envelope,failure_envelope
from trustevidence.schema import EnvelopeValidator
from trustevidence.validators import SemanticValidator,VerifierState
from trustevidence.backends.a1 import InMemoryA1AppendBackend
from trustevidence.backends.a2_merkle import A2MerkleLog
from trustevidence.errors import *

def test_example_schema_validates():
    EnvelopeValidator().validate(json.loads(Path(__file__).with_name("access_attestation_envelope.example.json").read_text()))
def test_canonical_and_domain_separation(emitter_pair):
    assert canon_te({"b":1,"a":2})==b'{"a":2,"b":1}'
    assert tuple_encode("ab","c")!=tuple_encode("a","bc")
    assert te_hash("TE-v2:payload","sha256","x")!=te_hash("TE-v2:leaf","sha256","x")
    c=signed_envelope("urn:e:1","urn:a:1",emitter_pair)["artefact_core"]
    changed={**c,"emitter_signature":{**c["emitter_signature"],"signature_value":"QUJD"}}
    assert core_hash(c)==core_hash(changed)
def test_a1_receipt_and_duplicate(emitter_pair,backend_pair,registry):
    env=signed_envelope("urn:e:a1","urn:a:a1",emitter_pair); b=InMemoryA1AppendBackend("urn:te:backend:a1",backend_pair); accepted=b.append(env)
    assert accepted["backend_receipt"]["backend_type"]=="central-audit"
    assert "root_hash" not in accepted["backend_receipt"]
    SemanticValidator(accepted_backend_id="urn:te:backend:a1",keys=registry).validate_envelope(accepted,verify_signatures=True)
    with pytest.raises(TrustEvidenceError) as exc: b.append(env)
    assert exc.value.code==DUPLICATE_EMISSION
def test_a2_inclusion_and_consistency(emitter_pair,backend_pair,registry):
    log=A2MerkleLog("urn:te:backend:a2","urn:te:log:test",backend_pair); accepted=[]
    for i in range(12): accepted.append(log.append(signed_envelope(f"urn:e:{i}",f"urn:a:{i}",emitter_pair)))
    for env in accepted:
        r=env["backend_receipt"]; p=log.proof_store.get(r["inclusion_proof_ref"]); assert log.verify_inclusion(r["core_hash"],r["root_hash"],p)
    for old in range(1,12):
        p=log.consistency_proof(old,12); assert log.verify_consistency(old,12,b64url_encode(log.root_hash(old)),b64url_encode(log.root_hash(12)),p)
    SemanticValidator(accepted_backend_id="urn:te:backend:a2",accepted_log_id="urn:te:log:test",keys=registry).validate_envelope(accepted[-1],verify_signatures=True)
def test_wrong_log_identity_and_verifier_state_loss(emitter_pair,backend_pair,registry):
    log=A2MerkleLog("urn:te:backend:a2","urn:te:log:test",backend_pair); env=log.append(signed_envelope("urn:e:bad","urn:a:bad",emitter_pair)); r=env["backend_receipt"]
    with pytest.raises(TrustEvidenceError) as exc: SemanticValidator(accepted_backend_id="urn:te:backend:a2",accepted_log_id="urn:te:other",keys=registry).validate_envelope(env,verify_signatures=True)
    assert exc.value.code==WRONG_LOG_IDENTITY
    with pytest.raises(TrustEvidenceError) as exc: SemanticValidator(accepted_backend_id="urn:te:backend:a2",accepted_log_id="urn:te:log:test").accept_checkpoint(r,None)
    assert exc.value.code==VERIFIER_STATE_LOSS
def test_fork_and_pre_boundary_non_emission(emitter_pair,backend_pair):
    log=A2MerkleLog("urn:te:backend:a2","urn:te:log:test",backend_pair); r=log.append(signed_envelope("urn:e:fork","urn:a:fork",emitter_pair))["backend_receipt"]
    st=VerifierState("urn:te:backend:a2","urn:te:log:test","sha256-te-v2",r["tree_size"],"AAAAAAAA")
    with pytest.raises(TrustEvidenceError) as exc: SemanticValidator(accepted_backend_id="urn:te:backend:a2",accepted_log_id="urn:te:log:test").accept_checkpoint(r,st)
    assert exc.value.code==FORK_EVIDENCE
    ok=failure_envelope("urn:e:fail","urn:a:fail",emitter_pair); SemanticValidator().validate_envelope(ok)
    bad=json.loads(json.dumps(ok)); bad["artefact_core"]["evidence_type"]="access-attestation"
    with pytest.raises(TrustEvidenceError) as exc: SemanticValidator().validate_envelope(bad)
    assert exc.value.code==PRE_BOUNDARY_NON_EMISSION
def test_postgres_ddl_contains_append_controls():
    ddl=Path(__file__).parents[1].joinpath("sql/a1_postgres.sql").read_text().lower()
    assert "bigserial primary key" in ddl and "unique" in ddl and "update, delete and truncate are not granted" in ddl
@pytest.mark.postgres
def test_postgres_integration_requires_dsn():
    import os
    if not os.getenv("TE_POSTGRES_DSN"): pytest.skip("TE_POSTGRES_DSN not supplied in sandbox")
