from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from pathlib import Path

import pytest

from scripts import build_release_archives
from scripts.release_common import (
    ASSET_NAME,
    CHECKSUM_PATH,
    EXPECTED_ROOT,
    MANIFEST_PATH,
    public_release_files,
    relative,
)

ROOT = Path(__file__).resolve().parents[1]


def test_public_release_set_excludes_submission_governance():
    rels = {relative(path) for path in public_release_files()}
    assert not any(rel.startswith("docs/route_c/") for rel in rels)
    assert ".github/workflows/" + "c6-source-" + "snapshot.yml" not in rels
    assert "docs/PUBLIC_RELEASE_SCOPE.md" in rels


def test_post_release_main_refuses_same_version_rebuild(tmp_path):
    archive = tmp_path / ASSET_NAME
    with pytest.raises(
        build_release_archives.ReleaseBuildRefused,
        match="v2.2.0 asset is immutable",
    ):
        build_release_archives.build(archive)
    assert not archive.exists()


def test_archive_payload_still_has_internal_catalogue_inputs():
    # The payload helper remains inspectable for future version development, but the
    # current post-release source state may not emit another v2.2.0 asset.
    payload = build_release_archives.archive_payload()
    assert MANIFEST_PATH in payload
    assert CHECKSUM_PATH in payload
    assert not any(rel.startswith("docs/route_c/") for rel in payload)
