# C1 baseline audit

## Repository identity at branch creation

- Repository: `antonioclim/TEA-Sim-TrustEvidence`.
- Default branch: `main`.
- Route C branch: `revision/jcis-route-c`.
- Public package version: `2.1.0`.
- Python requirement: `>=3.13,<3.14`.
- Exact-version software DOI recorded by the package: `10.5281/zenodo.21318387`.
- Provisional Route C release: `2.2.0`.

## Existing executable evidence

The `v2.1.0` tree already contains:

- Draft 2020-12 schemas for monitoring events, evidence envelopes and curation results;
- RFC 8785 canonicalisation under the TE-JCS application profile;
- Ed25519 fixture signatures;
- nonce-based payload commitments;
- a project-specific, RFC-9162-shaped local A2 Merkle model;
- unit, property-based and finite bounded checks;
- controlled mutation tests;
- retained workload, figure and table outputs;
- result contracts, file manifests and SHA-256 checksums;
- a one-command `make release-check` route.

These assets are reusable, but their evidence remains local and reference-implementation-bounded.

## Baseline deficiencies requiring C1 action

### CI absent

The latest `main` history removed `.github/workflows`. There is therefore no hosted independent execution of the current `v2.1.0` release-check route.

### Python-version drift in the deleted workflow

The deleted workflow used Python 3.12, whereas the current package and lock file require Python 3.13. Any restored workflow must use the current package requirement and the pinned Python 3.13/Linux dependency set.

### Integrity coupling

`make release-check` verifies both `FILE_MANIFEST.tsv` and `SHA256SUMS.txt`. New Route C documentation and workflow files must be represented in those integrity files before the release-check gate can pass.

### Scientific identity drift

The current repository title emphasises personal-health-monitoring curation, while the submitted manuscript emphasises cross-organisational audit-evidence boundaries. C2 must reconcile these identities before release metadata or manuscript text is changed.

### Standards and empirical gaps

The current package does not establish:

- official FHIR/BALP conformance;
- a complete cross-organisational FHIR case;
- production deployment;
- a persistent A2 service;
- a measured A1 backend;
- total production EHR overhead;
- operational key management;
- expert validation.

Route C will close only the bounded subset defined in the charter and claim ceiling.

## Existing release-check contract

The current Makefile requires:

1. source compilation;
2. unit and regression tests;
3. property-based tests;
4. finite bounded checks;
5. retained-result manifest validation;
6. result-contract validation;
7. public metadata and repository checks;
8. SHA-256 and file-manifest integrity checks;
9. quick integrated pipeline execution;
10. result analysis;
11. figure regeneration;
12. table regeneration;
13. comparison with retained reference outputs;
14. final repository checks.

C1 restores hosted CI around this existing contract rather than replacing it with a weaker smoke test.

## C1 acceptance criteria

- a workflow exists on `revision/jcis-route-c`;
- it uses Python 3.13 and the exact Linux lock file;
- it executes `make release-check`;
- mandatory unit, property and bounded tests are not skipped;
- generated outputs do not create an unexplained repository diff;
- integrity files include all distributed Route C documentation and CI files;
- the pull request remains draft until the workflow is green;
- `main` remains unmodified.
