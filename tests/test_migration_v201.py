from __future__ import annotations

import json
from pathlib import Path

import pytest

from trustevidence.migration import MigrationError, inspect_v201_object, migrate_v201_event

ROOT = Path(__file__).resolve().parents[1]


def test_incomplete_historical_object_is_not_silently_relabelled():
    old = {"evidence_version": "2.0.1", "event_type": "access-event", "payload_hash": "00" * 32}
    inspection = inspect_v201_object(old)
    assert inspection.recognised
    assert inspection.missing_v21_semantics
    with pytest.raises(MigrationError):
        migrate_v201_event(old)


def test_explicit_complete_mapping_can_be_admitted():
    event = json.loads((ROOT / "data_examples/personal_monitoring/access_event.json").read_text())
    migrated = migrate_v201_event({"evidence_version": "2.0.1"}, completed_mapping=event)
    assert migrated["source_event_id"] == event["source_event_id"]
