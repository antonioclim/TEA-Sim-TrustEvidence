# Result provenance

| Output | Provenance | Status |
|---|---|---|
| `schema_validation_summary.csv` | executable schema, semantic and minimisation experiment | regenerated in the integrated package |
| `canonicalisation_determinism.csv` | TE-JCS-1 experiment and selected RFC 8785-derived vectors | regenerated in the integrated package |
| `mutation_test_results.csv` | receipt, mutation and consistency regression | regenerated in the integrated package |
| `property_test_summary.csv` | deterministic Hypothesis execution summary | regenerated in the integrated package |
| `bounded_model_summary.csv` | finite bounded executable checker | regenerated in the integrated package |
| workload outputs | integrated 12 × {128, 512, 2,048}-leaf synthetic passage | executed and retained with raw rows and a run identifier |
| figure and table outputs | deterministic generators reading retained CSV/JSON sources | regenerated and hash-compared |

Only the outputs distributed in this archive and reproducible through its documented commands are treated as release-candidate evidence. Documentary values without executable or raw support are excluded from the retained reference set.
