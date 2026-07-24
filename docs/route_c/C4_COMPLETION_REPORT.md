# Phase C4 completion report

## Gate decision

```text
Phase: C4 — security, encryption boundary and adversarial Route C programme
Decision: PASS
Open C4 blockers: 0
Scope: exact synthetic HIE profile, deterministic test trust configuration and project-specific local A2 verifier
Release status: working branch; v2.2.0 has not yet been released
Main branch modified: no
```

C4 establishes a deterministic, retained and hosted mutation programme for the exact Route C healthcare case. It supports property-specific unauthorised-mutation, commitment, receipt-binding and retained-state claims. It also establishes explicit negative results: authorised signatures do not prove statement truth; an authorised backend receipt does not prove truthful tree size or event completeness; a stateless verifier does not detect a coherent split view; and exact same-state replay is accepted.

The exact closure workflow and artifact digests are recorded in draft PR #1 after this report and its integrity manifests are present on the tested branch head. This avoids a self-referential report update that would itself invalidate the cited branch-head workflow.

## Authoritative repository state

| Item | Value |
|---|---|
| Repository | `antonioclim/TEA-Sim-TrustEvidence` |
| Working branch | `revision/jcis-route-c` |
| Pull request | draft PR #1 |
| Original failed C4 run | `30005609826` |
| Original failed case | `RSIG-005` |
| Original failed artifact digest | `sha256:7e4835bac2606f52dc9e62131aab682c91fe2b65eab1fe4eed4d07d4e53d4799` |
| Final evidence materialisation commit | `f12804bcb52d23d16c0706b329e38bea7052b5a6` |
| Baseline public metadata during C4 | v2.1.0 |
| Target release | provisionally v2.2.0, pending C5–C6 |

## Implemented artefacts

### Stateful HIE verifier

`src/trustevidence/hie_state.py` introduces an in-memory retained-checkpoint wrapper. It delegates complete cryptographic and semantic verification to the existing HIE verifier and advances state only after acceptance. It supports:

- initial checkpoint establishment;
- same-checkpoint confirmation;
- rollback rejection;
- verifier-visible same-size fork rejection;
- consistency-proof requirement for larger states;
- valid prefix-extension advancement;
- non-advancement after rejection.

It does not provide durable persistence, transactions, crash recovery, concurrency control, gossip, witnessing, duplicate suppression or public transparency.

### Deterministic adversarial runner

`experiments/run_hie_security_mutations.py` generates the exact retained C4 corpus and verifies it without relying on manually entered result rows.

### Retained evidence

```text
results_expected/cmpb_reference/c4_hie_security/
├── README.md
├── hie_security_mutation_results.csv
├── hie_security_mutation_run.json
└── hie_security_case_evidence.jsonl
```

The CSV is validated by the public mutation-row JSON Schema. The JSONL retains candidate and consistency-proof digests, observed codes and checkpoint snapshots.

### Governance and claim controls

```text
docs/route_c/C4_SECURITY_PROTOCOL.md
docs/route_c/C4_ATTACK_REGISTER.csv
docs/route_c/C4_PROTOCOL_DEVIATION.md
docs/route_c/C4_SECURITY_AND_ENCRYPTION_BOUNDARY.md
docs/route_c/C4_HOSTILE_REVIEW.md
docs/route_c/CLAIM_CEILING.md
docs/route_c/CLAIM_EVIDENCE_LEDGER.csv
docs/route_c/REVIEWER_TRACEABILITY.md
```

## Final decision corpus

The final amended corpus contains:

```text
case count:                       67
passed decisions:                 67
failed decisions:                  0
expected rejections:              54
observed expected rejections:     54
false accepts:                     0
expected acceptances:             11
false rejects:                     0
expected-absence controls:         2
limitation acceptances:            6
rejected state cases:              8
state non-advancement failures:    0
portable test nonce exposed:   false
declared clinical marker exposed: false
```

### Case-class distribution

| Case class | Count |
|---|---:|
| Signed-core mutations | 18 |
| Receipt mutations | 12 |
| Retained-checkpoint controls | 10 |
| Payload-commitment controls | 7 |
| Re-signed malformed-receipt controls | 7 |
| Explicit limitation observations | 6 |
| Portable-custody controls | 2 |
| Trust-registry controls | 2 |
| Positive controls | 2 |
| Receipt/core replay control | 1 |

## Issuer-statement results

The final corpus rejects unauthorised or stale-signature changes to:

- actor token;
- actor organisation;
- actor role;
- emitter organisation;
- Consent version;
- invalid Consent state;
- policy version;
- policy digest;
- authorisation-decision reference;
- outcome reason;
- DiagnosticReport reference and version;
- provenance reference;
- frozen recipient;
- frozen purpose;
- unknown critical field;
- issuer-signature bytes;
- unknown issuer key;
- missing issuer signature;
- correct key identifier mapped to wrong key material.

