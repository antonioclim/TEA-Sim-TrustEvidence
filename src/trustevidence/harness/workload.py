"""Deterministic synthetic personal-monitoring workload generation."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Mapping

DEFAULT_EMITTED_AT: dict[str, str] = {
    "access_event.json": "2026-07-01T06:10:00.500Z",
    "aggregation_event.json": "2026-07-01T23:59:59.500Z",
    "cgm_monitoring_object_registration.json": "2026-07-01T06:00:00.500Z",
    "consent_grant_event.json": "2026-07-01T07:00:00.500Z",
    "consent_revocation_event.json": "2026-07-02T07:00:00.500Z",
    "disclosure_event.json": "2026-07-01T10:00:00.500Z",
    "failure_event.json": "2026-07-01T11:00:00.500Z",
    "provenance_transform_event.json": "2026-07-01T09:00:00.500Z",
    "wearable_monitoring_object_registration.json": "2026-07-01T06:05:00.500Z",
}


@dataclass(frozen=True, slots=True)
class WorkloadDescriptor:
    descriptor_id: str
    tree_size: int
    repetitions: int
    verification_samples: int
    deep_mutations: int = 1


def load_event_templates(directory: Path) -> dict[str, dict]:
    templates: dict[str, dict] = {}
    for name in sorted(DEFAULT_EMITTED_AT):
        path = directory / name
        templates[name] = json.loads(path.read_text(encoding="utf-8"))
    return templates


def sample_indices(tree_size: int, count: int) -> tuple[int, ...]:
    if tree_size <= 0 or count <= 0:
        return ()
    count = min(tree_size, count)
    if count == 1:
        return (tree_size // 2,)
    selected = {round(index * (tree_size - 1) / (count - 1)) for index in range(count)}
    # Rounding can collapse positions for small trees. Fill deterministically.
    if len(selected) < count:
        for index in range(tree_size):
            selected.add(index)
            if len(selected) == count:
                break
    return tuple(sorted(selected))


def iter_synthetic_events(
    templates: Mapping[str, dict],
    *,
    descriptor_id: str,
    repetition: int,
    tree_size: int,
) -> Iterator[tuple[int, str, dict, str]]:
    names = sorted(templates)
    for index in range(tree_size):
        name = names[(index + repetition) % len(names)]
        event = deepcopy(templates[name])
        event["source_event_id"] = (
            f"urn:te:event:{descriptor_id.lower()}:r{repetition:02d}:i{index:05d}"
        )
        yield index, name, event, DEFAULT_EMITTED_AT[name]
