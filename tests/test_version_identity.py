import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS_DOI = "10.5281/zenodo.21318387"
REVIEW_URL = "https://github.com/antonioclim/TEA-Sim-TrustEvidence/pull/1"


def test_software_version_identity():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == "2.2.0rc1"
    assert data["project"]["requires-python"] == ">=3.13,<3.14"
    assert data["project"]["urls"]["Release candidate review"] == REVIEW_URL
    assert "Release" not in data["project"]["urls"]


def test_release_metadata_is_an_honest_candidate():
    status = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    assert status["release_state"] == "release-candidate"
    assert status["software_version"] == "2.2.0"
    assert status["package_version"] == "2.2.0rc1"
    assert status["candidate_version"] == "2.2.0-rc.1"
    assert status["git_tag"] == "v2.2.0-rc.1"
    assert status["doi"] is None
    assert status["doi_url"] is None
    assert status["doi_state"] == "unassigned-release-candidate"
    assert status["candidate_review_url"] == REVIEW_URL
    assert status["previous_version_doi"] == PREVIOUS_DOI
    assert status["canonical_asset_name"] == "TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip"
    assert status["canonical_archive_root"] == "TEA-Sim-TrustEvidence-v2.2.0-rc.1"
    assert status["canonical_checksum_name"] == "TEA-Sim-TrustEvidence-v2.2.0-rc.1.sha256"
    assert status["publication_authorised"] is False


def test_zenodo_metadata_is_draft_not_publication_claim():
    zen = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    assert zen["version"] == "2.2.0-rc.1"
    assert "publication_date" not in zen
    assert zen["access_right"] == "open"
    assert zen["language"] == "eng"
    predecessors = [x for x in zen["related_identifiers"] if x["relation"] == "isNewVersionOf"]
    assert predecessors == [{
        "identifier": PREVIOUS_DOI,
        "relation": "isNewVersionOf",
        "scheme": "doi",
        "resource_type": "software",
    }]
    assert "DRAFT ONLY" in zen["notes"]
