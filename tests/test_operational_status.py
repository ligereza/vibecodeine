"""Tests for the unified, read-only MAK status envelope."""

from __future__ import annotations

from pathlib import Path

from flujo.knowledge.project_api import operational_status
from flujo.knowledge.project_ir import LearningStore, build_project_ir


def test_operational_status_is_read_only_and_surfaces_next_actions(tmp_path: Path) -> None:
    database = tmp_path / "learning.sqlite"
    store = LearningStore(database)
    project = build_project_ir(
        project_id="status-demo",
        title="Status demo",
        source_root=tmp_path,
        state="review_required",
        unknowns=["evidence"],
    )
    store.save_project(project)
    store.record_episode(
        project_id=project["project_id"],
        objective="bounded probe",
        phase="gate",
        action={"tool": "project_router"},
        observation={},
        outcome={"decision": "abstain"},
        validation={"status": "needs_evidence"},
        status="needs_evidence",
        episode_id="episode-status-demo",
    )
    before = (database.stat().st_size, database.stat().st_mtime_ns)

    result = operational_status(database, repo_root=tmp_path)

    after = (database.stat().st_size, database.stat().st_mtime_ns)
    assert before == after
    assert result["schema"] == "mak-operational-status-v1"
    assert result["read_only"] is True
    assert result["status"] == "attention"
    assert result["counts"]["attention"] >= 2
    ids = {item["id"] for item in result["attention"]}
    assert "projects:review_required" in ids
    assert "episodes:needs_evidence" in ids
    assert result["next_actions"]


def test_operational_status_reports_missing_ledger_without_writing(tmp_path: Path) -> None:
    database = tmp_path / "missing.sqlite"

    result = operational_status(database, repo_root=tmp_path)

    assert result["status"] == "unknown"
    assert result["read_only"] is True
    assert result["attention"][0]["id"] == "learning_ledger"
    assert not database.exists()
