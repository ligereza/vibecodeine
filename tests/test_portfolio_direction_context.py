import pytest

from flujo.knowledge.portfolio_direction_context import (
    build_portfolio_direction_context,
    validate_portfolio_direction_context,
)


pytestmark = pytest.mark.flujo


def _surfaces():
    archive = {
        "schema": "mak-archive-portfolio-view-v1",
        "status": "draft_only",
        "source": {"input_hash": "sha256:archive"},
        "selection": {
            "selected_item_count": 3,
            "declared_work_count": 1,
            "observed_field_count": 1,
            "practice_context_count": 1,
            "documented_record_count": 1,
        },
        "reconciliation": {"omitted_piece_count": 4},
    }
    review = {
        "schema": "mak-portfolio-review-context-v1",
        "available": True,
        "read_only": True,
        "project": {
            "unknowns": ["method"],
            "evidence": [{"kind": "application_package"}],
            "next_action": "provide_typed_archive_project_relation_with_source_refs",
        },
        "relation": {"status": "needs_evidence"},
    }
    receipt = {
        "schema": "mak-operation-receipt-v1",
        "available": True,
        "read_only": True,
        "status": "executed_structural_only",
        "operation": {"name": "expand_library_program", "expanded_count": 2},
    }
    measurement = {
        "schema": "mak-vizz-measurement-status-v1",
        "available": True,
        "read_only": True,
        "status": "unknown_measurement_refused",
        "measurement": {
            "unknown": True,
            "triangulation_attempted": False,
            "depth_result_present": False,
        },
        "next_action": "provide_physical_calibration_evidence_before_metric_measurement",
    }
    lineage = {
        "schema": "mak-vizz-lineage-status-v1",
        "available": True,
        "read_only": True,
        "status": "revision_context_only",
    }
    delta = {
        "schema": "mak-structural-delta-status-v1",
        "available": True,
        "read_only": True,
        "status": "revision_only_delta",
        "delta": {"evaluated_keys": 4, "shared_keys": 1, "residue_keys": 3},
    }
    return archive, review, receipt, measurement, lineage, delta


def test_direction_context_composes_three_layers_without_claims():
    payload = build_portfolio_direction_context(*_surfaces())

    assert validate_portfolio_direction_context(payload) is True
    assert payload["purpose"] == "vision_order_culture_computation_read_only_frame"
    assert payload["frame"]["vision"]["visible_item_count"] == 3
    assert payload["frame"]["order"]["shared_keys"] == 1
    assert payload["frame"]["culture_computation"]["project_unknown_count"] == 1
    assert payload["frame"]["instrument"]["measurement_unknown"] is True
    assert payload["control"]["selection_effect"] == "none"
    assert payload["control"]["normalize_execution"] is False
    assert payload["provenance"]["semantic_claim"] is False
    assert payload["provenance"]["learning_demonstrated"] is False


def test_direction_context_rejects_unavailable_component():
    surfaces = list(_surfaces())
    surfaces[4] = {"schema": "mak-vizz-lineage-status-v1", "available": False, "read_only": True}

    try:
        build_portfolio_direction_context(*surfaces)
    except ValueError as exc:
        assert str(exc) == "vizz_lineage_must_be_available_read_only"
    else:
        raise AssertionError("unavailable surface should be rejected")


def test_direction_context_rejects_tampered_frame_state_and_metric():
    payload = build_portfolio_direction_context(*_surfaces())
    payload["frame"]["order"]["state"] = "semantic_order"
    try:
        validate_portfolio_direction_context(payload)
    except ValueError as exc:
        assert str(exc) == "portfolio_direction_context_order_boundary_invalid"
    else:
        raise AssertionError("tampered order state should be rejected")

    payload = build_portfolio_direction_context(*_surfaces())
    payload["frame"]["vision"]["visible_item_count"] = -1
    try:
        validate_portfolio_direction_context(payload)
    except ValueError as exc:
        assert str(exc) == "frame.vision.visible_item_count_invalid"
    else:
        raise AssertionError("tampered vision metric should be rejected")
