from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import httpx
import yaml

from trustevidence.harness.replay_workload import replay_local
from trustevidence.harness.workload import load_jsonl


def _compose_parse(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, dict) or "services" not in doc:
        raise RuntimeError("docker-compose.full.yml has no services block")
    return doc


def dry_run(workload: Path, compose: Path) -> int:
    rows = load_jsonl(workload)
    doc = _compose_parse(compose)
    receipts = replay_local(rows)
    summary = {
        "mode": "dry-run",
        "workload_rows": len(rows),
        "compose_services": sorted(doc["services"].keys()),
        "receipt_rows": len(receipts),
        "docker_available": shutil.which("docker") is not None,
        "status": "PASS",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def external_run(workload: Path, hapi_base: str) -> int:
    if shutil.which("docker") is None:
        raise SystemExit("docker not found; external v2.0.0 smoke cannot execute in this environment")
    with httpx.Client(timeout=10.0) as client:
        r = client.get(hapi_base.rstrip("/") + "/metadata", headers={"Accept": "application/fhir+json"})
        r.raise_for_status()
    # The full external smoke is intentionally orchestrated by Make and scripts so
    # service logs can be captured under validation/ by the external validator.
    rows = load_jsonl(workload)
    print(json.dumps({"mode": "external", "workload_rows": len(rows), "hapi_metadata": "PASS"}, indent=2))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="v2.0.0 smoke harness")
    parser.add_argument("--workload", default="data/workloads/W_SMOKE_AUDITEVENT.jsonl")
    parser.add_argument("--compose", default="docker-compose.full.yml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--external", action="store_true")
    parser.add_argument("--hapi-base", default="http://localhost:8080/fhir")
    args = parser.parse_args(argv)
    if args.external:
        return external_run(Path(args.workload), args.hapi_base)
    return dry_run(Path(args.workload), Path(args.compose))


if __name__ == "__main__":
    raise SystemExit(main())
