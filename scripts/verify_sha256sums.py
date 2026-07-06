#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, sys
def digest(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()
def main() -> int:
    ap=argparse.ArgumentParser(description='Verify a standard sha256sum manifest.')
    ap.add_argument('manifest_positional', nargs='?', help='Manifest path, equivalent to --manifest')
    ap.add_argument('--root', default='.')
    ap.add_argument('--manifest', default=None)
    args=ap.parse_args()
    root=Path(args.root).resolve()
    manifest=Path(args.manifest or args.manifest_positional or 'SHA256SUMS.txt')
    if not manifest.is_absolute():
        manifest=root/manifest
    failures=[]; checked=0
    for lineno,line in enumerate(manifest.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():
            continue
        parts=line.split(None,1)
        if len(parts)!=2:
            failures.append(f'bad-line:{lineno}')
            continue
        want, rel=parts[0], parts[1].strip()
        p=root/rel
        if not p.exists():
            failures.append(f'missing:{rel}')
            continue
        got=digest(p); checked += 1
        if got != want:
            failures.append(f'mismatch:{rel}')
    if failures:
        print('SHA256SUMS verify: FAIL')
        print('\n'.join(failures[:300]))
        return 1
    print('SHA256SUMS verify: PASS')
    print(f'checked={checked}')
    return 0
if __name__=='__main__': raise SystemExit(main())
