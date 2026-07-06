# arguments/formal_core.md

Status: FORMAL_CORE v1 for v2.0.0. 
Evidence status: formal argument only. No implementation, measured benchmark, FHIR conformance test, legal-compliance assessment or cryptographic benchmark is claimed here.

## 0. Scope and inherited model

This file instantiates the v2.0.0 property-argument model. It uses the v2.0.0 backend identifiers `BE-A1`, `BE-A2`, `BE-A3`; adversary identifiers `ADV-1` ... `ADV-5`; and assumptions `A1` ... `A12`. It deliberately avoids the old manuscript's over-exposed simulation centre of gravity. v1.5.1 simulation outputs remain empirical simulation artefacts, not argument material.

The property matrix is exhaustive over the v2.0.0 property set, backend set and v2.0.0 adversary set: 7 properties × 3 backends × 5 adversaries = 105 rows. The machine-readable matrix is `tables/property_backend_adversary_matrix.csv`. Status counts are: `holds-under-assumption` = 80, `holds` = 0, `fails` = 25.

## 1. Cryptographic notation and objects

### TEA.D0 — Basic notation

Let `H` be the hash function selected for the evidence-log algorithm suite. Assumption `A1` states collision resistance and preimage resistance. Let `Sig.Verify(pk, m, sig)` be the signature-verification predicate used for emitters, backend checkpoints or replicated participants; its unforgeability is covered by `A3`.

A TrustEvidence artefact is denoted by `x`. Its deterministic byte representation is `canon_TE(x)`, supplied by canonical serialisation under `A2`. Payload or aggregate material is denoted by `p`. A verifier is honest when it executes the specified verification algorithm, preserves the state required by `A9`, and does not accept unchecked artefact substitutions.

### TEA.D1 — Domain-separated commitments

The reconstructed core uses explicit domain separation. The maintainer `||` below denotes canonical, length-delimited tuple encoding; it is not raw byte concatenation. This v2.0.0 correction closes the ambiguity attack in which different tuples could otherwise share the same byte string.

```text
payload_commit(p, ctx) = H("TE-v2:payload" || alg_id || ctx || p)
leaf_hash(x) = H("TE-v2:leaf" || alg_id || log_id || canon_TE(x))
node_hash(l, r) = H("TE-v2:node" || alg_id || log_id || l || r)
checkpoint_hash(cp) = H("TE-v2:cp" || alg_id || log_id || cp_fields)
```

This is not a claim that TrustEvidence is Certificate Transparency. It is an application-specific Merkle commitment discipline. The purpose is to avoid ambiguity between payload commitments, evidence leaves, internal nodes and checkpoints. Absence of such separation is treated as a argument-breaking defect.

### TEA.D2 — Evidence log, root and checkpoint

For an ordered evidence sequence `L = [x_0, ..., x_(n-1)]`, define `MTH_TE(L)` recursively with `leaf_hash` at leaves and `node_hash` at internal nodes. A checkpoint is:

```text
cp = (backend_id, log_id, tree_size, root_hash, alg_id, issued_at, signer_id, signature)
```

`AcceptCheckpoint(cp)` holds for a verifier only if `signature` validates under `A3`, `backend_id`, `alg_id` and `log_id` match the verifier's configured backend and log identity, `signer_id` is authorised for that `(backend_id, log_id)` pair, `tree_size`, `root_hash` and `issued_at` do not contradict retained verifier state under `A9` and bounded timestamp semantics under `A10`, and any conflict is recorded as fork evidence rather than silently overwritten.

### TEA.D3 — Inclusion argument

`VerifyInclusion(x, π, cp)` accepts when the argument `π` recomputes `cp.root_hash` from `leaf_hash(x)` under `cp.tree_size`, `cp.log_id` and `cp.alg_id`, and when `cp` is an accepted checkpoint. Failure to obtain a argument is an availability failure, not a false argument.

### TEA.D4 — Consistency argument

For accepted checkpoints `cp_m` and `cp_n` of the same `backend_id` and `log_id` with `cp_m.tree_size ≤ cp_n.tree_size`, `VerifyConsistency(cp_m, cp_n, κ)` accepts when `κ` proves that the leaves committed by `cp_m` are a prefix of the leaves committed by `cp_n`. The TrustEvidence model adopts the standard Merkle-tree idea that consistency arguments demonstrate append-only extension of tree heads; it does not claim a new CT argument algorithm.

