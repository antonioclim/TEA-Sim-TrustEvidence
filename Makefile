SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c
PYTHON ?= python
PYTHONPATH := src
COMPOSE ?= docker compose
COMPOSE_FILE ?= docker-compose.full.yml
COMPOSE_PROFILES ?= baselines,fabric,harness
WORKLOAD ?= data/workloads/W_SMOKE_AUDITEVENT.jsonl
REPETITIONS ?= 10
TE_BENCH_PROFILE ?= local
TE_REQUIRE_LIVE ?= 0
.PHONY: compile test figures-jcis validate-results-schema evaluation-smoke quick validate-lji2 validate-fsh-static validate-ig-static validate-legal repository-check clean-runtime checksums verify-checksums ci-local reviewer-check release-check smoke-dry dry-run up down smoke external-preflight experiments validate-results analyse-results reproduce-v1 sushi-build ig-publisher
compile:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall -q src tests experiments scripts
test:
	PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests -q
validate-protocol:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) experiments/validate_protocol.py | tee validation/PROTOCOL_VALIDATION_REPORT.txt
validate-lji2:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_lji2.py | tee validation/LJI2_VALIDATION_REPORT.txt
validate-fsh-static:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_fsh_static.py | tee validation/FSH_STATIC_CHECK.txt
validate-ig-static:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_ig_static.py | tee validation/IG_STATIC_CHECK.txt
validate-legal:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_legal_traceability.py | tee validation/LEGAL_TRACEABILITY_CHECK.txt
repository-check:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/repository_check.py | tee validation/REPOSITORY_CHECK.txt
clean-runtime:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/clean_release.py --root .
checksums: clean-runtime
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/make_output_manifest.py --output OUTPUT_MANIFEST.md
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/make_sha256sums.py --output SHA256SUMS.txt
verify-checksums:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/verify_sha256sums.py --root . --manifest SHA256SUMS.txt | tee validation/SHA256_VERIFY_REPORT.txt
ci-local: compile test validate-protocol validate-lji2 validate-fsh-static validate-ig-static validate-legal repository-check
	@echo "Local checks completed."
reviewer-check: ci-local
release-check: ci-local experiments validate-results analyse-results checksums verify-checksums
	@echo "Release check completed."
smoke-dry:
	mkdir -p validation results
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m trustevidence.harness.smoke --dry-run --workload $(WORKLOAD) --compose $(COMPOSE_FILE) | tee validation/DRY_SMOKE_REPORT.json
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m trustevidence.harness.replay_workload --mode local --workload $(WORKLOAD) --results results/local_smoke_receipts.jsonl | tee validation/LOCAL_REPLAY_REPORT.txt
dry-run: smoke-dry
up:
	COMPOSE_PROFILES=$(COMPOSE_PROFILES) $(COMPOSE) -f $(COMPOSE_FILE) up -d --build
down:
	COMPOSE_PROFILES=$(COMPOSE_PROFILES) $(COMPOSE) -f $(COMPOSE_FILE) down -v || true
smoke:
	mkdir -p validation results
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m trustevidence.harness.smoke --external --workload $(WORKLOAD) | tee validation/EXTERNAL_SMOKE_REPORT.txt
external-preflight:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/external_preflight.py | tee validation/EXTERNAL_PREFLIGHT.txt
experiments:
	mkdir -p results validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) experiments/run_experiments.py --profile $(TE_BENCH_PROFILE) --repetitions $(REPETITIONS) --results-dir results $(if $(filter 1,$(TE_REQUIRE_LIVE)),--require-live,)
validate-results:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) experiments/validate_results.py --results-dir results | tee validation/RESULTS_SCHEMA_VALIDATION_REPORT.txt
analyse-results:
	mkdir -p validation results
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) experiments/analyse_results.py --results-dir results --out results/statistical_summary.csv | tee validation/ANALYSIS_REPORT.txt
reproduce-v1:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m teasim reproduce-v1 --output-dir outputs/v1_5_1_reproduction
sushi-build:
	cd ig && npx --yes fsh-sushi .
ig-publisher:
	@if [ -z "$(PUBLISHER_JAR)" ]; then echo "Set PUBLISHER_JAR=/path/to/publisher.jar"; exit 2; fi
	java -jar $(PUBLISHER_JAR) -ig ig/ig.ini


validate-results-schema:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_results_schema.py --results-dir results | tee validation/RESULTS_SCHEMA_VALIDATION_REPORT.txt

evaluation-smoke:
	mkdir -p validation
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/run_evaluation_smoke.py | tee validation/EVALUATION_SMOKE.txt

quick: compile test
	mkdir -p validation results/quick
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) experiments/run_experiments.py --quick
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) experiments/validate_results.py --results-dir results/quick | tee validation/RESULTS_SCHEMA_VALIDATION_REPORT.txt
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) experiments/analyse_results.py --results-dir results/quick --out results/quick/statistical_summary.csv | tee validation/ANALYSIS_REPORT.txt
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/run_evaluation_smoke.py | tee validation/EVALUATION_SMOKE.txt

figures-jcis:
	mkdir -p figures/outputs
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) figures/scripts/generate_jcis_figures.py
