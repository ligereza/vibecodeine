"""Tests for the unified, read-only MAK status envelope."""

from __future__ import annotations

from pathlib import Path

from flujo.knowledge.project_api import operational_status
from flujo.knowledge.project_ir import LearningStore, build_project_ir
from flujo.knowledge.system_status import _provider_source_root, system_status


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


def test_system_status_keeps_component_contract_when_provider_box_is_absent(tmp_path: Path) -> None:
    result = system_status(
        tmp_path / "missing.sqlite",
        repo_root=tmp_path,
        physical_root=tmp_path,
    )

    assert result["schema"] == "mak-system-status-v1"
    assert all("severity" in component for component in result["components"].values())
    assert result["components"]["providers"]["severity"] == "attention"


def test_system_status_resolves_provider_box_from_physical_adapter_root(tmp_path: Path) -> None:
    repo = tmp_path / "flujo"
    physical = tmp_path / "mak"
    provider = physical / "cultura" / "mak_plataforma" / "providers.py"
    provider.parent.mkdir(parents=True)
    provider.write_text("# fixture provider registry\n", encoding="utf-8")

    assert _provider_source_root(repo, physical) == physical


def test_flujo_adapter_resolves_physical_learning_authority(tmp_path: Path, monkeypatch) -> None:
    from flujo.web import hub

    repo = tmp_path / "flujo"
    local = repo / "data" / "mak_knowledge.db"
    physical = tmp_path / "data" / "mak_knowledge.db"
    local.parent.mkdir(parents=True)
    physical.parent.mkdir(parents=True)
    local.write_bytes(b"")
    physical.write_bytes(b"authoritative")
    monkeypatch.delenv("MAK_LEARNING_DB", raising=False)
    monkeypatch.setattr(hub, "repo_root", lambda: repo)

    assert hub.project_learning_db() == physical
