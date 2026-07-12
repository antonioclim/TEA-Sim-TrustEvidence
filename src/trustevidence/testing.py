"""Deterministic TEST-ONLY keys for reproducible synthetic fixtures."""

from __future__ import annotations

import hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

FIXTURE_EMITTER_KEY_ID = "urn:te:key:fixture-emitter-v1"
FIXTURE_BACKEND_KEY_ID = "urn:te:key:fixture-backend-v1"
FIXTURE_BACKEND_ID = "urn:te:backend:a2-cmpb-reference"
FIXTURE_LOG_ID = "urn:te:log:cmpb-reference"


def deterministic_test_private_key(label: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(("TEA-Sim deterministic test key only: " + label).encode("utf-8")).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def fixture_emitter_private_key() -> Ed25519PrivateKey:
    return deterministic_test_private_key("emitter-v1")


def fixture_backend_private_key() -> Ed25519PrivateKey:
    return deterministic_test_private_key("backend-v1")
