# workload-calibration workstream Workload Calibration Kit

This kit records the external-workload calibration workstream for the TrustEvidence artefact. It separates verified public dataset metadata from local backend execution. The runtime used for workload-calibration workstream could access source pages for verification through the browser tool, but the execution container had no DNS/network access for direct dataset download. Therefore, full Synthea generation, BIG IDEAs extraction and MIMIC-on-FHIR Demo extraction are provided as maintainer-run pathways rather than claimed as completed external-data extraction.

## Evidence classes included

1. Verified public metadata from Synthea, BIG IDEAs and MIMIC-on-FHIR source pages.
2. Derived C1-C4 workload descriptors with explicit assumptions.
3. Local A2 Merkle reference-backend passage of deterministic TrustEvidence objects generated from those descriptors.
4. Smoke samples for extractor syntax and parser behaviour only.

## Quick reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m compileall -q src scripts
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/build_calibrated_scenarios.py --metadata metadata/VERIFIED_PUBLIC_SOURCE_PARAMETERS.csv --out calibrated_scenarios/calibrated_scenarios.csv --parameter-out calibrated_scenarios/PARAMETER_REGISTER_CALIBRATED.csv
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/run_calibrated_a2.py --scenarios calibrated_scenarios/calibrated_scenarios.csv --out benchmark_outputs/raw_runs/calibrated_a2_raw_runs.csv --summary-out benchmark_outputs/calibrated_a2_summary.csv --sample-count 128 --execution-cap 10000
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/repository_check.py
python scripts/verify_sha256sums.py SHA256SUMS.txt
```

## Full maintainer-run extraction

Use `download_or_fetch_synthea.sh`, `generate_synthea.sh`, `download_physionet_manifests.sh` and the three extractor scripts only where source licences, credentials, storage and ethics permit. This kit does not redistribute full BIG IDEAs, MIMIC-on-FHIR, MIMIC-IV or MIMIC-IV-ED data.

## Claim boundary

Permitted wording: externally informed workload descriptors and local A2 Merkle reference-backend execution of capped deterministic calibrated TrustEvidence event counts under declared assumptions.

Forbidden wording from this kit alone: clinical validation, full external dataset extraction, production performance, A1 PostgreSQL calibrated execution, A3 Rekor/Trillian/Fabric execution, FHIR/BALP conformance, legal compliance or generalisable healthcare workload performance.
