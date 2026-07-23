# Phase C5 completion report

## Gate decision

```text
Phase: C5 — paired local B0--B2 incremental-overhead experiment
Scientific corpus: PASS
Decision correctness: PASS
Result contracts: PASS
Retained evidence: PASS
Reviewer traceability: PASS
Temporary materialisation machinery removed: PASS
Post-report hosted validation: PASS
Final repository/release gate: PASS
Scope: one frozen synthetic HIE disclosure, one hosted Linux runner, local Python reference pipeline
Release status: working branch; v2.2.0 has not yet been released
Main branch modified: no
```

C5 supplies bounded empirical evidence for the incremental processing, canonical application-byte and local-storage-proxy effects of adding the complete local TrustEvidence reference path to the same frozen synthetic health-information-exchange case. It does not measure production electronic-health-record overhead, hospital response time, network or database cost, distributed scalability or organisational cost reduction.

The scientific, evidential and repository-mechanics parts of C5 are closed. Hosted workflow `30019941895` ran after the completion report, hostile review and reviewer-evidence registries had been incorporated into the integrity manifests. It reproduced the dedicated C5 check, the complete release contract, the C3 FHIR regression, the C4 security regression and a zero-byte integrity patch on tree `2e511289dc1863077123d4a955cc1f3240386646`.

## Research question

C5 asks:

> What additional local processing, canonical application-byte and local-storage-proxy cost is introduced when the complete TrustEvidence reference path is added to the same frozen synthetic cross-organisational health-information-exchange case?

The answer is expressed through paired `B1–B0`, `B2–B1` and `B2–B0` increments rather than through an unqualified latency value.

## Authoritative execution and repository state

| Item | Value |
|---|---|
| Repository | `antonioclim/TEA-Sim-TrustEvidence` |
| Working branch | `revision/jcis-route-c` |
| Pull request | draft PR #1 |
| Frozen protocol | `docs/route_c/MEASUREMENT_PROTOCOL.md` |
| Frozen instantiation | `docs/route_c/C5_EXECUTION_PLAN.md` |
| Successful confirmatory workflow | `30014318281` |
| Successful workflow head SHA | `91992f02547e6fc549968e83b552c6163ed6684d` |
| Workflow-event merge SHA recorded by the execution manifest | `5550c4792ba18780a56dbd4bd6cf3962c2d64198` |
| Evidence materialisation commit | `8fa54f83ac9dd72524db35d1f57bb019931c69ec` |
| Materialisation artifact digest | `sha256:a94b8c2a7a24583d33f88053832bcf2f8941b162ad07849b0568a8483bee3b7b` |
| First post-synchronisation all-green workflow | `30018761233` |
| First all-green validation tree | `6cc349f82a1bfa656fcdb1794c0bd8dc68546231` |
| Post-report gate-validation workflow | `30019941895` |
| Post-report gate-validation tree | `2e511289dc1863077123d4a955cc1f3240386646` |
| Post-report C5 artifact digest | `sha256:e1125e3eb333b67d15f1d0a5120e0449d18e5c9c818419af496cc6b67fe18b31` |
| Post-report release-check artifact digest | `sha256:fb0fc3006833b44c51fa9e2876d7874859a79e169aa931b76ac58b32c143987b` |
| Post-report integrity artifact digest | `sha256:9a148d22d112428f799e32b824ef725cc86ba138560aa2b6159702d2bfa2685d` |
| Run identifier | `route-c-hie-overhead-001` |
| Software status during measurement | `working-branch-pre-v2.2.0` |

The execution manifest records the GitHub pull-request merge-event SHA because the runner used `GITHUB_SHA` for that field. The workflow checked out the controlled Route C branch, and exact SHA-256 digests for the runner, protocol, source fixtures and outputs are retained. This provenance nuance is reported rather than silently rewritten after measurement.

## Pre-measurement engineering failures

The successful corpus was preceded by failures that occurred before any timed operation:

1. direct execution of the new runner could not resolve the sibling `experiments` module;
2. a diagnostic rerun retained that traceback and produced no C5 output files;
3. the import repair was committed and integrity-synchronised before measurement;
4. one wrapper run stopped before measurement because the repair wrapper was not idempotent;
5. the wrapper was corrected without changing the runner, workload, baselines, counts, estimator or claim ceiling.

These were workflow and packaging defects, not discarded timing observations. No partial timing corpus was used in the confirmatory estimates.

## Frozen workload and baselines

### Workload

