# TEA-Sim v2.2.0: Portable audit evidence for health information exchange

TEA-Sim TrustEvidence is a healthcare-specific audit-evidence boundary and executable reference profile. It distinguishes audit facts that may cross organisational boundaries from clinical payloads that remain under source custody.

- Exact-version DOI: <https://doi.org/10.5281/zenodo.21533962>
- GitHub release: <https://github.com/antonioclim/TEA-Sim-TrustEvidence/releases/tag/v2.2.0>
- Canonical asset: `TEA-Sim-TrustEvidence-v2.2.0.zip`
- Related peer-reviewed article: <https://doi.org/10.1080/08874417.2026.2720000>

## Related research and publication boundary

The software supports the peer-reviewed article:

> Clim, A. (2026). Designing portable audit evidence for health information exchange. *Journal of Computer Information Systems*. <https://doi.org/10.1080/08874417.2026.2720000>

The article reports the design rationale and bounded evaluation of the audit-evidence boundary. This repository provides the citable software, schemas, fixtures, validators, retained evidence and reproduction routes. A software metapaper may describe implementation, quality control, availability and reuse, but must not duplicate the article's research questions, numerical results or contribution argument. See `docs/RELATED_RESEARCH_AND_REUSE.md`.

## What this release executes

The release retains the v2.1.0 personal-monitoring schema and adds a separate health-information-exchange profile with:

- `HIE-DISCLOSURE-001`, a complete synthetic DiagnosticReport disclosure from Synthetic Hospital A to Synthetic Hospital B;
- Consent version 3, policy version 6 and authorisation decision D-204 bindings;
- a signed TrustEvidence envelope containing references, audit facts and a source-payload commitment, but not the DiagnosticReport or Observation payload values;
- a project-specific local A2 Merkle receipt, inclusion material and retained-checkpoint verification;
- a FHIR R4/BALP-facing implementation-guide corpus with retained SUSHI, IG Publisher and HL7 FHIR Validator evidence for the declared positive and intended-negative examples;
- 67 registered C4 security cases, including preserved limitation acceptances and the explicit result that an authorised receipt does not prove truthful tree size, actual log population, completeness or backend honesty;
- a frozen C5 B0-B2 paired local experiment with five excluded pilot blocks, twenty confirmatory paired blocks, sixty process runs and 7,680 retained operation timings;
- deterministic unit, property and finite bounded checks, result contracts, file manifests and SHA-256 catalogues.

## C5 local incremental result

For the exact synthetic W1 disclosure case on the reported GitHub-hosted runner, the complete B2 reference path added median local operation-level increments of 9.023 ms at p50, 9.290 ms at p95 and 9.668 ms at p99 relative to B0 local source processing. The exact fixture added 16,205 canonical application bytes and produced a 215,339-byte project-defined local storage proxy after 128 operations.

These values are **not** production-EHR latency, network traffic, database storage, service-level performance, scalability or organisational cost results. No negligible-overhead or equivalence margin was defined.

## Cryptographic and confidentiality boundary

SHA-256 is used for exact-byte commitments and Merkle hashing. Ed25519 authenticates issuer and backend statements under deterministic test registries. Base64 in FHIR Binary is encoding, not encryption. The release does not implement or evaluate operational transport security, at-rest encryption, hardware security modules, certificate lifecycle management, key rotation or revocation.

## Quick start

Use Python 3.13 in a fresh virtual environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check --no-input setuptools==82.0.1 wheel==0.46.3
python -m pip install --disable-pip-version-check --no-input -r environment/requirements-lock-py313-linux.txt
python -m pip install --disable-pip-version-check --no-input --no-build-isolation --no-deps -e .
make release-check
```

The detailed route is in `REVIEWER_REPRODUCTION.md`. The hosted workflow separately re-runs the official FHIR toolchain and the deterministic fresh-extraction release gate.

## Independent reproduction

A non-author reproducer may run the controlled reporting wrapper:

```bash
python scripts/run_independent_reproduction.py --mode core
```

The wrapper records the software version, environment, commit, commands, exit status and captured outputs under the ignored `results_local/` directory. Full instructions and the signed report template are in `independent_reproduction/`.

## Reuse

`docs/RELATED_RESEARCH_AND_REUSE.md` defines three bounded reuse routes:

1. profile a new cross-organisational healthcare event without copying its clinical payload;
2. reuse the mutation and result-contract corpus for research or teaching;
3. replace the local A2 backend while retaining the field/custody boundary and competency questions.

## Component and deployment boundary

`docs/DEPLOYABILITY_AND_COMPONENTS.md` lists the implemented components, integration points and omitted operational controls. The package is a reference implementation, not a hospital-ready system. In particular, it does not provide an operational FHIR server, identity provider, consent-decision service, durable replicated log, database, queue, HSM/KMS, monitoring platform, recovery process or organisational operating model.

## Reproducibility and retained evidence

The v2.1.0 monitoring reference corpus is preserved as a historical schema-profile corpus. Version 2.2.0 adds the C3 FHIR validation evidence, C4 mutation corpus and C5 paired local measurements. Measurement-variable outputs are retained rather than regenerated to manufacture byte equality; their contracts, row counts, derivations and source digests are checked.

The canonical public archive is deterministically built, contains archive-specific `FILE_MANIFEST.tsv` and `SHA256SUMS.txt`, excludes submission-specific `docs/route_c/` governance material, and is tested after fresh extraction. `docs/PUBLIC_RELEASE_SCOPE.md` defines that distribution boundary.

The `v2.2.0` tag and manually uploaded canonical release asset remain immutable. Later commits on `main` may correct metadata or improve public documentation. They do not alter the bytes, claims or identity of the archived v2.2.0 asset and must not be cited as a replacement release.

## Support, contribution and security

- Routine support: `SUPPORT.md`
- Contributions: `CONTRIBUTING.md`
- Security reporting and claim boundary: `SECURITY.md`

## Claim ceiling

The release supports bounded claims about the synthetic hero case, the declared official-validator corpus, registered mutation decisions, exact signed-byte preservation, local retained-checkpoint behaviour and the reported W1 B0-B2 increments. It does not establish:

- real-patient or operational-hospital validation;
- universal FHIR/BALP conformance or HL7/IHE certification;
- SCITT or RFC 9942 conformance;
- clinical, consent, policy or identity truth;
- encryption, confidentiality, privacy compliance or legal compliance;
- truthful tree size, actual log population, complete event capture or public transparency;
- replay prevention, global non-equivocation or backend honesty;
- production readiness, large-network scalability or hospital service-level acceptability;
- network/database/cloud cost, organisational cost reduction or improved organisational trust;
- expert validation or consensus.

## Citation

Clim, A. (2026). *TEA-Sim v2.2.0: Portable audit evidence for health information exchange* (Version 2.2.0) [Computer software]. Zenodo. <https://doi.org/10.5281/zenodo.21533962>
