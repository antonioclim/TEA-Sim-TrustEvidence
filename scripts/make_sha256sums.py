#!/usr/bin/env python3
from __future__ import annotations

from release_common import CHECKSUM_PATH, ROOT, relative, release_files, sha256


def main() -> int:
    rows = [(relative(path), sha256(path)) for path in release_files(exclude={CHECKSUM_PATH})]
    (ROOT / CHECKSUM_PATH).write_text("".join(f"{digest}  {path}\n" for path, digest in rows), encoding="utf-8")
    print(f"WROTE: {len(rows)} checksum rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
