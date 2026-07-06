# THREAT_MODEL.md

stage: v2.0.0 — System and Threat Model
Status: frozen for v2.0.0 input unless v2.0.0 red-team forces a correction.
Evidence status: this document is a formalisation artefact. Counts derived from the v1 archive are marked [COMPUTED]. No implementation, benchmark, conformance test or proof is claimed in v2.0.0.

## 1. Scope and modelling stance

The TrustEvidence system is modelled as an evidence-emission and verification layer for auditable health information exchange. It is not modelled as a clinical repository, an access-control engine, a consent-authoring system, or a replacement for FHIR, IHE ATNA or IHE BALP. Clinical payload custody remains outside the evidence backend. The evidence backend stores compact artefacts, commitments, ordering information and verification material.

This version defines the semantic security boundary for subsequent validation work. Formalised property arguments apply only over the actors, assets, adversaries and assumptions stated here. Measurement claims apply only to mechanisms that are actually executed. Standards mappings to FHIR/IHE artefacts cannot silently change the security model.

Backend names are disambiguated from assumption names as follows. The old v1 names A1/A2/A3 are preserved as backend aliases, but the formal threat model uses backend identifiers `BE-A1`, `BE-A2` and `BE-A3`. Assumptions are labelled `A1`, `A2`, …, to keep assumption identifiers separate from backend identifiers.

## 2. Actors and trust boundaries

### 2.1 Actor set

| Actor ID | Actor | Role in the model | Trust boundary implication |
|---|---|---|---|
| `ACT-DS` | Mobile, wearable, patient-generated or institutional data source | Produces observations, records, or event context that may later be represented by FHIR resources or operational events. | Not trusted to provide audit guarantees by itself. Device data can be noisy, delayed or unavailable. |
| `ACT-FB` | FHIR semantic boundary / evidence emitter | Converts operational events into semantically bounded event records and emits TrustEvidence artefacts. In later validation work this may be instantiated near a HAPI FHIR/BALP boundary. | Trusted only under explicit evidence-emission assumptions; it is not assumed infallible. |
| `ACT-PC` | Payload custodian / clinical repository maintainer | Holds the authoritative clinical payload or aggregate outside the evidence backend. | May be honest, negligent or malicious depending on adversary class. |
| `ACT-EB` | Evidence-backend maintainer or maintainer set | Stores evidence artefacts and exposes append, query and verification interfaces. | Trust varies by backend: single maintainer for `BE-A1`/`BE-A2`; multi-maintainer or replicated governance for `BE-A3`. |
| `ACT-VA` | Verifier / auditor | Checks evidence inclusion, consistency, ordering and linkage to the payload or policy state. | May be offline for inclusion checks, but requires retained checkpoints or witness information for stronger guarantees. |
| `ACT-REG` | Regulator, supervisory body or legally authorised reviewer | Consumes audit evidence and traceability outputs when legal or governance questions arise. | Not assumed to operate the evidence backend; may rely on exported verification packages. |
| `ACT-DSUB` | Data subject or authorised representative | Has an interest in access transparency, notification, consent-state evidence and dispute resolution. | Not necessarily a direct technical verifier, but relevant to legal traceability and notification requirements. |

### 2.2 Trust boundaries

| Boundary ID | Crossing | Meaning | Principal risks |
|---|---|---|---|
| `TB-1` | `ACT-DS` → `ACT-FB` | Source events or observations enter the semantic/evidence-emission boundary. | False source data, missing source data, replayed source data, or delayed event context. |
| `TB-2` | `ACT-FB` ↔ `ACT-PC` | Evidence artefacts bind to payload references, payload hashes, consent state and policy context without moving the clinical payload into the evidence backend. | Commitment mismatch, token mapping error, unauthorised payload alteration, or silent payload deletion. |
| `TB-3` | `ACT-FB` → `ACT-EB` | Evidence artefacts are appended to the selected evidence backend. | Dropped emission, reordered append, forged emitter identity, or backend-side omission. |
| `TB-4` | `ACT-EB` → `ACT-VA` | Backends provide evidence, checkpoints, inclusion proofs, consistency proofs or replicated ledger state to verifiers. | Split-view, stale checkpoint, incomplete proof, or query suppression. |
| `TB-5` | `ACT-VA`/`ACT-EB` → `ACT-REG`/`ACT-DSUB` | Verified audit evidence is translated into oversight, access-transparency or dispute-resolution material. | Overclaiming legal effect, loss of privacy context, or non-actionable evidence exports. |
| `TB-6` | Cross-organisation governance boundary | More than one organisation has a legitimate stake in the evidence trail. | No mutually trusted maintainer, divergent policy interpretation, collusive suppression, or metadata overexposure. |

