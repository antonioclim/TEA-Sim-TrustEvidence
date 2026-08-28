# Contributing

Contributions that improve correctness, reproducibility, documentation, test coverage or reuse are welcome.

## Suitable contributions

- reproducible bug fixes;
- additional negative or mutation cases with an explicit expected decision;
- independent verifier implementations;
- documentation corrections;
- accessibility and usability improvements;
- new synthetic healthcare-information-exchange examples;
- support for additional maintained tooling, provided the claim boundary remains explicit.

## Before submitting a change

1. Open an issue or concise proposal for changes that alter schemas, verification semantics, result contracts or public claims.
2. Work from the current default branch.
3. Keep changes narrowly scoped.
4. Add or update tests for behavioural changes.
5. Run the complete local release contract where the documented environment is available:

```bash
make release-check
```

6. State any check that could not be executed and why.

## Data and confidentiality

Contributions must not contain patient data, direct identifiers, credentials, private keys, access tokens, restricted datasets or institutional audit logs. Synthetic fixtures must be clearly labelled. Public-data contributions must identify the source, licence and redistribution boundary.

## Scientific and standards wording

A contribution must not imply clinical validation, production readiness, legal compliance, FHIR or IHE certification, complete event capture, backend honesty, public transparency or global non-equivocation unless new evidence directly establishes the specific claim.

FHIR, BALP, SCITT, COSE Receipts, canonicalisation, digital signatures and Merkle-tree mechanisms must be described as established standards or primitives where applicable.

## Code and documentation

- Use Python 3.13 for the locked reference environment.
- Preserve deterministic identifiers and seeds in retained tests.
- Prefer explicit validation failures to permissive fallbacks.
- Use British English in public documentation.
- Keep generated products out of source directories unless the release contract explicitly retains them.
- Update result contracts, provenance records, manifests and checksums when distributed files change.

## Licence

By submitting a contribution, you agree that it may be distributed under the repository's Apache License 2.0. Contributors remain responsible for ensuring that submitted material is legally reusable.
