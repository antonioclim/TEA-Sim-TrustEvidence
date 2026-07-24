# C5 secondary wearable-batch fixture

`wearable_monitoring_batch.json` is a synthetic, FHIR-shaped secondary workload fixture prepared before the C5 confirmatory run. It contains a pseudonymous patient token, a synthetic aggregation service, one batch-summary Observation and one Provenance resource. The summary records a sample count and missingness count but no raw wearable measurements.

The frozen C5 execution plan omits this secondary workload under the protocol's critical-path clause. It is retained as inspectable design material only. No W2 processing-time, message-size, storage or cross-workload generalisation is claimed.
