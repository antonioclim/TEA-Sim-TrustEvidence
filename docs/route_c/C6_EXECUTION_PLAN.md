# Phase C6 execution plan

## Objective

Construct and audit the integrated `v2.2.0-rc.1` candidate without publishing it, merging it to `main` or inventing a Zenodo DOI.

## Frozen candidate identity

```text
target final version:        2.2.0
PEP 440 candidate version:   2.2.0rc1
display candidate:           2.2.0-rc.1
candidate tag label:         v2.2.0-rc.1
public DOI at C6:            unassigned
publication authorised:      no
```

The personal-monitoring envelope remains version `2.1.0`; the new HIE envelope is a separate `1.0.0` profile. C6 must not relabel old objects.

## Work packages

1. **Identity and metadata** — align `pyproject.toml`, package fallback version, README, CFF, Zenodo draft, release metadata, versioning and release notes.
2. **Compatibility** — record additive interfaces and schema-versus-software version boundaries.
3. **Deployability** — inventory implemented components, integration points, omitted operational controls and cost/complexity non-claims.
4. **CI simplification** — remove one-time C3-C5 materialisation jobs and write permissions; retain read-only regression jobs.
5. **Supply-chain control** — pin every external GitHub Action to an observed 40-character commit SHA and enforce the rule in tests.
6. **Distribution boundary** — exclude submission-specific `docs/route_c/` material and temporary machinery from the public ZIP while preserving it in the branch.
7. **Archive construction** — build one deterministic candidate ZIP with archive-specific manifests and outer checksum.
8. **Hostile archive audit** — reject path traversal, duplicate members, unsafe roots, venue residue, manuscript files and common credential patterns.
9. **Fresh extraction** — install the locked environment from the extracted ZIP and execute the complete `make release-check` contract.
10. **Gate synchronisation** — regenerate repository manifests, require a zero-byte integrity patch and record final workflow/artifact digests.

## Gate

C6 passes only if:

- all candidate metadata agree and explicitly state that the DOI/public release are absent;
- no established v2.1.0 envelope is silently relabelled;
- the public candidate file set excludes Route C submission governance;
- all external Actions are immutable-SHA pinned;
- candidate ZIP construction is deterministic;
- outer and internal checksums and manifests agree;
- distribution secret/residue audit passes;
- the complete release contract passes both before and after extraction;
- C3, C4 and C5 regressions pass on the final tree;
- no generated repository drift remains;
- `main`, GitHub releases and Zenodo remain unchanged.
