# SPEC.md

Status: draft specification; language-agnostic first, then bound to the locked stack.  
Proof-control input: `proofs/formal_core_v1.md`, SHA-256 `a541f5538fd26f3a135fc5409255767634edea210917ee02c101243f6a8569b1` [COMPUTED from v2.0.0 artefacts].

## 0. Scope and non-claims

This specification defines the TrustEvidence envelope, the emission API state machine, the verification API boundary, and the error taxonomy needed by implementation, measurement, FHIR and legal-traceability components. It does not claim implementation, measured performance, FHIR conformance, legal compliance, blockchain deployment, or cryptographic benchmarking.

The specification operationalises the v2.0.0 formal corrections: canonical serialisation is explicit; hashing is domain-separated; checkpoint acceptance binds backend identity, log identity, algorithm, signer authorisation, verifier state and timestamp context; verifier-state loss is treated as a first-class error; and silent pre-boundary non-emission remains outside completeness unless monitoring produces a failure artefact.

## 1. Object model

The interface separates an emitted evidence core from the backend receipt that proves or records how the core was accepted by an evidence-storage backend.

```text
TrustEvidenceEnvelope = {
  envelope_version,
  artefact_core,
  backend_receipt?,
  extension[]?
}
```

`artefact_core` is produced by the emitting boundary before backend acceptance. `backend_receipt` is produced by an evidence-storage backend after acceptance or release preparation. This separation prevents circular hashing: the Merkle leaf commits to the core artefact, while the receipt commits to the core hash and backend state.

## 2. Canonical serialisation and domain separation

### 2.1 Canonical serialisation

`canon_te(obj)` is a deterministic UTF-8 JSON byte sequence with these rules:

1. Objects are serialised with lexicographically sorted property names.
2. Insignificant whitespace is forbidden.
3. String values use UTF-8 and must not rely on locale-specific normalisation.
4. Hashes, signatures and binary proof fragments are encoded as unpadded base64url strings.
5. Timestamps are UTC strings with explicit `Z`; sub-second precision is permitted only where declared by `time_source.max_skew_ms`.
6. Unknown extension members are serialised after recognised members by the same lexical ordering rule.
7. The canonical object signed by the emitter excludes `artefact_core.emitter_signature.signature_value` only; all other core fields are included.
8. The canonical object signed by a backend receipt excludes `backend_receipt.receipt_signature.signature_value` only; all other receipt fields are included.

v2.0.0 may replace this internal canonicalisation with a library implementation only if the byte-for-byte behaviour is tested against these rules. The JSON Schema constrains structure; it is not a canonicalisation engine.

### 2.2 Domain-separated hashes

The following domain tags are mandatory and are byte strings in the canonical tuple encoding. Raw concatenation is forbidden.

```text
TE-v2:payload        payload or aggregate commitment
TE-v2:artefact-core  core artefact hash
TE-v2:leaf           evidence-log leaf hash
TE-v2:node           Merkle internal-node hash
TE-v2:checkpoint     checkpoint hash
TE-v2:receipt        backend receipt hash
TE-v2:failure        explicit failure artefact hash
```

Derived values:

```text
payload_commitment = H("TE-v2:payload"       || alg_id || commitment_context || payload_or_aggregate_bytes)
core_hash          = H("TE-v2:artefact-core" || alg_id || canon_te(artefact_core_without_signature_value))
leaf_hash          = H("TE-v2:leaf"          || alg_id || backend_id || log_id || core_hash)
node_hash          = H("TE-v2:node"          || alg_id || backend_id || log_id || left_hash || right_hash)
checkpoint_hash    = H("TE-v2:checkpoint"    || alg_id || backend_id || log_id || tree_size || root_hash || issued_at)
receipt_hash       = H("TE-v2:receipt"       || alg_id || core_hash || checkpoint_hash || receipt_context)
failure_hash       = H("TE-v2:failure"       || alg_id || failed_state || failure_code || core_hash?)
```

## 3. TrustEvidence envelope fields

### 3.1 Core artefact fields

