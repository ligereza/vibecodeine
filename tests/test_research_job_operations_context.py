import pytest

from flujo.knowledge.research_job_operations_context import (
    build_research_job_operations_context,
    validate_research_job_operations_context,
)


pytestmark = pytest.mark.mak


def _payload():
    sha = "e4074504ce859a92225c040b8bce6732ea7ac6eee0dc4f01bace90c82e59d18a"
    source_sha = "d09cb1c902e51e1510db0c7d7017861789eb1c3dbdf0a0841d2690d680811f70"
    common = {"input_sha256": sha}
    return build_research_job_operations_context(
        3,
        {"status": "extracted", "next_process": "normalize"},
        {**common, "human_attestation": {"present": False}, "normalization_allowed": False},
        {**common, "job_id": 3},
        {**common, "dry_run": {"database_rows_created": 0}, "execution": {"attempted": False, "external_calls": 0}},
        {**common, "ready_for_attestation": False},
        {**common, "source_review_sha256": source_sha, "ready_for_attestation": False, "unknown_or_pending": 2, "conflicts": 1},
        {**common, "legal_conclusion": False},
        {"available": True, "policy": {"status": "candidate"}},
        generated_at="test",
    )


def test_job_context_separates_state_gates_and_execution():
    payload = _payload()
    assert validate_research_job_operations_context(payload)
    assert payload["job_id"] == 3
    assert payload["observed_job"] == {"status": "extracted", "next_process": "normalize"}
    assert payload["recovery"]["normalization_allowed"] is False
    assert payload["execution"] == {"attempted": False, "external_calls": 0, "database_rows_created": 0, "state_advance": False}
    assert payload["license_gate"]["legal_conclusion"] is False
    assert payload["learning"]["learning_demonstrated"] is False


def test_hash_drift_between_gates_is_rejected():
    sha = "e4074504ce859a92225c040b8bce6732ea7ac6eee0dc4f01bace90c82e59d18a"
    with pytest.raises(ValueError, match="input_sha256_mismatch"):
        build_research_job_operations_context(
            3,
            {"status": "extracted", "next_process": "normalize"},
            {"input_sha256": sha, "human_attestation": {"present": False}, "normalization_allowed": False},
            {"input_sha256": "0" * 64},
            {"input_sha256": sha, "dry_run": {}, "execution": {}},
            {"input_sha256": sha},
            {"input_sha256": sha, "source_review_sha256": "d09cb1c902e51e1510db0c7d7017861789eb1c3dbdf0a0841d2690d680811f70"},
            {"input_sha256": sha},
            {"policy": {"status": "candidate"}},
            generated_at="test",
        )
