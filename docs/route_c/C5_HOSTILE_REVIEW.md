# Hostile review of Phase C5

## Audit posture

A hostile reviewer should assume that a locally timed Python reference pipeline can be mistaken for production electronic-health-record overhead, that thousands of operation-level samples can be misreported as independent replicates and that deterministic byte counts can be promoted into network, database or organisational cost claims. This audit therefore asks what the C5 observations actually estimate, which design choices constrain them and which attractive interpretations remain unavailable.

## Evidence examined

- `docs/route_c/MEASUREMENT_PROTOCOL.md`;
- `docs/route_c/C5_EXECUTION_PLAN.md`;
- five retained pilot paired blocks, excluded from confirmatory estimates;
- twenty retained confirmatory paired blocks;
- sixty retained process-level runs;
- 7,680 retained operation-level M0–M7 observations;
- sixty paired B1–B0, B2–B1 and B2–B0 increments;
- eighteen aggregate estimates with deterministic percentile-bootstrap intervals;
- complete execution transcript, hardware disclosure and execution manifest;
- three public Draft 2020-12 C5 result contracts;
- source-fixture, source-file and retained-output digests;
- the pre-measurement import failures and subsequent software repair;
- the post-synchronisation hosted release workflow and zero-byte integrity patch.

## Attack 1 — “The experiment measures total overhead in an operational EHR exchange”

### Finding

The executed path is a single-process Python reference pipeline on one GitHub-hosted Ubuntu runner. It reads a warmed local fixture, performs local computation and opens no application network connection. It does not execute an EHR server, database transaction, message broker, authentication gateway, transport-layer exchange, durable audit store or receiving-hospital workflow.

Process creation, dependency loading and the fixed warm-up are outside M7. `run_duration_ms` is the loop duration for 128 admitted operations after warm-up and state reset, not user-visible hospital response time.

### Verdict

**Local reference-pipeline increment only.** `Total EHR overhead`, `end-to-end hospital latency` and equivalent wording are unsupported.

## Attack 2 — “One workload demonstrates scalability across healthcare networks”

### Finding

The sole confirmatory workload is `W1-HIE-DISCLOSURE`. The secondary wearable batch W2 was omitted before confirmatory materialisation under the frozen critical-path clause; no W2 estimate was generated. There is no multi-tenant concurrency, distributed node, network fan-out, database growth, hospital routing or long-running service state.

### Verdict

**No scalability result.** C5 cannot support generalisation across clinical resource classes, institutions, national infrastructures or large healthcare networks.

## Attack 3 — “The 7,680 operation samples are 7,680 independent replicates”

### Finding

The independent confirmatory unit is one fresh process-level baseline run within one paired block. There are twenty paired blocks and therefore twenty paired increments for each comparison and metric. The 128 operation samples inside a process define that process's nearest-rank p50, p95 and p99; they are not independent observations for the aggregate interval.

### Verdict

**Twenty paired replicates, not 7,680 independent replicates.** Treating operation count as the inferential sample size would be pseudoreplication.

## Attack 4 — “The p50, p95 and p99 values are service-level percentiles”

### Finding

For each process, M7 percentiles summarise 128 sequential operations after an identical full-B2 warm-up and state reset. The p99 is the 127th ordered observation. The aggregate table reports the median paired difference between process-level percentiles across twenty blocks.

No queueing, concurrency, network jitter, database contention, autoscaling or service-level objective was evaluated.

### Verdict

**Within-process operation percentiles only.** They are not hospital p95 or p99 measurements.

## Attack 5 — “B0 is a production FHIR exchange”

### Finding

B0 reads the frozen source Bundle, performs declared local checks and produces canonical source bytes. It does not execute HTTP transport, FHIR server persistence, terminology validation in the timed path, authorisation enforcement or receiver-side clinical processing.

### Verdict

**B0 is a local computational baseline.** B2–B0 is not an increment over an operational FHIR transaction.

## Attack 6 — “B1 is a complete conventional audit implementation”

### Finding

B1 adds local construction and canonical serialisation of the declared `AuditEvent`/`Provenance`-oriented projection. It does not persist, index, transmit or retain those resources and does not execute a security-information-and-event-management pipeline.

### Verdict

**B1 is a structured-audit projection baseline.** B1–B0 is not the cost of an operational conventional audit platform.

## Attack 7 — “B2 measures a production TrustEvidence deployment”

### Finding

B2 uses deterministic TEST-ONLY Ed25519 keys, a project-specific in-memory A2 Merkle model, local receipt construction and in-process verification. It performs no hardware-security-module operation, certificate validation, persistent log write, transaction commit, replicated checkpoint service, key rotation, revocation or recovery operation.

### Verdict

**Reference implementation only.** B2–B1 cannot be converted into production capacity, cost or readiness.

## Attack 8 — “The byte increments are network traffic”

### Finding

The byte measures are canonical serialised application representations. For the exact W1 fixture:

- B1–B0 adds 11,858 canonical application bytes;
- B2–B1 adds 4,347 canonical application bytes;
- B2–B0 adds 16,205 canonical application bytes.

They exclude HTTP headers, TLS records, compression, batching, framing, retries and transport acknowledgements.

### Verdict

**Canonical application-byte increments, not network bytes.** The values are exact only for the retained fixture and representation rules.

