#!/usr/bin/env python3
from pathlib import Path
import csv
import sys

root = Path(__file__).resolve().parents[1]
path = root / 'tables' / 'legal_traceability_matrix.csv'
rows = list(csv.DictReader(path.open(encoding='utf-8')))
errors: list[str] = []
for row in rows:
    if '[INTERPRETATION]' not in row.get('derived_requirement', ''):
        errors.append(row.get('obligation_id', '?') + ' lacks interpretation tag')
    if not row.get('verification_test', '').startswith('TE-LEGAL-'):
        errors.append(row.get('obligation_id', '?') + ' lacks TE-LEGAL test id')
if len(rows) != 22:
    errors.append(f'expected 22 rows, found {len(rows)}')
if errors:
    print('Legal traceability validation: FAIL')
    for error in errors:
        print('- ' + error)
    sys.exit(1)
print('Legal traceability validation: PASS')
print(f'matrix_rows={len(rows)}')
