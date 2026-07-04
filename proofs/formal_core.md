# Formal core: TrustEvidence properties

This note records the model-level properties used by the TrustEvidence reference implementation. It is a specification and proof sketch, not a mechanised proof and not a claim of production security.

## Basic notation

A TrustEvidence artefact is a canonical signed body plus optional backend receipt and verification material. Hash inputs are domain-separated and length-delimited. Leaf hashes, node hashes, payload commitments and checkpoint hashes use distinct domain strings.

## Properties

- Tamper-evidence: a verifier can detect alteration of a retained payload commitment or artefact unless the underlying hash or signature assumptions fail.
- Append-only consistency: a later accepted backend state extends an earlier accepted state rather than rewriting it.
- Inclusion verifiability: a verifier can check that an artefact is represented in a committed backend state.
- Non-equivocation: inconsistent histories are detectable when verifier-state comparison, witness/gossip mechanisms or ledger finality assumptions are available.
- Evidence completeness: completeness is limited to events that cross the instrumented evidence-emission boundary.
- Evidence soundness: an artefact can preserve a signed assertion; it cannot make a false clinical or legal assertion true.
- Freshness: freshness requires retained verifier state, timestamp semantics and backend-specific checkpoint or finality evidence.

## Backend consequences

A central audit repository provides local operational accountability but does not by itself provide portable inclusion proofs, append-only consistency against a controlling operator or non-equivocation.

An append-only hash log supports inclusion and consistency verification when checkpoints are retained and compared. It requires an honest witness, gossip channel or equivalent checkpoint-comparison mechanism for non-equivocation.

A ledger-like replicated backend can strengthen rewriting and split-view resistance only under an explicit finality or quorum-honesty assumption. The existence of a ledger-like backend does not by itself prove availability, privacy, legal compliance or clinical truth.

## Attack attempts considered

The model explicitly treats log truncation, rollback, fork-and-replay, hash-input ambiguity, checkpoint spoofing, verifier-state loss, colluding operators, stale checkpoints and pre-boundary non-emission as relevant failure cases. The strongest residual attack is silent non-emission before the evidence boundary; no backend can prove an event that was never emitted.
