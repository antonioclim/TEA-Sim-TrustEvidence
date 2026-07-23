#!/usr/bin/env python3
"""Validate retained CSV result rows against the public Draft 2020-12 contracts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results_expected" / "cmpb_reference"
SCHEMAS = ROOT / "schemas" / "results"
CONTRACTS = [
    ("schema_validation_summary.csv", "schema_validation_summary.schema.json"),
    ("field_deletion_results.csv", "field_deletion_results.schema.json"),
    ("competency_question_results.csv", "competency_question_results.schema.json"),
    ("canonicalisation_determinism.csv", "canonicalisation_determinism.schema.json"),
    ("mutation_test_results.csv", "mutation_test_results.schema.json"),
    (
        "c4_hie_security/hie_security_mutation_results.csv",
        "mutation_test_results.schema.json",
    ),
    ("property_test_summary.csv", "property_test_summary.schema.json"),
    ("bounded_model_summary.csv", "bounded_model_summary.schema.json"),
    ("workload_passage_summary.csv", "workload_passage_summary.schema.json"),
    ("receipt_size_summary.csv", "receipt_size_summary.schema.json"),
    (
        "c5_hie_overhead/retained_runs.csv",
        "hie_overhead_run.schema.json",
    ),
    (
        "c5_hie_overhead/paired_increments.csv",
        "hie_overhead_pair.schema.json",
    ),
    (
        "c5_hie_overhead/aggregate_estimates.csv",
        "hie_overhead_aggregate.schema.json",
    ),
    ("reproducibility_manifest.csv", "reproducibility_manifest.schema.json"),
]


def main() -> int:
    errors: list[str] = []
    validated = 0
    for csv_name, schema_name in CONTRACTS:
        csv_path = RESULTS / csv_name
        schema_path = SCHEMAS / schema_name
        if not csv_path.is_file() or not schema_path.is_file():
            errors.append(f"missing contract pair: {csv_name} / {schema_name}")
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            errors.append(f"no rows: {csv_name}")
            continue
        for index, row in enumerate(rows, 2):
            row_errors = sorted(validator.iter_errors(row), key=lambda item: list(item.path))
            for error in row_errors:
                errors.append(f"{csv_name}:{index}: {error.message}")
            validated += 1
    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(CONTRACTS)} result contracts and {validated} parsed CSV rows validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
