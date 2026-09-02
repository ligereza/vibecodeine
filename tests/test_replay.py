"""Tests for the versioned MAK replay/holdout contract."""

from __future__ import annotations

import copy
import json

import pytest
from integration_paths import MAK_ROOT

from flujo.knowledge.replay import (
    ReplaySuiteError,
    evaluate_predictions,
    load_replay_suite,
    validate_replay_suite,
)


def test_core_replay_suite_is_traceable_and_split_independent():
    suite = load_replay_suite(
        "context/learning/replay_suite_v1.json",
        source_root=MAK_ROOT,
    )
    assert suite["splits"] == {"replay": 2, "holdout": 2}
    assert suite["groups"] == 4
    assert len(suite["fingerprint"]) == 64


def test_replay_suite_rejects_group_leakage_and_fingerprint_drift():
    suite = {
        "schema": "mak-replay-suite-v1",
        "suite_id": "fixture",
        "cases": [
            {"case_id": "a", "group_id": "same", "split": "replay", "source_refs": ["a"], "validator": {"kind": "x"}, "expected": {"status": "passed"}},
            {"case_id": "b", "group_id": "same", "split": "holdout", "source_refs": ["b"], "validator": {"kind": "x"}, "expected": {"status": "passed"}},
        ],
    }
    with pytest.raises(ReplaySuiteError, match="group_leaks_split"):
        validate_replay_suite(suite)

    clean = copy.deepcopy(suite)
    clean["cases"][1]["group_id"] = "other"
    clean["fingerprint"] = "wrong"
    with pytest.raises(ReplaySuiteError, match="fingerprint_mismatch"):
        validate_replay_suite(clean)


def test_evaluation_distinguishes_abstention_and_failure_without_promotion():
    suite = load_replay_suite(
        "context/learning/replay_suite_v1.json", source_root=MAK_ROOT)
    passed = {case["case_id"]: "passed" for case in suite["cases"]}
    report = evaluate_predictions(suite, passed)
    assert report["status"] == "passed"
    assert report["accuracy"] == 1.0
    assert report["by_split"]["holdout"]["accuracy"] == 1.0

    partial = evaluate_predictions(suite, {suite["cases"][0]["case_id"]: "failed"})
    assert partial["status"] == "abstained"
    assert partial["missing"] == 3
