# MEASUREMENT_PROTOCOL.md

Status: measurement protocol and statistical plan for future external-service validation. No external-service measurement result is reported in this release.

## 1. Scope and evidence boundary

This protocol distinguishes the v1 simulation-results centre of gravity from a future live-service measurement plan. The old manuscript reported model outputs, not latency, throughput, legal risk, security proof or deployment behaviour [CITED:v1-manuscript-boundary]. The supplementary material likewise stated that v1 did not implement a FHIR server, validate FHIR JSON resources, create implementation-guide profiles, perform conformance testing or deploy a blockchain platform [CITED:v1-supplement-boundary]. This protocol defines what must be measured by a future live-service run; it does not convert dry-smoke or local-adapter tests into benchmark evidence.

External benchmarking may start only after the external smoke dependency is closed: `[external validation required:v2.0.0-external-services]`. Service availability checks are separated from benchmark observations. A service-health pass is a precondition, not a performance result [ASSUMED:v2.0.0-protocol].

## 2. Workloads W1-W5

The workloads are derived from v1 scenarios S1-S5, preserving governance shape rather than treating v1 storage numbers as measurements. The v1 scenario matrix varied organisations, access intensity, revocation probability, dispute risk and signature profile [CITED:v1-scenario-matrix]. The mapping is machine-readable in `tables/workloads.csv` and `experiments/workloads/W1.json` through `W5.json` [COMPUTED]. The planned run matrix is `tables/run_matrix.csv`, containing `250` workload/backend/repetition rows [COMPUTED:v2.0.0-artefacts].

The faithful mapping rule is: each W-workload emits the same evidence families as v1 — consent grant, access attestation, provenance assertion, integrity anchor and consent-state transition — through the TrustEvidence interface and backend adapters [ASSUMED:v2.0.0-protocol]. High-frequency observations remain payload context, not per-sample evidence writes, preserving the evidence-minimisation boundary [CITED:v1-event-model].

## 3. Backends and baselines

The measurement set contains authored backends and external baselines: A1 PostgreSQL central audit, A2 local Merkle hash log, A3 Fabric adapter, Trillian personality and Rekor adapter [COMPUTED:v2.0.0-artefacts]. HAPI FHIR supplies the FHIR-side AuditEvent workload endpoint; the future external validation remains responsible for FHIR profile conformance and BALP mapping [external IG QA required].

The same workload stream must be replayed across every backend. Any backend-specific transformation must be recorded in `results/hardware_software_disclosure.csv` or `results/service_preflight.csv` and must not alter event order, subject-token distribution, policy-state distribution or consent-transition schedule [ASSUMED:v2.0.0-protocol].

## 4. Metrics

The declared metrics are listed in `tables/metrics.csv` [COMPUTED]. They are write latency p50/p95/p99, sustained throughput, storage growth, proof size, verification time and audit-query cost [ASSUMED:v2.0.0-protocol]. Service availability and error-code counts are quality-control variables, not substitutes for performance measurements.

Latency uses monotonic clocks in the harness process [ASSUMED:v2.0.0-protocol]. Storage growth is backend-specific and the exact measurement method must be recorded in the returned hardware/software disclosure [ASSUMED:v2.0.0-protocol]. Proof size is the serialised byte count of verifier-required inclusion, consistency, witness or finality material [ASSUMED:v2.0.0-protocol].

## 5. Experimental design

Each workload/backend pair is run for `10` analysed repetitions [ASSUMED:v2.0.0-protocol]. The seed series is `20261001` through `20261010` [ASSUMED:v2.0.0-protocol]. Before measured repetitions, the external validator runs `make up && make smoke` and then a labelled service warm-up pass that is excluded from all tables and figures [external validation required:v2.0.0-external-services]. Warm-up observations are retained for diagnostics but not estimated in `statistical_summary.csv` [ASSUMED:v2.0.0-protocol].

No valid observation is deleted because it is inconvenient. A run is excluded only if a predeclared service-health failure, missing service identity, schema violation, clock failure or unrecoverable harness crash occurs; every exclusion is recorded in `results/anomaly_log.csv` [ASSUMED:v2.0.0-protocol].

## 6. Statistical analysis

Primary summaries report p50, p95 and p99 for write latency, plus median sustained throughput, final storage growth, proof-size distribution, verification time and audit-query cost [ASSUMED:v2.0.0-protocol]. Confidence intervals use percentile bootstrap over repetitions with `2000` resamples and a `95%` confidence level [ASSUMED:v2.0.0-protocol]. The bootstrap unit is the repetition, not the individual event, to avoid pseudo-replication [ASSUMED:v2.0.0-protocol].

Effect sizes are reported as paired median differences and log ratios relative to the next-weaker applicable backend: A2 versus A1, A3 versus A2, Trillian/Rekor versus local A2, and Fabric versus local A3 where the semantic comparison is justified [ASSUMED:v2.0.0-protocol]. No p-value is used as the main decision criterion [ASSUMED:v2.0.0-protocol].

## 7. Hardware and software disclosure

The external runner must complete `docs/EXTERNAL_SERVICES.md` and return `results/hardware_software_disclosure.csv`, including CPU model, core count, RAM, operating system, Docker version, Docker Compose version, service image names, image digests where available, HAPI endpoint, PostgreSQL version, Trillian source/digest, Rekor image/ref, Fabric samples ref, Fabric peer/orderer versions and harness Python version [external validation required]. Missing digests remain `[VERIFY]` until the external validation run pins them.

## 8. Result-file schemas

The exact CSV schemas are declared in `tables/result_schemas.csv` and in `schemas/results/*.schema.json` [COMPUTED:v2.0.0-artefacts]. Result ingestion rejects files that lack required headers, use undeclared evidence classes, omit run identifiers or mix warm-up and measured observations [ASSUMED:v2.0.0-protocol].

## 9. Placeholder registry

Every quantitative result sentence, table cell and figure slot in the future manuscript is controlled by the claim-evidence ledger and validated result schemas [COMPUTED:v2.0.0-artefacts]. No slot may be filled from dry-smoke output or from v1 simulation tables [ASSUMED:v2.0.0-protocol].

## 10. maintainer command sequence for external validation

```bash
make up
make smoke
make validate-protocol
TE_REQUIRE_LIVE=1 TE_BENCH_PROFILE=external REPETITIONS=10 make experiments
make validate-results
make analyse-results
```

The command sequence is a protocol, not an observed result. This release contains only protocol/schema validation and local-reference checks [MEASURED:v2.0.0-local]. External-service measurement observations remain `[external validation required]` until the external runner returns `results/` and service logs.
