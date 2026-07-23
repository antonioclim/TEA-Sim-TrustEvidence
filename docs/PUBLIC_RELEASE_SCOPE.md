# Public release distribution scope

## Distribution identity

The GitHub/Zenodo software archive is an **identified public software distribution**, not an anonymous manuscript file. Author and repository metadata are therefore retained. Anonymous and identified manuscript packages are constructed separately for journal submission.

## Included

The candidate archive includes source code, schemas, synthetic examples, retained scientific evidence, result contracts, standards-facing material, public method documentation, environment disclosure, tests, figures, tables and release/reproducibility utilities.

## Excluded

The deterministic public archive excludes:

- `docs/route_c/`, which contains submission-specific reviewer traceability, internal gate reports and venue workflow governance;
- temporary C6 source-snapshot workflow machinery;
- Git metadata, virtual environments, caches, build directories, local outputs and generated FHIR output caches;
- manuscript files, email files, submission PDFs and reviewer-response documents.

Exclusion from the public ZIP does not delete the internal branch records. The public archive receives its own `FILE_MANIFEST.tsv` and `SHA256SUMS.txt`, generated from the exact curated file set.

## Fixture-secret boundary

`data_examples/hie_disclosure/private_test_material/` contains deterministic TEST-ONLY material required to reproduce the source-payload commitment. It is not an operational secret and must not be reused. The distribution audit allowlists only the declared fixture files and still scans the remaining public content for common credential patterns.

## Publication boundary

C6 may build and validate a release-candidate archive. It does not authorise a public tag, GitHub release, Zenodo publication or DOI claim. Those actions belong to C9 after manuscript and submission-package gates.