## 3. Assets

| Asset ID | Asset | Integrity / confidentiality / availability concern | Later property connection |
|---|---|---|---|
| `AST-PAY` | Clinical payload or aggregate | Must remain authoritative outside the evidence backend; the evidence layer should not become a shadow clinical repository. | Payload commitments support tamper-evidence but do not prove clinical truth. |
| `AST-TEA` | TrustEvidence artefact | Must be authentic, canonical, minimally identifying and bound to the relevant event, actor, policy state and payload commitment. | Soundness, inclusion verifiability, metadata minimisation. |
| `AST-LOG` | Log state / backend state | Must preserve ordering, inclusion and append history according to backend semantics. | Append-only consistency, inclusion verifiability, non-equivocation. |
| `AST-CONS` | Consent state and consent-state transitions | Must be bound to the policy and event time used during access or disclosure. | Completeness, freshness, policy-version correctness. |
| `AST-POL` | Policy version, purpose or governance context | Must be identifiable at the time of emission and later audit. | Freshness, soundness, legal traceability. |
| `AST-ID` | Subject tokens, actor identities, organisation references and key bindings | Must support accountability without unnecessary disclosure. | Soundness and privacy-risk analysis. |
| `AST-CP` | Checkpoints, root hashes, tree sizes and backend signatures | Must be authentic and comparable across verifiers. | Consistency, inclusion verifiability, non-equivocation. |
| `AST-PROOF` | Inclusion proofs, consistency proofs and verification packages | Must be generated against the correct backend state and verified under declared algorithms. | Inclusion verifiability, append-only consistency. |
| `AST-VS` | Verifier state | Previous checkpoints, witnessed states and audit decisions must be retained sufficiently for later comparison. | Non-equivocation and rollback detection. |
| `AST-META` | Metadata exposed by evidence artefacts | Event type, time, organisation and token metadata may reveal sensitive patterns even without payload. | Privacy-risk boundary; not a v2.0.0 integrity theorem by itself. |

## 4. Backend abstractions

| Backend ID | v1 alias | Abstraction | Security-relevant semantics |
|---|---|---|---|
| `BE-A1` | A1 central audit | A single controlled audit repository, appendable and queryable inside one administrative domain. | Provides operational auditability when the controlling domain is trusted. Does not by itself provide independent append-only proof against a malicious maintainer. |
| `BE-A2` | A2 append-only hash log | A single log maintainer maintains domain-separated Merkle-tree state and returns signed checkpoints plus inclusion and consistency proofs. | Detects modification, deletion or rollback when verifiers keep prior checkpoints or compare witnessed checkpoints. Non-equivocation requires an external witness/gossip assumption. |
| `BE-A3` | A3 ledger-like replicated backend | Evidence state is replicated across organisational participants under a finality or consensus rule. | Resists unilateral maintainer rewriting under a quorum-honesty assumption. May increase metadata exposure and governance cost. |

The model intentionally treats `BE-A3` as an abstraction. Hyperledger Fabric is a planned instantiation in v2.0.0, not an assumption in v2.0.0. Similarly, Trillian and Rekor are planned external baselines, not hidden guarantees in this threat model.

## 5. Adversary classes

| Adversary ID | Name | Capabilities | Explicit non-capabilities | Main target assets |
|---|---|---|---|---|
| `ADV-1` | External tamperer | Observes, delays, drops, replays or modifies messages across network-facing boundaries; attempts to substitute payload references, commitments or evidence artefacts. | Cannot break declared cryptographic primitives; cannot forge uncompromised signatures; cannot directly administer the evidence backend. | `AST-PAY`, `AST-TEA`, `AST-CP`, `AST-PROOF`. |
| `ADV-2` | Malicious custodian insider | Has authorised or privileged access within the payload custodian or a single administrative audit domain; may alter payloads, delete local rows, backdate local records or suppress local disclosure of inconvenient evidence. | Cannot forge keys outside its domain; cannot alter witnessed checkpoints; cannot control independent organisations unless escalated to `ADV-4`. | `AST-PAY`, `AST-CONS`, `AST-POL`, `AST-ID`, `AST-LOG`. |
| `ADV-3` | Compromised evidence-log maintainer | Controls the maintainer of `BE-A1` or `BE-A2`, or a subset of operators in `BE-A3`; may omit leaves, reorder append requests, roll back state, issue stale proofs or refuse service. | Cannot violate `BE-A3` quorum honesty when that assumption is active; cannot forge external witnesses or verifier state. | `AST-LOG`, `AST-CP`, `AST-PROOF`, `AST-VS`. |
| `ADV-4` | maintainer–insider collusion | Coordinates a custodian insider with one or more evidence-backend operators; may combine payload alteration with evidence omission or selective proof disclosure. | Cannot defeat independent witnesses, honest quorum participants, or verifiers that retain prior checkpoints, unless the relevant assumptions are disabled. | `AST-PAY`, `AST-TEA`, `AST-LOG`, `AST-CONS`, `AST-CP`. |
| `ADV-5` | Equivocating log server / split-view adversary | Serves inconsistent log histories, roots or tree sizes to different verifiers while preserving local plausibility for each verifier. | Cannot remain undetected if sufficiently many verifiers compare checkpoints under `A7`, or if `BE-A3` finality plus `A8` is active. | `AST-CP`, `AST-VS`, `AST-PROOF`, `AST-LOG`. |

