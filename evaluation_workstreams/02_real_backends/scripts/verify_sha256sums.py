from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()
    root = Path.cwd()
    failures = []
    checked = 0
    for line in Path(args.manifest).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, rel = line.split(None, 1)
        except ValueError:
            failures.append(f"malformed line: {line}")
            continue
        rel = rel.strip()
        if rel.startswith("*"):
            rel = rel[1:]
        path = root / rel
        if not path.exists():
            failures.append(f"missing: {rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checked += 1
        if actual != expected:
            failures.append(f"mismatch: {rel}")
    if failures:
        for item in failures:
            print(item)
        return 1
    print(f"sha256 verification passed for {checked} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
