from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from pathlib import Path

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


def test_candidate_archive_has_internal_catalogues(tmp_path):
    archive = tmp_path / ASSET_NAME
    digest = build_release_archives.build(archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
    with zipfile.ZipFile(archive) as zf:
        assert zf.testzip() is None
        names = {name for name in zf.namelist() if not name.endswith("/")}
        prefix = EXPECTED_ROOT + "/"
        assert all(name.startswith(prefix) for name in names)
        rels = {name[len(prefix):] for name in names}
        assert MANIFEST_PATH in rels
        assert CHECKSUM_PATH in rels
        assert not any(rel.startswith("docs/route_c/") for rel in rels)
        manifest = list(csv.DictReader(io.StringIO(zf.read(prefix + MANIFEST_PATH).decode()), delimiter="	"))
        assert len(manifest) == len(rels) - 2
        checksums = zf.read(prefix + CHECKSUM_PATH).decode().splitlines()
        assert len(checksums) == len(rels) - 1
