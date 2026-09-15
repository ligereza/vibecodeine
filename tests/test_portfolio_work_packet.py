import pytest

from flujo.knowledge.portfolio_direction_context import build_portfolio_direction_context
from flujo.knowledge.portfolio_work_packet import (
    build_portfolio_work_packet,
    validate_portfolio_work_packet,
)
from test_portfolio_direction_context import _surfaces


pytestmark = pytest.mark.flujo


def test_work_packet_turns_direction_layers_into_non_executing_tasks():
    packet = build_portfolio_work_packet(build_portfolio_direction_context(*_surfaces()))

    assert validate_portfolio_work_packet(packet) is True
    assert [task["id"] for task in packet["tasks"]] == [
        "archive_orientation", "structural_order", "practice_relation", "vizz_calibration"
    ]
    assert packet["execution"] == {
        "task_count": 4,
        "executed_task_count": 0,
        "execution_allowed": False,
        "state_advance": False,
    }
    assert packet["control"]["selection_effect"] == "none"
    assert packet["control"]["promotion"] == "none"
    assert packet["control"]["normalize_execution"] is False
    assert packet["control"]["measurement_execution"] is False
    assert packet["provenance"]["task_execution"] is False


def test_work_packet_rejects_execution_enablement():
    packet = build_portfolio_work_packet(build_portfolio_direction_context(*_surfaces()))
    packet["tasks"][0]["execution_allowed"] = True

    with pytest.raises(ValueError, match="task_execution"):
        validate_portfolio_work_packet(packet)
