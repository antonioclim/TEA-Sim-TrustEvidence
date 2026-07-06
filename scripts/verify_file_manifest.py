#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--manifest', default='FILE_MANIFEST.tsv')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    rows = list(csv.DictReader((root / args.manifest).open(encoding='utf-8'), delimiter='	'))
    failures = []
    seen = set()
    for row in rows:
        rel = row.get('path', '')
        if not rel:
            failures.append('empty-path')
            continue
        if rel in seen:
            failures.append('duplicate:' + rel)
        seen.add(rel)
        path = root / rel
        if not path.exists():
            failures.append('missing:' + rel)
            continue
        if path.is_file() and str(path.stat().st_size) != row.get('size_bytes', ''):
            failures.append('size:' + rel)
    if failures:
        print('FILE_MANIFEST verify: FAIL')
        for failure in failures[:200]:
            print(failure)
        return 1
    print('FILE_MANIFEST verify: PASS')
    print(f'checked={len(rows)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
