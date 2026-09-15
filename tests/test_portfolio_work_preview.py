import pytest

from flujo.knowledge.portfolio_direction_context import build_portfolio_direction_context
from flujo.knowledge.portfolio_work_packet import build_portfolio_work_packet
from flujo.knowledge.portfolio_work_preview import (
    build_portfolio_work_preview,
    validate_portfolio_work_preview,
)
from test_portfolio_direction_context import _surfaces


pytestmark = pytest.mark.flujo


def test_work_preview_binds_project_context_without_typed_relation():
    direction = build_portfolio_direction_context(*_surfaces())
    packet = build_portfolio_work_packet(direction, project_id="project-5047cc3a2269b5031460")
    preview = build_portfolio_work_preview(packet, "practice_relation")

    assert validate_portfolio_work_preview(preview) is True
    assert preview["source"]["project_id"] == "project-5047cc3a2269b5031460"
    assert preview["source"]["relation_status"] == "needs_evidence"
    assert preview["provenance"]["typed_relation_present"] is False
    assert preview["control"]["selection_effect"] == "context_only"
    assert preview["control"]["normalize_execution"] is False
    assert preview["control"]["measurement_execution"] is False


def test_work_preview_rejects_typed_relation_in_provenance():
    direction = build_portfolio_direction_context(*_surfaces())
    packet = build_portfolio_work_packet(direction, project_id="project-5047cc3a2269b5031460")
    preview = build_portfolio_work_preview(packet, "archive_orientation")
    preview["provenance"]["typed_relation_present"] = True

    with pytest.raises(ValueError, match="provenance"):
        validate_portfolio_work_preview(preview)
