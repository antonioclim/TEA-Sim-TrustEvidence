# Security policy

## Supported version

Security reports are accepted for the latest public release and the current `main` branch. The current citable release is v2.2.0.

## Important claim boundary

TEA-Sim TrustEvidence is research software and a reference implementation. It does not provide or claim:

- production transport or at-rest encryption;
- certificate lifecycle, key rotation or revocation;
- hardware security module integration;
- identity proofing;
- durable replicated logging;
- replay prevention;
- global non-equivocation;
- event completeness;
- backend honesty;
- legal or regulatory compliance.

A signed statement or receipt authenticates the declared bytes and signer under the implemented assumptions. It does not establish that the source event is clinically true, complete or honestly submitted.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability.

Send a concise private report to `antonio.clim@csie.ase.ro` with the subject:

```text
[TEA-Sim security report]
```

Include:

- affected version or commit;
- threat scenario;
- minimal non-sensitive reproducer;
- expected and observed behaviour;
- potential impact;
- whether public disclosure has occurred.

Do not send credentials, private keys, patient data or restricted datasets.

## Response and disclosure

Receipt will be acknowledged when operationally possible. A report may be classified as:

- exploitable software defect;
- documentation or claim-boundary defect;
- expected limitation;
- unsupported production scenario;
- not reproducible.

No response-time or remediation-time service level is promised. Coordinated disclosure will be discussed for a reproducible defect. Public credit will be provided unless the reporter requests anonymity.
