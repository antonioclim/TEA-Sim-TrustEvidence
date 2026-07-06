# TEA-Sim v2.0.1: auditable trust-evidence reference artefacts

This archive contains the TEA-Sim reference implementation and supporting artefacts for an auditable trust-evidence boundary in health information systems. The package is intended for reviewer inspection and reproducible local evaluation.

The archive includes local reference implementation code, tests, generated figures, FHIR R4/BALP-facing draft artefacts, backend-evaluation workstreams, externally informed workload descriptors, property-validation artefacts and an expert-validation protocol. It does not claim production deployment, certification, legal compliance, clinical validation or full formal proof.

## Quick start

```bash
python -m compileall src tests experiments scripts
python -m pytest tests -q
python figures/scripts/generate_jcis_figures.py
make quick
make evaluation-smoke
```

The public release should be uploaded as a new version after final maintainer approval. The previous public Zenodo record is DOI `10.5281/zenodo.21193829`; this modified archive requires its own new version DOI before DOI-bound citation as a replacement record.

## Main directories

- `src/` - Python reference implementation modules.
- `tests/` - public tests for core behaviour and local property checks.
- `experiments/` - local experiment and result-validation scripts.
- `evaluation_workstreams/` - standards-facing, backend, workload and property-validation artefacts.
- `protocols/` - future expert-validation protocol materials.
- `figures/` and `figure_sources/` - script-generated figures and source CSVs.
- `docs/`, `tables/`, `references/` - supporting documentation, tables and bibliographic artefacts.

## Scope boundary

This is a design-science/reference-implementation package. It supports local reproducibility and claim-boundary inspection. It does not provide official FHIR/BALP conformance, PostgreSQL/A3 execution, real-world clinical deployment, legal compliance, expert consensus or complete formal verification.
