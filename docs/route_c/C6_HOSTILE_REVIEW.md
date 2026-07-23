# Phase C6 hostile release-candidate review

## Audit position

This review assumes that a hostile technical reviewer, release engineer or journal editor will treat every favourable C6 statement as false until the exact artefact, execution boundary and residual limitation are visible.

The authoritative C6 hosted candidate run is:

```text
workflow:       Route C CI
run ID:         30033737668
head SHA:       94c2600ce3cf5b5e267f8e3f67b01191824a32ae
conclusion:     success
candidate ZIP:  TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip
ZIP SHA-256:    dc842582f299a366879146f905d6be80f5688b3810c4cbebf9e0a925014a317c
```

The run passed the branch release contract, deterministic double construction, archive validation, fresh extraction, fresh-environment installation, a second complete release contract, source-tree drift rejection and the C3–C5 regression jobs.

## Hostile findings

### H-C6-01 — The candidate is not a public release

**Attack.** The metadata names `v2.2.0-rc.1`, therefore a public tag, GitHub release and Zenodo record must exist.

**Finding.** False. `RELEASE_METADATA.json` records an unassigned DOI and `publication_authorised: false`. The tag and release URLs are reserved identifiers only. No C6 claim may describe v2.2.0 or v2.2.0-rc.1 as published.

**Residual action.** C9 must reserve the exact DOI, convert candidate metadata to final v2.2.0 metadata, create the final tag and GitHub release, upload the same canonical ZIP byte stream to GitHub and Zenodo and verify both records.

### H-C6-02 — Fresh extraction is not hospital deployment

**Attack.** A complete clean-environment run proves deployment readiness.

**Finding.** False. Fresh extraction establishes package reproducibility on the declared Ubuntu/Python environment. It does not execute an authenticated FHIR server, hospital network, transactional database, key-management service, concurrency regime, failover path, clinical workflow or organisational operating model.

**Claim ceiling.** `environment- and version-bounded software reproducibility`, not `hospital deployability`.

### H-C6-03 — A component inventory is not deployability evidence

**Attack.** `docs/DEPLOYABILITY_AND_COMPONENTS.md` proves that hospitals can deploy the artefact.

**Finding.** False. The inventory separates implemented reference components from missing operational integration points. It identifies identity federation, authoritative Consent and policy services, HSM/KMS, TLS and at-rest controls, durable persistence, concurrency, availability, observability, governance and clinical-safety work as absent or unevaluated.

**Claim ceiling.** The candidate identifies deployment dependencies; it does not establish hospital readiness or implementation effort.

### H-C6-04 — Action pinning is not supply-chain security

**Attack.** Twenty-one full-SHA action references make the CI supply chain secure.

**Finding.** False. Full-SHA references prevent silent movement of action tags. They do not prove that the pinned action, runner image, package index, compiler, downloaded FHIR tooling or transitive dependency is free of vulnerabilities or compromise.

**Claim ceiling.** Mutable action references were eliminated from the inspected workflow. No general supply-chain-security claim is available.

### H-C6-05 — Distribution scanning is not privacy validation

**Attack.** A PASS from `audit_public_distribution.py` proves privacy or anonymity.

**Finding.** False. The scan checks a declared set of submission residues, local-path fragments and common credential patterns. It does not establish anonymity, absence of quasi-identifiers, resistance to inference, legal minimisation or compliance with GDPR, EHDS or another regime.