Three deliberately re-signed alternatives are accepted. These limitation cases establish that a valid issuer signature authenticates the issuer statement but does not independently prove actor identity, Consent truth or policy truth.

## Payload-commitment and custody results

One positive commitment case verified the exact canonical source Bundle and deterministic test nonce.

Six negative controls were rejected:

1. changed payload byte;
2. alternate JSON serialisation;
3. changed nonce;
4. changed representation profile;
5. changed commitment context;
6. nonce shorter than 128 bits.

Two expected-absence checks found neither:

- the deterministic test nonce; nor
- the declared source-clinical markers

in the inspected signed portable envelope and positive Portable Evidence Bundle.

These results establish exact-byte commitment behaviour for the retained fixture. They do not establish encryption, confidentiality, anonymity, clinical correctness or operational nonce secrecy.

## Receipt and proof results

The corpus rejects registered changes involving:

- core digest;
- leaf hash;
- proof sibling;
- root;
- receipt/proof index mismatch;
- receipt/proof tree-size mismatch;
- proof digest;
- expected backend identity;
- expected log identity;
- signer key identifier;
- receipt-signature bytes;
- unknown critical receipt field;
- re-signed core-binding substitution;
- re-signed malformed proof path;
- re-signed altered root;
- coherently relabelled leaf index;
- re-signed proof-digest mismatch;
- re-signed backend/log identity substitutions;
- wrong backend key material;
- receipt transplanted to another validly signed core.

The result does not mean every coherent statement by an authorised backend is independently true.

## Retained-state results

The stateful sequence produced the following registered decisions:

| Case | Decision | State effect |
|---|---|---|
| Same checkpoint | Accepted | no change |
| Smaller valid tree | Rejected as rollback | no change |
| Same-size alternative root | Rejected as fork | no change |
| Larger tree without consistency proof | Rejected | no change |
| Mutated consistency path | Rejected | no change |
| Wrong first root | Rejected | no change |
| Wrong first size | Rejected | no change |
| Wrong consistency identity | Rejected | no change |
| Valid prefix extension | Accepted | advanced from size 3 to size 5 |
| Old receipt after advancement | Rejected as rollback | no change |
| Exact same-state replay | Accepted limitation | no change |

The final retained checkpoint recorded by the authoritative result summary is:

```text
backend_id: urn:te:backend:a2-cmpb-reference
log_id: urn:te:log:cmpb-reference
size: 5
root: 21658af628005c9f7f8bda4554745eeed9b5c208d1462701a9afa11762fd2d57
```

## Falsified expectation and protocol amendment

The first hosted materialisation run expected a coherently changed and backend-re-signed tree size to fail with `TE-E-PROOF-PATH`. It was accepted. The materialisation job failed and did not commit its corpus.

The outcome was interpreted as a claim-boundary result rather than hidden or repaired away. An authorised backend can authenticate an internally admissible alternative tree-size statement; the stateless receipt verifier has no independent evidence of actual log population. The case was renamed:

```text
LIM-BACKEND-002
```

and registered as an expected limitation acceptance. The original run, job and artifact digest remain in `C4_PROTOCOL_DEVIATION.md`.

This amendment lowers the claim ceiling. It does not weaken the verifier or convert the original false accept into an attack-rejection success.

## Other explicit limitation acceptances

The six accepted limitation cases are:

1. authorised actor assertion;
2. authorised Consent-version assertion;
3. authorised policy-version assertion;
4. coherent stateless split view;
5. authorised alternative tree-size assertion;
6. exact same-state replay.

They must remain visible in the manuscript or supplement. Reporting only `67/67 passed` would be misleading.

## Encryption and confidentiality decision

The executed pipeline does not encrypt the clinical payload or portable evidence.

- SHA-256 is used for exact-byte commitments and Merkle hashing.
- Ed25519 is used for issuer and receipt signatures under deterministic test registries.
- Base64 in FHIR Binary is encoding, not encryption.
- TLS is not an evaluated hospital-exchange result because the pipeline opens no application exchange connection.
- encryption at rest, HSM use, access-control enforcement, key rotation and compromise response remain deployment controls.

## Complete hosted release contract

The branch-head closure workflow must execute the complete `make release-check`, separate C4 security validation, official FHIR regression and integrity preview on the same synchronised tree. The retained release-check transcript for the report-inclusive tree records:

