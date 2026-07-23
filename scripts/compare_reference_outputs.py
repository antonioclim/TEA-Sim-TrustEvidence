#!/usr/bin/env python3
"""Regenerate deterministic outputs and check workload semantic invariants."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "results_expected" / "cmpb_reference"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        print(result.stdout)
        raise SystemExit(result.returncode)


def main() -> int:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="teasim-compare-") as tmp_text:
        tmp = Path(tmp_text)
        deterministic = tmp / "deterministic"
        run([sys.executable, str(ROOT / "experiments/run_schema_validation.py"), "--output-dir", str(deterministic)])
        run([sys.executable, str(ROOT / "experiments/run_canonicalisation_tests.py"), "--output-dir", str(deterministic)])
        run([sys.executable, str(ROOT / "experiments/run_mutation_tests.py"), "--output-dir", str(deterministic)])
        comparisons = [
            "schema_validation_summary.csv", "field_deletion_results.csv", "competency_question_results.csv",
            "canonicalisation_determinism.csv", "canonicalisation_test_run.json",
            "mutation_test_results.csv", "mutation_test_run.json",
        ]
        for name in comparisons:
            if not (deterministic / name).is_file() or sha256(deterministic / name) != sha256(REFERENCE / name):
                errors.append(f"deterministic mismatch: {name}")

        c4 = tmp / "c4_hie_security"
        run([
            sys.executable,
            str(ROOT / "experiments/run_hie_security_mutations.py"),
            "--output-dir",
            str(c4),
        ])
        for name in (
            "hie_security_mutation_results.csv",
            "hie_security_mutation_run.json",
            "hie_security_case_evidence.jsonl",
        ):
            retained = REFERENCE / "c4_hie_security" / name
            if not (c4 / name).is_file() or not retained.is_file() or sha256(c4 / name) != sha256(retained):
                errors.append(f"deterministic mismatch: c4_hie_security/{name}")

        quick1 = tmp / "quick1"
        quick2 = tmp / "quick2"
        run([sys.executable, str(ROOT / "experiments/run_workload_passage.py"), "--quick", "--output-dir", str(quick1)])
        run([sys.executable, str(ROOT / "experiments/run_workload_passage.py"), "--quick", "--output-dir", str(quick2)])
        for directory in (quick1, quick2):
            meta = json.loads((directory / "run_metadata.json").read_text(encoding="utf-8"))
            if meta["validation_failures"] or meta["ordinary_verification_failures"] or meta["mutation_cases"] != meta["mutation_rejections"]:
                errors.append(f"quick workload decision failure: {directory.name}")
        events1 = [json.loads(line) for line in (quick1 / "raw_runs/workload_events.jsonl").read_text().splitlines()]
        events2 = [json.loads(line) for line in (quick2 / "raw_runs/workload_events.jsonl").read_text().splitlines()]
        if events1 != events2:
            errors.append("quick workload event identities/digests are not deterministic")
        sizes1 = list(csv.DictReader((quick1 / "receipt_size_summary.csv").open(newline="", encoding="utf-8")))
        sizes2 = list(csv.DictReader((quick2 / "receipt_size_summary.csv").open(newline="", encoding="utf-8")))
        if sizes1 != sizes2:
            errors.append("quick receipt/proof sizes are not deterministic")

    meta = json.loads((REFERENCE / "run_metadata.json").read_text(encoding="utf-8"))
    if meta.get("total_events") != 32256 or meta.get("successful_receipt_checks") != 1152:
        errors.append("retained full workload counts differ from protocol")
    if meta.get("validation_failures") != 0 or meta.get("ordinary_verification_failures") != 0:
        errors.append("retained full workload has validation or ordinary verification failures")
    if meta.get("mutation_cases") != 36 or meta.get("mutation_rejections") != 36:
        errors.append("retained deep-mutation decisions differ from protocol")

    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1
    print("PASS: deterministic outputs and workload semantic invariants verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
