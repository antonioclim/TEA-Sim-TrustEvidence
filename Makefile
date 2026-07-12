PYTHON ?= python
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: compile test property bounded results-manifest result-contracts metadata integrity quick analyse figures tables compare clean final-check release-check

compile:
	@tmp=$$(mktemp -d); PYTHONPYCACHEPREFIX=$$tmp $(PYTHON) -m compileall -q src tests property_tests experiments scripts bounded_model; rm -rf $$tmp

test:
	@tmp=$$(mktemp -d); PYTHONDONTWRITEBYTECODE=1 HYPOTHESIS_STORAGE_DIRECTORY=$$tmp $(PYTHON) -m pytest tests -q -p no:cacheprovider; status=$$?; rm -rf $$tmp; exit $$status

property:
	@tmp=$$(mktemp -d); PYTHONDONTWRITEBYTECODE=1 HYPOTHESIS_STORAGE_DIRECTORY=$$tmp $(PYTHON) -m pytest property_tests -q -p no:cacheprovider; status=$$?; rm -rf $$tmp; exit $$status

bounded:
	@tmp=$$(mktemp -d); PYTHONDONTWRITEBYTECODE=1 $(PYTHON) bounded_model/bounded_model_check.py --output-dir $$tmp; status=$$?; rm -rf $$tmp; exit $$status

results-manifest:
	$(PYTHON) scripts/make_reproducibility_manifest.py --check

result-contracts:
	$(PYTHON) scripts/validate_result_contracts.py

metadata:
	$(PYTHON) scripts/check_public_metadata.py
	$(PYTHON) scripts/repository_check.py

integrity:
	$(PYTHON) scripts/verify_sha256sums.py SHA256SUMS.txt
	$(PYTHON) scripts/verify_file_manifest.py FILE_MANIFEST.tsv

quick:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) experiments/run_cmpb_curation_pipeline.py --quick

analyse:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) experiments/analyse_cmpb_results.py

figures:
	$(PYTHON) figures/scripts/generate_cmpb_figures.py
	$(PYTHON) figures/scripts/make_contact_sheet.py

tables:
	$(PYTHON) tables/scripts/generate_manuscript_tables.py

compare:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/compare_reference_outputs.py

clean:
	$(PYTHON) scripts/clean_release.py --runtime-only --include-local-results

final-check:
	$(PYTHON) scripts/clean_release.py --runtime-only --include-local-results
	$(PYTHON) scripts/make_reproducibility_manifest.py --check
	$(PYTHON) scripts/validate_result_contracts.py
	$(PYTHON) scripts/check_public_metadata.py
	$(PYTHON) scripts/repository_check.py
	$(PYTHON) scripts/verify_sha256sums.py SHA256SUMS.txt
	$(PYTHON) scripts/verify_file_manifest.py FILE_MANIFEST.tsv

release-check: clean compile test property bounded results-manifest result-contracts metadata integrity quick analyse figures tables compare final-check
	@echo "RELEASE-CHECK: PASS"
