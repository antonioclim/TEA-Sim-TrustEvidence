# Hostile review of Phase C5

## Audit posture

A hostile reviewer should assume that a locally timed Python reference pipeline can be mistaken for production electronic-health-record overhead, that many operation-level samples can be misreported as independent replicates and that deterministic byte counts can be promoted into network, database or organisational cost claims. This audit therefore asks what the C5 observations actually estimate, which design choices constrain them and which apparently attractive interpretations remain unavailable.

## Evidence examined

- `docs/route_c/MEASUREMENT_PROTOCOL.md`;
- `docs/route_c/C5_EXECUTION_PLAN.md`;
- the retained five pilot and twenty confirmatory paired blocks;
- sixty retained process-level runs;
- 7,680 retained operation-level M0--M7 observations;
- sixty paired B1--B0, B2--B1 and B2--B0 increments;
- eighteen aggregate estimates with deterministic percentile-bootstrap intervals;
- the complete execution transcript, hardware disclosure and execution manifest;
- the three public Draft 2020-12 C5 result contracts;
- the source fixture, source-file digests and retained output digests;
- the first pre-measurement import failure and subsequent software repair.

## Attack 1 — “The experiment measures the total overhead added to an operational EHR exchange”

### Finding

The executed path is a single-process Python reference pipeline on one GitHub-hosted Ubuntu runner. It reads a warmed local fixture, performs local computation and opens no application network connection. It does not execute an EHR server, terminology service in the timed interval, database transaction, message broker, authentication gateway, transport-layer exchange, durable audit store or receiving-hospital workflow.

Process creation, dependency loading and the fixed warm-up are outside M7. The retained `run_duration_ms` is the loop duration for 128 admitted operations after warm-up and state reset, not user-visible hospital response time.

### Verdict

**Local reference-pipeline increment only.** The phrases `total EHR overhead`, `end-to-end hospital latency`, `exchange response time` and equivalents are not supported.

## Attack 2 — “One successful workload demonstrates scalability across healthcare networks”

### Finding

The sole confirmatory workload is `W1-HIE-DISCLOSURE`, the complete synthetic C3 disclosure case. The secondary wearable batch, W2, was omitted before confirmatory materialisation under the frozen critical-path clause; no W2 estimate was generated. The experiment contains no multi-tenant concurrency, distributed nodes, network fan-out, database growth, hospital-to-hospital routing or long-running service state.

### Verdict

**No scalability result.** C5 estimates one bounded local workload. It cannot support generalisation across clinical resource classes, institutions, national infrastructures or large healthcare networks.

## Attack 3 — “The 7,680 operation samples provide 7,680 independent replicates”

### Finding

The independent confirmatory unit is one fresh process-level baseline run within one paired block. There are twenty retained paired blocks and therefore twenty independent paired increments for each comparison and metric. The 128 operation samples inside a process define that process's nearest-rank p50, p95 and p99; they are not treated as independent observations for the paired confidence interval.

### Verdict

**Twenty paired replicates, not 7,680 independent replicates.** Reporting operation count as the inferential sample size would be pseudoreplication.

## Attack 4 — “The p50, p95 and p99 values are service-level latency percentiles”

### Finding

For each process, M7 percentiles summarise 128 sequential operations after an identical full-B2 warm-up and state reset. The p99 is the 127th ordered observation. The aggregate table then reports the median paired difference between process-level percentiles across twenty blocks.

No queueing, concurrency, network jitter, database contention, garbage-collection policy comparison, autoscaling or service-level objective was evaluated.

### Verdict

**Within-process operation percentiles only.** They are useful for comparing the three local baselines under the frozen design, not for claiming a hospital p95 or p99.

## Attack 5 — “The B0 baseline is a production FHIR exchange”

### Finding

B0 reads the frozen source Bundle, performs the declared local checks and produces canonical source bytes. It does not execute HTTP transport, FHIR server persistence, terminology validation, authorisation, access-control enforcement or receiver-side clinical processing.

