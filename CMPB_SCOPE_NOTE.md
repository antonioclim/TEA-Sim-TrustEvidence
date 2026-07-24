# Personal-monitoring module scope note

The `cmpb_method/` and personal-monitoring fixtures preserve the schema-first curation method released in v2.1.0. Their unit of analysis is a synthetic personal-monitoring accountability event, and their method curates evidence about registration, access, consent, transformation, disclosure, aggregation and failure without copying raw physiological values into the public envelope.

The v2.2.0 line is additive. It retains that module and adds the separate `TE-HIE-Envelope-1` health-information-exchange profile, the synthetic cross-organisational disclosure case, bounded official FHIR validation evidence, registered C4 security cases and the C5 paired local experiment.

Neither module is a generic governance framework, a clinical study, a production deployment or a universal standards-conformance claim. The local A2 implementation supports the declared receipt and verifier-visible checks only; it does not establish event completeness, backend honesty, public transparency or global non-equivocation.