| Field | Required | Function | FHIR/v2.0.0 disposition |
|---|---:|---|---|
| `artefact_core.artefact_id` | yes | Globally unique evidence artefact identifier. | Target AuditEvent/Provenance identifier FHIR-IG mapping. |
| `artefact_core.evidence_type` | yes | Declares consent receipt, access attestation, provenance assertion, integrity anchor, consent-state transition or failure artefact. | CodeSystem/ValueSet in v2.0.0 FHIR-IG mapping. |
| `artefact_core.event_id` | yes | Idempotency key for the operational event crossing the boundary. | Target AuditEvent/Provenance event identifier FHIR-IG mapping. |
| `artefact_core.event_action` | yes | Create/read/update/delete/execute/transform/anchor/revoke/fail semantic action. | Target AuditEvent action semantics or ValueSet FHIR-IG mapping. |
| `artefact_core.occurred_at` | yes | Time the operational event is asserted to have occurred. | Target AuditEvent/Provenance time semantics FHIR-IG mapping. |
| `artefact_core.emitted_at` | yes | Time the evidence artefact was emitted. | Target AuditEvent recorded/provenance time semantics FHIR-IG mapping. |
| `artefact_core.time_source` | yes | Declared time source and skew bound. | Out-of-band audit-control metadata; may become extension FHIR-IG mapping. |
| `artefact_core.emitter` | yes | Authenticated emitter role, organisation token and signing key reference. | Target AuditEvent agent/Provenance agent FHIR-IG mapping. |
| `artefact_core.subject_ref` | conditional | Tokenised subject or record context; direct identifiers are forbidden in the evidence backend. | Target AuditEvent entity/Provenance target or extension FHIR-IG mapping. |
| `artefact_core.semantic_binding` | yes | Conceptual FHIR resource class, resource token and version context. | Forward mapping to AuditEvent/Provenance/Consent/Observation FHIR-IG mapping. |
| `artefact_core.policy_binding` | conditional | Policy identifier, version, digest and source-of-truth token. | Extension or Provenance entity/policy reference FHIR-IG mapping. |
| `artefact_core.consent_binding` | conditional | Consent-state token, state value, version and effective time. | Target Consent reference and AuditEvent/Provenance context FHIR-IG mapping. |
| `artefact_core.payload_binding` | conditional | Payload reference token, commitment algorithm, digest and commitment context. | Out-of-band payload commitment; evidence-anchor extension FHIR-IG mapping. |
| `artefact_core.privacy_controls` | yes | Minimisation profile, tokenisation profile and retention boundary. | Extension or IG security narrative FHIR/legal mapping. |
| `artefact_core.emitter_signature` | yes | Signature over canonical core artefact. | Out-of-band cryptographic control; may be profiled as extension FHIR-IG mapping. |
| `artefact_core.failure` | conditional | Failure-state description when the artefact is a failure artefact. | AuditEvent outcome/extension target FHIR-IG mapping. |

### 3.2 Backend receipt fields

| Field | Required when receipt exists | Function | FHIR/v2.0.0 disposition |
|---|---:|---|---|
| `backend_receipt.backend_type` | yes | `central-audit`, `hash-log`, `ledger-like`, `trillian`, `rekor` or `fabric`. | Backend-type ValueSet / extension FHIR-IG mapping. |
| `backend_receipt.backend_id` | yes | Stable backend identity configured for verifier acceptance. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.log_id` | conditional | Log or channel identity; mandatory for hash-log, Trillian, Rekor and ledger-like receipts. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.alg_id` | yes | Algorithm suite for hashes and checkpoint signatures. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.core_hash` | yes | Hash of the signed core artefact. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.tree_size` | conditional | Merkle tree size at checkpoint. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.root_hash` | conditional | Merkle root or committed backend state hash. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.leaf_index` | conditional | Leaf position where known. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.inclusion_proof_ref` | conditional | URI, digest, or embedded reference to inclusion proof material. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.consistency_proof_ref` | conditional | URI, digest, or embedded reference to consistency proof material. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.witness_ref` | conditional | Witness/checkpoint-comparison reference for `BE-A2` non-equivocation. | Out-of-band or extension FHIR-IG mapping. |
| `backend_receipt.finality_ref` | conditional | Finality or transaction reference for `BE-A3`. | Out-of-band or extension FHIR-IG mapping. |
| `backend_receipt.issued_at` | yes | Receipt/checkpoint issuance time. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.signer_id` | yes | Authorised backend, witness or ledger signer. | Evidence-anchor extension FHIR-IG mapping. |
| `backend_receipt.receipt_signature` | yes | Signature over receipt fields. | Out-of-band cryptographic control; extension candidate FHIR-IG mapping. |

## 4. Emission API state machine

The emission API is a logical contract. v2.0.0 may implement it as Python functions, HTTP handlers, HAPI interceptors or backend adapters, but the state transitions must remain observable.

