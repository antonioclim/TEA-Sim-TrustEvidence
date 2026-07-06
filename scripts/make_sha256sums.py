#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib
EXCLUDE_NAMES={'SHA256SUMS.txt','FILE_MANIFEST.tsv'}
EXCLUDE_PARTS={'.git','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','node_modules'}
EXCLUDE_TOPLEVEL={'validation','results','dist','build'}
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()
def include(p, root):
    rel=p.relative_to(root)
    return p.is_file() and p.name not in EXCLUDE_NAMES and not any(part in EXCLUDE_PARTS for part in rel.parts) and (not rel.parts or rel.parts[0] not in EXCLUDE_TOPLEVEL)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--output', default='SHA256SUMS.txt'); args=ap.parse_args(); root=Path(args.root).resolve(); rows=[]
    for p in sorted(root.rglob('*')):
        if include(p, root):
            rows.append(f'{digest(p)}  {p.relative_to(root).as_posix()}')
    (root/args.output).write_text('\n'.join(rows)+'\n', encoding='utf-8')
    print(f'wrote {len(rows)} checksum rows to {root/args.output}')
if __name__=='__main__': main()
