
from __future__ import annotations
from pathlib import Path
import hashlib, sys
root = Path.cwd()
manifest = root / sys.argv[1]
ok = True
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip(): continue
    expected, rel = line.split(None, 1)
    rel = rel.strip()
    p = root / rel
    h = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    if h != expected:
        print(f"FAIL {rel}: expected={expected} actual={h}")
        ok = False
if not ok: sys.exit(1)
print("PASS: SHA256SUMS")
