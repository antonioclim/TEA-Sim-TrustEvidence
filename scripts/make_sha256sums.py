#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib
EXCLUDE_NAMES={'SHA256SUMS.txt'}
EXCLUDE_PARTS={'.git','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','node_modules','validation'}
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--output', default='SHA256SUMS.txt'); args=ap.parse_args(); root=Path(args.root).resolve(); rows=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if p.name in EXCLUDE_NAMES or any(part in EXCLUDE_PARTS for part in rel.parts): continue
        rows.append(f'{digest(p)}  {rel.as_posix()}')
    (root/args.output).write_text('\n'.join(rows)+'\n', encoding='utf-8')
    print(f'wrote {len(rows)} checksum rows to {root/args.output}')
if __name__=='__main__': main()
