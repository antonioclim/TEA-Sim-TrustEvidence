# Phase C6 completion report

## Formal verdict

```text
Gate C6:                              PASS
Authoritative hosted candidate run:  30033737668
Authoritative candidate head:        94c2600ce3cf5b5e267f8e3f67b01191824a32ae
Workflow conclusion:                 success
Candidate asset SHA-256:             dc842582f299a366879146f905d6be80f5688b3810c4cbebf9e0a925014a317c
Public release authorised:           no
GitHub release created:              no
Zenodo record created:               no
main modified:                       no
```

The completion report and reviewer-governance updates are internal `docs/route_c/` records added after the authoritative candidate run. They are excluded from the curated public ZIP by design. The branch integrity catalogues are synchronised after these records are added; that documentation-only synchronisation must not change the candidate asset digest above.

## Candidate identity

| Layer | Frozen value |
|---|---|
| Target final software version | `2.2.0` |
| PEP 440 package candidate | `2.2.0rc1` |
| Display candidate | `2.2.0-rc.1` |
| Reserved candidate tag | `v2.2.0-rc.1` |
| Reserved final tag | `v2.2.0` |
| Candidate archive root | `TEA-Sim-TrustEvidence-v2.2.0-rc.1` |
| Candidate ZIP | `TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip` |
| Candidate checksum file | `TEA-Sim-TrustEvidence-v2.2.0-rc.1.sha256` |
| New exact-version DOI | unassigned |
| Previous exact-version DOI | `10.5281/zenodo.21318387` |
| Publication authorised | `false` |

The personal-monitoring envelope remains version `2.1.0`. The additive HIE envelope is a separate `1.0.0` profile identified as `TE-HIE-Envelope-1`. C6 does not relabel historical envelopes.

## Integrated release-candidate content

C6 aligned:

```text
pyproject.toml
src/trustevidence/__init__.py
README.md
CITATION.cff
.zenodo.json
RELEASE_METADATA.json
CHANGELOG.md
RELEASE_NOTES_v2.2.0-rc.1.md
QUICKSTART.md
REPRODUCIBILITY.md
REVIEWER_REPRODUCTION.md
OUTPUT_MANIFEST.md
DATA_ACCESS.md
docs/VERSIONING_AND_CITATION.md
docs/MIGRATION_v2.1.0_TO_v2.2.0.md
docs/PUBLIC_RELEASE_SCOPE.md
docs/DEPLOYABILITY_AND_COMPONENTS.md
```

The metadata audit rejected a current-release or current-DOI representation. Candidate metadata consistently describes an unreleased v2.2.0-rc.1 review artefact and identifies v2.1.0 only as the previous exact release.

## CI simplification and supply-chain controls

The final workflow removed write-capable one-time C3–C5 materialisation jobs. Scientific and release-validation jobs operate with read-only repository permissions.

All 21 external GitHub Actions references in the final workflow are pinned to observed 40-character commit SHAs. The pinned set includes checkout, Python, Node, Java, Ruby and artifact-upload actions.

Pinning eliminates mutable tag references in the inspected workflow. It does not establish that the actions, runner image or dependencies are free of vulnerabilities or compromise.

## Public-distribution boundary

The public software distribution is identified, not anonymous. It retains author and repository metadata and is distinct from the anonymous journal-review package.

The archive includes source, schemas, synthetic examples, retained evidence, result contracts, standards-facing artefacts, tests, figures, tables and release utilities. It excludes:

- `docs/route_c/` submission and reviewer-governance records;
- temporary workflow and staging machinery;
- Git metadata, virtual environments, caches and local outputs;
- manuscript files, editorial email, submission PDFs and reviewer-response documents.

The hosted distribution audit reported:

```text
status:                         PASS
public files:                   360
source/text files scanned:      335
fatal findings:                 0
excluded governance prefix:     docs/route_c/
```

