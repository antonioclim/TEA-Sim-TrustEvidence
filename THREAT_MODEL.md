# TrustEvidence threat model

This document defines the system boundary for the TrustEvidence reference artefacts. Clinical payloads remain in authoritative clinical or organisational repositories. The TrustEvidence layer records compact evidence artefacts about consent state, provenance, access, integrity anchoring, policy context and backend receipts.

## Actors

- Data source: mobile, wearable, clinical or organisational system that provides payload context.
- FHIR semantic boundary: system boundary at which relevant events can be represented or related to FHIR resources.
- Payload custodian: organisation that remains responsible for clinical payload storage and re-identification governance.
- Evidence emitter: component that emits TrustEvidence artefacts.
- Evidence backend: central-audit, append-only hash-log or ledger-like storage mechanism.
- Verifier or auditor: party that checks artefact integrity, backend receipts and retained verifier state.

## Assets

- Clinical payloads and payload references.
- TrustEvidence artefacts.
- Backend log state and checkpoints.
- Consent, policy and provenance context.
- Verification state held by auditors or witnesses.

## Adversaries

- External tamperer attempting to alter payloads or evidence artefacts.
- Malicious custodian insider suppressing or modifying evidence before emission.
- Compromised evidence-log log log operator attempting deletion, rollback or inconsistent histories.
- Colluding custodian and backend participants.
- Split-view backend presenting inconsistent checkpoints to different verifiers.

## Property targets

- Tamper-evidence: changes to retained payload commitments or artefacts are detectable under the declared hash and signature assumptions.
- Inclusion verifiability: a verifier can check that a given artefact is included in a committed backend state.
- Append-only consistency: later backend states extend earlier accepted states rather than rewriting them.
- Non-equivocation: inconsistent histories are detectable when verifier-state comparison, witness mechanisms or finality assumptions are available.
- Boundary completeness: completeness covers only events that cross the instrumented evidence-emission boundary. Events silently suppressed before that boundary remain outside backend guarantees.

## Backend interpretation

A central audit backend is operationally simple but depends on the controlling organisation. An append-only hash log strengthens deletion and rollback detection when retained checkpoints are compared. A ledger-like backend adds replicated finality assumptions but increases operational and metadata burden. The model therefore treats ledger-like storage as conditional, not as the default architecture.
