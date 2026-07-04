# Draft TrustEvidence FHIR artefacts

This directory contains draft FHIR Shorthand source for TrustEvidence AuditEvent and Provenance artefacts. The source is intended for standards-aligned experimentation and does not claim HL7 or IHE endorsement.

Run static checks with:

```bash
make validate-fsh-static
make validate-ig-static
```

Run SUSHI in an environment with package access:

```bash
cd ig
npx --yes fsh-sushi .
```
