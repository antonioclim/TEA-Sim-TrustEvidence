# Output manifest

Reference outputs are retained under `results_expected/cmpb_reference/`. Reviewer executions write to ignored local directories.

| Evidence | Output | Generator | Reproducibility class |
|---|---|---|---|
| Schema validation | `results_expected/cmpb_reference/schema_validation_summary.csv` | `experiments/run_schema_validation.py` | byte-deterministic |
| Field deletion | `results_expected/cmpb_reference/field_deletion_results.csv` | `experiments/run_schema_validation.py` | byte-deterministic |
| Competency questions | `results_expected/cmpb_reference/competency_question_results.csv` | `experiments/run_schema_validation.py` | byte-deterministic |
| Canonicalisation | `results_expected/cmpb_reference/canonicalisation_determinism.csv` | `experiments/run_canonicalisation_tests.py` | byte-deterministic |
| Mutation and consistency | `results_expected/cmpb_reference/mutation_test_results.csv` | `experiments/run_mutation_tests.py` | byte-deterministic |
| Property tests | `results_expected/cmpb_reference/property_test_summary.csv` | `experiments/run_property_checks.py` | byte-deterministic |
| Bounded checks | `results_expected/cmpb_reference/bounded_model_summary.csv` | `bounded_model/bounded_model_check.py` | byte-deterministic |
| Workload summary | `results_expected/cmpb_reference/workload_passage_summary.csv` | `experiments/run_workload_passage.py` | measurement-variable |
| Receipt sizes | `results_expected/cmpb_reference/receipt_size_summary.csv` | `experiments/run_workload_passage.py` | byte-deterministic sizes; measurement run context |
| Raw timing rows | `results_expected/cmpb_reference/raw_runs/timing_samples.csv` | `experiments/run_workload_passage.py` | measurement-variable |
| Synthetic workload index | `results_expected/cmpb_reference/raw_runs/workload_events.jsonl` | `experiments/run_workload_passage.py` | byte-deterministic event identity |
| Result contracts | `schemas/results/*.schema.json` | `scripts/validate_result_contracts.py` | source-controlled Draft 2020-12 contracts |
| Result reproducibility manifest | `results_expected/cmpb_reference/reproducibility_manifest.csv` | `scripts/make_reproducibility_manifest.py` | byte-deterministic provenance register |
| Figures | `figures/outputs/Figure_1.* through Figure_5.*` | `figures/scripts/generate_cmpb_figures.py` | frozen-reference-derived |

## Interpretation

Byte-deterministic outputs are compared by SHA-256. Timing values are host-dependent and are checked by protocol, row count, decisions and recomputation rather than millisecond equality. Figures are regenerated from retained source tables with fixed metadata.
