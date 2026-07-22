# Route C bounded threat model

## Scope

This threat model applies to the `v2.2.0` Route C reference package. It covers the signed TrustEvidence envelope, nonce-based payload commitments, the project-specific local A2 Merkle model, retained checkpoints and the release artefacts. It does not describe a deployed hospital security architecture, a public transparency service, a production key-management system or a legal evidentiary framework.

## Protected assets

- the semantic content of the TrustEvidence evidence core;
- the exact canonical bytes signed by the emitter fixture or declared issuer;
- payload commitment values and withheld nonces;
- the local A2 leaf sequence, root and inclusion path;
- the binding between an evidence core and its receipt;
- retained verifier checkpoints;
- schemas, negative fixtures and expected outputs;
- software, manifests, figures and retained results distributed in the release.

## Trust boundaries

1. **Source context to curation pipeline.** Source event metadata may be incomplete or false. The reference package validates structure and declared semantics but cannot establish upstream truth.
2. **Curation pipeline to signed envelope.** Canonicalisation, minimisation and signing must preserve the declared fields and exclude prohibited payload.
3. **Signed envelope to local A2 model.** The local backend receives a digest derived from the signed evidence core. It must not reinterpret the healthcare semantics.
4. **Receipt to verifier.** The verifier must bind the evidence core, digest, backend and log identifiers, leaf index, tree size, path and checkpoint root.
5. **Repository to reviewer.** Release manifests, checksums and fresh-extraction procedures must expose accidental or malicious file changes.

## Adversary classes

| Adversary | Capabilities considered | Capabilities not established by this study |
|---|---|---|
| Network or file modifier | changes envelope, signature, receipt, proof or retained output | active TLS interception in an operational deployment |
| Malicious evidence submitter | supplies malformed, excessive or privacy-violating event metadata | compromise of a real clinical identity provider |
| Malicious local-log operator | relabels index or tree size, substitutes roots or presents stale state | globally coordinated split-view resistance |
| Repository modifier | changes code, figures, metadata or retained outputs | compromise of GitHub, Zenodo or signing infrastructure |
| Authorised-key attacker | possesses a valid fixture or authorised private key | post-compromise forensic attribution or non-repudiation |

## Security objectives

### SO-01 — Structural validity

Malformed JSON, duplicate keys, non-finite numbers and schema-invalid objects must be rejected before semantic or cryptographic processing.

### SO-02 — Payload minimisation

Direct identifiers, raw monitoring samples, clinical notes and credential material must not enter the public envelope. The test-only private payload remains outside the distributed evidence object.

### SO-03 — Canonical determinism

The declared TE-JCS profile must produce stable RFC 8785 canonical bytes for the same valid input under the executed implementation.

### SO-04 — Issuer-signature integrity

Any change to the signed evidence core must invalidate the Ed25519 signature under the declared public key.

### SO-05 — Payload-commitment integrity

A commitment must fail when the retained payload bytes or nonce change. A commitment does not provide confidentiality and does not prove that the source payload is clinically correct.

### SO-06 — Receipt binding

The local A2 verifier must reject substitution or relabelling of the evidence core digest, backend identity, log identity, leaf index, tree size, root or inclusion path.

### SO-07 — State-relative consistency

A verifier retaining a prior checkpoint must reject a stale state or expose a same-size divergent root when the two roots are compared. This is a state-relative detection property, not universal non-equivocation.

### SO-08 — Release integrity

The distributed tree must match its file manifest and SHA-256 checksum list; retained outputs must satisfy their contracts and regenerate according to the documented route.

## Mandatory mutation families

- evidence-core field mutation;
- actor or emitter substitution;
- consent or policy binding mutation;
- object/version token mutation;
- payload or nonce mutation;
- issuer signature mutation;
- receipt signature mutation;
- backend or log identifier substitution;
- leaf-index and tree-size relabelling;
- root and path mutation;
- stale checkpoint and same-size divergent root;
- direct-identifier and nested-payload insertion;
- malformed timestamp, duplicate key and non-finite value.

## Verification outcomes

The local verifier may return:

- `PASS`: all checks required by the selected local policy passed;
- a stable failure code identifying the first mandatory failed property;
- `INDETERMINATE` in documentation when the requested assurance requires an unexecuted external service, operational key state or unavailable source material.

A `PASS` does not mean that the underlying healthcare event occurred, that all relevant events were emitted, that the payload is clinically correct, or that the evidence is legally sufficient.

## Key assumptions

- Ed25519 and SHA-256 are used through the pinned cryptography implementation;
- deterministic private keys are test fixtures only;
- private fixture material is not a production deployment pattern;
- verifier public keys are supplied through the controlled test environment;
- no operational key rotation, revocation service, hardware security module or certificate policy is evaluated.

## Privacy assumptions and residual risks

The envelope may contain pseudonymous subject and actor tokens, controlled event types, organisations, purpose codes, time values and object types. These fields may remain linkable or permit inference even when raw physiological values are absent. The Route C package therefore supports payload minimisation, not anonymity or complete privacy protection.

## Non-goals

Route C does not establish:

- clinical truth or identity proofing;
- confidentiality of the public envelope;
- complete event capture;
- distributed consensus;
- public witnessing or gossip;
- prevention of a malicious authorised issuer from signing false statements;
- resistance after compromise of an authorised key;
- legal non-repudiation;
- production denial-of-service resistance;
- compliance with healthcare law or standards certification.

## Release blockers

The release is blocked by any false acceptance of a mandatory mutation, any change to verifier state after invalid verification, any direct-identifier or raw-payload finding in portable evidence, any mismatch between the evidence verified and the evidence transported through the FHIR case, or any unreconciled release-manifest difference.
