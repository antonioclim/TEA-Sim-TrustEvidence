# Route C local incremental measurement protocol

## Purpose

The Route C experiment answers a narrow question: what additional local processing and message-size cost is introduced when the complete TrustEvidence reference path is added to the same synthetic health-information-exchange case?

The experiment is not a production EHR benchmark, a hospital deployment study, a network-capacity study or a comparison of distributed transparency services.

## Baselines

### B0 — Source FHIR processing

B0 loads the frozen synthetic source case, validates the source resources under the declared local rules and serialises the source resource set required by the case.

### B1 — Conventional audit projection

B1 performs B0 and constructs the declared FHIR R4 audit projection, including the applicable AuditEvent and Provenance resources and the portable evidence bundle. B1 does not construct or sign a TrustEvidence envelope and does not append to the local A2 model.

### B2 — Complete local TrustEvidence path

B2 performs B1 and additionally:

1. extracts the declared TrustEvidence facts;
2. applies minimisation and semantic checks;
3. canonicalises the evidence core under TE-JCS;
4. signs the evidence core with the test issuer key;
5. appends the evidence-core digest to the local A2 Merkle model;
6. generates the signed structural receipt and inclusion path;
7. verifies the evidence-core signature, receipt binding, inclusion path and retained checkpoint.

The same source case, seed, timestamps and object bytes must be used for B0, B1 and B2 within each independent run.

## Workloads

### W1 — Cross-organisational disclosure

A synthetic Hospital A to Hospital B disclosure of a versioned DiagnosticReport and associated observations, authorised for treatment under a versioned consent and policy decision.

### W2 — Wearable monitoring batch

A synthetic batch representation of monitoring observations. Raw observations remain outside portable audit evidence; a count, interval, provenance context and commitment are used instead.

W1 is the primary workload. W2 is secondary and may be omitted only if the Route C critical path is threatened; any omission must be reported before manuscript freeze.

## Experimental unit

The primary replicate is an independent process-level run, not an individual timed operation. Request or operation samples inside a run may estimate within-run percentiles but do not increase the number of independent replicates.

## Repetitions

- pilot: five independent runs, excluded from confirmatory summaries;
- retained experiment: at least twenty independent runs per baseline and workload;
- the same randomised baseline order is applied within paired blocks;
- additional runs may be added only for a documented precision reason, not to obtain a favourable significance result.

## Warm-up

Each process performs a fixed warm-up sequence that exercises parsing, schema loading, canonicalisation, signing, receipt generation and verification. Warm-up observations are discarded. The warm-up definition and count are fixed before retained data collection.

## Timing boundaries

| ID | Interval |
|---|---|
| M0 | source load and validation |
| M1 | FHIR audit projection and serialisation |
| M2 | TrustEvidence extraction and semantic validation |
| M3 | RFC 8785 canonicalisation |
| M4 | issuer signing |
| M5 | local A2 append and receipt construction |
| M6 | statement, receipt and checkpoint verification |
| M7 | complete B0, B1 or B2 path |

A monotonic high-resolution clock is required. Wall-clock timestamps must not be subtracted to calculate latency.

## Metrics

### Latency

For every retained independent run:

- p50 of operation-level latency;
- p95;
- p99, provided the run contains enough observations to make the percentile interpretable;
- run duration;
- failure and retry count.

The manuscript reports the distribution of run-level summaries and does not pool all operations as independent experimental replicates.

### Message and artefact size

- source FHIR bytes;
- audit-projection bytes;
- TrustEvidence envelope bytes;
- signature material bytes;
- local receipt bytes;
- inclusion-proof bytes;
- total B0, B1 and B2 application bytes.

### Storage proxy

The local A2 storage proxy includes retained core digests, leaf inputs, receipt bytes, proof bytes and checkpoint data. It is not a database-storage measurement and must be labelled accordingly.

### Correctness

- number of successful valid cases;
- number of expected invalid cases rejected;
- false accepts;
- false rejects;
- digest and byte-preservation checks;
- payload-exclusion findings.

## Analysis

Primary comparisons are paired increments:

- `B1 - B0`: structured audit-projection increment;
- `B2 - B1`: TrustEvidence and local A2 increment;
- `B2 - B0`: total local reference-pipeline increment.

The analysis reports point estimates and 95% confidence intervals generated from independent run-level summaries. p-values are not required for the Route C claim. No equivalence or negligible-overhead claim is permitted without a prospectively justified margin.

## Failure handling

System-produced timeouts, verification failures, errors and slow tails remain in the retained data. Runs may be excluded only for documented external measurement corruption or operator/configuration error identified before inspection of the condition result. Excluded raw data remain archived with an exclusion reason.

The following are prohibited:

- selecting the best run;
- deleting tails;
- winsorisation or sigma clipping;
- combining pilot and retained data;
- changing the baseline definition after seeing results;
- entering numbers manually into manuscript tables;
- describing local B2 results as total production EHR overhead.

## Raw-data and provenance requirements

Every run must record:

- run ID and paired-block ID;
- software version and Git commit;
- Python and dependency versions;
- host and operating-system profile;
- workload and seed;
- baseline;
- warm-up count;
- operation count;
- raw timings;
- message sizes;
- failures;
- start and end time;
- file checksums.

Raw data are immutable after collection. Tables and figures are generated from retained data through versioned scripts.

## Claim ceiling

Successful execution supports local, reference-environment estimates of the incremental processing and message-size cost of the declared B0-B2 pipeline. It does not establish production performance, hospital service-level acceptability, distributed-system scalability, organisational cost reduction or deployment readiness.
