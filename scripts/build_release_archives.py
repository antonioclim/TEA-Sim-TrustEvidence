#!/usr/bin/env python3
"""Build the single deterministic public v2.1.0 release asset."""

from __future__ import annotations

import argparse
import hashlib
import stat
import zipfile
from pathlib import Path

from release_common import EXPECTED_ROOT, relative, release_files

FIXED_TIME = (1980, 1, 1, 0, 0, 0)
ASSET_NAME = "TEA-Sim-TrustEvidence-v2.1.0.zip"
SHA_NAME = "TEA-Sim-TrustEvidence-v2.1.0.sha256"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def build(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        root_info = zipfile.ZipInfo(EXPECTED_ROOT + "/", FIXED_TIME)
        root_info.create_system = 3
        root_info.external_attr = (stat.S_IFDIR | 0o755) << 16
        archive.writestr(root_info, b"")
        directories: set[str] = set()
        for path in release_files():
            rel = relative(path)
            current = EXPECTED_ROOT
            for part in rel.split("/")[:-1]:
                current += "/" + part
                directories.add(current + "/")
        for name in sorted(directories):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.create_system = 3
            info.external_attr = (stat.S_IFDIR | 0o755) << 16
            archive.writestr(info, b"")
        executable_prefixes = ("scripts/", "experiments/", "bounded_model/", "figures/scripts/", "tables/scripts/")
        for path in release_files():
            rel = relative(path)
            info = zipfile.ZipInfo(f"{EXPECTED_ROOT}/{rel}", FIXED_TIME)
            info.create_system = 3
            mode = 0o755 if path.suffix == ".sh" or (path.suffix == ".py" and rel.startswith(executable_prefixes)) else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    asset = args.output_dir / ASSET_NAME
    checksum = args.output_dir / SHA_NAME
    build(asset)
    digest = sha256(asset)
    checksum.write_text(f"{digest}  {ASSET_NAME}\n", encoding="utf-8", newline="\n")
    print(f"SHA256 {digest}")
    print(asset)
    print(checksum)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
