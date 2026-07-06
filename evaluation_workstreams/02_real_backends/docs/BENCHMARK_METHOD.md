# Benchmark method

The A2 Merkle benchmark uses deterministic synthetic TrustEvidence objects and measures local Python reference-implementation behaviour. For each configured object count, one warm-up run is discarded and ten repetitions are retained by default. The benchmark collects append latency, verification latency, receipt size, proof size and serialised local storage footprint.

Append latency measures canonicalisation, SHA-256 leaf generation, append-record creation and incremental root update. Verification latency measures inclusion-receipt verification against a final tree root for a deterministic sample of object indices. The benchmark is deliberately scoped to local reference-implementation behaviour and should not be interpreted as production throughput, clinical-system latency or a database/transparency-service comparison.

A1 PostgreSQL and A3 service execution are represented as explicit status rows when their runtime prerequisites are unavailable. That prevents implicit performance comparison against backends that were not executed.
