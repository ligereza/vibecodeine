from flujo.knowledge.portfolio_vizz_read_only_context import (
    build_portfolio_vizz_read_only_context,
    validate_portfolio_vizz_read_only_context,
)


def _inputs():
    return {
        "schema": "mak-vizz-measurement-status-v1",
        "status": "unknown_measurement_refused",
        "measurement": {"calibration_status": "CALIBRATION_EVIDENCE_REQUIRED", "triangulation_attempted": False, "depth_result_present": False},
    }, {
        "schema": "mak-vizz-lineage-status-v1",
        "status": "revision_context_only",
        "current": {"status": "unknown_measurement_refused", "ref": "grammar-lab:Q-650:artifact"},
        "revision": {"status": "revision_accepted"},
        "control": {"current_state_replaced": False},
    }, {
        "schema": "mak-structural-delta-status-v1",
        "status": "revision_only_delta",
        "delta": {"shared_keys": 2, "residue_keys": 15, "serialized_savings_bytes": -131},
    }, {
        "schema": "mak-portfolio-work-preview-v1",
        "preview_only": True,
        "source": {"project_id": "project-1", "relation_status": "needs_evidence"},
        "task": {"id": "vizz_calibration", "state": "vizz_measurement_refused", "human_gate": "physical_calibration_evidence", "execution_allowed": False},
        "provenance": {"task_execution": False},
    }


def test_portfolio_vizz_context_preserves_all_refusals():
    payload = build_portfolio_vizz_read_only_context(*_inputs(), generated_at="fixture")
    assert validate_portfolio_vizz_read_only_context(payload)
    assert payload["measurement"]["triangulation_attempted"] is False
    assert payload["measurement"]["depth_result_present"] is False
    assert payload["delta"]["serialized_savings_bytes"] == -131
    assert payload["control"]["measurement_execution"] is False
    assert payload["boundary"]["semantic_claim"] is False


def test_portfolio_vizz_context_rejects_measurement_opening():
    payload = build_portfolio_vizz_read_only_context(*_inputs())
    payload["measurement"]["triangulation_attempted"] = True
    try:
        validate_portfolio_vizz_read_only_context(payload)
    except ValueError as exc:
        assert str(exc) == "vizz_context_measurement_invalid"
    else:
        raise AssertionError("measurement opening was accepted")


def test_portfolio_vizz_context_rejects_preview_execution():
    payload = build_portfolio_vizz_read_only_context(*_inputs())
    payload["preview"]["execution_allowed"] = True
    try:
        validate_portfolio_vizz_read_only_context(payload)
    except ValueError as exc:
        assert str(exc) == "vizz_context_preview_invalid"
    else:
        raise AssertionError("preview execution was accepted")