| Check | Result |
|---|---:|
| Unit/regression pytest items | 45 passed |
| Property-test pytest items | 8 passed |
| Mandatory skips observed | 0 |
| Finite bounded checks | 29,105 |
| Bounded failures | 0 |
| Canonical objects checked | 729 |
| Append transitions checked | 1,641 |
| Inclusion proofs checked | 1,641 |
| Consistency proofs checked | 1,278 |
| Same-size fork pairs checked | 4,059 |
| Verifier checkpoint advances checked | 16 |
| Reproducibility-manifest rows | 56 current |
| Result contracts | 11 |
| Parsed retained CSV rows | 543 |
| Distributed files | 365 |
| SHA-256 entries | 364 |
| File-manifest rows | 363 |
| HIE retained files | 41 current |
| C3 positive FHIR units | 4 |
| C3 intended negative rejections | 2 of 2 |
| C4 registered cases | 67 |
| C4 expected rejections | 54 |
| C4 false accepts | 0 |
| C4 state non-advancement failures | 0 |
| Quick-pipeline events | 48 |
| Successful quick receipt checks | 16 |
| Quick baseline mutations | 2 of 2 rejected |
| Ordinary verification failures | 0 |
| Validation failures | 0 |
| Deterministic output comparison | PASS |
| Workload semantic invariants | PASS |
| Integrity patch | 0 bytes |
| Final contract | `RELEASE-CHECK: PASS` |

## Claims now permitted

- The final registered unauthorised issuer-side mutations were rejected under the deterministic test key registry.
- The exact commitment verified only for the declared source bytes, framing and nonce; the reported substitutions were rejected.
- The final registered inconsistent receipt, proof, identity, rollback, fork and consistency cases were rejected under the local verifier policy.
- Every rejected retained-state case left the checkpoint unchanged.
- A valid consistency proof advanced the local retained checkpoint from size three to size five.
- The six explicit limitation acceptances delimit authorised-signer truth, authorised-backend honesty, stateless split-view detection and replay prevention.

## Claims still prohibited

- generic security;
- tamper-proof or immutable operation;
- clinical truth or operational identity proofing;
- Consent or policy truth;
- legal non-repudiation;
- post-compromise security;
- encryption or confidentiality;
- truthful tree size, actual log population or event completeness proven by a receipt;
- replay prevention;
- public transparency or global non-equivocation;
- SCITT or RFC 9942 conformance;
- production penetration resistance;
- hospital deployment or production readiness.

## Reviewer-closure effect

C4 supplies the executable basis for Reviewer 1's requests concerning Merkle purpose and encryption wording. The response can now explain, with evidence, the distinct roles and limits of commitment, issuer signature, receipt signature, inclusion path and retained checkpoint. It must also state that the protocol implements no payload encryption and that transport and at-rest encryption were not evaluated.

C4 materially strengthens the validity response to Reviewer 2 by replacing an abstract security description with registered inputs, transformations, expected decisions, observed decisions and retained outputs.

C4 sharpens Reviewer 4's accountability/transparency/trust distinction: attributable signed evidence and local inclusion/consistency properties are evaluated, whereas backend honesty, event completeness, public transparency and organisational trust are not.

C4 does not close Reviewer 1's total-overhead request. That remains the principal empirical obligation of C5.

## Gate checklist

| C4 criterion | Verdict |
|---|---|
| Protocol and attack registry | PASS |
| Original failed expectation preserved | PASS |
| Protocol amendment documented | PASS |
| Signed-core mutation corpus | PASS |
| Wrong issuer and backend keys | PASS |
| Signature-byte mutations | PASS |
| Payload and nonce controls | PASS |
| Receipt index, size, root and path controls | PASS, with explicit authorised tree-size limitation |
| Rollback and same-size fork controls | PASS |
| Consistency-proof mutations | PASS |
| State non-advancement after rejection | PASS |
| Replay boundary | PASS as explicit limitation |
| Encryption/confidentiality boundary | PASS |
| Retained deterministic outputs | PASS |
| Result contract | PASS |
| Deterministic regeneration | PASS |
| Current checksums and file manifest | PASS |
| Hosted security job | PASS |
| Complete hosted `make release-check` | PASS |
| Official FHIR regression | PASS |
| Generated repository drift | PASS: none |
| Hostile review | PASS |
| **Gate C4** | **PASS** |

## Final C4 verdict

> Under the exact synthetic profile and deterministic test trust configuration, the final 67-case registry reproduced 54 expected rejections, 11 expected acceptances and two expected-absence controls with no final decision mismatch. Rejected retained-state cases did not advance the checkpoint. Six accepted cases explicitly demonstrate the boundary of issuer truth, backend honesty, stateless split-view detection and duplicate-replay handling. The original falsified tree-size expectation remains archived and narrows, rather than strengthens, the receipt claim.

C4 is closed. C5 may begin without reopening C4 unless a later experiment or release-candidate check falsifies a C4 invariant.
