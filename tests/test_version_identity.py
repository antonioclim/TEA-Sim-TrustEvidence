import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DOI = '10.5281/zenodo.21318387'
PREVIOUS_DOI = '10.5281/zenodo.21226180'
RELEASE_URL = 'https://github.com/antonioclim/TEA-Sim-TrustEvidence/releases/tag/v2.1.0'

def test_software_version_identity():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == "2.1.0"
    assert data["project"]["requires-python"] == ">=3.13,<3.14"

def test_release_metadata_is_internally_coherent():
    status = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    assert status["software_version"] == "2.1.0"
    assert status["release_date"] == "2026-07-12"
    assert status["git_tag"] == "v2.1.0"
    assert status["doi"] == DOI
    assert status["github_release_url"] == RELEASE_URL
    assert status["previous_version_doi"] == PREVIOUS_DOI
    assert status["canonical_asset_name"] == "TEA-Sim-TrustEvidence-v2.1.0.zip"
    assert status["canonical_archive_root"] == "TEA-Sim-TrustEvidence-v2.1.0"
    assert status["canonical_checksum_name"] == "TEA-Sim-TrustEvidence-v2.1.0.sha256"
    assert status["doi_state"] == "exact-version-identifier"
    assert status["doi"] != status["previous_version_doi"]
    assert not (ROOT / ("PRE_" + "PUBLICATION_DO_NOT_UPLOAD.md")).exists()
    assert not (ROOT / ("PUBLICATION_" + "STATUS.json")).exists()

def test_zenodo_metadata_relations():
    zen = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    assert zen["version"] == "2.1.0"
    assert zen["publication_date"] == "2026-07-12"
    assert zen["access_right"] == "open"
    assert zen["language"] == "eng"
    predecessors = [x for x in zen["related_identifiers"] if x["relation"] == "isNewVersionOf"]
    assert predecessors == [{
        "identifier": PREVIOUS_DOI,
        "relation": "isNewVersionOf",
        "scheme": "doi",
        "resource_type": "software",
    }]
    release_links = [x for x in zen["related_identifiers"] if x["identifier"] == RELEASE_URL]
    assert len(release_links) == 1
