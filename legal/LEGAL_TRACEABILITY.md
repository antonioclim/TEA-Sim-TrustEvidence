# Legal traceability

This document maps selected audit-trail obligations from EHDS, GDPR, ISO 27789, IHE BALP and IHE ATNA to technical requirements for the TrustEvidence reference artefacts. It is a traceability aid for engineering and evaluation. It is not legal advice, a Data Protection Impact Assessment, certification, CE marking, EHDS conformity, GDPR compliance or ISO 27789 conformance.

## Source-control rule

EHDS and GDPR references should be checked against the current EUR-Lex text before legal interpretation is used in a manuscript or compliance process. ISO 27789 references in this repository are limited to public catalogue-level information unless the licensed standard text is separately available. Terms such as “requirement” and “obligation” therefore refer to engineering traceability, not to a formal legal opinion.

## Minimum traceability questions

1. Which actor or organisation accessed or emitted the event?
2. Which subject or record context is referenced without exposing raw clinical payloads?
3. Which category of data or evidence event is represented?
4. When did the event occur, when was it emitted and when was any backend receipt issued?
5. Which origin, policy version, consent state and payload commitment are bound to the evidence artefact?
6. Which backend property is required: central accountability, append-only consistency, inclusion proof or stronger non-equivocation support?
7. Which verification route exists: schema validation, signature validation, proof verification, verifier-state comparison, witness comparison or ledger finality evidence?

## Engineering boundary

The repository can support traceability analysis by making evidence fields, backend receipts and verification assumptions explicit. It cannot by itself establish legal sufficiency, controller/processor allocation, national implementation rules, clinical workflow adequacy or certification status.

## Manuscript consequence

A manuscript may describe this material as legal-to-technical traceability for auditable health information exchange. It should not claim legal compliance, certification, conformance or production market readiness on the basis of this repository alone.
