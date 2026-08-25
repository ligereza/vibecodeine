"""Tests for the isolated routing-versus-operating-world experiment."""

from __future__ import annotations

from experiments.mak_operating_world.model import (
    Capability,
    OperatingCase,
    plan_case,
    validate_plan,
)


def _capabilities() -> tuple[Capability, ...]:
    return (
        Capability("capture", "capture_tool", frozenset({"source_available"}), frozenset({"captured"}), "capture_validator", "capture"),
        Capability("extract", "extract_tool", frozenset({"captured"}), frozenset({"claims"}), "extract_validator", "extract"),
        Capability("simulate", "simulate_tool", frozenset({"claims"}), frozenset({"simulation_verified"}), "simulation_validator", "simulate"),
    )


def test_world_model_composes_known_capabilities() -> None:
    case = OperatingCase(
        "composition", "p", "simulate", "simulate",
        frozenset({"source_available"}), frozenset({"simulation_verified"}),
        "planned", True, tuple(), frozenset(),
    )
    result = plan_case(case, {"schema": "ignored"}, _capabilities())
    assert result.status == "planned"
    assert result.plan == ("capture", "extract", "simulate")
    assert validate_plan(case, result)["status"] == "passed"


def test_world_model_reports_missing_capability_instead_of_guessing() -> None:
    case = OperatingCase(
        "gap", "p", "render", "render",
        frozenset({"source_available"}), frozenset({"render_verified"}),
        "capability_gap", False, tuple(), frozenset({"render_verified"}),
    )
    result = plan_case(case, {"schema": "ignored"}, _capabilities())
    assert result.status == "capability_gap"
    assert result.missing_facts == frozenset({"render_verified"})
    assert validate_plan(case, result)["status"] == "passed"


def test_composite_case_has_no_single_label_contract() -> None:
    case = OperatingCase(
        "composition", "p", "simulate", "simulate",
        frozenset({"source_available"}), frozenset({"simulation_verified"}),
        "planned", True, ("simulate_tool",), frozenset(),
    )
    assert case.composite is True
    assert len(case.legacy_tools) == 1
    assert len(plan_case(case, {"schema": "ignored"}, _capabilities()).plan) == 3
