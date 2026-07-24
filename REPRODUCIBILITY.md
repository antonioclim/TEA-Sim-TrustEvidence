# Reproducibility contract

## Reproducibility classes

| Class | Included evidence | Comparison rule |
|---|---|---|
| Byte-deterministic | schema decisions, canonicalisation vectors, mutation decisions, C4 security corpus, figure sources and deterministic files | SHA-256 equality |
| Semantic-deterministic | quick workload decisions and event identities | field-by-field equality after excluding elapsed times and host metadata |
| Measurement-variable | legacy workload timings and C5 paired local timings | same frozen protocol, row counts, decisions, source digests and recomputable summaries; milliseconds need not match |
| Frozen-reference-derived | figures and tables generated from retained reviewed reference sources | deterministic regeneration from retained sources |

## Reference outputs

`results_expected/cmpb_reference/` contains two provenance strata:

1. the preserved v2.1.0 personal-monitoring reference corpus; and
2. Route C C4 security and C5 paired-overhead evidence added on the controlled revision branch.

The legacy deterministic corpus remains byte-bound to its declared schema/profile version. C5 measurement-variable rows are retained from the successful confirmatory workflow and are checked through contracts, counts, paired derivations and source-file digests rather than being overwritten to make a release-candidate version string appear in the measurements.

Experiments default to `results_local/` and do not overwrite retained reference files. Top-level retained CSVs are validated against `schemas/results/*.schema.json`; `reproducibility_manifest.csv` records the evidence class, generator/source and hash for each retained result family.

## Repository and public-archive integrity

The repository `FILE_MANIFEST.tsv` and `SHA256SUMS.txt` cover the distributed branch tree, excluding only declared runtime/build directories and generated FHIR output caches. The public release-candidate ZIP is a curated subset: submission-specific `docs/route_c/` governance material is omitted, and archive-specific manifest and checksum files are generated inside the ZIP.

The C6 archive gate verifies:

- deterministic ZIP construction;
- one safe root directory;
- no duplicate, absolute or parent-traversal paths;
- absence of submission/reviewer residue and common credential patterns;
- archive-specific file-manifest and checksum parity;
- fresh extraction and a complete `make release-check` execution.

## Randomness and keys

Hypothesis uses deterministic settings with no example database. Synthetic workload selection is deterministic. Ed25519 private keys and payload nonces in tests are deterministic fixtures and must never be used operationally. The release audit treats the fixture directory as an explicit allowlisted test boundary, not an operational secret store.

## Timing boundary

Wall-clock values use `time.perf_counter_ns()`. The C5 primary inferential unit is the independent paired process block, not each operation. Reported local increments are host-, workload- and implementation-bounded. They are not comparative hospital benchmarks, network/service-level estimates or production-capacity claims.
