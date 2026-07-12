#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IGNORED_DIRS={'.git','.venv','venv','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','.tox','.nox','build','dist','htmlcov','results_local','local_outputs','node_modules'}
def ignored(rel): return any(part in IGNORED_DIRS or part.endswith('.egg-info') for part in rel.parts) or rel.suffix in {'.pyc','.pyo'} or rel.name in {'.DS_Store','Thumbs.db','.coverage'}
def h(p):
    x=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): x.update(b)
    return x.hexdigest()
arg=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'SHA256SUMS.txt'
sums=arg if arg.is_absolute() else ROOT/arg
rows=[]; errors=[]; seen=set()
for line in sums.read_text(encoding='utf-8').splitlines():
    if not line.strip(): continue
    m=line.split(None,1)
    if len(m)!=2: errors.append('malformed: '+line); continue
    digest, rel=m[0].lower(),m[1].lstrip('* ').replace('\\','/')
    if rel in seen: errors.append('duplicate: '+rel); continue
    seen.add(rel); p=ROOT/rel
    if not p.is_file(): errors.append('missing: '+rel); continue
    if h(p)!=digest: errors.append('sha256: '+rel)
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not ignored(p.relative_to(ROOT)) and p.name!='SHA256SUMS.txt'}
for rel in sorted(actual-seen): errors.append('unlisted: '+rel)
for rel in sorted(seen-actual): errors.append('listed-but-not-distributed: '+rel)
if errors: raise SystemExit('SHA256SUMS: FAIL\n'+'\n'.join(errors))
print(f'SHA256SUMS: PASS ({len(seen)} entries)')
