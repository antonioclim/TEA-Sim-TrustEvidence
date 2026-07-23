#!/usr/bin/env python3
"""Validate the deterministic curated release-candidate ZIP and catalogues."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path

from release_common import (
    ASSET_CHECKSUM_NAME,
    ASSET_NAME,
    CHECKSUM_PATH,
    EXPECTED_ROOT,
    MANIFEST_PATH,
    is_safe_relative,
    sha256_bytes,
)

REQUIRED = {
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "CITATION.cff",
    ".zenodo.json",
    "RELEASE_METADATA.json",
    MANIFEST_PATH,
    CHECKSUM_PATH,
    "docs/PUBLIC_RELEASE_SCOPE.md",
    "docs/DEPLOYABILITY_AND_COMPONENTS.md",
}
FORBIDDEN_PREFIXES = ("docs/route_c/",)
FORBIDDEN_PATHS = {".github/workflows/" + "c6-source-" + "snapshot.yml"}


def parse_asset_checksum(path: Path) -> tuple[str, str]:
    parts = path.read_text(encoding="utf-8").strip().split(None, 1)
    if len(parts) != 2:
        raise ValueError("malformed outer checksum file")
    return parts[0].lower(), parts[1].lstrip("* ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--checksum", type=Path, required=True)
    parser.add_argument("--extract-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    if not args.archive.is_file():
        errors.append(f"archive not found: {args.archive}")
    if not args.checksum.is_file():
        errors.append(f"checksum not found: {args.checksum}")
    if errors:
        print("RELEASE-ARCHIVE: FAIL")
        print("\n".join(errors))
        return 1

    if args.archive.name != ASSET_NAME:
        errors.append(f"asset name mismatch: {args.archive.name}")
    if args.checksum.name != ASSET_CHECKSUM_NAME:
        errors.append(f"checksum name mismatch: {args.checksum.name}")

    digest = hashlib.sha256(args.archive.read_bytes()).hexdigest()
    try:
        expected_digest, expected_name = parse_asset_checksum(args.checksum)
        if expected_name != ASSET_NAME:
            errors.append("outer checksum filename target mismatch")
        if expected_digest != digest:
            errors.append("outer checksum digest mismatch")
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    file_data: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(args.archive) as archive:
            bad = archive.testzip()
            if bad:
                errors.append(f"ZIP CRC failure: {bad}")
            seen: set[str] = set()
            root_prefix = EXPECTED_ROOT + "/"
            for info in archive.infolist():
                name = info.filename
                if name in seen:
                    errors.append(f"duplicate ZIP member: {name}")
                seen.add(name)
                if "\\" in name or not name.startswith(root_prefix):
                    errors.append(f"member outside canonical root: {name}")
                    continue
                rel = name[len(root_prefix) :]
                if not rel or info.is_dir():
                    continue
                if not is_safe_relative(rel):
                    errors.append(f"unsafe member path: {rel}")
                    continue
                if rel in FORBIDDEN_PATHS or any(
                    rel.startswith(prefix) for prefix in FORBIDDEN_PREFIXES
                ):
                    errors.append(f"forbidden public member: {rel}")
                file_data[rel] = archive.read(info)
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"cannot read archive: {exc}")

    for required in sorted(REQUIRED - set(file_data)):
        errors.append(f"required member missing: {required}")

    manifest_rows = 0
    checksum_rows = 0
    if MANIFEST_PATH in file_data:
        try:
            rows = list(
                csv.DictReader(
                    io.StringIO(file_data[MANIFEST_PATH].decode("utf-8")),
                    delimiter="\t",
                )
            )
            manifest_rows = len(rows)
            listed: set[str] = set()
            for row in rows:
                rel = row["path"]
                if rel in listed:
                    errors.append(f"duplicate manifest row: {rel}")
                    continue
                listed.add(rel)
                data = file_data.get(rel)
                if data is None:
                    errors.append(f"manifest member missing: {rel}")
                    continue
                if int(row["size_bytes"]) != len(data):
                    errors.append(f"manifest size mismatch: {rel}")
                if row["sha256"].lower() != sha256_bytes(data):
                    errors.append(f"manifest digest mismatch: {rel}")
            actual = set(file_data) - {MANIFEST_PATH, CHECKSUM_PATH}
            for rel in sorted(actual - listed):
                errors.append(f"unlisted archive member: {rel}")
            for rel in sorted(listed - actual):
                errors.append(f"manifest-only member: {rel}")
        except (KeyError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"cannot validate internal manifest: {exc}")

    if CHECKSUM_PATH in file_data:
        try:
            listed = set()
            for line in file_data[CHECKSUM_PATH].decode("utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split(None, 1)
                if len(parts) != 2:
                    errors.append(f"malformed internal checksum row: {line}")
                    continue
                expected, rel = parts[0].lower(), parts[1].lstrip("* ")
                checksum_rows += 1
                if rel in listed:
                    errors.append(f"duplicate internal checksum row: {rel}")
                    continue
                listed.add(rel)
                data = file_data.get(rel)
                if data is None:
                    errors.append(f"checksum member missing: {rel}")
                elif expected != sha256_bytes(data):
                    errors.append(f"internal checksum mismatch: {rel}")
            actual = set(file_data) - {CHECKSUM_PATH}
            for rel in sorted(actual - listed):
                errors.append(f"member absent from internal checksums: {rel}")
            for rel in sorted(listed - actual):
                errors.append(f"checksum-only member: {rel}")
        except UnicodeDecodeError as exc:
            errors.append(f"cannot decode internal checksums: {exc}")

    extracted_root: Path | None = None
    if args.extract_dir and not errors:
        if args.extract_dir.exists():
            shutil.rmtree(args.extract_dir)
        args.extract_dir.mkdir(parents=True)
        with zipfile.ZipFile(args.archive) as archive:
            archive.extractall(args.extract_dir)
        extracted_root = args.extract_dir / EXPECTED_ROOT
        if not extracted_root.is_dir():
            errors.append("extracted canonical root missing")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "archive": args.archive.name,
        "archive_sha256": digest,
        "canonical_root": EXPECTED_ROOT,
        "file_count": len(file_data),
        "manifest_rows": manifest_rows,
        "checksum_rows": checksum_rows,
        "extracted_root": str(extracted_root) if extracted_root else None,
        "errors": errors,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if errors:
        print("RELEASE-ARCHIVE: FAIL")
        print("\n".join(errors))
        return 1
    print(
        "RELEASE-ARCHIVE: PASS "
        f"({len(file_data)} files; {manifest_rows} manifest rows; "
        f"{checksum_rows} checksums; sha256 {digest})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
