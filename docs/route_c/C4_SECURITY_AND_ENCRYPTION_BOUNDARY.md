# C4 security, confidentiality and encryption boundary

## Purpose

This document prevents cryptographic mechanisms in the Route C reference package from being conflated with encryption, clinical truth, legal assurance or complete audit coverage.

## Mechanism-to-property map

| Mechanism | Implemented use | Property tested | Property not established |
|---|---|---|---|
| Deterministic application-profile canonicalisation | Produces stable bytes for the signed HIE core and committed source fixture | Deterministic bytes for admitted inputs | Semantic correctness, cross-language equivalence beyond tested vectors |
| SHA-256 nonce-based payload commitment | Binds exact source Bundle bytes, representation profile, context and nonce | Candidate-byte and nonce substitution detection | Encryption, confidentiality, clinical correctness, proof of possession by an operational custodian |
| Ed25519 issuer signature | Signs the declared HIE evidence core | Unauthorised mutation detection under the fixture key registry | Identity proofing, truth of actor/Consent/policy/clinical claims, legal non-repudiation, post-compromise security |
| Ed25519 receipt signature | Signs the project-specific local A2 receipt | Receipt-origin and receipt-byte authentication under the fixture registry | Backend honesty, truthful tree-size assertion, event completeness, public witnessing, trustworthy log operation after key compromise |
| Merkle inclusion path | Binds one core digest to one declared root, index, path and tree-size statement | Membership relative to the supplied local tree statement | Actual log population, event completeness, truthful backend operation, ordering truth beyond supplied state, global consistency |
| Retained checkpoint plus consistency proof | Compares a received state with one locally retained prior state | Rollback detection, verifier-visible same-size fork detection and accepted prefix extension | Gossip, cross-verifier comparison, public transparency, global non-equivocation |
| Closed JSON Schema | Rejects unknown and structurally inadmissible fields | Profile admission for the exact version | Safe interpretation of future extensions or universal semantic interoperability |

## Falsified expectation retained by C4

The first hosted C4 run expected a coherently relabelled and re-signed tree size to fail inclusion verification. It was accepted. The case is retained as `LIM-BACKEND-002`: a valid backend signature authenticates the supplied tree-size statement but does not independently prove the actual number of captured events or the operational honesty of the backend. The original failed workflow and artifact digest are recorded in `C4_PROTOCOL_DEVIATION.md`.

## Encryption statement

The Route C evidence protocol does **not** implement payload encryption. Hashing and digital signatures are not encryption. The FHIR `Binary` carries Base64-encoded exact signed JSON bytes; Base64 is an encoding, not confidentiality protection.

The reference pipeline does not open an application network connection between hospitals. Consequently, TLS is not an evaluated protocol result. GitHub Actions package downloads and the terminology-server connection belong to the build environment, not to the healthcare exchange design.

Encryption at rest, database transparent-data encryption, hardware security modules, envelope encryption, access-control enforcement and operational key rotation are deployment controls outside the executed Route C reference pipeline.

## Nonce treatment

The nonce is absent from the signed portable envelope and FHIR Portable Evidence Bundle. For deterministic reproduction, the package contains a clearly labelled TEST-ONLY nonce under `private_test_material/`. It has no secrecy value and must not be reused or interpreted as an operational secret.

## Reviewer-facing wording

Permitted:

> Hashing is used for exact-byte integrity commitments, while Ed25519 signatures authenticate the issuer statement and local receipt under the declared test key registries. The supplied reference pipeline does not encrypt the portable evidence or the clinical payload. A valid receipt authenticates a backend assertion but does not prove event completeness or truthful log population. Transport and at-rest encryption remain deployment controls and were not evaluated.

Prohibited:

- encrypted by hashing;
- tamper-proof;
- immutable;
- non-repudiable;
- complete audit trail;
- truthful tree size proven by a receipt;
- privacy guaranteed;
- secure hospital deployment;
- SCITT or RFC 9942 conformant;
- globally non-equivocating.
