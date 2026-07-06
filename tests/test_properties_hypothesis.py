import pytest
hypothesis = pytest.importorskip("hypothesis", reason="Hypothesis is required for property-based tests; install with pip install -e .[test].")
from hypothesis import given, settings, strategies as st
from trustevidence.crypto import DeterministicEd25519KeyPair
from trustevidence.backends.a2_merkle import A2MerkleLog
from trustevidence.envelope import signed_envelope
from trustevidence.canonical import b64url_encode,node_hash,te_hash
@settings(max_examples=50,deadline=None)
@given(labels=st.lists(st.text(min_size=1,max_size=10),min_size=1,max_size=25,unique=True))
def test_property_inclusion(labels):
    emitter_pair=DeterministicEd25519KeyPair.from_label("urn:te:key:emitter-hyp","emitter-hyp")
    backend_pair=DeterministicEd25519KeyPair.from_label("urn:te:key:backend-hyp","backend-hyp")
    log=A2MerkleLog("urn:te:backend:a2","urn:te:log:hyp",backend_pair); receipts=[]
    for i,l in enumerate(labels): receipts.append(log.append(signed_envelope(f"urn:e:{i}:{l}",f"urn:a:{i}",emitter_pair))["backend_receipt"])
    for r in receipts: assert log.verify_inclusion(r["core_hash"],r["root_hash"],log.proof_store.get(r["inclusion_proof_ref"]))
@settings(max_examples=50,deadline=None)
@given(n=st.integers(min_value=2,max_value=30), old_raw=st.integers(min_value=1,max_value=29))
def test_property_consistency(n,old_raw):
    emitter_pair=DeterministicEd25519KeyPair.from_label("urn:te:key:emitter-hypc","emitter-hypc")
    backend_pair=DeterministicEd25519KeyPair.from_label("urn:te:key:backend-hypc","backend-hypc")
    old=min(old_raw,n-1); log=A2MerkleLog("urn:te:backend:a2","urn:te:log:hypc",backend_pair)
    for i in range(n): log.append(signed_envelope(f"urn:e:c:{i}",f"urn:a:c:{i}",emitter_pair))
    assert log.verify_consistency(old,n,b64url_encode(log.root_hash(old)),b64url_encode(log.root_hash(n)),log.consistency_proof(old,n))
@settings(max_examples=30,deadline=None)
@given(st.binary(max_size=16),st.binary(max_size=16))
def test_property_domain_separation(a,b):
    left=te_hash("TE-v2:payload","sha256-te-v2",a); right=te_hash("TE-v2:payload","sha256-te-v2",b)
    assert node_hash(left,right,"urn:b","urn:l") != te_hash("TE-v2:payload","sha256-te-v2",left,right)