### Verdict

**B0 is a local computational baseline.** B2--B0 is a total increment over that baseline, not an increment over an operational FHIR transaction.

## Attack 6 — “B1 is a complete conventional healthcare auditing implementation”

### Finding

B1 adds the local construction and canonical serialisation of the declared AuditEvent/Provenance-oriented projection. It does not persist those resources, index them, transmit them, enforce retention, execute a security-information-and-event-management pipeline or model vendor-specific audit infrastructure.

### Verdict

**B1 is a structured-audit projection baseline.** B1--B0 estimates the additional local construction cost and canonical application bytes of that projection, not the cost of an operational conventional audit platform.

## Attack 7 — “B2 measures a production TrustEvidence deployment”

### Finding

B2 uses deterministic TEST-ONLY Ed25519 keys, a project-specific in-memory A2 Merkle model, local receipt construction and in-process verification. It performs no hardware-security-module operation, certificate validation, persistent log write, transaction commit, replicated checkpoint service, key rotation, revocation, access-control decision or recovery operation.

### Verdict

**Reference implementation only.** The B2--B1 increment cannot be converted into production deployment cost, capacity or readiness.

## Attack 8 — “The byte increments are network traffic”

### Finding

The byte measures are canonical serialised application representations. For the exact W1 fixture:

- B1--B0 adds 11,858 canonical application bytes;
- B2--B1 adds 4,347 canonical application bytes;
- B2--B0 adds 16,205 canonical application bytes.

They exclude HTTP headers, TLS records, compression, batching, framing, retries, transport acknowledgements and implementation-specific wire formats.

### Verdict

**Canonical application-byte increments, not network-byte measurements.** The fixed values are exact for the retained fixture and representation rules only.

## Attack 9 — “The 215,339-byte storage increment is database storage”

### Finding

The storage value is an explicitly constructed local proxy accumulated over 128 B2 operations. It includes project core-digest bytes, leaf-input bytes, receipt bytes, inclusion-proof bytes and the current checkpoint representation. It excludes database pages, indexes, write-ahead logs, replication, backups, filesystem allocation, encryption metadata, retention overhead and operational observability.

### Verdict

**Local storage proxy only.** It must not be reported as disk consumption, database growth or storage cost.

## Attack 10 — “The bootstrap interval generalises to hospitals”

### Finding

The interval is a deterministic percentile-bootstrap interval for the median of twenty paired-block increments on one host, one software revision and one synthetic workload. It quantifies the stability of the observed paired increments under that resampling procedure. It is not a random sample from hospitals, EHR products, clinicians, institutions or deployment environments.

### Verdict

**Run- and host-bounded uncertainty summary.** It is not a population confidence interval for healthcare organisations.

## Attack 11 — “The timing result proves negligible overhead”

### Finding

No equivalence, non-inferiority or negligible-overhead margin was prospectively defined. The observed B2--B0 median M7 increment is approximately 9.023 ms per local operation, with a 95% bootstrap interval of approximately 9.004--9.056 ms. Whether that value is acceptable depends on an operational context that C5 did not evaluate.

### Verdict

**No negligible or acceptable-overhead claim.** C5 reports magnitude; it does not supply a service-level judgement.

## Attack 12 — “The absence of failures proves reliability”

### Finding

All 60 retained process runs passed; the complete pilot-plus-confirmatory sequence produced 25 expected stale-signature mutation cases and rejected all 25, with zero false accepts, false rejects, validation failures, verification failures, source-digest failures or declared payload-exclusion findings.

The controls exercise the exact synthetic path and declared mutation. They do not model service crashes, partial writes, dependency outages, corrupted durable state, network partitions, concurrent updates or adversarial resource exhaustion.

### Verdict

**Decision correctness for the executed path, not operational reliability.**

## Attack 13 — “The pilot results were used to tune the confirmatory result after inspection”

### Finding

