# Schema-first curation method

## Method objective

The method curates an accountability object for a personal-monitoring workflow without copying the underlying physiological payload into the public evidence envelope.

## Processing stages

```text
detect → select → normalise → minimise → validate
       → canonicalise → sign → append → verify → preserve
```

1. **Detect** a monitoring-accountability event at a governed software boundary.
2. **Select** only declared evidence facts needed for the event class.
3. **Normalise** timestamps and controlled identifiers under the application profile.
4. **Minimise** by rejecting direct identifiers, raw values, sample arrays, credentials and unrestricted payload containers.
5. **Validate** against a closed event-discriminated schema and event-specific semantic rules.
6. **Canonicalise** the unsigned signed projection using TE-JCS-1.
7. **Sign** the evidence core with an identified Ed25519 key.
8. **Append** the core digest to the local A2 reference log.
9. **Verify** the core signature, receipt signature, binding, inclusion path and, where applicable, retained-checkpoint consistency.
10. **Preserve** the evidence envelope and checkpoint under an external retention policy.

## Event classes

The executable profile admits seven classes: monitoring-object registration, access event, consent-state transition, provenance transform, disclosure event, aggregation event and failure event.

## Canonicalisation and numbers

TE-JCS-1 uses RFC 8785 serialisation after strict JSON admission and timestamp normalisation. The signed biomedical evidence profile rejects floating-point numbers and unsafe integers. Security-sensitive identifiers and controlled codes are restricted to the declared string domain.

## Payload commitment

`sha256-nonce-v1` binds a representation profile, commitment context, nonce and payload bytes. The nonce must contain at least 128 bits and remains outside the public envelope. Commitment verification demonstrates byte binding only; it does not encrypt the payload or establish its clinical truth.

## Local A2 receipt

The tree construction and inclusion/consistency algorithms are shaped by RFC 9162, but leaf inputs, profiles and application semantics are project-specific. The method claims local verifier-visible checks only, not Certificate Transparency compatibility or global non-equivocation.