## Attack 9 — “The 215,339-byte increment is database storage”

### Finding

The value is a constructed local proxy accumulated over 128 B2 operations. It includes project core-digest bytes, leaf-input bytes, receipt bytes, inclusion-proof bytes and the current checkpoint representation. It excludes database pages, indexes, write-ahead logs, replication, backups, filesystem allocation, encryption metadata and observability.

### Verdict

**Local storage proxy only.** It is not disk consumption, database growth or storage cost.

## Attack 10 — “The bootstrap interval generalises to hospitals”

### Finding

The interval is a deterministic percentile-bootstrap interval for the median of twenty paired-block increments on one host, one software revision and one synthetic workload. It is not a random sample from hospitals, EHR products, clinicians or deployment environments.

### Verdict

**Run- and host-bounded uncertainty summary.** It is not a population confidence interval for healthcare organisations.

## Attack 11 — “Nine milliseconds is negligible overhead”

### Finding

No equivalence, non-inferiority or negligible-overhead margin was prospectively defined. The observed B2–B0 median M7 increment is 9.023 ms at p50, with a 95% bootstrap interval of 9.004–9.056 ms. Acceptability depends on an operational context that C5 did not evaluate.

### Verdict

**Magnitude only; no acceptability judgement.** `Negligible`, `acceptable` and `low overhead` are prohibited without an external margin.

## Attack 12 — “No observed failures proves reliability”

### Finding

All sixty retained process runs passed. Across pilot and confirmatory B2 processes, all 25 expected stale-signature mutations were rejected, with zero false accepts, false rejects, validation failures, verification failures, source-digest failures or declared payload-exclusion findings.

The controls do not model service crashes, partial writes, dependency outages, network partitions, concurrent updates or resource exhaustion.

### Verdict

**Decision correctness for the executed path, not operational reliability.**

## Attack 13 — “Pilot results were used to tune the confirmatory result”

### Finding

Five pilot paired blocks are retained separately and excluded from confirmatory estimates. The confirmatory design remained fixed at twenty paired blocks, three baselines, 128 operations, eight warm-up operations and 10,000 bootstrap resamples. No blocks were added after inspecting the result.

The same author implemented the protocol and runner, and pilot execution necessarily exposed engineering defects and approximate runtime magnitude.

### Verdict

**The exclusion rule is observable and was followed, but common-author and host-allocation risks remain.**

## Attack 14 — “Slow tails were discarded”

### Finding

Every process and operation produced by the successful materialisation is retained. The aggregate table preserves minima, maxima and p99-derived paired increments. B2–B1 p99 increments reached 11.293 ms; B2–B0 reached 13.327 ms.

### Verdict

**Observed tails remain visible.** They still do not characterise production tail latency.

## Attack 15 — “The named phase times must sum exactly to M7”

### Finding

M0–M6 time named sub-operations, whereas M7 times the admitted complete baseline path. Python control flow, instrumentation and uninstrumented glue can make the phase sum differ from M7. Both are retained rather than forced to match.

### Verdict

**M7 is the primary complete-operation interval.** Phase values explain composition only.

## Attack 16 — “The execution manifest identifies a simple branch commit”

### Finding

The execution manifest records `source_commit` from GitHub Actions `GITHUB_SHA`. For the pull-request workflow this is merge-event commit `5550c4792ba18780a56dbd4bd6cf3962c2d64198`, not the human-readable branch-head identifier. Artifact metadata records workflow head SHA `91992f02547e6fc549968e83b552c6163ed6684d`; source-file digests bind exact content, and materialisation commit `8fa54f83ac9dd72524db35d1f57bb019931c69ec` retains the outputs.

### Verdict

**Provenance is recoverable but must be described precisely.** The manifest field does not imply a merge into `main`.

## Attack 17 — “Failed materialisation attempts were adverse timing results”

### Finding

The failed visible attempts stopped before any timed operation because direct script execution could not resolve a sibling module or because the repair wrapper was not idempotent. The runner repair was committed before the successful confirmatory execution. None of those attempts produced a timing corpus.

### Verdict

**Engineering failures, not excluded measurements.** They remain traceable as workflow history.

## Consolidated hostile verdict

C5 is defensible when reported as follows:

> On one GitHub-hosted Ubuntu runner, the frozen synthetic W1 disclosure was evaluated in twenty independent paired process blocks after five excluded pilot blocks. Relative to local source processing, the complete B2 reference path added a median 9.023 ms to operation-level p50, 9.290 ms to p95 and 9.668 ms to p99; the corresponding 128-operation process-loop increment was 1,187.207 ms. The exact fixture added 16,205 canonical application bytes and a 215,339-byte local storage proxy over 128 operations. These are local reference-pipeline estimates, not production EHR, network, database, scalability or organisational-cost results.

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

The scientific C5 corpus satisfies its registered process, decision and result-contract criteria. The temporary materialisation workflow has been removed, reviewer and claim registries have been updated, and hosted workflow `30018761233` passed the dedicated C5 check, complete `make release-check`, C3 and C4 regressions and a zero-byte integrity-diff check on the synchronised pre-report tree.

Final Gate C5 closure requires one last all-green hosted run after this hostile verdict and the completion report are entered into `FILE_MANIFEST.tsv` and `SHA256SUMS.txt`. No further timing collection or empirical amendment is permitted.
