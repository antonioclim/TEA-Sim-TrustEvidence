
# BACKEND_EXECUTION_REPORT.md — backend-evaluation workstream real backend execution

created_utc: `2026-07-05T17:46:02Z`  
scope: backend-evaluation workstream only — A1/A2/A3 backend staging, probing, A2 local execution, benchmark summarisation, tamper testing and archive QA.  
claim_boundary: local reference-implementation evidence only; no production, clinical, legal-compliance or blockchain-service claim.

## 1. backend-evaluation workstream execution verdict

backend-evaluation workstream produced a mixed but useful backend evidence result. The A2 Merkle backend was corrected and executed locally with deterministic synthetic TrustEvidence objects at 1,000 and 10,000 object counts, ten retained repetitions per count and one discarded warm-up run per count. The pytest suite passed, the benchmark harness completed and all seven tamper/prefix/receipt-binding checks passed.

A1 PostgreSQL did not execute in this runtime. The schema and adapter are present, but the probe found no Docker executable, no `psql`, no `TEA_POSTGRES_DSN` and no Python PostgreSQL driver. Therefore no PostgreSQL timing, storage or verification claim is allowed.

A3 Rekor/Trillian/Fabric did not execute in this runtime. The adapter can construct synthetic hash-commitment envelopes, but no local Rekor CLI, Trillian server, Fabric peer or Docker pathway was available. Therefore A3 remains adapter/protocol evidence only.

## 2. Backend execution matrix

| Backend | Execution status | Evidence generated | Public wording allowed | Wording forbidden |
|---|---|---|---|---|
| A1 PostgreSQL | unavailable in current runtime | schema, adapter, probe log | PostgreSQL pathway specified and probed; execution unavailable in this runtime | PostgreSQL benchmark, PostgreSQL measured result, production database performance |
| A2 Merkle | executed locally | tests, benchmark, raw runs, tamper checks, inclusion receipts, proof sizes | local reference-implementation execution for the Merkle backend | production benchmark, cryptographic proof, deployment evidence |
| A3 transparency/ledger-like | adapter-only, not executed | synthetic Rekor-style hash-commitment adapter and probe log | adapter/protocol artefact, not executed backend evidence | local transparency-log execution, Fabric benchmark, blockchain benchmark |

## 3. A2 Merkle timing summary

| Object count | Repetitions | Warm-up discarded | Append p50 ms | Append p95 ms | Verify p50 ms | Verify p95 ms | Median storage bytes | Median receipt bytes | Median proof bytes | Status |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1,000 | 10 | 1 | 0.0117 | 0.0157 | 0.0275 | 0.0372 | 529416 | 1064 | 766 | executed |
| 10,000 | 10 | 1 | 0.0129 | 0.0215 | 0.0427 | 0.0735 | 5293946 | 1372 | 1072 | executed |

Interpretation: these are local Python reference-implementation measurements under the hardware profile included in `HARDWARE_PROFILE.txt`. The numbers may support a manuscript table labelled as local reference execution. They must not be presented as production performance, database performance, blockchain performance or clinical-system latency.

## 4. Tamper and receipt-binding tests

| Case | Property | Expected | Observed | Status |
|---|---|---|---|---|
| T1 | valid_inclusion_receipt | True | True | pass |
| T2 | payload_tamper_rejection | False | False | pass |
| T3 | root_tamper_rejection | False | False | pass |
| T4 | proof_tamper_rejection | False | False | pass |
| T5 | receipt_binding_rejection | False | False | pass |
| T6 | prefix_consistency_valid | True | True | pass |
| T7 | prefix_consistency_wrong_root_rejected | False | False | pass |


All listed tamper/prefix checks passed. These checks are useful reference-implementation evidence, but they are not a full cryptographic proof and do not replace formal/property validation workstream property-based or bounded-formal validation.

## 5. PostgreSQL probe result

The PostgreSQL probe recorded:

```json
{
  "allowable_public_wording": "PostgreSQL schema and adapter were prepared, but PostgreSQL execution was unavailable in the recorded runtime.",
  "backend": "A1_POSTGRES",
  "docker_path": null,
  "docker_version": "not found",
  "dsn_env_name": "TEA_POSTGRES_DSN",
  "dsn_present": false,
  "dsn_value_recorded": false,
  "execution_status": "not_executed",
  "forbidden_wording": "PostgreSQL measured benchmark; production database performance; PostgreSQL validation passed",
  "psql_path": null,
  "psql_version": "not found",
  "python_driver_psycopg2_available": false,
  "python_driver_psycopg_available": false,
  "reason": "Docker, psql or explicit local DSN unavailable"
}
```

A1 remains a blocked execution path in this runtime. A later maintainer run or maintainer environment may execute it only with a disposable local database and redacted DSN handling.

## 6. A3 probe result

The A3 probe recorded:

```json
{
  "allowable_public_wording": "A3 remained an adapter/protocol artefact, not executed backend evidence.",
  "backend": "A3_TRANSPARENCY_LEDGER_LIKE",
  "execution_status": "adapter_only_not_executed",
  "forbidden_wording": "local transparency-log execution; Fabric benchmark; blockchain benchmark; real-world deployment",
  "public_service_submission": "not attempted; synthetic hash commitments only",
  "reason": "No local Rekor/Trillian/Fabric service pathway was available; Docker is required for the supplied container paths and was not found.",
  "tool_status": {
    "docker": {
      "path": null,
      "version_probe": "not found"
    },
    "go": {
      "path": "/usr/local/go/bin/go",
      "version_probe": "go version go1.23.2 linux/amd64"
    },
    "peer": {
      "path": null,
      "version_probe": "not found"
    },
    "rekor-cli": {
      "path": null,
      "version_probe": "not found"
    },
    "trillian_log_server": {
      "path": null,
      "version_probe": "not found"
    }
  }
}
```

A3 remains adapter/protocol evidence only. Public services were not contacted and no health-like raw payloads were submitted to any external transparency log.

## 7. correction note

The backend-evaluation workstream Merkle implementation was corrected before final evidence generation. An initial import-path failure was fixed by making executable scripts add the local `src/` directory to `sys.path`; a Merkle root/proof mismatch for non-power-of-two tree sizes was fixed by aligning carried-odd tree construction, frontier-root bagging and proof generation. The final command log, pytest run, timing summary and tamper results were generated after this correction.

## 8. Claim-evidence decision

The backend workstream now supports a **strong design-science/reference-implementation backend section** centred on A2. It does not yet support the preferred evidence-supported claim involving executed A1 PostgreSQL plus A2 Merkle plus A3 transparency/ledger-like backend comparison. workload-calibration workstream may proceed, but the manuscript must either demote A1/A3 or await execution evidence from a suitable PostgreSQL/Docker/service environment.
