"""External backend adapters for v2.0.0.

These adapters intentionally separate authored TrustEvidence code from services
consumed as containers or externally managed test networks.
"""
from .fabric import FabricCliAdapter
from .hapi import HapiFhirAuditEventClient
from .rekor import RekorClientAdapter
from .trillian_personality import EvidenceTrillianPersonality

__all__ = [
    "FabricCliAdapter",
    "HapiFhirAuditEventClient",
    "RekorClientAdapter",
    "EvidenceTrillianPersonality",
]
