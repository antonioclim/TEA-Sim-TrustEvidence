import pytest
from trustevidence.crypto import DeterministicEd25519KeyPair, KeyRegistry
@pytest.fixture
def emitter_pair(): return DeterministicEd25519KeyPair.from_label("urn:te:key:emitter-test","emitter-test")
@pytest.fixture
def backend_pair(): return DeterministicEd25519KeyPair.from_label("urn:te:key:backend-test","backend-test")
@pytest.fixture
def registry(emitter_pair,backend_pair):
    r=KeyRegistry(); r.register_emitter(emitter_pair); r.register_backend(backend_pair); return r