| State | Name | Entry condition | Exit condition | Failure exits |
|---|---|---|---|---|
| `E0` | Operational event observed | Source system produces an in-scope event candidate. | Event is eligible for TrustEvidence emission. | `TE-E-PRE_BOUNDARY_NON_EMISSION` if monitoring later proves bypass. |
| `E1` | Boundary eligibility assessed | Event has crossed the configured evidence boundary. | Event type, actor and scope are recognised. | `TE-E-EVENT_OUT_OF_SCOPE`; `TE-E-DUPLICATE_EMISSION`. |
| `E2` | Semantic context bound | FHIR-adjacent context, policy source and consent source are queried or referenced. | Semantic, policy and consent bindings are complete or explicitly unavailable. | `TE-E-POLICY_STATE_UNRESOLVED`; `TE-E-CONSENT_STATE_UNRESOLVED`; `TE-E-FHIR_MAPPING_UNVERIFIED`. |
| `E3` | Payload commitment prepared | Payload or aggregate material is available or a reference-only event is declared. | `payload_commitment` is computed or payload binding is explicitly not applicable. | `TE-E-PAYLOAD_UNAVAILABLE`; `TE-E-PAYLOAD_COMMITMENT_MISMATCH`. |
| `E4` | Core artefact assembled | Required fields are populated. | JSON Schema validation passes. | `TE-E-SCHEMA_VALIDATION`. |
| `E5` | Core canonicalised and signed | Canonical bytes are constructed. | Emitter signature is produced. | `TE-E-CANONICAL_SERIALISATION`; `TE-E-UNAUTHORISED_SIGNER`. |
| `E6` | Submitted to backend | Signed core artefact is sent to selected backend. | Backend accepts, rejects, or times out. | `TE-E-BACKEND_UNAVAILABLE`; `TE-E-WRONG_BACKEND_IDENTITY`; `TE-E-WRONG_LOG_IDENTITY`. |
| `E7` | Receipt/checkpoint returned | Backend returns acceptance material. | Receipt validates under `AcceptCheckpoint` or backend-specific local rule. | `TE-E-UNAVAILABLE_PROOF`; `TE-E-STALE_CHECKPOINT`; `TE-E-FORK_EVIDENCE`; `TE-E-UNSATISFIED_FINALITY`; `TE-E-MISSING_WITNESS`. |
| `E8` | Verifier-visible committed evidence | Envelope contains signed core and accepted backend receipt. | Envelope can be exported, queried, or verified. | `TE-E-VERIFIER_STATE_LOSS` at verifier side. |
| `EF` | Failure artefact emitted | A failure is in scope and can itself be recorded. | Failure envelope is available for audit. | If failure emission also fails, maintainer incident record is required; completeness proposition does not cover silent loss. |

## 5. Verification API

The verifier API exposes local checks separately from checks that require backend, witness, finality or payload access.

| Operation | Input | Offline possible? | Online dependency | Main success condition | Main failure codes |
|---|---|---:|---|---|---|
| `ValidateSchema(envelope)` | Envelope JSON | yes | none | Envelope satisfies `schema/trust_evidence_envelope.schema.json`. | `TE-E-SCHEMA_VALIDATION`. |
| `ComputeCoreHash(envelope)` | Core artefact | yes | none | Canonical bytes reproduce `backend_receipt.core_hash` where receipt exists. | `TE-E-CANONICAL_SERIALISATION`; `TE-E-DOMAIN_TAG_MISMATCH`. |
| `VerifyEmitterSignature(envelope)` | Core artefact and key material | yes if key cached | key discovery may be online | Signature verifies against authorised emitter key. | `TE-E-UNAUTHORISED_SIGNER`. |
| `VerifyPayloadCommitment(envelope, payload?)` | Payload or aggregate material | yes if payload available | custodian access may be online | Recomputed commitment matches. | `TE-E-PAYLOAD_UNAVAILABLE`; `TE-E-PAYLOAD_COMMITMENT_MISMATCH`. |
| `AcceptCheckpoint(receipt, verifier_state)` | Backend receipt | yes if signer/config cached | key/state retrieval may be online | Backend/log/algorithm/signer/time/state all match. | `TE-E-WRONG_BACKEND_IDENTITY`; `TE-E-WRONG_LOG_IDENTITY`; `TE-E-STALE_CHECKPOINT`; `TE-E-ROLLBACK_DETECTED`. |
| `VerifyInclusion(envelope, proof?)` | Envelope and inclusion proof | yes if proof embedded/cached | backend proof retrieval if reference only | Leaf recomputes to accepted root. | `TE-E-UNAVAILABLE_PROOF`; `TE-E-DOMAIN_TAG_MISMATCH`. |
| `VerifyConsistency(old_cp, new_cp, proof?)` | Two checkpoints | yes if proof cached | backend/witness proof retrieval | New checkpoint is append-only extension of old checkpoint. | `TE-E-ROLLBACK_DETECTED`; `TE-E-FORK_EVIDENCE`; `TE-E-UNAVAILABLE_PROOF`. |
| `CheckWitness(receipt)` | `BE-A2` receipt | no, unless witness state cached | witness/gossip/checkpoint-comparison source | At least one configured witness confirms comparable checkpoint state. | `TE-E-MISSING_WITNESS`; `TE-E-FORK_EVIDENCE`. |
| `CheckFinality(receipt)` | `BE-A3` receipt | usually no | ledger/finality service or cached finality proof | Finality reference satisfies configured `A8`. | `TE-E-UNSATISFIED_FINALITY`. |
| `EvaluateFreshness(envelope, verifier_state, policy)` | Envelope and local audit policy | yes | time-source/key checks may be online | Receipt and event times fall within declared freshness window and do not roll back state. | `TE-E-TIMESTAMP_SKEW_EXCEEDED`; `TE-E-FRESHNESS_WINDOW_EXPIRED`; `TE-E-VERIFIER_STATE_LOSS`. |

