import json
from pathlib import Path

import httpx
import yaml

from trustevidence.adapters.common import CommandResult
from trustevidence.adapters.fabric import FabricCliAdapter
from trustevidence.adapters.rekor import RekorClientAdapter
from trustevidence.adapters.trillian_personality import EvidenceTrillianPersonality
from trustevidence.crypto import DeterministicEd25519KeyPair
from trustevidence.envelope import signed_envelope
from trustevidence.harness.replay_workload import replay_local
from trustevidence.harness.workload import load_jsonl
from trustevidence.schema import EnvelopeValidator


class FakeRunner:
    def run(self, args, *, timeout=60):
        self.args = args
        return CommandResult(args=args, returncode=0, stdout="Chaincode invoke successful. txid: TX123", stderr="")


class FakeTrillianClient:
    def __init__(self):
        self.count = 0
    def queue_leaf(self, *, log_id, leaf_value):
        self.count += 1
        self.leaf_value = leaf_value
        return {"queued": True}
    def get_latest_signed_log_root(self, *, log_id):
        return {"tree_size": self.count, "root_hash": b"R" * 32}
    def get_inclusion_proof_by_hash(self, *, log_id, leaf_hash, tree_size):
        return {"proof": []}
    def get_consistency_proof(self, *, log_id, first_tree_size, second_tree_size):
        return {"proof": []}


def _pair(label="smoke"):
    return DeterministicEd25519KeyPair.from_label(f"urn:te:key:{label}", label)


def test_fabric_adapter_normalises_cli_receipt():
    emitter = _pair("emitter")
    backend = _pair("backend")
    env = signed_envelope("urn:te:event:fabric", "urn:te:artefact:fabric", emitter)
    adapter = FabricCliAdapter("urn:te:backend:fabric:test", backend, runner=FakeRunner())
    out = adapter.append(env)
    receipt = out["backend_receipt"]
    assert receipt["backend_type"] == "fabric"
    assert receipt["finality_ref"].endswith("TX123")
    EnvelopeValidator().validate(out)


def test_trillian_personality_receipt_shape_validates():
    emitter = _pair("emitter-trillian")
    backend = _pair("backend-trillian")
    env = signed_envelope("urn:te:event:trillian", "urn:te:artefact:trillian", emitter)
    adapter = EvidenceTrillianPersonality("urn:te:backend:trillian:test", 42, backend, FakeTrillianClient())
    out = adapter.append(env)
    receipt = out["backend_receipt"]
    assert receipt["backend_type"] == "trillian"
    assert receipt["tree_size"] == 1
    assert receipt["root_hash"]
    EnvelopeValidator().validate(out)


def test_rekor_adapter_parses_openapi_style_response(monkeypatch):
    emitter = _pair("emitter-rekor")
    backend = _pair("backend-rekor")
    env = signed_envelope("urn:te:event:rekor", "urn:te:artefact:rekor", emitter)
    payload = {
        "abc123": {
            "logIndex": 7,
            "verification": {"inclusionProof": {"treeSize": 8, "rootHash": "ab" * 32}, "signedEntryTimestamp": "AA"},
        }
    }

    def handler(request):
        assert request.url.path == "/api/v1/log/entries"
        return httpx.Response(201, json=payload)

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", client_factory)
    adapter = RekorClientAdapter("http://rekor.example", "urn:te:backend:rekor:test", backend)
    out = adapter.append(env)
    receipt = out["backend_receipt"]
    assert receipt["backend_type"] == "rekor"
    assert receipt["tree_size"] == 8
    assert receipt["leaf_index"] == 7
    assert receipt["inclusion_proof_ref"].endswith("abc123")
    EnvelopeValidator().validate(out)


def test_workload_replay_and_compose_parse():
    rows = load_jsonl("data/workloads/W_SMOKE_AUDITEVENT.jsonl")
    receipts = replay_local(rows)
    assert len(rows) == 5
    assert len(receipts) == 15
    with open("docker-compose.full.yml", "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    for service in ["hapi-fhir", "tea-a1-postgres", "trillian-log-server", "rekor-server", "fabric-cli"]:
        assert service in doc["services"]