A passive metadata observer is not modelled as an additional adversary class in v2.0.0. Metadata exposure is instead a risk dimension attached to any adversary or authorised reader that can observe `AST-META`. This prevents privacy leakage from being confused with integrity or non-equivocation theorems in v2.0.0.

## 6. Assumption set for later theorem statements

| Assumption ID | Assumption | Needed by |
|---|---|---|
| `A1` | Cryptographic hash functions used for commitments, Merkle leaves and Merkle nodes are collision-resistant and preimage-resistant at the security level claimed by the selected algorithm suite. | Tamper-evidence, append-only consistency, inclusion verifiability. |
| `A2` | Canonical serialisation is deterministic, schema-bound and domain-separated across payload commitments, evidence leaves, internal tree nodes and checkpoints. | Prevention of hash ambiguity and proof replay across contexts. |
| `A3` | Signature keys for emitters, backend checkpoints and replicated participants are authenticated, rotated under recorded policy, and unforgeable for parties not compromised by the adversary. | Soundness, checkpoint authenticity, replicated finality. |
| `A4` | In-scope operational events that pass the evidence-emission boundary are emitted exactly once or are accompanied by an explicit failure artefact. Silent global non-emission is outside any completeness theorem unless additional monitoring is introduced. | Evidence completeness; emission state machine in v2.0.0. |
| `A5` | Payload commitments bind to payload material or aggregates that can be recomputed or otherwise verified according to the custodian retention policy. | Payload-tamper detection. |
| `A6` | Consent and policy state used at emission time is obtained from an identified source of truth and the evidence artefact records the relevant state reference or version. | Consent-state soundness and policy freshness. |
| `A7` | For `BE-A2`, at least one honest witness, auditor gossip channel or equivalent checkpoint-comparison mechanism exists, and verifiers retain or can retrieve prior checkpoints. | Non-equivocation and rollback detection for a single-maintainer hash log. |
| `A8` | For `BE-A3`, replicated participants satisfy the declared quorum-honesty or fault-threshold condition of the concrete ledger implementation. | Resistance to unilateral rewriting and split-view. |
| `A9` | Verifiers retain enough state to compare future checkpoints, including log identity, tree size, root hash, algorithm identifiers and timestamp context. | Consistency checks, rollback detection, freshness. |
| `A10` | Event timestamps are produced by a declared time source with bounded skew appropriate to the audit use case, and the model does not treat timestamp presence as proof of real-world simultaneity. | Freshness and event-order interpretation. |
| `A11` | Subject identifiers are tokenised or pseudonymised before entering the evidence backend, and any re-identification table remains outside the evidence backend under separate governance. | Metadata minimisation and legal traceability. |
| `A12` | Availability, denial-of-service resistance and disaster recovery are treated as operational requirements, not as properties proved by Merkle inclusion or ledger replication alone. | Prevents overclaiming integrity mechanisms as availability guarantees. |

## 7. Property targets to be formalised in v2.0.0

This section names properties only; it does not prove them. v2.0.0 must replace these descriptions with definitions, theorem statements and attack attempts.