The deterministic payload-commitment nonce is retained only as an explicitly documented TEST-ONLY fixture. It is not operational key material and must not be reused.

## Deterministic archive result

The hosted C6 job built the candidate twice from the same candidate tree and required byte-for-byte identity for both the ZIP and outer checksum file.

The authoritative result is:

```text
asset:            TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip
size:             6,031,564 bytes
SHA-256:          dc842582f299a366879146f905d6be80f5688b3810c4cbebf9e0a925014a317c
canonical root:   TEA-Sim-TrustEvidence-v2.2.0-rc.1
archive files:    360
manifest rows:    358
checksum rows:    359
archive errors:   0
```

An independent local rebuild from the extracted candidate reproduced the same ZIP digest and byte stream.

## Fresh-extraction execution

The hosted release-candidate job:

1. executed `make release-check` on the checked-out candidate;
2. audited the curated public distribution;
3. built the archive twice and compared the byte streams;
4. validated the outer checksum, canonical archive root, member safety, internal manifest and internal checksums;
5. extracted the archive into a clean directory;
6. created a new Python virtual environment;
7. installed the locked environment from the extracted archive;
8. executed the complete `make release-check` contract again;
9. rejected any source-tree drift.

Both the pre-archive and fresh-extraction contracts returned:

```text
RELEASE-CHECK: PASS
```

## Hosted contract counts

### Checked-out candidate tree

```text
unit/regression pytest items:        52 passed
property-test items:                 8 passed
finite bounded checks:               29,105
bounded failures:                    0
reproducibility-manifest rows:       66 current
result contracts:                    14
retained CSV rows validated:         691
distributed branch files:            391
branch SHA-256 entries:              390
branch file-manifest rows:           389
immutable Action references:         21
```

### Fresh public archive

```text
distributed files:                   360
internal SHA-256 entries:            359
internal file-manifest rows:         358
```

### C3–C5 regression evidence

```text
C3 retained files:                   41
FHIR positive units:                 4
intended negative rejections:        2
adjudicated publisher warnings:      33

C4 registered cases:                 67
expected rejections:                 54
false accepts:                       0
state non-advancement failures:      0

C5 retained process runs:            60
raw operation timings:               7,680
paired increments:                   60
aggregate estimates:                 18
```

The legacy quick pipeline also retained 48 events, 16 successful receipt checks, two controlled mutations rejected, zero ordinary verification failures, zero validation failures and 66 result rows.

## Hosted workflow and artifact provenance

```text
workflow name:   Route C CI
run ID:          30033737668
run number:      373
head branch:     revision/jcis-route-c
head SHA:        94c2600ce3cf5b5e267f8e3f67b01191824a32ae
conclusion:      success
```

Hosted artifact digests:

```text
route-c-v2.2.0-rc.1
sha256:ac34cec6db37099204cc77afc9eee3922d2ee5bb3de85d007322d34d01dbb8ca

route-c-release-check-log
sha256:82c872007bcbe9d698320d3d88cc649405cba56202cbdc5bd2788b91cde8a8d9

route-c-integrity-files
sha256:4e5e62d820a232c76aa6c6e6de39ab86b5715bd7dcf60e612bcd7b188d582b43

route-c-fhir-validation
sha256:a04fcc1aa58ac7c33eaed47e1c07d16fc703097b53785b9f3b6a0d7cb4899fc1

route-c-c4-security-validation
sha256:7863d209417ad6fda6ffb21c2fcfc8798cb7dfd2f02f9e661b2a45b16b5f9c60

route-c-c5-overhead-validation
sha256:0794b892c27228c137c959bb5f2784637a45f5cdb3e0fbfa5eb1dc5bf45adccd
```

The GitHub artifact digest identifies the artifact wrapper. The canonical candidate ZIP inside the C6 artifact has the separate SHA-256 `dc842582...a317c` reported above.

## Deployability and practical-significance result

C6 provides an explicit inventory of implemented components and omitted production controls. Implemented reference components include:

