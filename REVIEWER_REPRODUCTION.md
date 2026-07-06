# Reviewer reproduction guide

## 1. Static source and test checks

```bash
python -m pip install -e '.[test]'
python -m compileall src tests experiments scripts
python -m pytest tests -q
python scripts/repository_check.py
```

## 2. Local experiment smoke run

```bash
python experiments/run_experiments.py --quick
python scripts/validate_results_schema.py --results-dir results/quick
python experiments/analyse_results.py --results-dir results/quick --out results/quick/statistical_summary.csv
```

The generated `results/quick/` directory is runtime output and is not part of the static checksum manifest.

## 3. evidence-supported evidence smoke checks

```bash
python scripts/run_evaluation_workstreams_smoke.py
```

This command re-runs local JSON integrity lint for the FHIR/BALP examples, the executable bounded model and the property-test subset. It does not run IG Publisher, the HL7 FHIR Validator, PostgreSQL, Rekor, Trillian, Fabric or expert-panel analysis.

## 4. Manifest verification

```bash
python scripts/verify_sha256sums.py SHA256SUMS.txt
sha256sum -c SHA256SUMS.txt
```

Both commands verify the same standard two-column checksum manifest.
