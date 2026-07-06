#!/usr/bin/env python3
"""Create a compact manifest of release files."""
from __future__ import annotations

import argparse
from pathlib import Path

EXCLUDE_NAMES = {"SHA256SUMS.txt", "OUTPUT_MANIFEST.md"}
EXCLUDE_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".hypothesis",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "validation",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="OUTPUT_MANIFEST.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rows: list[tuple[str, int]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if path.name in EXCLUDE_NAMES:
            continue
        if any(part in EXCLUDE_PARTS for part in rel.parts):
            continue
        rows.append((rel.as_posix(), path.stat().st_size))

    lines = ["# Output manifest", "", f"Total files listed: {len(rows)}", ""]
    lines.extend(f"- `{rel}` ({size} bytes)" for rel, size in rows)
    (root / args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} manifest rows to {root / args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
