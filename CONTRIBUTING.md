# Contributing

Contributions are welcome when they preserve the project's bounded scientific identity, reproducibility and claim ceiling.

## Suitable contributions

- defect fixes with a minimal reproducer;
- additional positive and intended-negative fixtures;
- independent verifier implementations;
- documentation improvements;
- result-contract or validation improvements;
- new workflow profiles that do not copy unjustified clinical payload;
- reproducibility reports from a fresh environment.

## Scientific constraints

A contribution must not introduce or imply:

- clinical validation without approved evidence;
- production readiness;
- legal or regulatory compliance;
- universal FHIR/BALP conformance;
- complete event capture;
- backend honesty;
- global non-equivocation;
- patient data or restricted material in the public repository.

## Development route

1. Open an issue describing the defect or proposed extension.
2. Fork the repository and create a focused branch.
3. Install the locked Python 3.13 environment.
4. Add or update tests and machine-readable evidence.
5. Run:

```bash
make release-check
```

6. Rebuild the integrity catalogues only after the intended files are final:

```bash
python scripts/rebuild_integrity_files.py
```

7. Run `make release-check` again and submit a pull request.

## Pull-request evidence

The pull request should state:

- the exact problem;
- the scientific or software boundary affected;
- files changed;
- tests added;
- commands executed;
- observed results;
- any limitation or claim change.

Generated caches, local reports, credentials, submission files, chat transcripts and absolute local paths must not be committed.

## Authorship and citation

Code or documentation contributions do not automatically determine authorship on a scholarly article. Substantial scholarly contributions will be assessed under the applicable journal and CRediT criteria. All contributors retain acknowledgement through Git history.
