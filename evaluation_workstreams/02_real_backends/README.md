# REAL_BACKENDS_KIT — backend-evaluation workstream local backend execution evidence

This kit contains the backend-evaluation workstream reference backend artefacts for the TrustEvidence auditability package. It is a stage-level scientific evidence kit, not a final public GitHub or Zenodo release.

## Evidence status

- **A1 PostgreSQL**: schema, Python backend adapter and probe scripts are included. Execution requires either Docker with PostgreSQL or a locally supplied PostgreSQL DSN in `TEA_POSTGRES_DSN`. In the current runtime, Docker, `psql` and a DSN were unavailable, so A1 is marked unavailable rather than measured.
- **A2 Merkle**: pure-Python deterministic canonicalisation, append receipts, inclusion proofs, prefix consistency checks, pytest tests, tamper tests and local reference benchmark results are included.
- **A3 Rekor/Trillian/Fabric**: adapter/protocol scaffolding and environment probes are included. No local Rekor, Trillian or Fabric service was available in the current runtime, so A3 is adapter-only and not an executed backend.

## Reproduction commands

From the root of this kit:

```bash
python -m compileall src tests experiments scripts
python -m pytest
python experiments/run_backend_benchmark.py --objects 1000 10000 --repetitions 10 --out benchmark_outputs/backend_benchmark_summary.csv --raw-dir benchmark_outputs/raw_runs
python experiments/tamper_tests.py --out benchmark_outputs/tamper_detection_results.csv
python scripts/probe_postgres.py --out benchmark_outputs/probes/postgres_probe.json
python scripts/probe_a3.py --out benchmark_outputs/probes/a3_probe.json
python scripts/repository_check.py
python scripts/verify_sha256sums.py SHA256SUMS.txt
```

The benchmark reports are **local reference-implementation measurements** under the declared runtime. They are not production performance claims, clinical validation, legal compliance evidence or blockchain benchmark evidence.
