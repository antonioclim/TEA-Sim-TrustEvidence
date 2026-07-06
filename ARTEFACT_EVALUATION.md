# Artefact evaluation notes

This repository is designed for source-level inspection and reproducibility. It
provides installable Python packages, tests, deterministic local experiments,
result schemas, analysis code, a preserved v1.5.1 reproduction tree, draft FHIR
Shorthand source and Docker entry points for live service integrations.

Reviewers can run:

```bash
python -m pip install -e '.[test]'
make ci-local
make experiments
make validate-results
make analyse-results
make reproduce-v1
```
