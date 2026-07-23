# C5 execution plan: paired local B0--B2 overhead experiment

## Status

Frozen before the hosted confirmatory materialisation. This plan instantiates `MEASUREMENT_PROTOCOL.md` without changing its baselines, primary comparisons, minimum replicate count, failure rules or claim ceiling after inspection of confirmatory results.

## Question

C5 asks one bounded empirical question:

> What additional local processing, application-byte and local-storage-proxy cost is introduced when the complete TrustEvidence reference path is added to the same frozen synthetic cross-organisational health-information-exchange case?

The answer will describe the reported Python reference environment only. It will not be interpreted as production EHR overhead, hospital latency, a service-level result, a network-capacity result or an organisational cost estimate.

## Confirmatory workload decision

`W1-HIE-DISCLOSURE` is the sole confirmatory workload. It is the complete C3 synthetic disclosure of a versioned DiagnosticReport from Synthetic Hospital A to Synthetic Hospital B under Consent version 3, policy version 6 and authorisation decision D-204.

The protocol designated the wearable batch (`W2`) as secondary and allowed its omission if the Route C critical path was threatened. A pre-confirmatory engineering feasibility run showed that the generic monitoring-envelope path would multiply hosted execution time beyond the bounded revision schedule. That engineering observation is not a retained C5 measurement and will not be reported as an overhead result. W2 is therefore omitted before confirmatory materialisation, and no W2 overhead estimate or cross-workload generalisation will be claimed.

## Baselines

### B0 — source FHIR processing

For every operation, B0 reads the frozen source Bundle, applies the declared local source checks and produces TE-JCS canonical source bytes.

### B1 — conventional audit projection

B1 performs B0 and constructs a conventional FHIR R4 AuditEvent/Provenance-oriented collection from the retained C3 resources. It does not construct or sign a TrustEvidence envelope and does not append to the local A2 model.

### B2 — complete local TrustEvidence path

B2 performs B1 and additionally:

1. constructs the declared HIE disclosure event and nonce-framed source commitment;
2. applies the HIE semantic and minimisation checks;
3. canonicalises the unsigned evidence core and constructs its domain-separated SHA-256 digest;
4. signs the issuer statement with the deterministic TEST-ONLY Ed25519 fixture key;
5. appends the core digest to the project-specific local A2 Merkle model;
6. issues the signed receipt, inclusion path and, after the first operation, a consistency proof;
7. verifies the issuer statement, receipt binding, inclusion path and retained-checkpoint transition;
8. executes one stale-signature mutation control after the retained operation sequence.

## Experimental unit and pairing

The independent replicate is one fresh Python worker process for one baseline in one paired block. Process start-up and fixed warm-up are outside the measured M7 interval. The measured interval begins after warm-up and state reset.

Within each paired block, B0, B1 and B2 receive exactly the same:

- workload and source fixture;
- seed;
- operation count;
- deterministic operation identifiers and timestamps;
- fixture key material;
- host allocation and software revision.

The B0/B1/B2 order is deterministically shuffled per block. The order is retained in every process-level and operation-level row.

## Frozen counts

```text
pilot paired blocks:        5 (retained, excluded from confirmatory estimates)
confirmatory paired blocks: 20
baselines per block:        3
confirmatory processes:     60
operations per process:     128
warm-up operations:         8 full B2 operations in every process
bootstrap resamples:        10,000
```

No additional confirmatory blocks may be added to improve the apparent result. A larger sample would require a separately justified, prospectively recorded precision amendment.

## Timing boundaries

A monotonic high-resolution `perf_counter_ns` clock is used.

| ID | Executed interval |
|---|---|
| M0 | source-file read, strict JSON admission, local source checks and source canonicalisation |
| M1 | conventional AuditEvent/Provenance projection and canonical serialisation |
| M2 | TrustEvidence fact construction, commitment and semantic/minimisation validation |
| M3 | TE-JCS unsigned-core canonicalisation and domain-separated core-digest construction |
| M4 | Ed25519 issuer signing, envelope construction, envelope validation and signed-envelope serialisation |
| M5 | local A2 append, receipt/proof construction and storage-proxy update |
| M6 | issuer, receipt, inclusion and retained-checkpoint verification |
| M7 | complete operation path admitted by the selected baseline |

For every process, the runner retains all 128 operation-level M0--M7 observations and reports nearest-rank p50, p95 and p99. For 128 observations, p99 is the 127th ordered observation.

## Size boundaries

Application-byte values are canonical serialised byte counts:

- B0 total = source FHIR bytes;
- B1 total = source FHIR bytes + conventional audit-projection bytes;
- B2 total = source FHIR bytes + conventional audit-projection bytes + complete signed TrustEvidence envelope with receipt.

The signed-envelope, signature-material, receipt and inclusion-proof sizes are also retained separately. The local A2 storage proxy accumulates core-digest bytes, project leaf-input bytes, receipt bytes, inclusion-proof bytes and the current checkpoint representation. It is not a database-storage measurement.

## Primary estimands

The confirmatory analysis reports paired increments for:

- `B1 - B0`: conventional structured-audit increment;
- `B2 - B1`: TrustEvidence plus local-A2 increment;
- `B2 - B0`: total local reference-pipeline increment.

For each comparison it reports the median and mean paired increment, minimum and maximum, and a deterministic percentile-bootstrap 95% interval for the median paired increment. Metrics are process-loop duration, M7 p50/p95/p99, median total application bytes and final local-storage-proxy bytes.

No p-value is required. No negligible-overhead or equivalence claim is permitted because no prospective equivalence margin was defined.

## Failure and exclusion rules

All system-produced failures and slow tails remain in the retained evidence. A process is successful only if:

- every valid operation is accepted;
- the expected stale-signature mutation is rejected for B2;
- no false accept or false reject occurs;
- the source digest remains identical;
- the declared portable-payload scan reports no finding.

No run may be excluded after inspection of its baseline result. Operator or infrastructure corruption would remain archived with a reason and would stop the C5 gate pending an explicit amendment.

## Evidence outputs

```text
results_expected/cmpb_reference/c5_hie_overhead/
├── README.md
├── pilot_runs.csv
├── retained_runs.csv
├── paired_increments.csv
├── aggregate_estimates.csv
├── pilot_operation_timings.jsonl
├── retained_operation_timings.jsonl
├── run_summary.json
├── hardware_profile.json
└── execution_manifest.json
```

The three CSV structures have public Draft 2020-12 row contracts. Derived rows are regenerated from retained process rows during checking. The execution manifest binds source files and output digests.

## Gate criteria

C5 passes only if:

```text
5 pilot blocks retained and excluded
at least 20 complete retained paired blocks
all three baselines present in every block
all valid operations accepted
all expected invalid controls rejected
false accepts = 0
false rejects = 0
source-digest failures = 0
payload-exclusion findings = 0
retained row contracts pass
derived CSV regeneration matches exactly
hosted release-check passes
integrity patch = 0 bytes
```

## Claim ceiling

A passing C5 experiment supports only host- and implementation-bounded estimates of the incremental processing, canonical application-byte and local-storage-proxy costs of the declared W1 B0--B2 pipeline. It does not establish production EHR overhead, hospital service-level acceptability, multi-user concurrency, distributed-system scalability, network cost, database storage, operational key-management cost, organisational cost reduction or deployment readiness.
