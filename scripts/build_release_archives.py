#!/usr/bin/env python3
"""Build the deterministic curated v2.2.0 final-release asset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import stat
import zipfile
from pathlib import Path

try:  # direct script execution and package import are both supported
    from .release_common import (
        ASSET_CHECKSUM_NAME,
        ASSET_NAME,
        CHECKSUM_PATH,
        EXPECTED_ROOT,
        MANIFEST_PATH,
        ROOT,
        public_release_files,
        relative,
        role_for,
        sha256_bytes,
    )
except ImportError:  # pragma: no cover - exercised by command-line execution
    from release_common import (
        ASSET_CHECKSUM_NAME,
        ASSET_NAME,
        CHECKSUM_PATH,
        EXPECTED_ROOT,
        MANIFEST_PATH,
        ROOT,
        public_release_files,
        relative,
        role_for,
        sha256_bytes,
    )

FIXED_TIME = (1980, 1, 1, 0, 0, 0)
EXECUTABLE_PREFIXES = (
    "scripts/",
    "experiments/",
    "bounded_model/",
    "figures/scripts/",
    "tables/scripts/",
)


class ReleaseBuildRefused(RuntimeError):
    """Raised when a published release version is immutable in this source state."""


def require_release_build_authorised() -> None:
    metadata = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    if metadata.get("release_asset_build_authorised") is not True:
        commit = metadata.get("immutable_release_commit_sha", "unknown")
        digest = metadata.get("canonical_asset_sha256", "unknown")
        raise ReleaseBuildRefused(
            "the v2.2.0 asset is immutable and may not be rebuilt from the "
            "post-release documentation state; use the published asset from "
            f"commit {commit} with SHA-256 {digest}, or create a new version"
        )


def archive_payload() -> dict[str, bytes]:
    """Return the public files plus archive-specific integrity catalogues."""

    payload = {
        relative(path): path.read_bytes()
        for path in public_release_files(exclude={MANIFEST_PATH, CHECKSUM_PATH})
    }

    manifest_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        manifest_buffer,
        fieldnames=["path", "size_bytes", "sha256", "role"],
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    for rel in sorted(payload):
        data = payload[rel]
        writer.writerow(
            {
                "path": rel,
                "size_bytes": len(data),
                "sha256": sha256_bytes(data),
                "role": role_for(rel),
            }
        )
    payload[MANIFEST_PATH] = manifest_buffer.getvalue().encode("utf-8")

    # SHA256SUMS covers every archived file except itself, including the
    # archive-specific FILE_MANIFEST.tsv.
    checksum_text = "".join(
        f"{sha256_bytes(payload[rel])}  {rel}\n" for rel in sorted(payload)
    )
    payload[CHECKSUM_PATH] = checksum_text.encode("utf-8")
    return payload


def build(destination: Path) -> str:
    require_release_build_authorised()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = archive_payload()
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        root_info = zipfile.ZipInfo(EXPECTED_ROOT + "/", FIXED_TIME)
        root_info.create_system = 3
        root_info.external_attr = (stat.S_IFDIR | 0o755) << 16
        archive.writestr(root_info, b"")

        directories: set[str] = set()
        for rel in payload:
            current = EXPECTED_ROOT
            for part in rel.split("/")[:-1]:
                current += "/" + part
                directories.add(current + "/")
        for name in sorted(directories):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.create_system = 3
            info.external_attr = (stat.S_IFDIR | 0o755) << 16
            archive.writestr(info, b"")

        for rel in sorted(payload):
            info = zipfile.ZipInfo(f"{EXPECTED_ROOT}/{rel}", FIXED_TIME)
            info.create_system = 3
            executable = rel.endswith(".sh") or (
                rel.endswith(".py") and rel.startswith(EXECUTABLE_PREFIXES)
            )
            mode = 0o755 if executable else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(
                info,
                payload[rel],
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

    return hashlib.sha256(destination.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    asset = args.output_dir / ASSET_NAME
    checksum = args.output_dir / ASSET_CHECKSUM_NAME
    try:
        digest = build(asset)
    except ReleaseBuildRefused as exc:
        print(f"RELEASE-BUILD-REFUSED: {exc}")
        return 2
    checksum.write_text(
        f"{digest}  {ASSET_NAME}\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"RELEASE-ASSET: {asset}")
    print(f"RELEASE-SHA256: {digest}")
    print(f"RELEASE-CHECKSUM: {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