### TEA.D5 — Verifier state and witness state

Verifier state `VS` contains at least `log_id`, accepted `tree_size`, `root_hash`, `alg_id`, `issued_at` context and the source of the checkpoint. Witness state is a comparable copy of accepted checkpoints held by a party other than the log maintainer. `BE-A2` non-equivocation depends on `A7`: at least one honest witness, gossip channel or equivalent checkpoint-comparison mechanism.

## 2. Formal property definitions

### TEA.P1 — Tamper-evidence

A backend provides tamper-evidence for artefact `x` and payload material `p` if, after an honest verifier has accepted an artefact or checkpoint binding `x` to `payload_commit(p, ctx)`, an adversary cannot make the verifier accept different material `p'` or a conflicting artefact `x'` for the same evidential role without violating `A1`, `A2`, `A3`, `A5`, or a backend-specific preservation assumption.

This property detects inconsistency. It does not prove that the original clinical payload was true, complete or clinically meaningful.

### TEA.P2 — Append-only consistency

A backend provides append-only consistency to verifier state `VS` if any later accepted checkpoint must either extend the earlier accepted checkpoint by appending leaves or be rejected by `VerifyConsistency`. For `BE-A2`, this property is only meaningful for verifiers that retain or compare prior checkpoints under `A9`; for global fork detection under malicious single-log operation, `A7` is required.

### TEA.P3 — Inclusion verifiability

A backend provides inclusion verifiability if an honest verifier can check, from a argument object and an accepted checkpoint or finality object, that a specific artefact was included in the committed backend state. Operational retrieval from a database is not sufficient for this formal property.

### TEA.P4 — Non-equivocation

A backend provides non-equivocation if an adversary cannot indefinitely maintain mutually inconsistent accepted histories for honest verifiers without detection. This is not a pure Merkle property. For `BE-A2`, it requires `A7`. For `BE-A3`, it requires `A8`. `BE-A1` has no independent non-equivocation mechanism.

### TEA.P5 — Evidence completeness

Evidence completeness is bounded to the emission boundary: every in-scope operational event that crosses the TrustEvidence emission boundary must either appear as an evidence artefact in the backend or produce an explicit failure artefact. Completeness is not claimed for silent pre-boundary non-emission, uninstrumented workflows, or deliberate source suppression outside `A4`.

### TEA.P6 — Evidence soundness

Evidence soundness means that an accepted artefact is well-formed, emitted by an authenticated actor, bound to declared event, payload, consent-state and policy-version references, and accepted under the declared canonical serialisation and key rules. It does not prove clinical truth, clinical sufficiency, legal enforceability or semantic correctness of an authorised but false statement.

### TEA.P7 — Freshness

Freshness means that accepted evidence is recent enough for a specified audit question and is not silently rolled back to a stale accepted state. Freshness depends on retained verifier state (`A9`) and bounded timestamp semantics (`A10`). Timestamp presence alone is not argument of real-world simultaneity.

## 3. Formalised property arguments

### TEA.PA1 - Commitment tamper-evidence property argument

**Statement.** Under `A1`, `A2`, `A3` and `A5`, if an honest verifier accepts an artefact `x` that binds a payload commitment `payload_commit(p, ctx)` and later recomputes the commitment over available material `p'`, then the verifier rejects when `p' ≠ p`, except by a hash collision, a serialisation/domain-separation failure, signature/key failure, or invalid retention of the material required by `A5`.

**Argument.** The artefact contains or references the commitment `payload_commit(p, ctx)`. Under `A2`, the canonical commitment context is deterministic and cannot be reinterpreted as a different artefact field or Merkle node. If `p'` is substituted and the verifier recomputes `payload_commit(p', ctx)`, equality with `payload_commit(p, ctx)` implies a collision or preimage break under `A1`, unless `ctx` or the artefact was also altered. Altering `ctx` or the artefact requires either acceptance of a different signed/bound artefact, contradicting `A3`, or a backend-preservation failure handled by `TEA.T2` ... `TEA.T5`. `A5` is necessary because a verifier that cannot recompute or otherwise validate the retained material cannot perform the comparison.

