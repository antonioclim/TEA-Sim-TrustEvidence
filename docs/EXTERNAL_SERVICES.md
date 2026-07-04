# External services

The Docker Compose stack is provided for live integration work with HAPI FHIR,
PostgreSQL, Trillian, Rekor and Hyperledger Fabric.

```bash
python -m pip install -e '.[test,external,postgres]'
make external-preflight
make up
make smoke
make down
```

External benchmark CSV files are generated only when the live services are
available.
