#!/usr/bin/env python3
"""Run unit, Hypothesis, and bounded checks and emit machine-readable summaries."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "cmpb-property-checks-001"

PROPERTY_TESTS = {
    "property_tests/test_envelope_properties.py::test_canonicalisation_is_deterministic_under_recursive_key_reordering": (
        "P4", 100, "canonicalisation determinism"
    ),
    "property_tests/test_envelope_properties.py::test_payload_commitment_binds_withheld_material_but_evidence_verification_needs_neither": (
        "P6", 100, "payload non-disclosure under evidence-only verification"
    ),
    "property_tests/test_merkle_properties.py::test_append_monotonicity_and_prefix_roots": (
        "P1", 80, "append monotonicity"
    ),
    "property_tests/test_merkle_properties.py::test_inclusion_soundness_and_path_mutation_rejection": (
        "P2", 80, "inclusion soundness"
    ),
    "property_tests/test_merkle_properties.py::test_consistency_soundness_and_mutation_rejection": (
        "P8", 80, "prefix consistency"
    ),
    "property_tests/test_merkle_properties.py::test_receipt_binding_rejects_resigned_coherent_looking_mutations": (
        "P5", 80, "receipt binding"
    ),
    "property_tests/test_merkle_properties.py::test_same_size_root_comparison_detects_verifier_visible_fork": (
        "P7", 80, "same-size verifier-visible fork comparison"
    ),
    "property_tests/test_merkle_properties.py::test_larger_checkpoint_requires_and_accepts_valid_consistency_proof": (
        "P8", 80, "retained-checkpoint extension verification"
    ),
}


def run_command(command: list[str], log_path: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["HYPOTHESIS_STORAGE_DIRECTORY"] = str(log_path.parent / "hypothesis-storage")
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(completed.stdout, encoding="utf-8")
    return completed


def parse_pytest_pass_count(text: str) -> int:
    match = re.search(r"(\d+) passed(?:,| in)", text)
    return int(match.group(1)) if match else 0


def property_sections(text: str) -> dict[str, str]:
    marker = "Hypothesis Statistics"
    if marker not in text:
        return {}
    tail = text.split(marker, 1)[1]
    starts = list(re.finditer(r"(?m)^(property_tests/[^\n]+::[^\n]+):\n", tail))
    sections: dict[str, str] = {}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(tail)
        sections[match.group(1)] = tail[match.end():end]
    return sections


def parse_examples(section: str, label: str) -> int:
    return sum(int(value) for value in re.findall(rf"(\d+) {label} examples", section))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results_expected/cmpb_reference/property_checks",
    )
    parser.add_argument("--log-dir", type=Path, default=ROOT / "results_local/property_logs")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    logs = args.log_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    unit = run_command(
        [sys.executable, "-m", "pytest", "tests", "-p", "no:cacheprovider"],
        logs / "unit_tests.log",
    )
    properties = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "property_tests",
            "--hypothesis-show-statistics",
            "-p",
            "no:cacheprovider",
        ],
        logs / "property_tests.log",
    )
    bounded = run_command(
        [
            sys.executable,
            "bounded_model/bounded_model_check.py",
            "--output-dir",
            str(output),
        ],
        logs / "bounded_model.log",
    )

    sections = property_sections(properties.stdout)
    rows = []
    for test_id, (property_id, declared_examples, property_name) in PROPERTY_TESTS.items():
        section = sections.get(test_id, "")
        passing = parse_examples(section, "passing")
        failing = parse_examples(section, "failing")
        invalid = parse_examples(section, "invalid")
        rows.append({
            "run_id": RUN_ID,
            "test_id": test_id,
            "property_id": property_id,
            "property_name": property_name,
            "declared_max_examples": declared_examples,
            "passing_examples_reported": passing,
            "failing_examples_reported": failing,
            "invalid_draws_reported": invalid,
            "status": "PASS" if properties.returncode == 0 and passing == declared_examples and failing == 0 else "FAIL",
            "scope": "deterministic Hypothesis generation with database=None and derandomize=True; finite generated examples, not proof",
        })
    with (output / "property_test_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    bounded_summary = json.loads((output / "bounded_model_summary.json").read_text(encoding="utf-8")) if (output / "bounded_model_summary.json").exists() else {}
    facts = {
        "run_id": RUN_ID,
        "software_version": version("teasim-trustevidence"),
        "python_version": sys.version.split()[0],
        "pytest_version": version("pytest"),
        "hypothesis_version": version("hypothesis"),
        "rfc8785_version": version("rfc8785"),
        "unit_test_exit_code": unit.returncode,
        "unit_tests_passed": parse_pytest_pass_count(unit.stdout),
        "property_test_exit_code": properties.returncode,
        "property_tests_passed": parse_pytest_pass_count(properties.stdout),
        "declared_property_examples": sum(item[1] for item in PROPERTY_TESTS.values()),
        "reported_property_passing_examples": sum(int(row["passing_examples_reported"]) for row in rows),
        "reported_property_failing_examples": sum(int(row["failing_examples_reported"]) for row in rows),
        "bounded_model_exit_code": bounded.returncode,
        "bounded_checks_executed": bounded_summary.get("checks_executed", 0),
        "bounded_failures": bounded_summary.get("failures", -1),
        "duplicate_leaf_index_ambiguity_observed": bounded_summary.get("duplicate_leaf_index_ambiguity_observed"),
        "settings": {
            "database": None,
            "derandomize": True,
            "deadline": None,
            "cache_provider": "disabled",
        },
        "claim_boundary": "property-based and finite bounded executable checks; no unbounded theorem, mechanised proof, operational security guarantee, or global non-equivocation result",
    }
    (output / "property_test_run.json").write_text(
        json.dumps(facts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    overall = (
        unit.returncode == 0
        and properties.returncode == 0
        and bounded.returncode == 0
        and all(row["status"] == "PASS" for row in rows)
        and facts["bounded_failures"] == 0
    )
    print(json.dumps({"run_id": RUN_ID, "status": "PASS" if overall else "FAIL", **facts}, sort_keys=True))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
