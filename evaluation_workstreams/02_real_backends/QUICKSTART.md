# Quickstart

```bash
python -m compileall src tests experiments scripts
python -m pytest
python experiments/run_backend_benchmark.py --objects 1000 --repetitions 2 --out benchmark_outputs/smoke_backend_summary.csv --raw-dir benchmark_outputs/smoke_raw_runs
python experiments/tamper_tests.py --out benchmark_outputs/smoke_tamper_results.csv
python scripts/repository_check.py
```

For PostgreSQL execution, set `TEA_POSTGRES_DSN` to a local, disposable PostgreSQL database and then run:

```bash
python scripts/probe_postgres.py --out benchmark_outputs/probes/postgres_probe.json
python experiments/run_backend_benchmark.py --backend postgres --objects 1000 --repetitions 3 --dsn-env TEA_POSTGRES_DSN --out benchmark_outputs/postgres_backend_summary.csv
```

Do not use live clinical, patient-identifiable or operational audit data with this kit.
