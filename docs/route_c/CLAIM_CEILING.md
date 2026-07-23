# Route C claim ceiling

## Purpose

This document defines the strongest wording that the emergency JCIS revision may use. A claim becomes available only after the required evidence has been executed on the release candidate used for the manuscript. Repository availability, schema presence, planned tests and adapter code are not execution evidence.

## Claim rules

1. Every manuscript claim must identify an artefact, an executed method, an environment and a limitation.
2. A signature authenticates a declared statement under the applicable key assumptions; it does not establish factual or clinical truth.
3. A receipt signature authenticates a backend statement under the applicable key assumptions; it does not establish backend honesty, truthful tree size, actual log population or event completeness.
4. A cryptographic commitment binds declared bytes; it is not encryption, anonymisation or proof that those bytes are clinically correct.
5. Merkle inclusion establishes membership relative to a declared local tree statement; it does not establish event completeness, occurrence uniqueness, truthful tree population or universal non-equivocation.
6. A retained-checkpoint comparison may expose rollback or a same-size divergent root to that verifier; it does not prevent a malicious operator from showing different views to isolated parties.
7. Exact same-state replay is accepted by the bounded verifier; freshness and duplicate suppression are higher-layer controls.
8. A SUSHI build is not FHIR conformance. Official-validator wording is permitted only for the exact corpus, package versions and tools that were executed.
9. Synthetic or public-derived data are not operational patient deployment evidence.
10. Local timing results describe the measured reference pipeline and host; they are not production estimates.

## Conditional claims

| Claim ID | Permitted wording after evidence passes | Required evidence | Mandatory qualification |
|---|---|---|---|
| RC-C01 | TrustEvidence operationalises a field-level audit-evidence boundary | schema, field registry, hero case and field-deletion analysis | boundary remains a reference profile, not a standard |
| RC-C02 | The declared synthetic disclosure case produced a complete signed TrustEvidence envelope | retained case inputs, envelope, signature verification and provenance | no clinical-truth or real-patient claim |
| RC-C03 | The executed FHIR R4 examples passed the declared validator toolchain | SUSHI, IG Publisher or Validator logs as declared, positive and negative corpus | no HL7 or IHE certification claim |
| RC-C04 | The envelope uses RFC 8785 canonicalisation under the TE application profile | cross-run vectors and current implementation tests | application profile, not a universal FHIR canonical form |
| RC-C05 | The issuer signature rejected the declared unauthorised statement mutations | signature mutation suite | authorised re-signing remains acceptable and does not prove statement truth |
| RC-C06 | Payload commitments detected the reported changes when the retained nonce and payload bytes were supplied | commitment mutation tests | commitment is neither encryption nor clinical validation |
| RC-C07 | The local A2 model rejected the registered inconsistent receipt and retained-state cases and reported its expected limitation acceptances | receipt, proof, checkpoint, limitation and mutation results | local project-specific model; no truthful-tree-size, completeness or public-transparency claim |
| RC-C08 | No forbidden clinical fields were identified by the executed scans | package, log, result and evidence scans | absence is limited to the declared scan corpus and rules |
| RC-C09 | The B0-B2 experiment measured local incremental processing and message-size overhead | preregistered inputs, at least 20 independent runs, raw data, p50/p95/p99 | not total production EHR overhead |
| RC-C10 | The exact release was reproducible under the declared fresh-extraction procedure | CI, fresh extraction, manifests, checksums and regenerated outputs | environment- and version-bounded |

## Claims prohibited in Route C

The manuscript, supplement, repository, release notes and reviewer response must not state or imply:

- FHIR compliance, universal FHIR conformance or HL7 certification;
- BALP conformance or IHE certification unless an exact applicable profile is officially validated and the wording is correspondingly narrow;
- SCITT conformance or RFC 9942 receipt conformance;
- a production transparency service or blockchain deployment;
- production readiness or hospital readiness;
- measured organisational cost reduction;
- improved organisational trust;
- complete event capture or complete audit trails;
- truthful tree size or actual log population proven by a receipt;
- replay prevention;
- prevention of equivocation, rollback or key compromise;
- clinical validity, clinical truth or patient safety;
- GDPR, EHDS, ISO or other legal/regulatory compliance;
- formal verification;
- expert validation or consensus;
- scalability to large healthcare networks;
- superiority over all FHIR or healthcare-audit implementations.

## Wording controls

| Avoid | Use instead |
|---|---|
| secure | the specified property was verified under the declared assumptions |
| immutable | append-only behaviour was observed in the local reference model |
| encrypted by hashing | committed by a cryptographic digest; no confidentiality claim |
| tamper-proof | the final registered unauthorised mutations were rejected and limitation acceptances were reported |
| receipt proves the log contained N events | the authorised backend receipt asserted tree size N; actual log population was not independently established |
| FHIR compliant | the reported examples passed the named FHIR validation toolchain |
| real-world validation | synthetic or public-derived case evaluation |
| total EHR overhead | total local reference-pipeline increment over the declared baseline |
| trust improvement | attributable, context-bound audit evidence |
| complete audit trail | completeness was not established |
| expert validated | no expert-validation result is claimed |

## Demotion rule

If a required test or validator is absent, fails, or is not reproducible on the release candidate, the associated claim is either removed or rewritten as a limitation. A failure must not be hidden in repository documentation while the manuscript retains the stronger wording. When an empirical result falsifies a preregistered expected rejection, the original failure must remain traceable and the final protocol must identify the resulting limitation rather than silently redefining it as a security success.
