# TEA-Sim v2.2.0-rc.1 release-candidate notes

## Candidate identity

- Target final release: `2.2.0`
- PEP 440 package version: `2.2.0rc1`
- Candidate label/tag reserved for testing: `v2.2.0-rc.1`
- Candidate asset: `TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip`
- Previous exact release: `v2.1.0`, DOI <https://doi.org/10.5281/zenodo.21318387>
- Current v2.2.0 DOI: **unassigned**
- Publication authorised: **no**

The candidate tag and release URLs recorded in metadata are planned identifiers. No public candidate or final release is asserted by this file.

## Principal additions since v2.1.0

- A healthcare-specific audit-evidence boundary and separate `TE-HIE-Envelope-1` profile.
- A complete synthetic DiagnosticReport disclosure between two synthetic hospitals, including Consent version 3, policy version 6, decision D-204, signed envelope, local receipt and verification report.
- A bounded FHIR R4/BALP-facing implementation guide with retained official-tool evidence for four positive units and two intended negative rejections.
- Sixty-seven deterministic C4 security cases, including six explicit limitation acceptances and a preserved failed original expectation concerning authorised false tree-size assertions.
- A paired C5 B0-B2 local experiment: five excluded pilot blocks, twenty confirmatory paired blocks, sixty process runs and 7,680 operation timings.
- B2-B0 median local increments of 9.023 ms at p50, 9.290 ms at p95 and 9.668 ms at p99 for W1 on the reported host.
- Exact-fixture increments of 16,205 canonical application bytes and a 215,339-byte local storage proxy after 128 B2 operations.
- Public component/deployability and distribution-boundary documents.
- Deterministic archive construction, fresh-extraction execution, archive-specific checksums and supply-chain pin auditing.

## Compatibility

The established personal-monitoring envelope remains at version `2.1.0`. The HIE envelope is a separate version `1.0.0` profile. Existing v2.1.0 envelopes must not be relabelled as HIE envelopes, and HIE envelopes must not be presented as backwards-compatible personal-monitoring envelopes. The Python distribution version changes because the software package adds a substantial, additive profile and evidence programme.

## Claim boundary

The candidate is not evidence of production-EHR latency, hospital readiness, large-network scalability, database or network cost, clinical validity, legal compliance, event completeness, backend honesty, replay prevention, global non-equivocation, organisational trust improvement or cost reduction.

## Publication hand-off

C9 must replace candidate metadata with final `v2.2.0` metadata, assign the exact Zenodo DOI, create the final GitHub tag/release, upload the identical canonical ZIP byte stream to GitHub and Zenodo, verify both records and then update the manuscript availability statement. Until that hand-off, this file is release-candidate documentation only.
