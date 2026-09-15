import pytest


pytestmark = pytest.mark.mak

from flujo.knowledge.research_operations_read_only_context import (
    build_research_operations_read_only_context,
    validate_research_operations_read_only_context,
)


def _payload():
    return build_research_operations_read_only_context(
        {"available": True, "adapters": [{"slug": "research"}], "jobs": 2},
        {"available": True, "jobs": [
            {"id": 2, "status": "extracted", "next_process": "normalize", "steps": 12, "done_steps": 3},
            {"id": 1, "status": "planned", "next_process": "discover", "steps": 12, "done_steps": 0},
        ]},
        {"status": "candidate_only", "total": 10, "returned": 10, "sampled": False, "counts": {"paired_family": 9, "quarantine": 1}, "promotion": "none"},
        {"status": "candidate_only", "counts": {"rescue": 2, "review": 1}, "promotion": "none"},
        {"available": True, "policy": {"status": "candidate", "eligible_examples": 2, "evaluation": {"holdout_accuracy": 1.0, "holdout_baseline": 0.5}}},
        generated_at="test",
    )


def test_observed_jobs_are_not_execution_or_learning():
    payload = _payload()
    assert validate_research_operations_read_only_context(payload)
    assert payload["job_state_observed"]["status_counts"] == {"extracted": 1, "planned": 1}
    assert payload["recovery"] == {"verified": False, "observed_receipts": 0, "reason": "job_listing_has_no_recovery_receipt"}
    assert payload["real_execution"]["verified"] is False
    assert payload["boundary"]["learning_demonstrated"] is False


def test_candidate_promotion_drift_is_rejected():
    payload = _payload()
    payload["candidate_outputs"]["rescue"]["promotion"] = "promoted"
    with pytest.raises(ValueError, match="research_operations_rescue_invalid"):
        validate_research_operations_read_only_context(payload)


def test_execution_flag_cannot_be_opened():
    payload = _payload()
    payload["control"]["execution"] = True
    with pytest.raises(ValueError, match="research_operations_boundary_or_control_invalid"):
        validate_research_operations_read_only_context(payload)
