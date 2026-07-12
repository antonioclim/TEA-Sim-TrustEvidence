# Experiment drivers

- `run_schema_validation.py` executes positive, negative and required-field deletion checks.
- `run_canonicalisation_tests.py` executes TE-JCS-1 admission and selected RFC 8785-derived vectors.
- `run_mutation_tests.py` executes signed-core, receipt, proof, commitment and consistency controls.
- `run_workload_passage.py` executes the bounded synthetic passage and retains raw timing/event rows.
- `analyse_cmpb_results.py` recomputes workload summaries from raw rows.
- `run_cmpb_curation_pipeline.py` orchestrates the deterministic layers and quick/full workload route.

Reference outputs are read-only. Reviewer runs default to the ignored `results_local/` directory.
