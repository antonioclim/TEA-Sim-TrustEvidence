from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from typing import Any

from trustevidence.adapters.common import CommandResult, CommandRunner, envelope_digest_b64, now_z, signed_receipt
from trustevidence.canonical import core_hash_b64
from trustevidence.errors import UNAVAILABLE_PROOF, TrustEvidenceError


class SubprocessRunner:
    def run(self, args: list[str], *, timeout: int = 60) -> CommandResult:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return CommandResult(args=args, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def _parse_tx_id(text: str) -> str | None:
    patterns = [r"txid[:=]\s*([A-Za-z0-9._:-]+)", r"transaction ID[:=]\s*([A-Za-z0-9._:-]+)"]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1)
    return None


@dataclass(slots=True)
class FabricCliAdapter:
    """Adapter that invokes the Fabric peer CLI inside the Fabric test network.

    This is deliberately a wire-level adapter over Fabric's native toolchain. It
    does not assume a mature Python Fabric SDK. The default command expects a
    `fabric-cli` container created by docker-compose.full.yml and a chaincode
    named `trustevidence` exposing `PutEvidence` and `ReadEvidence`.
    """

    backend_id: str
    signer: Any
    channel_name: str = "te-channel"
    chaincode_name: str = "trustevidence"
    cli_container: str = "fabric-cli"
    runner: CommandRunner | None = None
    alg_id: str = "sha256-te-v2"
    timeout_s: int = 120

    @property
    def log_id(self) -> str:
        return f"fabric:{self.channel_name}:{self.chaincode_name}"

    def _invoke_args(self, artefact_id: str, event_id: str, core_hash: str, envelope_hash: str) -> list[str]:
        payload = {"Args": ["PutEvidence", artefact_id, event_id, core_hash, envelope_hash]}
        return [
            "docker", "exec", self.cli_container,
            "peer", "chaincode", "invoke",
            "-C", self.channel_name,
            "-n", self.chaincode_name,
            "-c", json.dumps(payload, separators=(",", ":")),
        ]

    def append(self, envelope: dict[str, Any]) -> dict[str, Any]:
        core = envelope["artefact_core"]
        artefact_id = core["artefact_id"]
        event_id = core["event_id"]
        core_hash = core_hash_b64(core, self.alg_id)
        envelope_hash = envelope_digest_b64(envelope)
        runner = self.runner or SubprocessRunner()
        result = runner.run(self._invoke_args(artefact_id, event_id, core_hash, envelope_hash), timeout=self.timeout_s)
        if result.returncode != 0:
            raise TrustEvidenceError(UNAVAILABLE_PROOF, f"Fabric invoke failed: {result.stderr or result.stdout}")
        tx_id = _parse_tx_id(result.stdout + "\n" + result.stderr) or f"unparsed-{envelope_hash[:16]}"
        receipt = {
            "backend_type": "fabric",
            "backend_id": self.backend_id,
            "log_id": self.log_id,
            "alg_id": self.alg_id,
            "core_hash": core_hash,
            "inclusion_proof_ref": f"urn:te:fabric:query:{self.channel_name}:{self.chaincode_name}:{artefact_id}",
            "finality_ref": f"urn:te:fabric:tx:{tx_id}",
            "issued_at": now_z(),
            "signer_id": self.signer.key_id,
        }
        out = dict(envelope)
        out["backend_receipt"] = signed_receipt(receipt, self.signer)
        return out
