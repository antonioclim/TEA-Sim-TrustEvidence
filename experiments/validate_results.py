from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', default='results')
    args = parser.parse_args()
    results_dir = Path(args.results_dir)
    errors: list[str] = []
    for schema_path in sorted((ROOT / 'schemas/results').glob('*.schema.json')):
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
        path = results_dir / schema['file']
        if not path.exists():
            errors.append(f'missing {path}')
            continue
        with path.open(newline='', encoding='utf-8') as f:
            header = next(csv.reader(f), [])
        if header != schema['required_columns']:
            errors.append(f'header mismatch {path}')
    if errors:
        print('Result schema validation: FAIL')
        for error in errors:
            print('- ' + error)
        return 1
    print('Result schema validation: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