| Property target | v2.0.0 meaning | Principal assumptions |
|---|---|---|
| Tamper-evidence | An unauthorised change to an already committed payload reference, evidence artefact, or log entry becomes detectable by a verifier with the relevant commitment or proof. | `A1`, `A2`, `A3`, `A5`. |
| Append-only consistency | Later log state extends earlier accepted log state rather than rewriting or deleting accepted leaves. | `A1`, `A2`, `A7` or `A8`, `A9`. |
| Inclusion verifiability | A verifier can check that a specific artefact was included in a committed backend state under the declared algorithm and log identity. | `A1`, `A2`, `A3`, `A9`. |
| Non-equivocation | The backend cannot indefinitely maintain inconsistent accepted histories for different verifiers without detection under the relevant witness or quorum assumption. | `A7` for `BE-A2`; `A8` for `BE-A3`; generally fails for unaided `BE-A1`. |
| Evidence completeness | Every in-scope event that crosses the emission boundary appears in the evidence backend or produces a failure artefact. | `A4`, plus v2.0.0 state-machine instrumentation. |
| Evidence soundness | Accepted evidence artefacts correspond to authenticated emitters, declared event types and correct binding material. | `A2`, `A3`, `A6`. |
| Freshness | Evidence is recent enough for the audit question and cannot be silently rolled back to a stale accepted state under the declared verifier state. | `A7`/`A8`, `A9`, `A10`. |

## 8. Mapping v1 qualitative THREAT_ROWS into the formal frame

The v1 archive contains seven qualitative threat rows [COMPUTED]. v2.0.0 converts them into formal targets; it does not preserve their qualitative ratings as proof.

| v1 threat row | Formal adversary / risk | Assets | Formal property target | Assumptions that will matter | Backend consequence to test in v2.0.0 |
|---|---|---|---|---|---|
| Payload modified after anchoring | `ADV-1` or `ADV-2` modifies `AST-PAY` after an evidence artefact records a payload commitment. | `AST-PAY`, `AST-TEA` | Tamper-evidence | `A1`, `A2`, `A5` | All backends can detect mismatch only if the commitment is preserved and the payload can be recomputed; `BE-A2`/`BE-A3` strengthen preservation of the commitment itself. |
| Ordinary audit-row deletion | Accidental or low-privilege deletion of an evidence row. | `AST-LOG`, `AST-TEA` | Append-only consistency, inclusion verifiability | `A1`, `A2`, `A9` | `BE-A1` detection depends on local controls; `BE-A2` detects deletion through consistency proofs if prior state exists; `BE-A3` depends on replicated finality. |
| Malicious central-administrator deletion | `ADV-2` or `ADV-3` deletes or rewrites local audit history. | `AST-LOG`, `AST-CP`, `AST-VS` | Append-only consistency, non-equivocation | `A7`, `A8`, `A9` | Unaided `BE-A1` fails against the controlling administrator; `BE-A2` requires witness/gossip; `BE-A3` requires quorum honesty. |
| Access after consent revocation | `ADV-2` or an operational race creates access evidence inconsistent with current consent state. | `AST-CONS`, `AST-POL`, `AST-TEA` | Evidence soundness, completeness, freshness | `A4`, `A6`, `A10` | No backend fixes an incorrect consent source; stronger backends only make the emitted state transition harder to suppress after emission. |
| Policy-version mismatch | Evidence records the wrong policy version or omits the applicable policy context. | `AST-POL`, `AST-TEA` | Soundness, freshness | `A6`, `A10` | Hashing or replication preserves the emitted version; correctness still depends on the semantic boundary. |
| Interorganisational dispute | `ADV-3`, `ADV-4` or `ADV-5` exploits lack of a mutually trusted maintainer. | `AST-LOG`, `AST-CP`, `AST-PROOF`, `AST-VS` | Non-equivocation, inclusion verifiability | `A7`, `A8`, `A9` | `BE-A3` is justified only when independent finality is required; `BE-A2` may suffice if witness/gossip is acceptable. |
| Metadata exposure risk | Authorised or adversarial readers infer sensitive patterns from `AST-META`. | `AST-META`, `AST-ID` | Privacy-risk boundary, not a v2.0.0 integrity theorem | `A11`, `A12` | Replication can expand the observer set; minimisation and retention controls become requirements for v2.0.0/v2.0.0. |

## 9. Exclusions and honest boundary

The v2.0.0 model does not prove any property. It does not claim that a FHIR server, HAPI BALP interceptor, Trillian, Rekor or Hyperledger Fabric system has been deployed. It does not claim legal compliance. It does not claim that metadata minimisation removes all privacy risk. It does not claim that evidence completeness holds for events that never cross an instrumented emission boundary. These exclusions are design constraints, not weaknesses to be hidden.

## 10. Immediate consequences for v2.0.0

v2.0.0 must state theorems over the tuple `(backend, adversary, assumptions, property)`. Any theorem that relies on `A4`, `A7`, `A8`, `A9` or `A10` must place that assumption in the theorem statement. Any theorem about `BE-A2` non-equivocation without `A7` is invalid by construction. Any theorem about `BE-A3` against collusion without `A8` is invalid by construction. Any theorem about evidence completeness that ignores silent non-emission is invalid by construction.
