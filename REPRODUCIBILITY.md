# Reproducibility contract

## Reproducibility classes

| Class | Included evidence | Comparison rule |
|---|---|---|
| Byte-deterministic | schema decisions, canonicalisation vectors, mutation decisions, property summaries, figure sources and figure files | SHA-256 equality |
| Semantic-deterministic | quick workload decisions and event identities | field-by-field equality after excluding elapsed times and host metadata |
| Measurement-variable | append and verification timings | same protocol, row counts, decisions and recomputable summaries; milliseconds need not match |
| Frozen-reference-derived | manuscript figures and tables generated from the retained reviewed reference sources | deterministic regeneration from retained sources |

## Reference outputs

`results_expected/cmpb_reference/` contains the reviewed v2.1.0 reference outputs. Experiments default to `results_local/` and do not overwrite reference files. The workload timing rows describe one run on one host and must not be compared as a performance threshold. Top-level retained CSVs are validated against `schemas/results/*.schema.json`, and `reproducibility_manifest.csv` records the hash, evidence class and generator or source for every retained result file except itself.

## Integrity model

`FILE_MANIFEST.tsv` excludes itself and `SHA256SUMS.txt` to avoid circularity. It records path, size, SHA-256, media type, role, generator, source inputs and reproducibility class. `SHA256SUMS.txt` covers every distributed file except itself, including the manifest.

The verifiers check root identity, safe relative paths, duplicate rows, missing files, unexpected release files, sizes, hashes and prohibited residue. Runtime-only directories listed in `.gitignore` are ignored after execution but are forbidden in the ZIP at build time.

## Randomness and keys

Hypothesis uses deterministic settings with no example database. Synthetic workload selection is deterministic. Ed25519 private keys and payload nonces in tests are deterministic fixtures and must never be used operationally.

## Timing boundary

Wall-clock values are collected with `time.perf_counter_ns()`. The package reports medians and nearest-rank 95th percentiles. It makes no inferential, comparative, service-level or production-capacity claim.
