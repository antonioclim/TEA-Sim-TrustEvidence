# Output manifest

Reference outputs are retained under `results_expected/cmpb_reference/`. Ordinary reviewer executions write to ignored local directories and do not overwrite the retained corpus.

| Evidence family | Principal output | Generator or checker | Reproducibility class |
|---|---|---|---|
| Legacy schema validation | `schema_validation_summary.csv` | `experiments/run_schema_validation.py` | byte-deterministic |
| Legacy field deletion and competency questions | `field_deletion_results.csv`; `competency_question_results.csv` | `experiments/run_schema_validation.py` | byte-deterministic |
| Legacy canonicalisation | `canonicalisation_determinism.csv` | `experiments/run_canonicalisation_tests.py` | byte-deterministic |
| Legacy mutation and consistency | `mutation_test_results.csv` | `experiments/run_mutation_tests.py` | byte-deterministic |
| Legacy property tests | `property_test_summary.csv` | `experiments/run_property_checks.py` | byte-deterministic |
| Finite bounded checks | `bounded_model_summary.csv/json`; observations | `bounded_model/bounded_model_check.py` | byte-deterministic |
| Legacy workload passage | `workload_passage_summary.csv`; raw timings/events | `experiments/run_workload_passage.py` | measurement-variable plus deterministic identities |
| C3 HIE case | `data_examples/hie_disclosure/`; `standards/fhir_ig/validation/` | HIE builder, semantic checks and official toolchain | byte-deterministic retained case/tool evidence |
| C4 security programme | `c4_hie_security/*` | `experiments/run_hie_security_mutations.py` | byte-deterministic registered decisions |
| C5 paired experiment | `c5_hie_overhead/*` | `experiments/run_hie_incremental_overhead.py` | measurement-variable raw timings; deterministic contracts and derivations |
| Result contracts | `schemas/results/*.schema.json` | `scripts/validate_result_contracts.py` | source-controlled Draft 2020-12 contracts |
| Result provenance register | `reproducibility_manifest.csv` | `scripts/make_reproducibility_manifest.py` | byte-deterministic |
| Figures and tables | `figures/outputs/`; `tables/outputs/` | programmatic generators | frozen-reference-derived |
| Repository integrity | top-level `FILE_MANIFEST.tsv`; `SHA256SUMS.txt` | `scripts/rebuild_integrity_files.py` | exact branch tree |
| Candidate archive integrity | catalogues inside the deterministic ZIP plus outer `.sha256` | release builder and archive checker | exact curated public distribution |

## Interpretation

Byte-deterministic outputs are compared by SHA-256. Measurement-variable timings are checked through the frozen protocol, independent-unit counts, decisions, source digests, paired derivations and recomputable summaries rather than millisecond equality. The legacy v2.1.0 corpus retains its declared schema/profile identity; C4 and C5 are separately identified Route C evidence strata.
