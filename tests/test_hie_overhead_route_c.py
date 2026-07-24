"""Route C C5 paired local-overhead experiment regression tests."""

from __future__ import annotations

from copy import deepcopy

from experiments.run_hie_incremental_overhead import (
    BASELINES,
    CONFIRMATORY_WORKLOADS,
    PRIMARY_METRICS,
    build_aggregate_rows,
    build_pair_rows,
    load_and_validate_source,
    local_validate_source,
    process_operation,
    run_warmup,
    setup_context,
    verify_expected_invalid,
)

WORKLOAD = "W1-HIE-DISCLOSURE"


def _context(baseline: str):
    return setup_context(
        workload_id=WORKLOAD,
        baseline=baseline,
        phase="retained",
        block_id="R999",
        seed=2026072399,
        operation_count=1,
        warmup_count=1,
    )


def test_c5_confirmatory_scope_is_the_primary_hie_workload() -> None:
    assert CONFIRMATORY_WORKLOADS == (WORKLOAD,)


def test_c5_b0_b1_b2_preserve_source_and_expand_processing_boundary() -> None:
    observed = {}
    for baseline in BASELINES:
        context = _context(baseline)
        run_warmup(context)
        result = process_operation(context, operation_index=0, measure=True)
        assert result["accepted"]
        assert result["source_digest_preserved"]
        assert result["payload_exclusion_findings"] == 0
        observed[baseline] = result

    assert len({observed[name]["source_sha256"] for name in BASELINES}) == 1
    assert observed["B0"]["audit_projection_bytes"] == 0
    assert observed["B0"]["complete_portable_envelope_bytes"] == 0
    assert observed["B1"]["audit_projection_bytes"] > 0
    assert observed["B1"]["complete_portable_envelope_bytes"] == 0
    assert observed["B2"]["audit_projection_bytes"] == observed["B1"]["audit_projection_bytes"]
    assert observed["B2"]["complete_portable_envelope_bytes"] > 0
    assert observed["B2"]["signature_material_bytes"] > 0
    assert observed["B2"]["receipt_bytes"] > 0
    assert observed["B2"]["inclusion_proof_bytes"] > 0
    assert observed["B0"]["total_application_bytes"] < observed["B1"]["total_application_bytes"]
    assert observed["B1"]["total_application_bytes"] < observed["B2"]["total_application_bytes"]


def test_c5_b2_expected_stale_signature_mutation_is_rejected() -> None:
    context = _context("B2")
    run_warmup(context)
    result = process_operation(context, operation_index=0, measure=True)
    assert result["accepted"]
    expected, rejected, false_accepts = verify_expected_invalid(context)
    assert (expected, rejected, false_accepts) == (1, 1, 0)


def test_c5_secondary_fixture_contains_counts_but_no_raw_values() -> None:
    context = setup_context(
        workload_id="W2-WEARABLE-BATCH",
        baseline="B0",
        phase="pilot",
        block_id="P999",
        seed=2026072398,
        operation_count=1,
        warmup_count=1,
    )
    source, _, _ = load_and_validate_source(context.workload_id)
    local_validate_source(context.workload_id, source)
    text = str(source)
    assert "sample-count" in text
    assert "missingness-count" in text
    assert "valueQuantity" not in text
    assert "valueSampledData" not in text


def test_c5_pairing_and_bootstrap_derivation_are_deterministic() -> None:
    rows = []
    for block_index, block_id in enumerate(("R001", "R002"), 1):
        for baseline_index, baseline in enumerate(BASELINES):
            value = float(block_index * 10 + baseline_index)
            rows.append(
                {
                    "workload_id": WORKLOAD,
                    "paired_block_id": block_id,
                    "baseline": baseline,
                    "seed": str(100 + block_index),
                    "baseline_order": "B0>B2>B1",
                    "run_duration_ms": str(value),
                    "m7_p50_ms": str(value + 0.1),
                    "m7_p95_ms": str(value + 0.2),
                    "m7_p99_ms": str(value + 0.3),
                    "total_application_bytes_median": str(1000 + baseline_index * 100),
                    "storage_proxy_final_bytes": str(baseline_index * 1000),
                }
            )
    first_pairs = build_pair_rows(deepcopy(rows))
    second_pairs = build_pair_rows(deepcopy(rows))
    assert first_pairs == second_pairs
    assert len(first_pairs) == 6

    first = build_aggregate_rows(
        first_pairs,
        bootstrap_resamples=100,
        workloads=(WORKLOAD,),
    )
    second = build_aggregate_rows(
        second_pairs,
        bootstrap_resamples=100,
        workloads=(WORKLOAD,),
    )
    assert first == second
    assert len(first) == 3 * len(PRIMARY_METRICS)
