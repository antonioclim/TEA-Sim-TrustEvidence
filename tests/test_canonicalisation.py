from __future__ import annotations

import csv

import pytest

from trustevidence.canonical import CanonicalisationError, canonicalise_json_text, canonicalise_te, normalise_timestamp_ms


def test_object_order_is_ignored_and_array_order_is_retained():
    assert canonicalise_te({"b": 2, "a": [1, 2]}) == canonicalise_te({"a": [1, 2], "b": 2})
    assert canonicalise_te({"a": [1, 2]}) != canonicalise_te({"a": [2, 1]})


def test_strict_admission_rejects_duplicate_names_floats_and_unsafe_integers():
    with pytest.raises(CanonicalisationError):
        canonicalise_json_text('{"a":1,"a":2}', te_profile=True)
    with pytest.raises(CanonicalisationError):
        canonicalise_te({"x": 0.1})
    with pytest.raises(CanonicalisationError):
        canonicalise_te({"x": 9_007_199_254_740_992})


def test_timestamp_normalisation_is_exact():
    assert normalise_timestamp_ms("2026-07-01T08:10:00.500+02:00") == "2026-07-01T06:10:00.500Z"
    assert normalise_timestamp_ms("2026-07-01T06:10:00Z") == "2026-07-01T06:10:00.000Z"
    with pytest.raises(CanonicalisationError):
        normalise_timestamp_ms("2026-07-01T06:10:00.000001Z")


def test_retained_canonicalisation_matrix_passes(root_path=None):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    rows = list(csv.DictReader((root / "results_expected/cmpb_reference/canonicalisation_determinism.csv").open(newline="", encoding="utf-8")))
    assert len(rows) == 35
    assert all(row["passed"] == "true" for row in rows)