The sole confirmatory workload was `W1-HIE-DISCLOSURE`: the complete synthetic disclosure of a versioned `DiagnosticReport` from Synthetic Hospital A to Synthetic Hospital B under Consent version 3, policy version 6 and authorisation decision D-204.

The secondary wearable workload W2 was omitted before confirmatory materialisation under the prospectively stated critical-path clause. No W2 estimate or cross-workload generalisation is available.

### B0 — source processing

B0 reads the frozen source FHIR Bundle, applies the declared local checks and produces canonical source bytes.

### B1 — conventional audit projection

B1 performs B0 and constructs the local `AuditEvent`/`Provenance`-oriented projection. It does not construct or sign a TrustEvidence envelope and does not append to the A2 model.

### B2 — complete local TrustEvidence path

B2 performs B1 and adds:

1. disclosure-event and source-commitment construction;
2. HIE semantic and minimisation checks;
3. unsigned-core canonicalisation and domain-separated digest construction;
4. deterministic TEST-ONLY Ed25519 issuer signing;
5. local A2 append and checkpoint update;
6. receipt, inclusion-path and consistency-proof construction;
7. issuer, receipt, inclusion and retained-checkpoint verification;
8. one stale-signature mutation control after each process sequence.

## Experimental unit and counts

```text
pilot paired blocks retained:          5
pilot process runs:                   15
pilot inclusion in estimates:          excluded
confirmatory paired blocks:           20
baselines per block:                   3
confirmatory process runs:            60
operations per process:              128
retained operation observations:   7,680
full-B2 warm-up operations/process:    8
paired increment rows:                60
aggregate estimate rows:              18
bootstrap resamples:              10,000
```

The independent replicate is one fresh Python process for one baseline within one paired block. Operation-level observations calculate each process's nearest-rank p50, p95 and p99; they are not treated as independent replicates for the aggregate interval.

Within every block, B0, B1 and B2 used the same workload, seed, source fixture, operation count, deterministic identifiers, timestamps and test key material. Baseline order was deterministically shuffled and retained in every row.

## Host and execution boundary

```text
host class:          GitHub-hosted Ubuntu runner
logical CPUs:        4
reported memory:     16,372,444 KiB
architecture:        x86_64
kernel:              Linux 6.17.0-1020-azure
Python:              CPython 3.13.14
cryptography:        49.0.0
jsonschema:          4.26.0
rfc8785:             0.1.4
application network: none
filesystem state:    warmed local fixture access
```

No operational EHR, FHIR server, database, transport connection, message broker, hardware security module or distributed log service was executed in the timed path.

## Decision and integrity results

```text
failed process runs:             0
validation failures:             0
verification failures:           0
false accepts:                   0
false rejects:                   0
expected invalid cases:         25
expected invalid rejections:    25
source-digest failures:          0
payload-exclusion findings:      0
```

All five pilot and twenty confirmatory B2 processes produced their expected stale-signature mutation, and all 25 were rejected. The source digest remained unchanged and the declared portable-payload scan produced no finding.

## Primary paired estimates

All intervals below are deterministic percentile-bootstrap 95% intervals for the median of twenty paired-block increments.

### Complete operation interval M7

| Comparison | p50 increment, ms | 95% interval | p95 increment, ms | 95% interval | p99 increment, ms | 95% interval |
|---|---:|---:|---:|---:|---:|---:|
| B1–B0 | 1.968 | 1.961–1.977 | 2.036 | 2.020–2.044 | 2.129 | 2.059–2.176 |
| B2–B1 | 7.046 | 7.030–7.075 | 7.268 | 7.241–7.329 | 7.583 | 7.452–8.031 |
| B2–B0 | 9.023 | 9.004–9.056 | 9.290 | 9.265–9.354 | 9.668 | 9.543–10.162 |

The p99 paired increments retain the observed tails. B2–B1 ranged from 7.098 to 11.293 ms; B2–B0 ranged from 9.294 to 13.327 ms.

### Process-loop duration for 128 operations

| Comparison | Median increment, ms | 95% interval | Mean increment, ms | Minimum–maximum, ms |
|---|---:|---:|---:|---:|
| B1–B0 | 275.996 | 275.506–277.520 | 276.517 | 270.977–282.230 |
| B2–B1 | 912.091 | 907.795–918.914 | 915.391 | 903.368–946.300 |
| B2–B0 | 1,187.207 | 1,184.322–1,194.523 | 1,191.908 | 1,177.000–1,223.855 |

Process start-up and fixed warm-up are outside these loop-duration increments.

## Application-byte and storage-proxy estimates

For the exact W1 fixture and canonical representation rules:

