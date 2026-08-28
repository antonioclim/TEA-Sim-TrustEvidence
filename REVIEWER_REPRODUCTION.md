# Reviewer reproduction

## Controlled report route

After installing the locked Python 3.13 environment, a reviewer or independent reproducer may run:

```bash
python scripts/run_independent_reproduction.py --mode core
```

The wrapper executes non-destructive metadata, integrity, HIE, security and overhead checks and records:

- software and package version;
- repository commit, where Git is available;
- host and Python information;
- each command and elapsed time;
- exit status;
- captured standard output and standard error;
- an overall pass/fail decision.

Reports are written under `results_local/independent_reproduction/`, which is excluded from the public distribution. The reproducer should complete `independent_reproduction/REPORT_TEMPLATE.md` and return the report without credentials, tokens, private keys or local clinical data.

Use `--mode full` to include unit/regression tests, property tests, finite bounded checks, the quick curation pipeline and reference-output comparison.

## One-command local route

After installing the locked Python 3.13 environment, run:

```bash
make release-check
```

Expected high-level outcomes include:

- all unit/regression and deterministic Hypothesis tests pass;
- the finite bounded state space completes without a recorded failure;
- retained result contracts and the result-level provenance manifest are current;
- the C3 synthetic HIE case, semantic/privacy checks and retained official-tool evidence pass their checkers;
- all 67 C4 registered decisions and limitation acceptances agree with the retained corpus;
- C5 retains five excluded pilot blocks, twenty confirmatory paired blocks, sixty process runs, 7,680 operation timings and the registered paired derivations;
- metadata, Action pins, distribution scope, manifests and checksums pass;
- deterministic legacy outputs, figures and tables regenerate without unexplained drift.

## Official FHIR route

The hosted workflow executes:

```bash
bash scripts/run_c3_fhir_validation.sh ephemeral
```

This route uses the recorded FHIR R4, local IG and applicable BALP packages. Its result applies only to the declared positive and intended-negative corpus; it is not HL7/IHE certification or universal FHIR/BALP conformance.

## C5 result boundary

The retained W1 experiment reports paired local reference-pipeline increments. The independent inferential unit is the paired process block, not each operation. The values are not production-EHR latency, network bytes, database storage, scalability or service-level results.

## Candidate archive route

Build and validate the deterministic release:

```bash
mkdir -p dist
python scripts/audit_public_distribution.py --report dist/public-distribution-audit.json
python scripts/build_release_archives.py --output-dir dist
python scripts/check_release_archive.py \
  --archive dist/TEA-Sim-TrustEvidence-v2.2.0.zip \
  --checksum dist/TEA-Sim-TrustEvidence-v2.2.0.sha256 \
  --extract-dir dist/fresh-extraction \
  --report dist/release-archive-audit.json
```

Run `make release-check` from the extracted canonical root after installing the same lock file. Successful execution supports version- and environment-bounded reproducibility of the reference implementation. It does not establish clinical utility, production readiness, hospital deployability, legal compliance, organisational effectiveness, event completeness, backend honesty or global non-equivocation.

## Release versus main

The canonical scientific software object is the immutable `v2.2.0` release asset archived under DOI `10.5281/zenodo.21533962`. Post-release documentation and metadata corrections on `main` do not alter that asset. An independent report must identify whether it reproduced the tagged release or a later commit on `main`.
