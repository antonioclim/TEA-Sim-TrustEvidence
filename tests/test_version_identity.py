import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS_DOI = "10.5281/zenodo.21318387"
DOI = "10.5281/zenodo.21533962"
DOI_URL = "https://doi.org/10.5281/zenodo.21533962"
RELEASE_URL = "https://github.com/antonioclim/TEA-Sim-TrustEvidence/releases/tag/v2.2.0"


def test_software_version_identity():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == "2.2.0"
    assert data["project"]["requires-python"] == ">=3.13,<3.14"
    assert data["project"]["urls"]["Release"] == RELEASE_URL
    assert data["project"]["urls"]["DOI"] == DOI_URL


def test_curation_result_schema_accepts_final_software_version():
    schema = json.loads(
        (ROOT / "src" / "trustevidence" / "schemas" / "curation_result.schema.json").read_text(
            encoding="utf-8"
        )
    )
    pattern = schema["properties"]["software_version"]["pattern"]
    assert re.fullmatch(pattern, "2.1.0")
    assert re.fullmatch(pattern, "2.2.0rc1")
    assert re.fullmatch(pattern, "2.2.0")
    assert re.fullmatch(pattern, "2.2.0+local.1")
    assert not re.fullmatch(pattern, "2.3.0")


def test_release_metadata_is_final():
    status = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    assert status["release_state"] == "final-release"
    assert status["software_version"] == "2.2.0"
    assert status["package_version"] == "2.2.0"
    assert status["git_tag"] == "v2.2.0"
    assert status["doi"] == DOI
    assert status["doi_url"] == DOI_URL
    assert status["doi_state"] == "exact-version"
    assert status["release_url"] == RELEASE_URL
    assert status["previous_version_doi"] == PREVIOUS_DOI
    assert status["canonical_asset_name"] == "TEA-Sim-TrustEvidence-v2.2.0.zip"
    assert status["canonical_archive_root"] == "TEA-Sim-TrustEvidence-v2.2.0"
    assert status["canonical_checksum_name"] == "TEA-Sim-TrustEvidence-v2.2.0.sha256"
    assert status["publication_authorised"] is True


def test_zenodo_metadata_is_final():
    zen = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    assert zen["version"] == "2.2.0"
    assert zen["publication_date"] == "2026-07-24"
    assert zen["access_right"] == "open"
    assert zen["language"] == "eng"
    predecessors = [x for x in zen["related_identifiers"] if x["relation"] == "isNewVersionOf"]
    assert predecessors == [
        {
            "identifier": PREVIOUS_DOI,
            "relation": "isNewVersionOf",
            "scheme": "doi",
            "resource_type": "software",
        }
    ]
    assert DOI in zen["notes"]
