# Figure provenance

All figures are generated programmatically from CSV or JSON sources retained in this archive. No generative-image system, manual drawing application or external rendering service is used.

## Figure 1 - Schema-first curation boundary

- Sources: `figures/sources/figure1_nodes.csv` and `figures/sources/figure1_edges.csv`.
- Scientific basis: the declared curation sequence and the implemented validation, canonicalisation, signing and local-receipt stages.
- Transformation: deterministic box-and-arrow rendering in `figures/scripts/generate_cmpb_figures.py`.
- Permitted interpretation: monitoring payloads remain in a governed payload path while selected accountability metadata enter the evidence pathway.
- Boundary: the figure does not demonstrate clinical utility, production deployment or legal compliance.

## Figure 2 - Evidence envelope and payload minimisation

- Source: `figures/sources/figure2_components.csv`.
- Evidence inputs: the three normative schemas under `src/trustevidence/schemas/` and the recursive minimisation checks in `src/trustevidence/validators.py`.
- Transformation: deterministic nested-envelope rendering with retained, excluded and withheld content lists.
- Permitted interpretation: the public envelope retains monitoring-accountability metadata and cryptographic bindings while excluding raw samples, physiological values, direct identifiers and the commitment nonce.
- Boundary: a payload commitment is not encryption or anonymisation and does not establish source truth.

## Figure 3 - Execution and verification pipeline

- Sources: `figures/sources/figure3_stages.csv` and `figures/sources/figure3_edges.csv`.
- Evidence inputs: the executed schema, canonicalisation, signature, inclusion, mutation and consistency pathways in `src/`, `experiments/`, `tests/` and `property_tests/`.
- Transformation: deterministic two-row pipeline rendering.
- Permitted interpretation: each stage has a separate failure boundary; later cryptographic verification does not substitute for schema, semantic or minimisation controls.
- Boundary: the pipeline is not a production service architecture or a global transparency-witness network.

## Figure 4 - Bounded local passage and receipt sizes

- Source: `figures/sources/figure4_passage_results.csv`.
- Evidence inputs: `results_expected/cmpb_reference/workload_passage_summary.csv`, `receipt_size_summary.csv`, `raw_runs/timing_samples.csv` and `run_metadata.json`.
- Transformation: deterministic plotting of median canonical receipt/proof sizes with executed aggregate control counts. Authentication-path depth is taken from the retained receipt-size summary.
- Evidence status: the integrated run executed 32,256 synthetic events, 1,152 sampled receipt checks and 36 re-signed proof-path mutations over 12 repetitions at each of 128, 512 and 2,048 leaves.
- Permitted interpretation: the stated local implementation completed the bounded synthetic passage and receipt/proof sizes increased over the tested tree sizes.
- Boundary: timing values are single-host descriptive measurements; no comparative, production, clinical, population or extrapolated scalability conclusion is supported.

## Figure 5 - Failure modes addressed and not addressed

- Source: `figures/sources/figure5_failure_modes.csv`.
- Evidence inputs: retained schema-validation, field-deletion, canonicalisation, mutation, property and bounded-check result files under `results_expected/cmpb_reference/`.
- Transformation: deterministic status-position plot distinguishing executed controls, bounded/partial evidence and out-of-scope failures.
- Permitted interpretation: the listed local controls behaved as reported within their finite assumptions.
- Boundary: executed controls do not constitute exhaustive security, formal proof, global non-equivocation, operational key assurance or clinical validation.

## Output specifications

Each figure is emitted as vector PDF, editable SVG and 600 dpi PNG. PDF dates and SVG identifiers are fixed to support byte-level regeneration. Figure dimensions and rendered-layout outcomes are recorded in `figures/outputs/FIGURE_LAYOUT_QA.csv`.

## Normative standards basis

| Method element | Verified reference |
|---|---|
| JSON canonicalisation | Rundgren, A., Jordan, B., & Erdtman, S. (2020). *JSON Canonicalization Scheme (JCS)* (RFC 8785). RFC Editor. https://doi.org/10.17487/RFC8785 |
| Merkle inclusion and consistency algorithms | Laurie, B., Messeri, E., & Stradling, R. (2021). *Certificate Transparency Version 2.0* (RFC 9162). RFC Editor. https://doi.org/10.17487/RFC9162 |
| Ed25519 primitive | Josefsson, S., & Liusvaara, I. (2017). *Edwards-Curve Digital Signature Algorithm (EdDSA)* (RFC 8032). RFC Editor. https://doi.org/10.17487/RFC8032 |
