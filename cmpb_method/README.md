# CMPB method layer

The method layer is organised around three machine-readable objects:

1. `MonitoringEvent`: closed adapter-facing metadata with no raw physiological value;
2. `TrustEvidenceEnvelope`: a versioned, event-discriminated public evidence object;
3. `CurationResult`: a stage-level execution record.

`COMPETENCY_QUESTIONS.md` defines the audit questions. `competency_question_register.csv` is the machine-readable register used by the experiment. `BIOMEDICAL_RELEVANCE_NOTE.md` explains why the fixtures are more specific than a generic event-log demonstration.
