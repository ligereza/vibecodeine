from flujo.departments import cultura_capabilities, cultura_opportunity_gate, cultura_sources
from flujo.knowledge.cultura_research_read_only_context import (
    build_cultura_research_read_only_context,
    validate_cultura_research_read_only_context,
)


def _context():
    return build_cultura_research_read_only_context(
        cultura_sources("/home/mak"),
        cultura_capabilities("/home/mak"),
        cultura_opportunity_gate("/home/mak"),
        {"adapters": [{"slug": "fixture"}], "jobs": 1},
        {"jobs": [{"status": "planned"}]},
        generated_at="fixture",
    )


def test_cultura_research_context_preserves_gates():
    payload = _context()
    assert validate_cultura_research_read_only_context(payload)
    assert payload["boundary"]["cultura_is_offline_first"] is True
    assert payload["boundary"]["live_scrape_requires_explicit_gate"] is True
    assert payload["boundary"]["proposal_is_draft_until_review"] is True
    assert payload["boundary"]["semantic_claim"] is False
    assert payload["control"]["network"] is False


def test_cultura_research_context_counts_job_states_without_learning_claim():
    payload = _context()
    assert payload["cultura"]["entry_count"] >= 0
    assert payload["research"]["adapter_count"] == 1
    assert payload["research"]["job_status_counts"] == {"planned": 1}
    assert payload["boundary"]["job_state_is_not_learning"] is True


def test_cultura_research_context_rejects_open_network_policy():
    payload = _context()
    payload["cultura"]["provider_policy"]["network"] = "called"
    try:
        validate_cultura_research_read_only_context(payload)
    except ValueError as exc:
        assert str(exc) == "cultura_research_context_provider_policy_invalid"
    else:
        raise AssertionError("open network policy was accepted")
