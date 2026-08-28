# Support

## Scope

TEA-Sim TrustEvidence is research software and a reference implementation. Support covers installation, reproducibility, test behaviour, documentation and clearly isolated software defects.

The project does not provide clinical advice, legal or regulatory advice, production operations support, service-level guarantees or incident response for healthcare organisations.

## Requesting support

Use a GitHub issue for non-sensitive questions and reproducible defects. Include:

- the exact release or commit;
- operating system and architecture;
- Python version;
- the command executed;
- expected and observed behaviour;
- the shortest non-sensitive input that reproduces the problem;
- the complete error message or relevant log excerpt.

Do not upload patient data, credentials, private keys, access tokens, restricted datasets or institutional logs.

Before opening an issue, run the documented quick route where feasible:

```bash
make release-check
```

For the version-bounded reproduction procedure, see `REVIEWER_REPRODUCTION.md` and `docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md`.

## Security-sensitive reports

Do not disclose exploitable details in a public issue. Follow `SECURITY.md`.

## Maintenance boundary

Support is provided on a reasonable-effort basis. The repository does not promise response times, long-term compatibility with untested platforms or maintenance of external FHIR, terminology or package services.
