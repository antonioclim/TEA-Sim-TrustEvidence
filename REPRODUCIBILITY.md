# Reproducibility

The local reproducibility path is:

```bash
python -m pip install -e .[test]
make ci-local
make experiments
make validate-results
make analyse-results
```

The expected local checks are source compilation, unit tests, static FHIR Shorthand checks, static implementation-guide checks, legal traceability validation, local experiment generation, result-schema validation and result analysis.

External-service measurements over HAPI FHIR, PostgreSQL, Trillian, Rekor and Hyperledger Fabric are not claimed by the archived local results. To run those services, use `docker-compose.full.yml`, `make up`, `make smoke` and the external-service notes in `docs/EXTERNAL_SERVICES.md`.
