#!/usr/bin/env python3
"""Verify the immutable v2.2.0 release identity and, optionally, its public assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_METADATA = ROOT / "RELEASE_METADATA.json"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_outer_checksum(path: Path) -> tuple[str, str]:
    parts = path.read_text(encoding="utf-8").strip().split(None, 1)
    if len(parts) != 2:
        raise ValueError("malformed outer checksum file")
    return parts[0].lower(), parts[1].lstrip("* ")


def validate_metadata(metadata: dict[str, object]) -> list[str]:
    errors: list[str] = []
    expected = {
        "release_state": "final-release",
        "source_state": "post-release-documentation",
        "software_version": "2.2.0",
        "git_tag": "v2.2.0",
        "doi": "10.5281/zenodo.21533962",
        "canonical_asset_name": "TEA-Sim-TrustEvidence-v2.2.0.zip",
        "canonical_archive_root": "TEA-Sim-TrustEvidence-v2.2.0",
        "canonical_checksum_name": "TEA-Sim-TrustEvidence-v2.2.0.sha256",
        "canonical_asset_size_bytes": 6_026_306,
        "canonical_asset_sha256": "e9b2b6e3829f4158e561812cbb146a5b212877d6c39e740467777cc9944b7a3c",
        "immutable_release_commit_sha": "ac44a59c690bd18906163ed901477a8173208694",
        "release_asset_immutable": True,
        "release_asset_build_authorised": False,
        "post_release_documentation_updates_permitted": True,
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            errors.append(f"RELEASE_METADATA {key} mismatch")
    commit = str(metadata.get("immutable_release_commit_sha", ""))
    digest = str(metadata.get("canonical_asset_sha256", ""))
    if not HEX_40.fullmatch(commit):
        errors.append("immutable release commit is not a 40-character SHA")
    if not HEX_64.fullmatch(digest):
        errors.append("canonical asset digest is not a 64-character SHA-256")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--checksum", type=Path)
    args = parser.parse_args()

    if (args.archive is None) != (args.checksum is None):
        parser.error("--archive and --checksum must be supplied together")

    metadata = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
    errors = validate_metadata(metadata)

    if args.archive is not None and args.checksum is not None:
        archive = args.archive.resolve()
        checksum = args.checksum.resolve()
        if not archive.is_file():
            errors.append(f"archive not found: {archive}")
        if not checksum.is_file():
            errors.append(f"checksum not found: {checksum}")
        if archive.is_file() and checksum.is_file():
            expected_name = str(metadata["canonical_asset_name"])
            expected_checksum_name = str(metadata["canonical_checksum_name"])
            expected_size = int(metadata["canonical_asset_size_bytes"])
            expected_digest = str(metadata["canonical_asset_sha256"])
            expected_root = str(metadata["canonical_archive_root"]) + "/"

            if archive.name != expected_name:
                errors.append(f"asset name mismatch: {archive.name}")
            if checksum.name != expected_checksum_name:
                errors.append(f"checksum name mismatch: {checksum.name}")
            if archive.stat().st_size != expected_size:
                errors.append(
                    f"asset size mismatch: {archive.stat().st_size} != {expected_size}"
                )
            observed_digest = sha256(archive)
            if observed_digest != expected_digest:
                errors.append(
                    f"asset SHA-256 mismatch: {observed_digest} != {expected_digest}"
                )
            try:
                listed_digest, listed_name = parse_outer_checksum(checksum)
                if listed_digest != expected_digest:
                    errors.append("outer checksum digest differs from release metadata")
                if listed_name != expected_name:
                    errors.append("outer checksum filename differs from release metadata")
            except (OSError, ValueError) as exc:
                errors.append(str(exc))

            try:
                with zipfile.ZipFile(archive) as package:
                    bad_member = package.testzip()
                    if bad_member:
                        errors.append(f"ZIP CRC failure: {bad_member}")
                    names = package.namelist()
                    if not names or not all(name.startswith(expected_root) for name in names):
                        errors.append("ZIP member outside the immutable canonical root")
            except (OSError, zipfile.BadZipFile) as exc:
                errors.append(f"cannot read immutable release archive: {exc}")

    if errors:
        print("IMMUTABLE-RELEASE: FAIL")
        print("\n".join(errors))
        return 1

    if args.archive is None:
        print(
            "IMMUTABLE-RELEASE: PASS "
            "(metadata; v2.2.0 same-version rebuild disabled)"
        )
    else:
        print(
            "IMMUTABLE-RELEASE: PASS "
            f"({metadata['canonical_asset_name']}; "
            f"{metadata['canonical_asset_size_bytes']} bytes; "
            f"sha256 {metadata['canonical_asset_sha256']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
