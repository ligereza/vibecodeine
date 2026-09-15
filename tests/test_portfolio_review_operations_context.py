import pytest

from flujo.knowledge.portfolio_review_operations_context import (
    build_portfolio_review_operations_context,
    validate_portfolio_review_operations_context,
)


pytestmark = pytest.mark.mak


def _payload():
    inbox = {"schema": "faro-portfolio-inbox-v1", "id": "item-1.jpg", "fecha": "2026-09-13", "tipo_contenido": "image", "status": "inbox", "selection": "pendiente", "classification": {"triage": "record"}}
    audit = {"item": {"source_id": "item-1.jpg", "current": {"selection": "pendiente", "classification": {"triage": "record"}, "decision_draft": {"status": "committed", "owner": "human"}}, "timeline_total": 2}, "contract": {}}
    direction = {"schema": "mak-portfolio-direction-context-v1", "frame": {"vision": {"state": "bounded_observation", "source_hash": "sha256:" + "1" * 64}, "order": {"state": "structural_order_only"}, "culture_computation": {"state": "observed_practice_context"}, "instrument": {"state": "vizz_measurement_refused", "measurement_status": "unknown_measurement_refused", "triangulation_attempted": False, "depth_result_present": False, "measurement_claim_allowed": False}}}
    return build_portfolio_review_operations_context("item-1.jpg", inbox, audit, direction, {"counts": {"selections": 2}}, {"items": [], "public_promotion": False}, {"available": True, "policy": {"status": "candidate"}}, generated_at="test")


def test_item_context_keeps_human_history_separate_from_execution():
    payload = _payload()
    assert validate_portfolio_review_operations_context(payload)
    assert payload["source"]["asset_path_exposed"] is False
    assert payload["decisions"]["actor"] == "human"
    assert payload["execution"] == {"portfolio_task_executed": False, "render_preview_executed": False, "publication": False}
    assert payload["learning"]["learning_demonstrated"] is False
    assert payload["vizz"]["measurement_claim_allowed"] is False


def test_item_context_rejects_public_promotion():
    payload = _payload()
    payload["candidate"]["public_promotion"] = True
    with pytest.raises(ValueError, match="portfolio_review_operations_candidate_invalid"):
        validate_portfolio_review_operations_context(payload)


def test_item_context_rejects_local_path_in_hash():
    payload = _payload()
    payload["source"]["source_hash"] = "sha256:/home/mak/private"
    with pytest.raises(ValueError, match="portfolio_review_operations_source_hash_invalid|source.source_hash_invalid"):
        validate_portfolio_review_operations_context(payload)


def test_item_context_keeps_external_candidate_unpromoted():
    payload = _payload()
    payload["candidate"] = {"present": True, "status": "candidate_present", "public_promotion": False}
    assert validate_portfolio_review_operations_context(payload)
