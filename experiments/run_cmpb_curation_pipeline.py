#!/usr/bin/env python3
"""Run the integrated quick or full local evidence pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = (args.output_dir or (ROOT / "results_local" / ("quick" if args.quick else "full"))).resolve()
    output.mkdir(parents=True, exist_ok=True)

    deterministic = output / "deterministic"
    run([sys.executable, str(ROOT / "experiments/run_schema_validation.py"), "--output-dir", str(deterministic)])
    run([sys.executable, str(ROOT / "experiments/run_canonicalisation_tests.py"), "--output-dir", str(deterministic)])
    run([sys.executable, str(ROOT / "experiments/run_mutation_tests.py"), "--output-dir", str(deterministic)])

    workload_command = [
        sys.executable,
        str(ROOT / "experiments/run_workload_passage.py"),
        "--output-dir",
        str(output),
    ]
    if args.quick:
        workload_command.append("--quick")
    run(workload_command)
    run([
        sys.executable,
        str(ROOT / "experiments/analyse_cmpb_results.py"),
        "--input-dir",
        str(output),
        "--output-dir",
        str(output),
    ])
    print(json.dumps({"pipeline": "PASS", "quick": args.quick, "output_dir": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
