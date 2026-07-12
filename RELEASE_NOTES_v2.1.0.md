# TEA-Sim v2.1.0 release notes

## Release identity

- Version: `2.1.0`
- Tag: `v2.1.0`
- Exact-version DOI: <https://doi.org/10.5281/zenodo.21318387>
- Previous version: <https://doi.org/10.5281/zenodo.21226180>
- Canonical asset: `TEA-Sim-TrustEvidence-v2.1.0.zip`

## Main changes since v2.0.1

- Reframed the package as a schema-first biomedical data-curation method for personal health monitoring audit evidence.
- Consolidated the public implementation under `src/trustevidence`.
- Added closed event-discriminated schemas and semantic minimisation checks.
- Added deterministic TE-JCS-1 canonicalisation, Ed25519 test-fixture signatures and a local A2 Merkle receipt with retained-checkpoint consistency checks.
- Added controlled mutation tests, deterministic Hypothesis tests and finite bounded executable checks.
- Added an externally informed synthetic workload passage at 128, 512 and 2,048 leaves.
- Added programmatically generated PDF, SVG and 600-dpi PNG figures.
- Made public text and generated CSV files stable across Git add, commit and clone.
- Made repository, manifest and checksum checks work in an ordinary Git clone containing `.git/` and a local `.venv/`.
- Established one canonical ZIP byte stream for both the GitHub release and Zenodo record.

## Executed reference evidence

- 34 unit and deterministic regression tests.
- 8 deterministic Hypothesis tests reporting 680 generated examples.
- 29,105 finite bounded checks with no recorded failure.
- 32,256 synthetic workload events.
- 1,152 successful sampled receipt checks.
- 36/36 re-signed proof-path mutations rejected.
- No validation failure or ordinary sampled-verification failure in the retained workload passage.

## Scope boundary

The release is a local reference implementation over synthetic monitoring-accountability events. It does not claim clinical validation, production deployment, legal compliance, FHIR/BALP conformance, global non-equivocation, operational key-management adequacy or complete formal verification. Timing values are single-host descriptive observations rather than comparative benchmarks.
