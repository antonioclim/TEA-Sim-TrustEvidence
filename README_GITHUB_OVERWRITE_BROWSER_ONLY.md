# Browser-only GitHub overwrite patch

Use this ZIP when the v2.0.1 repository files are already on GitHub and you only need to update the public Zenodo DOI metadata.

Overwrite these repository paths from the browser:

- `.zenodo.json`
- `CITATION.cff`
- `README.md`
- `DATA_ACCESS.md`
- `CHANGELOG.md`
- `docs/DOI_AND_METADATA_RECONCILIATION.md`
- `docs/DOI_AND_VERSIONING.md`
- `scripts/repository_check.py`
- `figures/scripts/generate_jcis_figures.py`
- `SHA256SUMS.txt`
- `FILE_MANIFEST.tsv`

Then open the GitHub release page, choose **Edit**, and replace the release-description text with the content of `GITHUB_RELEASE_NOTES_v2.0.1_UPDATED.md`.

Suggested commit message:

`Update Zenodo DOI metadata for v2.0.1`

After committing, rerun GitHub Actions. The expected repository-check result is PASS.
