#!/usr/bin/env python3
from __future__ import annotations

import csv
from release_common import (
    CHECKSUM_PATH, MANIFEST_PATH, ROOT, generator_for, media_type, relative,
    release_files, reproducibility_class_for, role_for, sha256, sources_for,
)


def main() -> int:
    rows = []
    for path in release_files(exclude={MANIFEST_PATH, CHECKSUM_PATH}):
        rel = relative(path)
        rows.append({
            "path": rel,
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "media_type": media_type(path),
            "role": role_for(rel),
            "generator": generator_for(rel),
            "source_inputs": sources_for(rel),
            "reproducibility_class": reproducibility_class_for(rel),
        })
    with (ROOT / MANIFEST_PATH).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE: {len(rows)} manifest rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
