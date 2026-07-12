#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IGNORED_DIRS={'.git','.venv','venv','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','.tox','.nox','build','dist','htmlcov','results_local','local_outputs','node_modules'}
def ignored(rel): return any(part in IGNORED_DIRS or part.endswith('.egg-info') for part in rel.parts) or rel.suffix in {'.pyc','.pyo'} or rel.name in {'.DS_Store','Thumbs.db','.coverage'}
def files(): return sorted([p for p in ROOT.rglob('*') if p.is_file() and not ignored(p.relative_to(ROOT))], key=lambda p:p.relative_to(ROOT).as_posix())
def h(p):
    x=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): x.update(b)
    return x.hexdigest()
def role(rel):
    if rel.startswith('src/'): return 'source'
    if rel.startswith('tests/') or rel.startswith('property_tests/'): return 'test'
    if rel.startswith('results_expected/'): return 'retained_result'
    if rel.startswith('figures/'): return 'figure'
    if rel.startswith('docs/'): return 'documentation'
    if rel.startswith('scripts/'): return 'script'
    return 'repository'
base=[p for p in files() if p.name not in {'FILE_MANIFEST.tsv','SHA256SUMS.txt'}]
with (ROOT/'FILE_MANIFEST.tsv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','size_bytes','sha256','role'],delimiter='\t',lineterminator='\n')
    w.writeheader()
    for p in base:
        rel=p.relative_to(ROOT).as_posix(); w.writerow({'path':rel,'size_bytes':p.stat().st_size,'sha256':h(p),'role':role(rel)})
sha_files=[p for p in files() if p.name!='SHA256SUMS.txt']
(ROOT/'SHA256SUMS.txt').write_text(''.join(f'{h(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in sha_files),encoding='utf-8',newline='\n')
print(f'INTEGRITY-REBUILD: PASS ({len(base)} manifest rows; {len(sha_files)} checksums)')
