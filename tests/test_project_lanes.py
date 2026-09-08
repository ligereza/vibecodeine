"""Tests for the cross-domain cultural-research lane registry."""

from __future__ import annotations

from pathlib import Path

from tools import project_lanes


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "knowledge" / "lane_registry" / "mak_cross_domain_registry_2026-08-20.json"


def test_registry_is_one_first_layer_and_has_requested_lines() -> None:
    registry = project_lanes.load_registry(REGISTRY)
    assert project_lanes.validate_registry(registry) == []
    assert registry["layer"] == "cultural_research_first"
    lane_ids = {lane["lane_id"] for lane in registry["lanes"]}
    assert {"pnp_search_ecology", "tennis_decision_lab", "research_capture_scraping", "deep_learning_micelio"} <= lane_ids
    assert len(lane_ids) >= 12


def test_implemented_lanes_have_declared_consumers() -> None:
    registry = project_lanes.load_registry(REGISTRY)
    for lane in registry["lanes"]:
        if lane["current_state"] == "implemented":
            assert lane.get("consumer", {}).get("tool_id")


def test_summary_preserves_proposal_and_partial_states() -> None:
    registry = project_lanes.load_registry(REGISTRY)
    result = project_lanes.summary(registry)
    assert result["lane_count"] >= 12
    assert result["states"]["proposal"] >= 1
    assert result["states"]["partial"] >= 1
