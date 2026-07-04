#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path
results = Path(__file__).resolve().parents[2] / "results"
measurement_files = [
    "raw_write_measurements.csv", "proof_measurements.csv", "storage_snapshots.csv",
    "audit_query_measurements.csv", "statistical_summary.csv", "run_summary.csv",
]
rows = 0
for name in measurement_files:
    p = results / name
    if not p.exists():
        continue
    with p.open(newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        next(reader, None)
        rows += sum(1 for _ in reader)
if rows == 0:
    raise SystemExit("Figure 06 is requires external validation: no  validated measurement rows are available.")
raise SystemExit("Figure 06 production plotting must be finalised after  schema-valid measurement rows are returned.")
