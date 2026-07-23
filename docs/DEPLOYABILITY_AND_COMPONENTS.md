# Component and deployability inventory

## Purpose

This inventory separates what the v2.2.0 release candidate implements from what an operational hospital deployment would still require. It supports architectural assessment without converting a reference implementation into a hospital-readiness claim.

## Implemented components

| Component | Repository location | Executed evidence | Maturity boundary |
|---|---|---|---|
| Closed monitoring schemas and validators | `src/trustevidence/schemas`, `schema.py`, `validators.py` | unit, mutation and retained result-contract checks | reference profile; not a clinical data standard |
| HIE disclosure schema and semantic checks | `hie.py`, `hie_validation.py`, HIE schemas | complete synthetic hero case; positive/negative semantic checks | one bounded disclosure profile |
| Canonicalisation and commitments | `canonical.py`, `crypto.py`, `hashing.py` | deterministic vectors and controlled mutations | application profile; no confidentiality or clinical-truth claim |
| Issuer signatures | `crypto.py`, `hie.py` | authorised-key verification and unauthorised-mutation rejection | deterministic TEST-ONLY trust registries |
| Local A2 Merkle model | `backends/a2_merkle.py`, `hie_state.py` | inclusion, consistency, rollback/fork visibility and limitation cases | in-memory/local model; not a persistent transparency service |
| FHIR R4 projection | `standards/fhir_ig` | SUSHI, IG Publisher and HL7 FHIR Validator results for the declared corpus | no HL7/IHE certification or universal conformance |
| C4 adversarial programme | `run_hie_security_mutations.py` | 67 registered cases with explicit limitation acceptances | bounded registered attacks; not operational penetration testing |
| C5 incremental experiment | `run_hie_incremental_overhead.py` | paired W1 B0-B2 local processing and representation increments | one host, one synthetic workload, no network/database/concurrency |
| Reproducibility and release controls | `Makefile`, `scripts`, CI workflow | manifests, result contracts, fresh extraction and archive checks | environment- and version-bounded |

## Required operational integration points not supplied

| Operational concern | Required production capability | Candidate status |
|---|---|---|
| FHIR exchange | authenticated FHIR server/client endpoints, routing and transaction handling | not implemented or timed |
| Identity | workforce/patient/service identity proofing and federation | tokens and roles are deterministic fixtures |
| Consent and policy | authoritative consent service, policy decision point and version lifecycle | synthetic Consent/policy/decision bindings only |
| Key management | HSM/KMS, certificate issuance, rotation, revocation, compromise recovery | absent |
| Confidentiality | TLS configuration, encryption at rest, secret management and access isolation | not evaluated |
| Durable custody | transactional database/log persistence, indexing, backup, retention and deletion | absent; C5 storage value is a project proxy |
| Concurrency and scale | multi-user load, queues, replicas, partition behaviour, autoscaling and capacity planning | not evaluated |
| Availability | failover, retry, idempotency, partial-write recovery and disaster recovery | not evaluated |
| Observability | operational metrics, alerts, audit review workflow and incident response | not implemented |
| Governance | data-controller/processor roles, legal basis, DPIA, policy ownership and operating procedures | outside the software claim |
| Independent witnessing | public transparency, gossip, witness quorum or external checkpoint federation | absent |
| Clinical safety | clinical validation, human factors, safety case and patient-impact assessment | absent |

## Deployment interpretation

The candidate demonstrates that a declared evidence object can be constructed, signed, projected, appended and checked in a local reference path. It does not establish that a hospital can deploy the approach without material integration work. A realistic deployment study would need an explicit architecture, threat model, operating model, service-level criteria, representative concurrent workloads, key lifecycle, durable storage, security testing and organisational evaluation.

## Cost and complexity interpretation

C5 measures local processing and canonical representation increments; this inventory identifies added components. Neither establishes organisational cost reduction. The approach may reduce some dispute-reconstruction effort while adding signature, receipt, key-management, storage and governance work. Those opposing effects require empirical organisational study and must not be collapsed into a cost-saving claim.
