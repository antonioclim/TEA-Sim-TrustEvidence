#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--manifest', default='SHA256SUMS.txt'); args=ap.parse_args(); root=Path(args.root).resolve(); failures=[]; checked=0
    for line in (root/args.manifest).read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        want, rel=line.split(None, 1); p=root/rel.strip()
        if not p.exists(): failures.append(f'missing:{rel.strip()}'); continue
        got=digest(p); checked+=1
        if got != want: failures.append(f'mismatch:{rel.strip()}')
    if failures:
        print('SHA256SUMS verify: FAIL'); print('\n'.join(failures[:200])); return 1
    print('SHA256SUMS verify: PASS'); print(f'checked={checked}'); return 0
if __name__=='__main__': raise SystemExit(main())
