# Versioning and citation

## Current repository state

This tree is the unreleased TEA-Sim TrustEvidence candidate `2.2.0-rc.1`:

- target software release: `2.2.0`;
- PEP 440 package version: `2.2.0rc1`;
- candidate label: `v2.2.0-rc.1`;
- candidate archive root: `TEA-Sim-TrustEvidence-v2.2.0-rc.1`;
- candidate asset: `TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip`;
- candidate checksum file: `TEA-Sim-TrustEvidence-v2.2.0-rc.1.sha256`;
- controlled review location: <https://github.com/antonioclim/TEA-Sim-TrustEvidence/pull/1>;
- v2.2.0 exact-version DOI: **not assigned**;
- public v2.2.0 GitHub release: **not created**.

The previous published exact version is `v2.1.0`, DOI <https://doi.org/10.5281/zenodo.21318387>.

## Candidate citation

Before the final release, cite the candidate by exact version and commit, for example:

> Clim, A. (2026). *TEA-Sim v2.2.0-rc.1: Portable audit evidence for health information exchange* (Version 2.2.0-rc.1) [Computer software; unreleased release candidate]. GitHub repository, exact commit.

Do not cite the v2.1.0 DOI as if it identified v2.2.0. Do not invent a v2.2.0 DOI. C9 will replace this section with the final Zenodo DOI and final GitHub release URL after both records use the identical canonical archive byte stream.

## Schema versus software versions

The Python distribution version is not the wire/schema version. The personal-monitoring envelope remains `2.1.0`; the new HIE envelope is `1.0.0`. This preserves explicit compatibility boundaries and prevents historical objects from being relabelled merely because the software distribution has advanced.
