# Independent reproduction kit

## Purpose

This kit lets a non-author reproduce the declared software checks and return a structured report without changing the retained evidence.

## Preconditions

- use the canonical v2.2.0 release or identify the exact later commit;
- use Python 3.13 and the locked Linux requirements where possible;
- work on synthetic/public fixtures only;
- do not place credentials, tokens, private keys or patient data in the report.

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check --no-input setuptools==82.0.1 wheel==0.46.3
python -m pip install --disable-pip-version-check --no-input -r environment/requirements-lock-py313-linux.txt
python -m pip install --disable-pip-version-check --no-input --no-build-isolation --no-deps -e .
```

## Core run

```bash
python scripts/run_independent_reproduction.py --mode core
```

The core run checks public metadata, repository identity, retained result contracts, integrity catalogues, the HIE case, retained FHIR evidence, the security corpus and the paired-overhead corpus.

## Full run

```bash
python scripts/run_independent_reproduction.py --mode full
```

The full run adds unit/regression tests, property tests, finite bounded checks, the quick curation pipeline and deterministic output comparison.

## Returned material

Return:

1. generated `independent_reproduction_report.json`;
2. generated `independent_reproduction_report.md`;
3. completed `REPORT_TEMPLATE.md`;
4. a concise list of any manual deviations.

Do not edit failed outputs to make the run appear successful. Retain packaging, dependency and test failures as evidence.

## Interpretation

A passing report establishes only that the declared checks passed in the reported environment for the identified software state. It does not establish clinical validity, production readiness, legal compliance, complete event capture, backend honesty or global non-equivocation.