**Attack Attempt.** The adversary changes the clinical payload and says that the evidence layer still supports it. The attack fails if the verifier recomputes the payload commitment from retained material. The attack succeeds outside the property argument if the custodian no longer retains verifiable material, if the commitment context is ambiguous, or if the attacker can also replace all preserved evidence state. Those cases are not hidden: they are exactly `A2`, `A5` and backend-preservation assumptions.

### TEA.PA2 - Central audit limitation property argument for `BE-A1`

**Statement.** `BE-A1` can support operational auditability against `ADV-1`, but it does not provide independent inclusion verifiability, append-only consistency against a malicious maintainer, or non-equivocation against `ADV-2`, `ADV-3`, `ADV-4` or `ADV-5` without an additional external witness or immutability mechanism not present in the `BE-A1` abstraction.

**Argument.** In `BE-A1`, the controlling administrative domain is the source of the audit record and of later exports. Against `ADV-1`, v2.0.0 states that the external tamperer cannot directly administer the evidence backend; therefore a correctly operated central audit repository can remain operationally consistent for that adversary class. For adversaries with administrative or maintainer reach, the same party can alter or delete stored rows and present different exports to different verifiers. Because `BE-A1` has no Merkle consistency argument, no signed independent checkpoint, no witness channel and no quorum finality object, a verifier lacks an external object against which to distinguish a complete history from a rewritten one. Thus `BE-A1` fails independent inclusion verifiability and non-equivocation as formal properties, even if it remains useful as an operational audit database.

**Attack Attempt.** A malicious administrator deletes an access event and exports the remaining database as the complete audit trail. A verifier who sees only the database export cannot reconstruct the missing row or prove that deletion occurred. The attack is blocked only by adding a mechanism outside `BE-A1`, such as WORM storage, external notarisation, hash-log checkpointing or replicated finality. Those additions turn the backend into a different abstraction for v2.0.0 purposes.

### TEA.PA3 - `BE-A2` inclusion and append-only property argument

**Statement.** Under `A1`, `A2`, `A3` and `A9`, `BE-A2` provides inclusion verifiability and local append-only consistency for honest verifiers that accept signed checkpoints, retain prior verifier state and verify inclusion/consistency arguments. Against `ADV-3`, `ADV-4` or `ADV-5`, this property argument does not establish global non-equivocation; that stronger property requires `A7` and is handled only by `TEA.T4`.

**Argument.** Inclusion verification recomputes a root from `leaf_hash(x)` and the supplied path. Under `A2`, the leaf and node hashes cannot be confused across domains; under `A1`, a different leaf sequence cannot produce the same accepted root except by collision; under `A3`, an adversary cannot forge a signed checkpoint for a different root under the configured log identity. Consistency verification compares an earlier accepted checkpoint and a later accepted checkpoint of the same log identity. If the argument verifies, the earlier leaves are committed as a prefix of the later tree. If a log maintainer rewrites or deletes an accepted leaf, the new tree either fails consistency against retained verifier state or requires a collision in the Merkle construction. `A9` is necessary because a verifier that forgets all prior checkpoints has no local basis for rollback detection.

**Attack Attempt.** The log maintainer rolls back to a smaller tree and returns an inclusion argument for a convenient subset of leaves. An honest verifier retaining the earlier larger or incompatible checkpoint rejects because tree size, root hash or consistency argument does not match the retained state. The attack succeeds only if the verifier has lost state or never compares checkpoints; this is why `A9` is a property argument assumption and why v2.0.0 must attack verifier-state loss explicitly.

### TEA.PA4 - `BE-A2` non-equivocation condition and split-view counterexample condition

**Statement.** `BE-A2` provides non-equivocation against `ADV-3`, `ADV-4` and `ADV-5` only under `A7` and `A9`. Without `A7`, a single compromised log can maintain locally consistent but mutually inconsistent histories for different verifiers.

**Argument.** A Merkle log can prove inclusion and consistency within one history. It does not, by itself, force all verifiers to see the same signed checkpoint sequence. A split-view adversary can sign checkpoint sequence `S_A` for verifier `V_A` and sequence `S_B` for verifier `V_B`. Each sequence can be internally append-only and have valid inclusion arguments. If `V_A` and `V_B` never compare checkpoint identity, tree size and root hash, neither local verifier detects the fork. Under `A7`, at least one honest witness or gossip channel compares checkpoints for the same log identity and comparable time/tree-size context. Inconsistent signed roots for non-prefix histories are then exposed as conflicting commitments, so the fork cannot persist undetected.

