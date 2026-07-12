"""Deterministic synthetic workload helpers for the CMPB reference passage."""

from .workload import (
    DEFAULT_EMITTED_AT,
    WorkloadDescriptor,
    iter_synthetic_events,
    load_event_templates,
    sample_indices,
)

__all__ = [
    "DEFAULT_EMITTED_AT",
    "WorkloadDescriptor",
    "iter_synthetic_events",
    "load_event_templates",
    "sample_indices",
]
