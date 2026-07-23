# Route C C5 local incremental-overhead evidence

This directory retains the process-level paired B0--B2 experiment for the
selected frozen synthetic workload(s). Pilot runs are retained but excluded
from the confirmatory estimates.

## Frozen execution

- pilot paired blocks: 5
- retained paired blocks: 20
- baselines per block: B0, B1 and B2
- confirmatory workloads: W1-HIE-DISCLOSURE
- secondary workload status: W2 was omitted from confirmatory materialisation under the frozen critical-path clause; no W2 overhead estimate is claimed
- operation samples per process-level run: 128
- identical full-path warm-up operations per process: 8
- confidence interval: deterministic percentile bootstrap over independent paired-block increments

## Baselines

- B0 parses, locally validates and canonicalises the frozen source FHIR case.
- B1 performs B0 and constructs the conventional AuditEvent/Provenance projection.
- B2 performs B1 and adds fact extraction, minimisation/semantic validation,
  TE-JCS canonicalisation, Ed25519 issuer signing, local A2 append/receipt,
  inclusion/consistency material and complete verification.

## Evidence files

- `pilot_runs.csv`: process-level pilot summaries, excluded from confirmatory analysis;
- `retained_runs.csv`: process-level retained summaries;
- `paired_increments.csv`: B1-B0, B2-B1 and B2-B0 paired differences;
- `aggregate_estimates.csv`: median paired increments and 95% bootstrap intervals;
- `pilot_operation_timings.jsonl` and `retained_operation_timings.jsonl`: raw operation-level measurements;
- `run_summary.json`: counts, correctness decisions and claim boundary;
- `hardware_profile.json`: host and software disclosure;
- `execution_manifest.json`: source commit, workflow provenance and file digests.

## Claim boundary

The retained values estimate processing, application-byte and local-storage-
proxy increments in the declared Python reference pipeline on the reported
host. They do not estimate production EHR overhead, hospital latency, network
capacity, distributed-service scalability, organisational cost reduction or a
service-level guarantee. No equivalence or negligible-overhead margin was
preregistered; therefore no such claim is made.
