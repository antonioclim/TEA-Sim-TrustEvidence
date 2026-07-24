# C4 security and mutation protocol

## Status

Frozen before the first hosted C4 execution and amended once after that execution falsified the expected rejection for an authorised tree-size assertion. The complete deviation, original workflow identifiers and artifact digest are retained in `C4_PROTOCOL_DEVIATION.md`.

The protocol applies only to the synthetic `HIE-DISCLOSURE-001` case, the project-defined `TE-HIE-Envelope-1` profile, deterministic test keys and the project-specific local A2 Merkle receipt implementation.

## Objective

C4 tests whether the bounded verifier rejects preregistered unauthorised semantic, signature, commitment, receipt, proof and retained-checkpoint changes, and whether rejected evidence leaves local retained state unchanged. It also records expected acceptances that expose the claim boundary: an authorised issuer can assert different schema-valid facts, an authorised backend can make internally admissible statements that are not independently true, a stateless verifier cannot detect a coherent split view, and exact same-state replay is not rejected.

## Security questions

1. Do stale issuer signatures reject changes to actor, organisation, Consent, policy, decision, outcome, resource and provenance facts?
2. Are wrong issuer/backend keys and signature-byte changes rejected under the declared key registries?
3. Does the payload commitment bind the exact candidate bytes, nonce, representation profile and context?
4. Do receipt signatures, identity pinning, digest binding and Merkle reconstruction reject unauthorised or internally inconsistent receipt changes?
5. Which coherent statements by an authorised or compromised backend remain acceptable because receipt authentication does not prove backend honesty or log completeness?
6. Does retained state detect rollback and verifier-visible same-size forks and require a valid prefix-extension proof before advancement?
7. Does rejected verification leave retained state unchanged?
8. Which attacks remain outside the model even when every implemented check passes?

## Case families

| Family | IDs | Expected decision | Principal property |
|---|---|---|---|
| Positive controls | `POS-HIE-*` | accept | Baseline and multi-leaf receipt validity |
| Signed-core mutations | `CORE-*` | reject | Closed schema, semantic constraints and issuer-signature binding |
| Authorised-issuer limitations | `LIM-ISSUER-*` | accept | Signature authenticity is not statement truth |
| Receipt mutations | `RCP-*` | reject | Receipt signature, identity, proof and digest binding |
| Re-signed malformed receipts | `RSIG-001`–`RSIG-004`, `RSIG-006`–`RSIG-009` | reject | Independent binding, path, identity and key-registry checks survive backend re-signing |
| Authorised-backend limitations | `LIM-BACKEND-*` | accept under declared conditions | Backend authentication is not backend honesty, log completeness or global consistency |
| Receipt/core replay | `RPL-*` | reject | Receipt cannot be transplanted to another signed core |
| Retained-state controls | `STATE-*` | mixed, preregistered | Rollback, fork, consistency and state advancement |
| Duplicate-replay limitation | `LIM-REPLAY-*` | accept | Freshness and duplicate suppression are higher-layer controls |
| Payload commitment | `COMMIT-*` | mixed, preregistered | Exact-byte, nonce, framing and portable-custody controls |

## Protocol amendment

The first hosted execution observed that a coherently changed tree-size claim, re-signed by the authorised backend test key, remained acceptable. The original case `RSIG-005` was therefore not repaired or silently removed. It was renamed `LIM-BACKEND-002` and reclassified as an expected limitation acceptance. The initial failed corpus remains archived and identified in `C4_PROTOCOL_DEVIATION.md`.

## False-accept definition

A false accept occurs only when a case registered in the final amended protocol as `expected_outcome = rejected` is accepted. Expected limitation acceptances are reported separately and are never counted as successful attack rejection.

## State rule

The stateful wrapper shall update its retained checkpoint only after the complete HIE verifier accepts the envelope and, where required, the consistency proof. Every rejected `STATE-*` case must preserve the exact pre-verification checkpoint tuple:

```text
backend_id, log_id, tree_size, root_digest
```

## Evidence outputs

```text
results_expected/cmpb_reference/c4_hie_security/
├── hie_security_mutation_results.csv
├── hie_security_mutation_run.json
├── hie_security_case_evidence.jsonl
└── README.md
```

The CSV uses the existing public mutation-result row contract. The JSONL retains candidate/proof digests, observed codes and state snapshots. The summary reports false accepts, false rejects, limitation acceptances and state non-advancement failures.

## Pass criteria

```text
all final registered rows passed
false_accept_count = 0
false_reject_count = 0
state_nonadvancement_failure_count = 0
portable_nonce_exposed = false
declared_clinical_source_marker_exposed = false
deterministic rerun equality = PASS
hosted make release-check = PASS
integrity patch = 0 bytes
```

A PASS does not require every adversarially framed input to be rejected. Expected limitation acceptances must remain visible and must narrow the manuscript claims.

## Stop conditions

C4 stops if any final expected rejection is accepted; any positive control is rejected; an expected limitation decision differs from the amended registry; a rejected state case changes the checkpoint; the exact result files are not deterministic; the result contract fails; the retained outputs drift from regeneration; or the complete hosted release contract fails.

## Claim ceiling

A C4 pass supports controlled-mutation rejection under the exact synthetic profile and test trust configuration. It also establishes explicit negative results concerning authorised-signer truth, authorised-backend tree-size assertions, stateless split views and duplicate replay. It does not support identity proofing, clinical truth, Consent truth, policy truth, legal non-repudiation, post-compromise security, confidentiality, production penetration resistance, replay prevention, complete event capture, public transparency or global non-equivocation.
