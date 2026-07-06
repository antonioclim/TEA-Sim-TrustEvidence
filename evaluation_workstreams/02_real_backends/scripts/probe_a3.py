from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def get_version(path: str | None, args: list[str]) -> str:
    if not path:
        return "not found"
    try:
        p = subprocess.run([path, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
        return p.stdout.strip().splitlines()[0] if p.stdout.strip() else f"exit={p.returncode}"
    except Exception as exc:
        return f"unavailable: {exc.__class__.__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="benchmark_outputs/probes/a3_probe.json")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    tools = {
        "docker": (shutil.which("docker"), ["--version"]),
        "rekor-cli": (shutil.which("rekor-cli"), ["version"]),
        "trillian_log_server": (shutil.which("trillian_log_server"), ["--help"]),
        "peer": (shutil.which("peer"), ["version"]),
        "go": (shutil.which("go"), ["version"]),
    }
    status = {
        "backend": "A3_TRANSPARENCY_LEDGER_LIKE",
        "tool_status": {name: {"path": path, "version_probe": get_version(path, ver_args)} for name, (path, ver_args) in tools.items()},
        "execution_status": "adapter_only_not_executed",
        "reason": "No local Rekor/Trillian/Fabric service pathway was available; Docker is required for the supplied container paths and was not found.",
        "public_service_submission": "not attempted; synthetic hash commitments only",
        "allowable_public_wording": "A3 remained an adapter/protocol artefact, not executed backend evidence.",
        "forbidden_wording": "local transparency-log execution; Fabric benchmark; blockchain benchmark; real-world deployment",
    }
    out.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
