#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {'.git','.venv','venv','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','.tox','.nox','build','dist','htmlcov','results_local','local_outputs','node_modules'}

def ignored(rel: Path) -> bool:
    return any(part in IGNORED_DIRS or part.endswith('.egg-info') for part in rel.parts) or rel.suffix in {'.pyc','.pyo'} or rel.name in {'.DS_Store','Thumbs.db','.coverage'}
def h(p):
    x=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): x.update(b)
    return x.hexdigest()

arg = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'FILE_MANIFEST.tsv'
manifest = arg if arg.is_absolute() else ROOT/arg
with manifest.open(encoding='utf-8', newline='') as f:
    rows=list(csv.DictReader(f, delimiter='\t'))
if not rows: raise SystemExit('Manifest has no rows')
keys=set(rows[0])
def pick(*names):
    for n in names:
        if n in keys: return n
    raise SystemExit(f'Missing manifest column; found {sorted(keys)}')
pcol=pick('path','relative_path','file','filename')
scol=pick('size_bytes','bytes','size')
hcol=pick('sha256','sha256_hex','hash')
seen=set(); errors=[]
for row in rows:
    rel=row[pcol].replace('\\','/')
    if rel in seen: errors.append(f'duplicate row: {rel}'); continue
    seen.add(rel); p=ROOT/rel
    if not p.is_file(): errors.append(f'missing: {rel}'); continue
    if p.stat().st_size != int(row[scol]): errors.append(f'size: {rel}')
    if h(p).lower() != row[hcol].strip().lower(): errors.append(f'sha256: {rel}')
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not ignored(p.relative_to(ROOT)) and p.name not in {'FILE_MANIFEST.tsv','SHA256SUMS.txt'}}
for rel in sorted(actual-seen): errors.append(f'unlisted: {rel}')
for rel in sorted(seen-actual): errors.append(f'listed-but-not-distributed: {rel}')
if errors: raise SystemExit('FILE-MANIFEST: FAIL\n'+'\n'.join(errors))
print(f'FILE-MANIFEST: PASS ({len(rows)} rows)')
