from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def version(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
        return p.stdout.strip().splitlines()[0] if p.stdout.strip() else f"exit={p.returncode}"
    except Exception as exc:
        return f"unavailable: {exc.__class__.__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="benchmark_outputs/probes/postgres_probe.json")
    parser.add_argument("--dsn-env", default="TEA_POSTGRES_DSN")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    docker = shutil.which("docker")
    psql = shutil.which("psql")
    dsn_present = bool(os.environ.get(args.dsn_env))
    psycopg = importlib.util.find_spec("psycopg") is not None
    psycopg2 = importlib.util.find_spec("psycopg2") is not None

    status = {
        "backend": "A1_POSTGRES",
        "docker_path": docker,
        "docker_version": version([docker, "--version"]) if docker else "not found",
        "psql_path": psql,
        "psql_version": version([psql, "--version"]) if psql else "not found",
        "dsn_env_name": args.dsn_env,
        "dsn_present": dsn_present,
        "dsn_value_recorded": False,
        "python_driver_psycopg_available": psycopg,
        "python_driver_psycopg2_available": psycopg2,
        "execution_status": "not_executed",
        "reason": "Docker, psql or explicit local DSN unavailable" if not dsn_present else "DSN present; connection deliberately not attempted by probe without maintainer-run command",
        "allowable_public_wording": "PostgreSQL schema and adapter were prepared, but PostgreSQL execution was unavailable in the recorded runtime.",
        "forbidden_wording": "PostgreSQL measured benchmark; production database performance; PostgreSQL validation passed",
    }
    out.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
