# Software and module scope

TEA-Sim TrustEvidence v2.2.0 contains two related but distinct reference profiles.

The personal-monitoring module preserves the schema-first curation method released in v2.1.0. Its unit of analysis is a synthetic personal-monitoring accountability event. It represents registration, access, consent, transformation, disclosure, aggregation and failure evidence without copying raw physiological values into the public envelope.

The v2.2.0 health-information-exchange module adds the separate `TE-HIE-Envelope-1` profile, a synthetic cross-organisational DiagnosticReport disclosure case, bounded official FHIR validation evidence, registered security cases and a paired local reference-pipeline experiment.

The software is a research reference implementation. It is not a generic governance framework, clinical study, production deployment or universal standards-conformance claim. The local A2 implementation supports the declared receipt and verifier-visible checks only. It does not establish event completeness, backend honesty, public transparency or global non-equivocation.
