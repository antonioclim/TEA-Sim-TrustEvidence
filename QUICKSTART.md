# Quick start

## Supported local route

Use Python 3.13 in a fresh virtual environment. The complete local release contract requires no database, Docker daemon or network service after the locked Python dependencies have been installed. The official FHIR regression is a separate hosted route because it additionally requires Java, Node, Ruby, SUSHI, Jekyll and the retained validator toolchain.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check --no-input setuptools==82.0.1 wheel==0.46.3
python -m pip install --disable-pip-version-check --no-input -r environment/requirements-lock-py313-linux.txt
python -m pip install --disable-pip-version-check --no-input --no-build-isolation --no-deps -e .
make release-check
```

The contract compiles the source, runs unit and property tests, executes the finite bounded model, validates retained result contracts and provenance, checks metadata and immutable Action pins, audits the public distribution, verifies repository integrity, checks the C3/C4/C5 retained evidence, regenerates the legacy quick outputs, figures and tables, and rejects generated drift.

## Principal individual checks

```bash
python scripts/check_public_metadata.py
python scripts/check_action_pins.py
python scripts/audit_public_distribution.py
python scripts/verify_sha256sums.py SHA256SUMS.txt
python scripts/verify_file_manifest.py FILE_MANIFEST.tsv
python experiments/run_hie_hero_case.py --check
python scripts/check_c3_retained_evidence.py
python experiments/run_hie_security_mutations.py --check
python experiments/run_hie_incremental_overhead.py --check
python scripts/validate_result_contracts.py
python scripts/make_reproducibility_manifest.py --check
```

## Candidate archive

```bash
mkdir -p dist
python scripts/build_release_archives.py --output-dir dist
python scripts/check_release_archive.py \
  --archive dist/TEA-Sim-TrustEvidence-v2.2.0.zip \
  --checksum dist/TEA-Sim-TrustEvidence-v2.2.0.sha256 \
  --extract-dir dist/fresh-extraction
```

The hosted C6 job builds the archive twice, requires byte equality, extracts it into a new directory, installs the locked environment there and executes the complete `make release-check` contract again.
