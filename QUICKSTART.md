# Quick start

## Supported reviewer route

Use Python 3.13 in a fresh virtual environment. Core execution requires no Docker, Java, Node, database or network service after dependencies have been installed.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test,figures]'
```

Before integrity checks, remove installation/build residue generated in the source tree:

```bash
python scripts/clean_release.py --runtime-only
```

Run the complete local gate:

```bash
make release-check
```

The gate compiles the source, runs unit and property tests, executes the bounded model, verifies repository identity and release metadata, runs the quick integrated pipeline, regenerates figures, compares deterministic outputs and rechecks the clean tree.

## Individual commands

```bash
export PYTHONDONTWRITEBYTECODE=1
export HYPOTHESIS_STORAGE_DIRECTORY="$(mktemp -d)"
python -m compileall src tests property_tests experiments scripts bounded_model
python -m pytest tests -q -p no:cacheprovider
python -m pytest property_tests -q -p no:cacheprovider
python bounded_model/bounded_model_check.py
python scripts/make_reproducibility_manifest.py --check
python scripts/validate_result_contracts.py
python scripts/repository_check.py
python scripts/verify_sha256sums.py SHA256SUMS.txt
python scripts/verify_file_manifest.py FILE_MANIFEST.tsv
python experiments/run_cmpb_curation_pipeline.py --quick
python experiments/analyse_cmpb_results.py
python figures/scripts/generate_cmpb_figures.py
python scripts/compare_reference_outputs.py
python scripts/repository_check.py
```

Set `PYTHONPYCACHEPREFIX` to a temporary directory before `compileall` when a pristine repository tree must be retained. The Makefile does this automatically.
