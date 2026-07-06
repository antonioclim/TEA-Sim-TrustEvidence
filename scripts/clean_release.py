#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil
RUNTIME={"__pycache__",".pytest_cache",".hypothesis",".mypy_cache",".ruff_cache",".tox","node_modules"}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root', default='.'); args=ap.parse_args(); root=Path(args.root).resolve(); removed=[]
    for p in sorted(root.rglob('*'), key=lambda x: len(x.parts), reverse=True):
        if p.is_dir() and (p.name in RUNTIME or p.name.endswith('.egg-info')):
            shutil.rmtree(p, ignore_errors=True); removed.append(str(p.relative_to(root)))
    for p in list(root.rglob('*')):
        if p.is_file() and (p.suffix in {'.pyc','.pyo'} or p.name in {'.DS_Store','Thumbs.db'}):
            p.unlink(missing_ok=True); removed.append(str(p.relative_to(root)))
    print(f'cleaned_runtime_items={len(removed)}')
if __name__=='__main__': main()