Verifier state must store, per `(backend_id, log_id, alg_id)`, the greatest accepted `tree_size`, corresponding `root_hash`, `issued_at`, checkpoint source, and any detected fork evidence. A verifier that loses this state may still perform local schema and signature checks, but it must not claim rollback detection or freshness.

## 6. Error taxonomy

Error codes are stable API values. Human-readable text may change; code meanings must not.

| Code | Class | Reject evidence? | Meaning |
|---|---|---:|---|
| `TE-E-SCHEMA_VALIDATION` | structure | yes | Envelope does not satisfy the JSON Schema. |
| `TE-E-CANONICAL_SERIALISATION` | cryptographic-input | yes | Canonical byte sequence cannot be derived deterministically. |
| `TE-E-DOMAIN_TAG_MISMATCH` | cryptographic-input | yes | Hash/proof uses the wrong TrustEvidence domain tag or algorithm context. |
| `TE-E-UNAUTHORISED_SIGNER` | identity | yes | Emitter, backend, witness or ledger signer is not authorised for the configured role. |
| `TE-E-WRONG_BACKEND_IDENTITY` | identity | yes | Receipt backend identity does not match verifier configuration. |
| `TE-E-WRONG_LOG_IDENTITY` | identity | yes | Receipt log/channel identity does not match verifier configuration. |
| `TE-E-STALE_CHECKPOINT` | verifier-state | yes | Checkpoint is older than the verifier's retained accepted state. |
| `TE-E-ROLLBACK_DETECTED` | verifier-state | yes | Later state fails monotonic tree-size or consistency checks. |
| `TE-E-FORK_EVIDENCE` | non-equivocation | yes | Conflicting accepted histories are detected. |
| `TE-E-MISSING_WITNESS` | non-equivocation | conditional | `BE-A2` non-equivocation was requested but witness/gossip evidence is absent. |
| `TE-E-UNSATISFIED_FINALITY` | finality | conditional | `BE-A3` finality or quorum condition is not satisfied. |
| `TE-E-UNAVAILABLE_PROOF` | availability | conditional | Proof is unavailable; this is not a false proof but prevents inclusion/consistency verification. |
| `TE-E-VERIFIER_STATE_LOSS` | verifier-state | conditional | Verifier has lost state required for rollback/freshness claims. |
| `TE-E-TIMESTAMP_SKEW_EXCEEDED` | time | conditional | Timestamp source exceeds configured skew bound. |
| `TE-E-FRESHNESS_WINDOW_EXPIRED` | time | conditional | Evidence is too old for the declared audit question. |
| `TE-E-PRE_BOUNDARY_NON_EMISSION` | completeness-boundary | no if later failure artefact exists | Monitoring indicates an in-scope event bypassed the emission boundary. |
| `TE-E-EVENT_OUT_OF_SCOPE` | emission-boundary | no | Event is outside the configured evidence-emission scope. |
| `TE-E-DUPLICATE_EMISSION` | idempotency | conditional | Event idempotency key already exists. |
| `TE-E-POLICY_STATE_UNRESOLVED` | semantic | conditional | Policy source/version could not be resolved at emission time. |
| `TE-E-CONSENT_STATE_UNRESOLVED` | semantic | conditional | Consent state could not be resolved at emission time. |
| `TE-E-PAYLOAD_UNAVAILABLE` | payload | conditional | Payload or aggregate material needed for a commitment is unavailable. |
| `TE-E-PAYLOAD_COMMITMENT_MISMATCH` | payload | yes | Recomputed payload commitment conflicts with recorded commitment. |
| `TE-E-BACKEND_UNAVAILABLE` | availability | conditional | Backend did not accept or acknowledge the artefact within policy bounds. |
| `TE-E-FHIR_MAPPING_UNVERIFIED` | standards | conditional | Field/resource mapping has not yet been verified by v2.0.0. |

