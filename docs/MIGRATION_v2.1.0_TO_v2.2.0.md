# Migration from v2.1.0 to v2.2.0

The v2.2.0 line is an additive healthcare-information-exchange extension. It does not silently revise or relabel the established v2.1.0 personal-monitoring envelope.

## Version identities

| Layer | v2.1.0 | v2.2.0 line |
|---|---|---|
| Python distribution | `2.1.0` | `2.2.0` |
| Personal-monitoring envelope | `2.1.0` | remains `2.1.0` |
| HIE disclosure event | absent | `1.0.0` |
| HIE TrustEvidence envelope | absent | `1.0.0`, profile `TE-HIE-Envelope-1` |

## Additive interfaces

- `trustevidence.hie` constructs and verifies the bounded HIE envelope.
- `trustevidence.hie_validation` applies the HIE semantic and minimisation checks.
- `trustevidence.hie_state` provides the retained local-checkpoint verification boundary.
- `hie_disclosure_event.schema.json` and `hie_trust_evidence_envelope.schema.json` define the new closed HIE structures.
- C3, C4 and C5 experiment drivers and retained evidence are added without changing the historical v2.1.0 monitoring corpus.

## Compatibility rules

1. Keep existing v2.1.0 monitoring envelopes at `envelope_version: 2.1.0`.
2. Do not translate an existing monitoring envelope into the HIE profile by changing only the version or profile field.
3. Construct an HIE envelope from a declared HIE disclosure event and the required consent, policy, decision, source-commitment and provenance bindings.
4. Treat the deterministic test keys and nonces as fixtures only.
5. Revalidate every HIE object against the HIE schema and semantic checks; schema acceptance alone is insufficient.
6. Treat A2 receipts as authenticated backend statements, not proof of truthful tree size, actual population, completeness or backend honesty.

## Operational migration

No operational migration is supplied because neither v2.1.0 nor v2.2.0 is a production deployment. A hospital implementation would additionally require identity and certificate lifecycle management, consent and policy services, durable storage, concurrency control, transport security, access control, observability, recovery and governance procedures. These are enumerated in `DEPLOYABILITY_AND_COMPONENTS.md` and are not implied by this software migration note.
