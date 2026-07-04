# Measurement protocol

This protocol defines how to run local and external TrustEvidence measurements. The repository includes local reference execution. External-service measurements require Docker Compose services for HAPI FHIR, PostgreSQL, Trillian, Rekor and Hyperledger Fabric.

## Workloads

Workloads W1–W5 preserve the governance shape of the original TEA-Sim scenarios: low-complexity direct care, interorganisational shared care, secondary-use governance, high-dispute/high-revocation governance and cryptographic-agility transition. The workload definitions are stored in `experiments/workloads/`.

## Backends

The planned backend set is A1 central audit, A2 local Merkle hash log, A3 Fabric adapter, Trillian personality and Rekor adapter. Local runs exercise the in-repository reference paths. External runs require the configured services.

## Metrics

Metrics include write latency, sustained throughput, storage growth, proof size, verification time, audit-query cost, service availability and error counts. Service-availability checks are preconditions rather than performance results.

## Local execution

```bash
make ci-local
make experiments
make validate-results
make analyse-results
```

## External execution

```bash
make up
make smoke
TE_REQUIRE_LIVE=1 TE_BENCH_PROFILE=external REPETITIONS=10 make experiments
make validate-results
make analyse-results
```

External measurements should be reported only after the returned result files pass schema validation and anomaly review.
