from __future__ import annotations

import base64
import json
from typing import Any

from .canonical import canonical_bytes, sha256_hex


def build_synthetic_rekor_payload(obj: dict[str, Any]) -> dict[str, Any]:
    """Build a synthetic hash-commitment envelope suitable for local Rekor-style tests.

    This function does not submit to a public Rekor service and deliberately keeps
    clinical-like payloads out of external transparency infrastructure.
    """
    digest = sha256_hex(canonical_bytes(obj))
    return {
        "kind": "hashedrekord",
        "apiVersion": "0.0.1",
        "spec": {
            "data": {
                "hash": {
                    "algorithm": "sha256",
                    "value": digest,
                }
            },
            "signature": {
                "content": base64.b64encode(b"synthetic-local-signature-placeholder").decode("ascii"),
                "publicKey": {"content": base64.b64encode(b"synthetic-local-public-key-placeholder").decode("ascii")},
            },
        },
    }


def payload_json(obj: dict[str, Any]) -> str:
    return json.dumps(build_synthetic_rekor_payload(obj), sort_keys=True, indent=2)