Five pilot paired blocks are retained in separate files and excluded from the confirmatory estimates. The confirmatory design remained fixed at twenty paired blocks, three baselines, 128 operations, eight warm-up operations and 10,000 bootstrap resamples. No additional confirmatory blocks were added after inspecting the result.

### Residual risk

The same author implemented the runner and protocol, and the host allocation was not under experimental control. Pilot execution can reveal engineering defects and runtime magnitude even when excluded statistically.

### Verdict

**The exclusion rule is observable and was followed.** This reduces, but does not eliminate, researcher-degrees-of-freedom concerns.

## Attack 14 — “Slow tails were discarded”

### Finding

The retained rows include every process and operation produced by the successful confirmatory materialisation. The aggregate table retains minima, maxima and p99-derived paired increments. In particular, the B2--B1 p99 increment ranged up to 11.293 ms and the B2--B0 p99 increment ranged up to 13.327 ms, even though their median paired increments were lower.

### Verdict

**The observed slow tails remain visible.** They are not sufficient to characterise production tail latency, but they must not be omitted from the supplement or number registry.

## Attack 15 — “The timing phases sum exactly to the complete operation interval”

### Finding

M0--M6 time named sub-operations, whereas M7 times the admitted complete baseline path. Instrumentation, Python control flow and uninstrumented glue can make the M0--M6 sum differ from M7. C5 retains both `m7_sum_ms` and the M7 interval rather than asserting identity.

### Verdict

**M7 is the primary complete-operation interval.** Phase values explain composition but should not be arithmetically forced to equal M7.

## Attack 16 — “The execution manifest identifies a simple branch commit”

### Finding

The execution manifest records `source_commit` from the GitHub Actions `GITHUB_SHA` environment. For a pull-request workflow this is the workflow-event merge commit, `5550c4792ba18780a56dbd4bd6cf3962c2d64198`, rather than the human-readable branch-head identifier. The artifact metadata separately records the workflow head SHA, and the manifest retains SHA-256 digests for the runner, protocol and source fixtures. The materialisation commit retains the exact result files and their digests.

### Verdict

**Provenance is recoverable but must be described precisely.** The manifest field is a PR merge-event commit, not evidence that the main branch was modified or that the measurement ran after merge. Source-file digests are the strongest exact-content binding.

## Attack 17 — “The first failed materialisation was an adverse performance result that was hidden”

### Finding

The first two visible materialisation attempts failed before any timed operation because direct script execution could not resolve the sibling `experiments` module. A subsequent wrapper attempt also stopped before measurement because the repair wrapper was not idempotent. The runner repair was committed before the successful confirmatory execution. None of those failed attempts produced a timing corpus.

### Verdict

**Engineering failures, not excluded measurements.** They should remain traceable as workflow history but do not constitute omitted performance observations.

## Consolidated hostile verdict

C5 is defensible when reported as follows:

> On one GitHub-hosted Ubuntu runner, the frozen synthetic W1 disclosure was evaluated in twenty independent paired process blocks after five excluded pilot blocks. Relative to local source processing, the complete B2 reference path added a median 9.023 ms to the operation-level p50, 9.290 ms to p95 and 9.668 ms to p99; the corresponding 128-operation process-loop increment was 1,187.207 ms. The exact fixture added 16,205 canonical application bytes and a 215,339-byte local storage proxy over 128 operations. These are local reference-pipeline estimates, not production EHR, network, database, scalability or organisational-cost results.

C5 is not defensible if reduced to:

```text
TrustEvidence adds only 9 ms to an EHR exchange
negligible overhead
production-ready performance
scales to large hospital networks
16 KB network cost
215 KB database storage
cost reduction demonstrated
```

## Gate condition

The scientific C5 corpus satisfies its registered process, decision and result-contract criteria. Final Gate C5 closure additionally requires removal of temporary materialisation machinery, current integrity files, claim-ledger updates, one clean hosted C5 validation and one all-green complete `make release-check` on the final synchronised branch tree.
