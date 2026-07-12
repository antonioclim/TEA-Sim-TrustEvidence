# Migration from v2.0.1 to v2.1.0

v2.1.0 is a method and schema revision, not a metadata-only patch. Historical v2.0.1 objects must not be relabelled as v2.1.0 envelopes.

## Breaking changes

- the public semantic package is `trustevidence` only;
- evidence events use a closed event-discriminated model;
- the operational actor and software emitter are distinct;
- arbitrary extension values are not admitted into the signed core;
- canonicalisation follows TE-JCS-1 rather than Python `json.dumps` as a cross-language contract;
- local A2 receipts bind leaf index, tree size, inline proof, proof digest, backend/log identity and signer identity;
- a larger retained-checkpoint advance requires TE-A2-Consistency-1 proof material;
- raw monitoring values and commitment nonces are excluded from the public envelope.

`trustevidence.migration.v201` provides an explicit inspection and translation boundary. It refuses silent migration when required v2.1 semantic facts are absent.
