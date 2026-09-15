import pytest

from flujo.knowledge.portfolio_review_cultura_research_context import (
    build_portfolio_review_cultura_research_context,
    validate_portfolio_review_cultura_research_context,
)


pytestmark = pytest.mark.mak


def _payload():
    return build_portfolio_review_cultura_research_context(
        "item-1.jpg",
        {"source": {"source_hash": "sha256:" + "1" * 64}, "candidate": {"present": False}, "decisions": {"current": {"selection": "pendiente"}, "history_count": 2}},
        {"schema": "mak-cultura-research-read-only-context-v1", "generated_at": "test", "cultura": {"offline": {"offline_first": True}}},
        {"schema": "mak-research-operations-context-v1", "input_sha256": "2" * 64},
        generated_at="test",
    )


def test_bridge_remains_unbound_and_read_only():
    payload = _payload()
    assert validate_portfolio_review_cultura_research_context(payload)
    assert payload["origin_guard"] == {"status": "unbound", "join_basis": "explicit_item_id_only", "typed_relation_present": False, "selection_effect": "none"}
    assert payload["cultura"]["scope"] == "offline_first"
    assert payload["research"]["job_state_is_not_execution"] is True
    assert payload["control"]["learning_demonstrated"] is False


def test_bridge_rejects_typed_relation_drift():
    payload = _payload()
    payload["origin_guard"]["typed_relation_present"] = True
    with pytest.raises(ValueError, match="portfolio_review_cultura_research_origin_invalid"):
        validate_portfolio_review_cultura_research_context(payload)
