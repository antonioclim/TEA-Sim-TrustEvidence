# Reproducibility

This archive is structured so that reviewers can inspect and rerun the local reference-implementation checks without external services.

Recommended local sequence:

1. Install Python dependencies listed in the requirements files.
2. Run `python -m compileall src tests experiments scripts`.
3. Run `python -m pytest tests -q`.
4. Regenerate figures with `python figures/scripts/generate_jcis_figures.py`.
5. Run `make quick`.
6. Run `make evaluation-smoke`.
7. Verify `SHA256SUMS.txt` and `FILE_MANIFEST.tsv` after extraction.

External services, full FHIR validators, PostgreSQL execution and transparency-log execution are deliberately not asserted unless the relevant tools and credentials are supplied by the maintainer.