| Comparison | Median application-byte increment | Local storage-proxy increment after 128 operations |
|---|---:|---:|
| B1–B0 | 11,858 bytes | 0 bytes |
| B2–B1 | 4,347 bytes | 215,339 bytes |
| B2–B0 | 16,205 bytes | 215,339 bytes |

The underlying median totals were:

```text
B0 canonical source bytes:                       5,131
B1 source plus conventional audit projection:  16,989
B2 source plus audit plus complete TE envelope: 21,336
```

The 215,339-byte value is an accumulated project storage proxy, not a database or filesystem measurement. The application-byte values are not network-byte values and exclude transport framing, TLS, compression and retries.

## Interpretation by comparison

### B1–B0

The conventional structured-audit projection added a median 1.968 ms to operation p50 and 11,858 canonical application bytes relative to source processing. This is the local cost of constructing the declared projection, not an operational `AuditEvent` repository cost.

### B2–B1

The complete TrustEvidence and local-A2 path added a median 7.046 ms to operation p50, 4,347 canonical application bytes and the 215,339-byte final storage proxy relative to B1. This isolates the local reference-implementation increment beyond the conventional projection.

### B2–B0

The complete B2 path added a median 9.023 ms to operation p50, 9.290 ms to p95 and 9.668 ms to p99 relative to B0. The corresponding median process-loop increment for 128 operations was 1,187.207 ms, and the exact fixture added 16,205 canonical application bytes.

No prospective negligible-overhead or equivalence margin was defined. These magnitudes are therefore reported without an acceptability judgement.

## Retained evidence

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

The retained corpus is approximately 7.4 MB uncompressed. The three C5 CSV families pass their public Draft 2020-12 contracts. Derived paired and aggregate rows regenerate from retained process rows during `--check`.

The successful materialisation transcript reported:

```text
C5-OVERHEAD-CHECK: PASS
60 retained process runs
7,680 retained raw timings
60 paired increments
18 aggregate estimates
66 reproducibility-manifest rows written
14 result contracts and 691 parsed CSV rows validated
383 file-manifest rows and 384 checksums rebuilt at materialisation
```

The post-report gate-validation workflow `30019941895` reported:

```text
50 unit/regression pytest items passed
8 property-test items passed
29,105 finite bounded checks; zero failures
66 reproducibility-manifest rows current
14 result contracts and 691 parsed CSV rows validated
387 distributed files
386 SHA-256 entries verified
385 file-manifest rows verified
C3-RETAINED-EVIDENCE: PASS
C4-HIE-SECURITY: PASS
C5-OVERHEAD-CHECK: PASS
RELEASE-CHECK: PASS
integrity patch: 0 bytes
```

## Reviewer-closure effect

### Reviewer 1

C5 supplies the requested overhead summary with a necessary correction of scope. The response may report the paired local B0–B2 processing and byte increments for the synthetic W1 case. It must not call them total production-EHR overhead.

### Reviewer 2

C5 provides an explicit Input–Processing–Output empirical chain, retained raw measurements, a frozen estimator and a machine-readable source for every manuscript number. It supports the requested numerical-consistency and methods/results-ordering repairs, which remain manuscript obligations in C7–C8.

### Reviewer 4

C5 supplies bounded evidence for local processing and representation cost. It does not answer large-network scalability, hospital deployability or organisational cost reduction. Those questions remain explicit limitations and, where applicable, C6–C7 discussion obligations.

## Claims now supported

- On the reported host and synthetic W1 case, the declared B0–B2 local reference pipeline produced the retained paired processing increments.
- The complete B2 path added the reported canonical application bytes relative to B0 and B1.
- The local A2 representation produced the reported final storage proxy over 128 operations.
- All retained valid operations passed and all 25 expected stale-signature controls were rejected.
- The pilot blocks were retained and excluded from confirmatory estimates as prospectively specified.

## Claims still prohibited

- total production EHR overhead;
- hospital response time or service-level acceptability;
- negligible or equivalent overhead;
- network capacity or wire-byte cost;
- database, filesystem or cloud-storage cost;
- multi-user concurrency or distributed-system scalability;
- deployment readiness;
- organisational cost reduction;
- generalisation beyond the synthetic W1 case and reported host.

## Final gate closure

```text
Gate C5 = PASS
open C5 scientific blockers = 0
open C5 release-mechanics blockers = 0
additional C5 measurement authorised = no
```

C5 closes only the host- and implementation-bounded W1 local-overhead question. Manuscript integration, component/deployability analysis, release-candidate construction and final reviewer responses remain C6–C8 obligations.
