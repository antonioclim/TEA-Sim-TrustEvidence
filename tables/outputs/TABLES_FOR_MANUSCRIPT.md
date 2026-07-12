# Tables for the CMPB manuscript

These tables are generated from retained CSV sources. Wording is deliberately bounded to the executed evidence.

## Table 1. Curation problem decomposition

| Curation stage | Biomedical accountability question | Retained evidence | Excluded content | Failure control |
| --- | --- | --- | --- | --- |
| Detect | Which monitoring-related action occurred? | Event identifier, event type and occurrence time | Physiological values and raw signal samples | Input/schema admission |
| Select | Which facts are necessary for later accountability? | Actor/emitter, pseudonymous subject, object roles, purpose and outcome | Unrestricted source payload | Declared-core competency questions |
| Normalise and minimise | Can equivalent metadata be represented consistently without direct identifiers? | UTC timestamps, controlled codes and tokenised references | Emails, names, local paths and public commitment nonce | Timestamp and recursive minimisation checks |
| Validate | Does one event-specific semantic branch hold? | Closed event facts plus conditional policy/consent bindings | Unknown extension fields | Draft 2020-12 schema and semantic rules |
| Canonicalise and sign | Are the curated facts bound to deterministic bytes and an emitter identity? | TE-JCS-1 digest and Ed25519 signature | Circular signature content | Canonicalisation vectors and signature mutation tests |
| Append and receive | Can a verifier reconstruct local inclusion and bind the receipt to the evidence? | Core/leaf digests, index, size, root, proof and receipt signature | Backend-internal payload data | Inclusion, mutation and consistency checks |
| Preserve and compare | Can a retained verifier detect rollback or conflicting same-size roots? | Evidence envelope, curation result and retained checkpoint | Claims of global witness agreement | Checkpoint rollback/fork and prefix-consistency controls |

**Table note.** The stages distinguish monitoring-accountability curation from the governed physiological-payload pathway.

## Table 2. TrustEvidence envelope specification

| Component | Cardinality | Principal fields | Validation or binding |
| --- | --- | --- | --- |
| Envelope wrapper | required | envelope_version; profile; evidence_core | Closed root; optional backend_receipt |
| Evidence identity and time | required | evidence_id; event_id; event_type; occurred_at; emitted_at; time_source | URN patterns; exact UTC timestamp profile; emitter signature |
| Operational origin | emitter required; actor event-dependent | emitter; actor | Actor/emitter separation and event-specific requirements |
| Biomedical context | required | subject_context; objects; purpose_code; outcome; event_facts | Pseudonymous subject; controlled object roles; one event branch |
| Governance context | conditional | policy_binding; consent_binding | Required for access, consent and disclosure branches as specified |
| Minimisation and payload binding | privacy profile required; commitment optional | privacy_profile; optional payload commitment inside event facts | Recursive leakage rejection; nonce withheld from public envelope |
| Emitter authenticity | required | emitter_signature | Domain-separated Ed25519 verification against fixture key registry |
| Local A2 receipt | optional at envelope creation; required for receipt verification | backend/log identity; core and leaf digests; leaf index; tree size; root; proof; receipt signature | Signed receipt; proof digest; inclusion reconstruction; retained-checkpoint comparison |

**Table note.** Required and conditional elements follow the v2.1.0 closed schema and local A2 receipt profile.

## Table 3. Validation and failure-injection evidence

| Evidence layer | Executed units | Expected decision | Observed result | Interpretation boundary |
| --- | --- | --- | --- | --- |
| Positive schema/input/envelope cases | 19 | accepted | 19/19 accepted | Synthetic fixtures only |
| Controlled schema/semantic/minimisation negatives | 34 | rejected | 34/34 rejected | Specified case catalogue, not exhaustive |
| Required/conditional field deletion | 185 | rejected | 185/185 rejected | Supports declared-core wording, not universal minimality |
| Canonicalisation and strict-admission cases | 35 | specified equality/difference/rejection | 35/35 matched | Selected RFC vectors; Python pathway |
| Receipt, mutation and consistency cases | 57 | specified acceptance/rejection/absence | 57/57 matched | Local fixture keys and local A2 profile |
| Hypothesis property examples | 680 | property holds for generated examples | 680 passing; 0 reported failures | Finite deterministic generation, not proof |
| Finite bounded checks | 29,105 | property holds in bounded domain | 29,105 checks; 0 failures | Domain {0,1,2}; histories through length five |
| Duplicate-leaf occurrence uniqueness | 1 | counterexample retained | Limitation observed | Membership does not by itself prove unique occurrence |

**Table note.** Counts are executed schema, canonicalisation, mutation and property evidence. Generated and bounded checks are finite and are not formal proof.

## Table 4. Executed local reference passage

| Descriptor | Leaves | Events | Append p50 (ms) | Append p95 (ms) | Verify p50 (ms) | Verify p95 (ms) | Receipt median (bytes) | Proof median (bytes) | Receipt checks | Mutation rejections | Validation failures | Evidence status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W128 | 128 | 1,536 | 0.010489000 | 0.015765000 | 4.266067000 | 5.150278000 | 1,415 | 545 | 384 | 12/12 | 0 | executed; single-host descriptive local reference |
| W512 | 512 | 6,144 | 0.010413500 | 0.014450000 | 4.309459500 | 5.142139000 | 1,551 | 680 | 384 | 12/12 | 0 | executed; single-host descriptive local reference |
| W2048 | 2,048 | 24,576 | 0.010269000 | 0.014714000 | 4.444148500 | 6.006398000 | 1,688 | 815 | 384 | 12/12 | 0 | executed; single-host descriptive local reference |

**Table note.** Timing values are single-host descriptive measurements; they are not comparative benchmarks or production capacity estimates.
