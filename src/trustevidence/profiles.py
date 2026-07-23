"""Central profile and version identifiers.

The software distribution is v2.2.0-rc.1.  The established personal-
monitoring method and envelope remain at version 2.1.0 because Route C adds a
separate HIE profile rather than relabelling historical objects.
"""

SOFTWARE_RELEASE_LABEL = "v2.1.0"
DISTRIBUTION_RELEASE_LABEL = "v2.2.0-rc.1"
ENVELOPE_VERSION = "2.1.0"
INPUT_VERSION = "1.0.0"
RESULT_VERSION = "1.0.0"

ENVELOPE_PROFILE = "TE-CMPB-Envelope-1"
MINIMISATION_PROFILE = "TE-PHM-Min-1"
TOKENISATION_PROFILE = "TE-Token-Pseudonymous-1"
CANONICALISATION_PROFILE = "TE-JCS-1"
TIMESTAMP_PROFILE = "TE-Timestamp-UTC-ms-1"
HASH_PROFILE = "TE-HASH-1"
RECEIPT_PROFILE = "TE-A2-Receipt-1"
INCLUSION_PROFILE = "TE-A2-Inclusion-1"
CONSISTENCY_PROFILE = "TE-A2-Consistency-1"
TREE_PROFILE = "TE-A2-Binary-Merkle-1"
RESULT_PROFILE = "TE-Curation-Result-1"
COMMITMENT_PROFILE = "sha256-nonce-v1"

EVENT_TYPES = (
    "monitoring-object-registration",
    "access-event",
    "consent-state-transition",
    "provenance-transform",
    "disclosure-event",
    "aggregation-event",
    "failure-event",
)

STAGES = (
    "detect", "select", "normalise", "minimise", "validate",
    "canonicalise", "sign", "append", "verify", "preserve",
)