**Important false-positive adjudication.** An independent broad scan matched `/mnt/data/`, `/home/oai/` and `C:\Users\` inside `scripts/audit_public_distribution.py`. Those strings are the scanner's detection expressions, not leaked paths. The hosted audit intentionally excludes the scanner source from self-scanning and reported no distribution error.

**Claim ceiling.** No declared forbidden submission residue or common secret pattern was identified in the inspected public distribution.

### H-C6-06 — The deterministic nonce fixture is not an operational secret

**Attack.** `payload_commitment_nonce.hex` is a leaked production nonce.

**Finding.** False under the declared package boundary. The file is deterministic TEST-ONLY material required for exact commitment reproduction. It is stored in an explicitly named fixture directory and accompanied by a warning not to reuse it operationally.

**Residual risk.** Reviewers may still misinterpret the filename. C7/C8 must describe it as a reproducibility fixture, never as operational key material.

### H-C6-07 — The archive is large and includes legacy evidence

**Attack.** A 6,031,564-byte ZIP containing 360 files is unnecessarily broad and weakens the claim that Route C is focused.

**Finding.** Partly valid. The candidate retains legacy v2.1.0 personal-monitoring evidence together with the additive HIE profile and C3–C5 evidence. This increases volume but preserves provenance, compatibility and the exact evidence chain. The archive excludes submission-specific Route C governance and receives archive-specific manifests and checksums.

**Residual action.** C7 should cite only evidence needed by the revised study. Legacy outputs must not be presented as new Route C results.

### H-C6-08 — Candidate, package and envelope versions can be confused

**Attack.** The use of `2.2.0rc1`, `2.2.0-rc.1`, `2.1.0` and `1.0.0` is incoherent.

**Finding.** The identities refer to different layers:

```text
final software target:            2.2.0
PEP 440 package candidate:        2.2.0rc1
display candidate:                2.2.0-rc.1
legacy personal-monitoring core:  2.1.0
HIE envelope profile:             1.0.0 / TE-HIE-Envelope-1
```

The separation is defensible only if all public and manuscript wording preserves it. Existing personal-monitoring envelopes must not be relabelled as HIE envelopes.

### H-C6-09 — Deterministic ZIP construction does not make measurements deterministic

**Attack.** Byte-identical archives imply bit-for-bit repeatability of C5 timings.

**Finding.** False. The release archive is byte-deterministic; C5 timing data are retained measurement evidence. A new host run is expected to reproduce the protocol, row counts, decisions and calculation structure, not identical milliseconds.

**Claim ceiling.** The release reproduces deterministic artefacts and verifies the retained measurement corpus; it does not promise bit-for-bit timing reproduction.

### H-C6-10 — Official FHIR regression still has bounded scope

**Attack.** Passing the C6 FHIR regression proves FHIR or BALP conformance generally.

**Finding.** False. The hosted run re-executed the declared SUSHI, IG Publisher and HL7 FHIR Validator pathway for four positive units and two intended negative units. Thirty-three adjudicated publisher warnings remain. No HL7/IHE certification, universal profile conformance or clinical interoperability claim follows.

### H-C6-11 — Release checks are not independent verification

**Attack.** The candidate verifies itself with its own scripts and therefore proves independent correctness.

**Finding.** Valid criticism. C6 executes the candidate in an independently provisioned hosted environment and a clean extraction, but the core implementation and most verifiers are from the same project. No independently implemented cross-language verifier is supplied.

**Claim ceiling.** Independent environment execution, not independent implementation verification.

### H-C6-12 — The local A2 model remains non-persistent

**Attack.** The release archive and clean run convert the A2 model into a deployable transparency service.

**Finding.** False. The A2 path remains a project-specific local model. Durable custody, transactional persistence, crash recovery, concurrency, witnessing, gossip and public non-equivocation remain absent.

### H-C6-13 — Cost and complexity are not resolved

**Attack.** C5 timing and C6 component inventory prove that the approach reduces auditing cost and complexity.

**Finding.** False. C5 measures local processing and representation increments; C6 identifies additional components. Neither measures implementation labour, licensing, infrastructure, operations, incident handling, governance or dispute-resolution cost. Both beneficial and adverse organisational effects remain plausible.

### H-C6-14 — An identified software archive cannot be given to blinded reviewers without care

**Attack.** The public candidate is safe to attach directly to the anonymous review package.

**Finding.** False. The GitHub/Zenodo distribution is intentionally identified and includes author, ORCID and repository metadata. Anonymous manuscript and review artefacts must be constructed separately in C8. The candidate can support the identified editorial package or a properly anonymised review route; it must not be confused with the anonymous manuscript.

### H-C6-15 — A green run cannot repair an obsolete manuscript

**Attack.** The release candidate itself resolves the reviewer reports.

**Finding.** False. The submitted manuscript still states that IG Publisher and the HL7 FHIR Validator were not executed and reports older local timing results. C7 must reconstruct the article, and C8 must map each reviewer comment to the revised text and exact evidence.

## Adversarial conclusion

C6 establishes a strong release-engineering result: the exact candidate was built deterministically, audited, extracted and executed successfully in the declared hosted environment. It does not establish production readiness, hospital deployability, organisational cost reduction, privacy, legal compliance, universal standards conformance, independent implementation verification or publication status.

The defensible C6 claim is:

> The exact v2.2.0-rc.1 software candidate passed the declared hosted branch and fresh-extraction release contracts, and its curated 360-file public archive was reproduced byte-for-byte with matching internal and external integrity catalogues. The result is environment- and version-bounded and does not constitute a public release or deployment validation.
