# TEA-Sim v2.0.1: auditable trust-evidence reference artefacts

This archive contains the TEA-Sim reference implementation and supporting artefacts for an auditable trust-evidence boundary in health information systems. The package is intended for reviewer inspection and reproducible local evaluation.

The archive includes local reference implementation code, tests, generated figures, FHIR R4/BALP-facing draft artefacts, backend-evaluation workstreams, externally informed workload descriptors, property-validation artefacts and an expert-validation protocol. It does not claim production deployment, certification, legal compliance, clinical validation or full formal proof.

## Public records and citation

Zenodo software record: `10.5281/zenodo.21226180`  
DOI link: <https://doi.org/10.5281/zenodo.21226180>  
GitHub repository: <https://github.com/antonioclim/TEA-Sim-TrustEvidence>  
GitHub release: <https://github.com/antonioclim/TEA-Sim-TrustEvidence/releases/tag/v2.0.1>

Recommended citation:

> Clim, A. (2026). TEA-Sim v2.0.1: Auditable trust-evidence reference artefacts (2.0.1). Zenodo. https://doi.org/10.5281/zenodo.21226180

The previous Zenodo version is `10.5281/zenodo.21193829`. The current archive is version `2.0.1` and should be cited using the v2.0.1 DOI above.

## Quick start

```bash
python -m compileall src tests experiments scripts
python -m pytest tests -q
python figures/scripts/generate_jcis_figures.py
make quick
make evaluation-smoke
```

## Main directories

- `src/` - Python reference implementation modules.
- `tests/` - public tests for core behaviour and local property checks.
- `experiments/` - local experiment and result-validation scripts.
- `evaluation_workstreams/` - standards-facing, backend, workload and property-validation artefacts.
- `protocols/` - future expert-validation protocol materials.
- `figures/` and `figure_sources/` - script-generated figures and source CSVs.
- `docs/`, `tables/` and `references/` - supporting documentation, tables and bibliographic artefacts.

## Scope boundary

This is a design-science/reference-implementation package. It supports local reproducibility and claim-boundary inspection. It does not provide official FHIR/BALP conformance, PostgreSQL/A3 execution, real-world clinical deployment, legal compliance, expert consensus or complete formal verification.