## 7. Backend-specific receipt profiles

### 7.1 `BE-A1` central audit

Required receipt fields: `backend_type`, `backend_id`, `core_hash`, `issued_at`, `signer_id`, `receipt_signature`.  
Unsupported positive claims: portable inclusion proof, Merkle consistency proof, non-equivocation.  
Verifier consequence: local operational auditability only unless an external witness or immutability mechanism is added, at which point the backend is no longer plain `BE-A1`.

### 7.2 `BE-A2` hash log

Required receipt fields: all `BE-A1` fields plus `log_id`, `alg_id`, `tree_size`, `root_hash`, `leaf_index`, `inclusion_proof_ref`; `consistency_proof_ref` is required for state advance beyond the first accepted checkpoint. `witness_ref` is required whenever non-equivocation is asserted.  
Verifier consequence: inclusion and local append-only consistency may be verified from proofs; non-equivocation requires `A7` witness/gossip/checkpoint comparison.

### 7.3 `BE-A3` ledger-like backend

Required receipt fields: all identity and core-hash fields plus `log_id` or channel identity, `finality_ref`, `issued_at`, `signer_id`, `receipt_signature`; Merkle fields are optional unless the ledger adapter exposes a Merkle commitment.  
Verifier consequence: split-view and rewriting resistance are claimable only under concrete `A8` finality/quorum semantics supplied by v2.0.0.

### 7.4 External baselines

Trillian and Rekor are treated as `BE-A2`-class transparency-log baselines unless their deployed configuration supplies an explicit witness/checkpoint-comparison mechanism. Fabric is treated as `BE-A3` only after v2.0.0 binds endorsement, ordering and commit/finality semantics to `A8`.

## 8. Stack binding

The language-agnostic specification is bound to the locked stack as follows:

| Component | v2.0.0 binding | later maintainer run |
|---|---|---|
| Python harness | v2.0.0 implements schema validation, canonicalisation, hashing, A1/A2 adapters and verifier state. | v2.0.0 |
| PostgreSQL | A1 append table and verifier-state persistence substrate. | v2.0.0 |
| Merkle core | RFC-9162-style inclusion/consistency proofs using the v2.0.0 domain tags. | v2.0.0 |
| HAPI FHIR JPA + BALP path | Event source/workload substrate; exact resource profiles deferred. | v2.0.0/v2.0.0 |
| Trillian/Rekor | A2-class external transparency-log baselines. | v2.0.0 |
| Hyperledger Fabric | A3-class ledger-like backend once `A8` is concretely bound. | v2.0.0 |
| FSH/SUSHI/IG Publisher | v2.0.0 profiles and QA; all exact element paths remain FHIR-IG mapping. | v2.0.0 |

## 9. Field completeness checks before v2.0.0

A v2.0.0 implementation must fail closed unless:

1. every required field in the JSON Schema is present;
2. every conditional field required by evidence type and backend type is present;
3. `core_hash`, `leaf_hash`, `checkpoint_hash` and `receipt_hash` are recomputable from canonical bytes;
4. backend/log identity matches verifier configuration;
5. signer authorisation is checked against role and identity;
6. verifier state is persisted before accepting a state advance;
7. failure artefacts are emitted for instrumented boundary failures;
8. pre-boundary non-emission is never hidden by a false completeness claim.

## 10. Boundary paragraph for later manuscript reuse

The TrustEvidence interface specified here defines evidence artefact and receipt semantics; it does not by itself prove that all relevant events were emitted, that clinical content is true, that FHIR conformance has been achieved, or that any legal obligation has been satisfied. Proof claims attach only to the formal properties under v2.0.0 assumptions; measurement claims attach only after v2.0.0; standards claims attach only after v2.0.0 validation; legal-traceability claims attach only after v2.0.0.
