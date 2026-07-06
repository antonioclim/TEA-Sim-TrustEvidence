# R4 versus R5 decision — v2.0.0

Decision: use FHIR R4 (4.0.1) for the first TrustEvidence IG draft.

Rationale:

1. IHE BALP v1.1.4 is the closest audit-pattern neighbour and is published on FHIR R4.
2. The operational path in this release targets HAPI FHIR/BALP integration, making R4 the lower-risk starting point.
3. The v2.0.0 artefacts constrain only R4 element paths checked in the current artefacts; v2.0.0 must run tooling and decide whether to derive from BALP profiles or remain mapped to them.

This decision does not preclude a later R5 migration, but any migration must be explicit.