- closed monitoring and HIE schemas;
- semantic and minimisation checks;
- canonicalisation and commitments;
- issuer signatures under test registries;
- a local A2 Merkle model;
- a bounded FHIR R4/BALP-facing projection;
- C4 adversarial evidence;
- C5 local incremental evidence;
- reproducibility and release controls.

Operational capabilities not supplied include:

- authenticated FHIR server/client integration;
- workforce, patient and service identity federation;
- authoritative Consent and policy lifecycle;
- HSM/KMS, rotation, revocation and compromise recovery;
- TLS and at-rest encryption configuration;
- transactional persistent custody, indexing and backup;
- concurrency, replication, partition and capacity testing;
- failover, retry, idempotency and disaster recovery;
- observability and incident response;
- legal and organisational operating procedures;
- independent witnessing and public transparency;
- clinical-safety and human-factors evaluation.

C6 therefore supports a component and integration-point analysis. It does not support hospital readiness, production deployability, scalability or organisational cost reduction.

## Hostile audit disposition

The hostile C6 review identified and retained the following limitations:

- release candidate, not public release;
- environment reproducibility, not deployment validation;
- component inventory, not deployability evidence;
- full-SHA Actions, not general supply-chain security;
- residue and secret-pattern scan, not privacy validation;
- deterministic TEST-ONLY fixture, not operational secret management;
- deterministic archive, not deterministic timing values;
- official FHIR evidence remains corpus-bounded and retains 33 adjudicated warnings;
- project verifier execution is not an independent cross-language implementation;
- local A2 remains non-persistent and non-public;
- C5 plus component inventory do not establish cost reduction;
- the identified public archive is not the anonymous review package;
- release engineering does not repair the manuscript without C7/C8.

No hostile finding requires withdrawal of the bounded C6 release-reproducibility claim.

## Claim promotions after C6

C6 permits the following bounded statements:

- the exact candidate metadata are coherent and do not assert a public DOI or release;
- all inspected external Actions references are immutable full SHAs;
- the declared public distribution scan reported no listed submission residue or common secret pattern;
- the candidate archive was built deterministically and passed internal and external integrity checks;
- the full release contract passed before and after fresh extraction;
- C3, C4 and C5 evidence passed regression on the candidate;
- the component inventory identifies operational work that remains absent.

C6 does not permit claims of public publication, hospital deployment, production performance, large-network scalability, independent implementation verification, privacy, legal compliance, organisational trust improvement or cost reduction.

## Gate checklist

- [x] Candidate identity and version boundaries agree.
- [x] No new DOI was invented.
- [x] Publication remains unauthorised.
- [x] v2.1.0 objects were not relabelled.
- [x] Candidate metadata are coherent.
- [x] One-time C3–C5 materialisation jobs were removed.
- [x] External Actions are pinned to full SHAs.
- [x] Public and internal branch scopes are separated.
- [x] Distribution residue/secret-pattern audit passed.
- [x] Deterministic double archive construction passed.
- [x] Outer checksum passed.
- [x] Internal manifest and checksums passed.
- [x] Path, root and duplicate-member checks passed.
- [x] Pre-archive release contract passed.
- [x] Fresh-extraction release contract passed.
- [x] C3 official FHIR regression passed.
- [x] C4 security regression passed.
- [x] C5 overhead-corpus validation passed.
- [x] Source-tree drift check passed.
- [x] `main` remained unchanged.
- [x] No GitHub release or Zenodo record was created.

## Formal closure

```text
Gate C6 = PASS
public release permission = DENIED UNTIL C9
merge to main = DENIED UNTIL C7/C8/C9 HAND-OFF
next owning phase = C7
```

C7 must now reconstruct the manuscript from the C2–C6 evidence rather than append new paragraphs to the submitted version. C8 must construct the response and anonymous/identified submission package. C9 remains responsible for the final v2.2.0 GitHub/Zenodo publication sequence.
