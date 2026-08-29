# Post-release documentation policy

## Canonical object

The canonical v2.2.0 software object is the manually uploaded archive associated with:

- Git tag `v2.2.0`;
- exact-version DOI `10.5281/zenodo.21533962`;
- SHA-256 `e9b2b6e3829f4158e561812cbb146a5b212877d6c39e740467777cc9944b7a3c`.

The tag and release asset are not rewritten.

## Permitted changes on `main`

Later commits may:

- correct public metadata;
- add related-publication identifiers;
- improve support, contribution or security documentation;
- add non-destructive reproduction helpers;
- clarify reuse and claim boundaries.

These commits do not become part of v2.2.0 merely because they are on `main`.

## Versioning trigger

A new software version is required when a change modifies:

- executable behaviour;
- schemas or validation semantics;
- fixtures or retained scientific evidence;
- dependencies material to execution;
- result contracts;
- the canonical distribution.

A metadata-only correction to the published Zenodo record does not require a new software version or DOI.

## Citation rule

For scientific reproduction, cite and execute the exact tagged release. For a later `main` commit, record its commit SHA separately and do not describe it as the archived v2.2.0 byte stream.

## Build guard

The current `main` branch is explicitly marked `post-release-documentation` in `RELEASE_METADATA.json`. Its `release_asset_build_authorised` field is `false`. `scripts/build_release_archives.py` therefore refuses to create another archive named `TEA-Sim-TrustEvidence-v2.2.0.zip`.

This guard prevents a later documentation snapshot from producing different bytes under an already published version, filename and DOI. The current CI downloads and verifies the immutable public asset instead of rebuilding it from post-release `main`.

## Future distribution

Any source snapshot that includes post-release files from `main` and is intended for archival distribution requires a new software version, tag, canonical asset and exact-version DOI. Documentation-only commits may remain on `main` without being presented as v2.2.0 release bytes.
