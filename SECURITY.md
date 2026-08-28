# Security policy

## Supported version

Security reports are assessed against the current public release and the default branch. Historical releases are retained for reproducibility but may not receive backported fixes.

## Reporting a vulnerability

Do not open a public issue containing exploitable details, credentials, private keys, access tokens or sensitive institutional information.

Send a concise report to the maintainer at `antonio.clim@csie.ase.ro` with:

- the affected release or commit;
- the affected component;
- prerequisites and threat assumptions;
- reproducible steps using synthetic or non-sensitive data;
- observed and expected behaviour;
- potential impact;
- any proposed mitigation.

A report should distinguish a software defect from a limitation already declared by the project.

## Declared assurance boundary

The reference implementation evaluates bounded structural, semantic, signature, commitment, receipt and retained-checkpoint properties. It does not establish:

- clinical truth or identity proofing;
- confidentiality or operational key management;
- event completeness;
- truthful backend population or backend honesty;
- replay prevention across deployments;
- public transparency or global non-equivocation;
- production readiness or legal compliance.

Reports that demonstrate a violation of a stated invariant within the documented threat model are in scope. Requests to treat an explicitly excluded property as already guaranteed are not vulnerability reports.

## Sensitive data

Do not send patient data or production logs. Replace sensitive material with a minimal synthetic reproducer.
