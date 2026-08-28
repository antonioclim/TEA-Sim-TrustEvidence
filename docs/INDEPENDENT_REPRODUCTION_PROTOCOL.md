# Independent reproduction protocol

## Purpose

This protocol records whether a person other than the author can obtain, install and execute the public TEA-Sim TrustEvidence release from the published documentation.

It evaluates reproducibility and usability of the reference software. It does not evaluate clinical utility, production readiness, legal compliance or organisational effectiveness.

## Independence classification

Record one category:

- **Independent:** no private files, unpublished commands or author intervention were used.
- **Assisted:** the author or maintainer supplied troubleshooting beyond the public documentation.
- **Author-executed:** useful as a regression check but not independent reproduction.

Only the first category supports an independent-reproduction statement.

## Environment record

Record:

- operator name or persistent identifier;
- organisation;
- date and time zone;
- operating system and version;
- architecture;
- CPU and memory;
- Python version;
- package manager version;
- exact release DOI, tag and archive checksum;
- whether application network access was disabled after dependency installation.

Do not include usernames, local absolute paths, credentials or sensitive system information in the public report.

## Procedure A — repository route

1. Obtain the exact v2.2.0 release.
2. Verify the canonical ZIP against `TEA-Sim-TrustEvidence-v2.2.0.sha256`.
3. Extract into a new directory.
4. Create a fresh Python 3.13 virtual environment.
5. Install the locked dependencies exactly as documented.
6. Run:

```bash
make release-check
```

7. Retain the complete console transcript.
8. Record elapsed wall-clock time separately from scientific timing results.

## Procedure B — targeted reviewer route

Run and record:

```bash
python scripts/check_public_metadata.py
python scripts/verify_sha256sums.py SHA256SUMS.txt
python scripts/verify_file_manifest.py FILE_MANIFEST.tsv
python experiments/run_hie_hero_case.py --check
python scripts/check_c3_retained_evidence.py
python experiments/run_hie_security_mutations.py --check
python experiments/run_hie_incremental_overhead.py --check
python scripts/validate_result_contracts.py
python scripts/make_reproducibility_manifest.py --check
```

## Decision table

For each command record:

| Field | Required value |
|---|---|
| Command | Exact command |
| Exit code | Integer |
| Start and end time | ISO 8601 |
| Outcome | PASS, FAIL or NOT RUN |
| First failing stage | Exact stage or `none` |
| Intervention | `none` or full description |
| Evidence | Transcript filename and SHA-256 |

## Acceptance criteria

An independent reproduction passes only if:

- the exact release and checksum are verified;
- installation uses a fresh environment;
- no private artefact or unpublished command is required;
- `make release-check` exits successfully;
- retained-result checks report their documented decisions;
- generated drift is absent;
- the report identifies all deviations.

A failed reproduction must be retained. Packaging, dependency and documentation failures are software evidence and must not be silently discarded.

## Public report template

```text
Release:
DOI:
Git tag:
Canonical ZIP SHA-256:
Operator:
Organisation:
Independence category:
Environment:
Commands executed:
Overall outcome:
Failures or interventions:
Transcript SHA-256:
Permission to cite this report:
```

The operator may return the report through a GitHub issue if it contains no sensitive information. Security-sensitive findings must follow `SECURITY.md`.
