from flujo.knowledge.learning_read_only_context import (
    build_learning_read_only_context,
    validate_learning_read_only_context,
)


def _inputs():
    return {
        "schema": "mak-system-status-v1",
        "status": "attention",
    }, {
        "available": True,
        "database": "mak_knowledge.db",
        "policy": {
            "schema": "mak-learning-policy-v1",
            "status": "candidate",
            "reason": "holdout_gate_passed",
            "eligible_examples": 12,
            "excluded": {"episode_not_verified": 19, "missing_route_label": 67},
            "recordable": True,
            "evaluation": {"train_count": 6, "holdout_count": 6, "holdout_accuracy": 1.0, "holdout_baseline": 0.833333},
        },
        "projects": {"active": 37, "review_required": 6},
        "episodes": {"verified": 76, "needs_evidence": 16},
        "episodes_open": {"needs_evidence": 14},
        "rules": {"candidate": 1},
    }


def test_learning_context_separates_evaluation_from_learning():
    payload = build_learning_read_only_context(*_inputs(), generated_at="fixture")
    assert validate_learning_read_only_context(payload)
    assert payload["policy"]["holdout_accuracy"] == 1.0
    assert payload["boundary"]["evaluation_is_not_learning"] is True
    assert payload["boundary"]["learning_demonstrated"] is False
    assert payload["control"]["promotion"] == "none"


def test_learning_context_rejects_promoted_candidate():
    payload = build_learning_read_only_context(*_inputs())
    payload["policy"]["status"] = "promoted"
    try:
        validate_learning_read_only_context(payload)
    except ValueError as exc:
        assert str(exc) == "learning_context_policy_invalid"
    else:
        raise AssertionError("promoted policy was accepted")


def test_learning_context_rejects_learning_claim():
    payload = build_learning_read_only_context(*_inputs())
    payload["boundary"]["learning_demonstrated"] = True
    try:
        validate_learning_read_only_context(payload)
    except ValueError as exc:
        assert str(exc) == "learning_context_boundary_invalid"
    else:
        raise AssertionError("learning claim was accepted")