**Attack Attempt.** The adversary gives a regulator a clean history and gives a data subject a history containing a disputed access notification, with both histories internally consistent. The attack works without `A7`; it fails under `A7` when a witness, auditor or gossip channel compares signed checkpoints and identifies incompatible roots. This property argument deliberately refuses to describe a single-maintainer hash log as non-equivocating unless the witness condition exists.

### TEA.PA5 - `BE-A3` finality property argument

**Statement.** Under `A3`, `A8` and `A9`, `BE-A3` provides append-only consistency, inclusion verifiability and non-equivocation for finalised emitted evidence artefacts against `ADV-1` ... `ADV-5` within the declared finality model. The property argument excludes availability, confidentiality, metadata minimisation, semantic correctness and legal enforceability. It fails when the concrete ledger implementation violates the quorum-honesty or fault-threshold condition in `A8`, or when a later Fabric configuration does not supply a verification object with the assumed finality semantics.

**Argument.** In `BE-A3`, accepted evidence state is finalised by a replicated participant set rather than by a single log maintainer. If `A8` holds, the adversary cannot unilaterally finalise two conflicting histories for the same log identity and finality height. If an adversary proposes a state omitting a previously finalised artefact, honest participants reject it or the verifier rejects it against retained finality state under `A9`. If the adversary presents a forged finality object, `A3` rejects the signature or participant-authentication material. Inclusion follows from a backend receipt or argument that binds an artefact to finalised state; append-only consistency follows from finality ordering; non-equivocation follows from the impossibility, under `A8`, of finalising conflicting histories without enough faulty participants.

**Attack Attempt.** A colluding custodian and backend subset attempt to finalise a history that omits a disputed access event. The attack fails if the omitted event had already been finalised and the quorum-honesty condition still holds. The attack succeeds outside the property argument if the faulty set exceeds the declared threshold, if finality is only probabilistic but treated as absolute, or if verifier state is lost. a future implementation must bind this property argument to a concrete Fabric configuration rather than leaving `A8` as rhetoric.

### TEA.PA6 - Evidence-completeness boundary property argument

**Statement.** Under `A4`, a backend can provide evidence completeness only for in-scope events that cross the evidence-emission boundary. No backend in `{BE-A1, BE-A2, BE-A3}` proves completeness for silent pre-boundary non-emission, uninstrumented workflows, or events deliberately suppressed before `ACT-FB` observes them.

**Argument.** Completeness is a statement about the relation between operational events and emitted artefacts. If an event crosses the boundary and `A4` is enforced, the state machine must either append an artefact or produce an explicit failure artefact. Backends can preserve or verify what is emitted: `BE-A1` preserves operational rows while the maintainer is trusted, `BE-A2` preserves witnessed emitted leaves, and `BE-A3` preserves finalised emitted artefacts under `A8`. If an event never reaches the emission boundary, the backend receives no input and therefore no cryptographic or replicated mechanism can distinguish absence of an event from non-emission. A property argument that claimed otherwise would confuse monitoring completeness with log integrity.

**Attack Attempt.** A custodian accesses data through an uninstrumented channel and later points to the absence of evidence as argument that no access occurred. The attack is outside the positive property argument and demonstrates the boundary: absence of evidence is not evidence of absence unless a future implementation introduces end-to-end workflow instrumentation and failure artefacts. This is a major evaluation criterion for the later implementation.

### TEA.PA7 - Evidence-soundness property argument

**Statement.** Under `A2`, `A3` and `A6`, an accepted TrustEvidence artefact is sound with respect to its authenticated emitter, declared event type, canonical payload/policy/consent bindings and verification context. The property argument does not establish clinical truth, legal enforceability or correctness of an authorised actor's semantic assertion.

**Argument.** Canonical serialisation under `A2` fixes the bytes that are signed, hashed and logged. Signature verification under `A3` binds the artefact to an authenticated emitter or backend checkpoint. The consent and policy references required by `A6` bind the artefact to an identified state source or version. Therefore, if an honest verifier accepts the artefact, it has verified the stated cryptographic and structural bindings. The argument does not inspect the real-world clinical fact or legal sufficiency of the underlying event; it only shows that the evidence statement was made, bound and preserved under the declared rules.

