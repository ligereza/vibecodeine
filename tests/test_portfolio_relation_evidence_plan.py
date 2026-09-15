import pytest

from flujo.knowledge.portfolio_relation_evidence_plan import (
    build_relation_evidence_plan,
    validate_relation_evidence_plan,
)


pytestmark = pytest.mark.flujo


def _context():
    return {
        "schema": "mak-portfolio-review-context-v1",
        "available": True,
        "read_only": True,
        "project": {
            "project_id": "project-1",
            "title": "SCD",
            "state": "review_required",
            "unknowns": [
                "official_call: missing",
                "method: missing",
            ],
            "evidence": [{"kind": "application_package", "status": "observed", "source_ref": "/tmp/no-new-path"}],
        },
        "relation": {
            "status": "needs_evidence",
            "typed_relation_present": False,
            "selection_effect": "none",
            "evidence_refs": [],
        },
    }


def test_relation_plan_preserves_missing_evidence_and_no_relation():
    result = build_relation_evidence_plan(_context())

    assert validate_relation_evidence_plan(result) is True
    assert result["project"]["unknown_count"] == 2
    assert result["unresolved_count"] == 2
    assert result["requirements"][0]["expected_evidence_kind"] == "official_call_source"
    assert result["observed_evidence"][0]["reference_class"] == "local_source_reference"
    assert result["relation"]["typed_relation_present"] is False
    assert result["control"]["selection_effect"] == "none"


def test_relation_plan_rejects_typed_relation_tamper():
    result = build_relation_evidence_plan(_context())
    result["relation"]["typed_relation_present"] = True

    with pytest.raises(ValueError, match="relation"):
        validate_relation_evidence_plan(result)
