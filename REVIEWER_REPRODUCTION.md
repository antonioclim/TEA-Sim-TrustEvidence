# Reviewer reproduction

## Choose the software object

For reproduction of the citable v2.2.0 software object, use the manually uploaded canonical release asset and verify SHA-256 `e9b2b6e3829f4158e561812cbb146a5b212877d6c39e740467777cc9944b7a3c`. The `v2.2.0` tag and asset are immutable.

The current `main` branch contains later metadata, support and independent-reproduction documentation. Record its commit SHA if it is used. It is not the archived v2.2.0 byte stream and its archive builder deliberately refuses a same-version rebuild.

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

## Immutable release-asset route

Download `TEA-Sim-TrustEvidence-v2.2.0.zip` and `TEA-Sim-TrustEvidence-v2.2.0.sha256` from the v2.2.0 GitHub Release, then run:

```bash
python scripts/check_immutable_release_asset.py \
  --archive /path/to/TEA-Sim-TrustEvidence-v2.2.0.zip \
  --checksum /path/to/TEA-Sim-TrustEvidence-v2.2.0.sha256
```

Run `make release-check` from the extracted canonical root after installing the same lock file. Successful execution supports version- and environment-bounded reproducibility of the reference implementation. It does not establish clinical utility, production readiness, hospital deployability, legal compliance, organisational effectiveness, event completeness, backend honesty or global non-equivocation.
