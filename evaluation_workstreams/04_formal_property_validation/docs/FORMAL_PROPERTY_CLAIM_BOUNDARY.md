# FORMAL_PROPERTY_CLAIM_BOUNDARY.md

formal/property validation workstream supports property-based and bounded executable checks for the A2 Merkle reference backend only. The evidence does not establish mathematical security proof, comprehensive formal verification, production assurance, legal compliance, clinical validation or FHIR/BALP conformance.

## Supported wording

The local A2 Merkle reference implementation is accompanied by property-based tests and bounded executable checks for append-only, inclusion-verification, tamper-rejection, deterministic canonicalisation, receipt self-consistency/path-binding, checkpointed tree-size rejection, prefix-consistency and verifier-visible same-size root-comparison assumptions under stated local-reference conditions.

## Not supported

Do not use `formally verified`, `cryptographic proof`, `proved secure`, `non-equivocation guaranteed`, `production secure`, `FHIR/BALP conformant`, `GDPR compliant`, `EHDS compliant`, `ISO 27789 conformant` or `clinical validation` wording.

## Receipt boundary

`receipt_digest` is a local self-consistency commitment over receipt fields and proof material. It is not a digital signature, not notarisation and not an external witness.
