# Quick start

Install the package and run the local reproducibility checks:

```bash
python -m pip install -e .[test]
make ci-local
make experiments
make validate-results
make analyse-results
```

The local profile uses the in-repository reference implementation and does not require Docker. External-service runs require Docker Compose and the services described in `docs/EXTERNAL_SERVICES.md`.
