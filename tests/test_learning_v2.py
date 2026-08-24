"""Tests for the durable MAK Learn v2 control/evaluation surface."""

from __future__ import annotations

import sqlite3

import pytest

from flujo.knowledge.project_ir import (
    LearningStore,
    ProjectIRError,
    build_project_ir,
    inventory_source,
)


def _store(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "scene.blend").write_bytes(b"blend-fixture")
    store = LearningStore(tmp_path / "learning.sqlite")
    project = build_project_ir(
        project_id="learn-v2-demo",
        title="Learn v2 demo",
        source_root=root,
        artifacts=inventory_source(root),
        state="candidate",
    )
    store.save_project(project)
    return store


def test_run_events_are_append_only_and_idempotent(tmp_path):
    store = _store(tmp_path)
    event = dict(
        project_id="learn-v2-demo",
        event_type="director.propose",
        state="proposed",
        payload={"candidate_actions": [{"tool": "read_only_probe"}]},
        source_snapshot_hash="sha256:source",
        code_commit="abc1234",
        tool_versions={"python": "3.12", "blender": "4.x"},
        event_id="event-demo",
    )
    assert store.append_run_event(**event) == "event-demo"
    assert store.append_run_event(**event) == "event-demo"

    with sqlite3.connect(store.database) as con:
        assert con.execute("SELECT COUNT(*) FROM mak_run_events").fetchone()[0] == 1

    with pytest.raises(ProjectIRError, match="run_event_id_conflict"):
        store.append_run_event(**{**event, "payload": {"candidate_actions": []}})

    with sqlite3.connect(store.database) as con:
        with pytest.raises(sqlite3.IntegrityError, match="mak_run_events_append_only"):
            con.execute("UPDATE mak_run_events SET state='recorded' WHERE event_id='event-demo'")
        with pytest.raises(sqlite3.IntegrityError, match="mak_run_events_append_only"):
            con.execute("DELETE FROM mak_run_events WHERE event_id='event-demo'")


def test_run_event_requires_versioned_provenance(tmp_path):
    store = _store(tmp_path)
    with pytest.raises(ProjectIRError, match="source_snapshot_hash"):
        store.append_run_event(
            project_id="learn-v2-demo", event_type="director.inspect", state="running",
            payload={}, source_snapshot_hash="", code_commit="abc1234",
            tool_versions={},
        )
    with pytest.raises(ProjectIRError, match="code_commit"):
        store.append_run_event(
            project_id="learn-v2-demo", event_type="director.inspect", state="running",
            payload={}, source_snapshot_hash="sha256:source", code_commit="",
            tool_versions={},
        )


def test_evaluation_is_durable_but_never_promotes_a_rule(tmp_path):
    store = _store(tmp_path)
    rule_id = store.upsert_rule(
        trigger={"format_family": "3d"},
        action={"tool": "read_only_probe"},
    )
    evaluation_id = store.record_learning_evaluation(
        target_kind="semantic_rule",
        target_id=rule_id,
        dataset_fingerprint="sha256:holdout",
        split_kind="holdout",
        status="passed",
        metrics={"accuracy": 1.0, "holdout_count": 2},
        evidence=[{"path": "tests/test_learning_v2.py", "status": "passed"}],
        candidate_policy_id="policy-candidate-1",
        evaluation_id="evaluation-demo",
    )
    assert evaluation_id == "evaluation-demo"
    assert store.rules(status="candidate")[0]["rule_id"] == rule_id
    with sqlite3.connect(store.database) as con:
        row = con.execute(
            "SELECT status,split_kind,dataset_fingerprint FROM learning_evaluations WHERE evaluation_id=?",
            (evaluation_id,),
        ).fetchone()
    assert row == ("passed", "holdout", "sha256:holdout")
    with sqlite3.connect(store.database) as con:
        with pytest.raises(sqlite3.IntegrityError, match="learning_evaluations_append_only"):
            con.execute("UPDATE learning_evaluations SET status='failed' WHERE evaluation_id=?", (evaluation_id,))
        with pytest.raises(sqlite3.IntegrityError, match="learning_evaluations_append_only"):
            con.execute("DELETE FROM learning_evaluations WHERE evaluation_id=?", (evaluation_id,))


def test_evaluation_rejects_untracked_dataset(tmp_path):
    store = _store(tmp_path)
    with pytest.raises(ProjectIRError, match="dataset_fingerprint"):
        store.record_learning_evaluation(
            target_kind="policy", target_id="candidate", dataset_fingerprint="",
            split_kind="replay", status="abstained", metrics={},
        )
