#!/usr/bin/env python3
"""Generate or verify the retained result-level reproducibility manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import tempfile
from pathlib import Path

from release_common import ROOT, generator_for, reproducibility_class_for

RESULTS = ROOT / "results_expected" / "cmpb_reference"
OUTPUT = RESULTS / "reproducibility_manifest.csv"
FIELDS = ["path", "sha256", "evidence_class", "verification_status", "command_or_source"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def content() -> str:
    rows = []
    for path in sorted(RESULTS.rglob("*")):
        if not path.is_file() or path == OUTPUT:
            continue
        rel = path.relative_to(ROOT).as_posix()
        rows.append({
            "path": rel,
            "sha256": digest(path),
            "evidence_class": reproducibility_class_for(rel),
            "verification_status": "retained v2.1.0 reference output",
            "command_or_source": generator_for(rel),
        })
    with tempfile.TemporaryDirectory() as tmp:
        candidate = Path(tmp) / OUTPUT.name
        with candidate.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        return candidate.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = content()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("FAIL: reproducibility_manifest.csv is missing or stale")
            return 1
        print(f"PASS: reproducibility manifest is current ({expected.count(chr(10)) - 1} rows)")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"WROTE: reproducibility_manifest.csv ({expected.count(chr(10)) - 1} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