**Attack Attempt.** An authorised organisation emits an artefact saying that access was permitted when its internal policy interpretation was wrong. The artefact can still be cryptographically sound in v2.0.0 terms while semantically or legally incorrect. This is not a contradiction; it is the reason v2.0.0 must bind FHIR semantics carefully and v2.0.0 must translate legal duties into verification criteria.

### TEA.PA8 - Freshness and rollback property argument

**Statement.** Freshness is conditional rather than intrinsic to any backend. `BE-A1` freshness holds only while the central maintainer remains outside the adversary model; `BE-A2` freshness requires `A9` and `A10`, plus `A7` for compromised or split-view operation; `BE-A3` freshness requires `A8`, `A9` and `A10`. A verifier that lacks prior state or bounded timestamp semantics cannot distinguish a current checkpoint from a stale but locally valid checkpoint.

**Argument.** Freshness depends on comparing the presented evidence state with an expected audit context: prior checkpoint, accepted finality state, issued-at semantics, or policy-event time. `A9` supplies retained comparison state. `A10` supplies bounded meaning for timestamps and rejects the false inference that a timestamp alone proves real-world simultaneity. For `BE-A2`, a malicious log can replay an old but valid checkpoint unless a witness or verifier-state comparison exposes it; hence `A7` is needed against `ADV-3`, `ADV-4` and `ADV-5`. For `BE-A3`, a stale state is rejected if it conflicts with retained finality state and the quorum condition in `A8` holds. Without these assumptions, a stale response may be syntactically valid and locally consistent.

**Attack Attempt.** A verifier loses its last accepted checkpoint and asks a compromised log for the latest state. The log returns an older signed checkpoint. The verifier can verify the signature but cannot know it is stale without a witness, retained state or independent time/context signal. The attack survives if `A9` is false; the implementation and validation plan must therefore specify verifier-state storage and freshness checks as operational requirements.

### TEA.PA9 - Property–backend–adversary matrix property argument

**Statement.** The status of each property for each backend and each v2.0.0 adversary is exactly the status listed in `tables/property_backend_adversary_matrix.csv`, generated from the property-argument conditions above. The matrix contains 105 rows.

**Argument.** Each matrix row is a specialisation of `TEA.T1` ... `TEA.T8` to a property, backend and adversary. Rows marked `holds-under-assumption` cite the exact v2.0.0 assumptions that must be active. Rows marked `fails` identify the absent mechanism or excluded event class. No row marked `holds-under-assumption` should be converted into an unconditional manuscript claim.

**Attack Attempt.** A future manuscript sentence says, “the hash log provides non-equivocation”. The matrix rejects the sentence unless it includes `A7` and `A9`. A future sentence says, “the ledger proves evidence completeness”. The matrix rejects the sentence unless it is bounded to emitted events under `A4`. The matrix is therefore a claim-control device as much as a argument summary.

## 4. Consequences for the reconstructed manuscript

The formal core supports a stronger manuscript only if its boundaries remain visible. The defensible claim is not that stronger backends are universally superior. The defensible claim is that each backend occupies a different point in a property/adversary space: `BE-A1` is operationally simple but lacks independent argument; `BE-A2` supplies inclusion and consistency arguments but needs witnessing for non-equivocation; `BE-A3` can support non-equivocation under quorum honesty but imports governance, metadata and implementation assumptions.

The v2.0.0 core removes a tempting but false inference from v1: the old threat-coverage table cannot be treated as argument. It is replaced by explicit definitions, property argument assumptions and adversarial attack attempts.


## 5. v2.0.0 freeze note

The v2.0.0 review evaluated this formal core against rollback, fork-and-replay, domain-ambiguity, checkpoint-spoofing, colluding-quorum, verifier-state-loss and freshness time-of-check cases. No property argument is presented as an unconditional guarantee. The corrections above tighten canonical encoding, checkpoint acceptance, BE-A2 non-equivocation wording, BE-A3 finality scope and freshness conditions. The strongest surviving system attack is silent pre-boundary non-emission: a custodian or workflow path that never crosses the evidence-emission boundary cannot be made complete by any backend. This is outside the positive completeness property argument because `A4` deliberately scopes completeness to boundary-crossing events or explicit failure artefacts.
