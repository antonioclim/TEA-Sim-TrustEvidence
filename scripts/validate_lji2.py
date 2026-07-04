#!/usr/bin/env python3
from pathlib import Path
import csv, sys
root=Path(__file__).resolve().parents[1]
expected={'tables/lji2_criteria.csv':14,'tables/lji2_axioms.csv':9,'tables/lji2_screening_rules.csv':7,'tables/lji2_wuest_gervais_refinement.csv':8,'tables/lji2_sensitivity_plan.csv':12,'tables/lji1_retirement_bridge.csv':8,'tables/delphi_panel_criteria.csv':4,'tables/delphi_round_plan.csv':4}
for rel,n in expected.items():
    with (root/rel).open(newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    if len(rows)!=n: print(f'FAIL {rel}: expected {n}, got {len(rows)}'); sys.exit(1)
print('LJI 2.0 validation: PASS')
