
from __future__ import annotations
import hashlib, sys
from pathlib import Path

def main() -> None:
    manifest = Path(sys.argv[1] if len(sys.argv) > 1 else 'SHA256SUMS.txt')
    base = manifest.parent
    ok = True; checked = 0
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip('*')
        if rel == manifest.name:
            continue
        path = base / rel
        if not path.exists():
            print(f'MISSING {rel}'); ok = False; continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            print(f'FAIL {rel}: {actual} != {digest}'); ok = False
        checked += 1
    print(f'checked {checked} files')
    if not ok:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
