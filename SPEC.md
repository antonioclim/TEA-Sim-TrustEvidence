# TrustEvidence interface specification

TrustEvidence artefacts are compact audit-evidence envelopes. They bind an evidence event, semantic context, policy and consent state, payload commitment and optional backend receipt without storing clinical payloads in the evidence backend.

## Envelope structure

The envelope contains:

1. `envelope_version` — version of the envelope format.
2. `artefact_core` — signed semantic body.
3. `backend_receipt` — optional backend acknowledgement and proof reference.
4. `verification_material` — optional proof or witness material supplied to verifiers.
5. `extensions` — controlled extension area for implementation-specific data.

The signed semantic body is canonicalised before hashing or signing. Backend receipts are not part of the signed semantic body because they are produced after backend acceptance.

## Core fields

Important fields include `artefact_id`, `evidence_type`, `event_id`, `event_action`, `occurred_at`, `emitted_at`, `emitter`, `subject_ref`, `semantic_binding`, `policy_binding`, `consent_binding`, `payload_binding`, `privacy_controls` and `emitter_signature`.

## Backend receipt fields

Backend receipts may include `backend_type`, `backend_id`, `log_id`, `alg_id`, `core_hash`, `tree_size`, `root_hash`, `leaf_index`, `inclusion_proof_ref`, `consistency_proof_ref`, `witness_ref`, `finality_ref`, `issued_at`, `signer_id` and `receipt_signature`.

## Verification modes

Offline verification can check schema validity, canonicalisation, signatures, supplied proof material, backend identity, log identity, retained verifier state and timestamp coherence. Online verification is required when the verifier must retrieve current checkpoints, witness state, finality evidence or live policy/consent state.

## FHIR relationship

The FHIR material in this repository is draft FHIR Shorthand. It supports a standards-aligned mapping to AuditEvent and Provenance, but this repository does not claim HL7 endorsement, IHE endorsement or FHIR/BALP conformance. Full conformance requires successful SUSHI and implementation-guide publisher validation in the target environment.
