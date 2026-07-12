"""Replay a retained synthetic workload-event index without raw payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator


def read_workload_index(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            required = {"descriptor_id", "repetition", "event_index", "event_id", "event_type", "core_digest"}
            missing = required - set(value)
            if missing:
                raise ValueError(f"line {line_number} missing fields: {sorted(missing)}")
            yield value
