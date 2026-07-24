"""Public API for the TEA-Sim v2.2.0 release.

The pre-existing personal-monitoring envelope profile remains version 2.1.0;
the software distribution version is independent from that wire/schema version.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("teasim-trustevidence")
except PackageNotFoundError:
    __version__ = "2.2.0+uninstalled"

from .canonical import canonicalise_rfc8785, canonicalise_te, strict_json_loads
from .crypto import commit_payload, verify_payload_commitment
from .curation import curate_monitoring_event
from .envelope import build_signed_envelope
from .schema import load_schema, validate_structure
from .validators import ValidationResult, validate_curation_result, validate_envelope, validate_monitoring_event

__all__ = [
    "__version__",
    "build_signed_envelope",
    "canonicalise_rfc8785",
    "canonicalise_te",
    "commit_payload",
    "curate_monitoring_event",
    "load_schema",
    "strict_json_loads",
    "validate_structure",
    "ValidationResult",
    "validate_monitoring_event",
    "validate_envelope",
    "validate_curation_result",
    "verify_payload_commitment",
]
