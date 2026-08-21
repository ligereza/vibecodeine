"""Read-only coverage for the unified MAK consumer status."""

from __future__ import annotations

import json
import os
from pathlib import Path

from flujo.knowledge import system_status as status_module
from flujo.knowledge.runtime_tools import resolve_blender


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_resolve_blender_uses_repo_sibling_without_path_or_install(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "flujo"
    binary = tmp_path / "blender" / "blender"
    _touch(binary, "fixture")
    binary.chmod(0o755)
    monkeypatch.delenv("BLENDER_EXE", raising=False)
    monkeypatch.setattr("flujo.knowledge.runtime_tools.shutil.which", lambda _: None)

    assert resolve_blender(root) == binary.resolve()


def test_system_status_is_read_only_and_redacts_provider_values(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "flujo"
    physical = tmp_path / "mak"
    for relative in (
        "agents.md",
        "cultura/mak_plataforma/hub.py",
        "src/flujo/knowledge/project_api.py",
        "web/package.json",
        ".github/workflows/issue_descarga_ig.yml",
    ):
        _touch(repo / relative, "fixture")
    for relative in (
        "plataforma/hub.py",
        "research/interfaz.py",
        "codex/interfaz_codex.py",
        "searxng/settings.yml",
        "actions-runner/placeholder",
        "RD/AUTOMATIZACION/RD.blend",
    ):
        _touch(physical / relative, "fixture")
    (physical / "portfolio_media").mkdir(parents=True)
    secret = "do-not-return-this-value"
    (physical / "research" / "research.env").write_text(
        f"GROQ_API_KEY={secret}\n", encoding="utf-8"
    )

    monkeypatch.setattr(status_module, "_listener", lambda port: {"host": "127.0.0.1", "port": port, "reachable": True})
    monkeypatch.setattr(status_module, "_process_snapshot", lambda tokens: {"running": True, "count": 1})
    fake_blender = physical / "blender" / "blender"
    _touch(fake_blender, "fixture")
    fake_blender.chmod(0o755)
    monkeypatch.setattr(status_module, "resolve_blender", lambda root: fake_blender)

    before = sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))
    result = status_module.system_status(
        tmp_path / "missing.sqlite", repo_root=repo, physical_root=physical
    )
    after = sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))

    assert result["schema"] == "mak-system-status-v1"
    assert result["read_only"] is True
    assert result["components"]["hub"]["status"] == "ready"
    assert result["components"]["render"]["status"] in {"ready", "active"}
    assert result["components"]["lanes"]["status"] == "attention"
    assert result["components"]["providers"]["evidence"]["configured"] >= 1
    encoded = json.dumps(result, ensure_ascii=False)
    assert secret not in encoded
    assert before == after


def test_lane_registry_is_reported_without_promotion() -> None:
    repo = Path(__file__).resolve().parents[1]
    result = status_module._lane_registry_component(repo)

    assert result["status"] == "ready"
    assert result["read_only"] is True
    assert result["evidence"]["valid"] is True
    assert result["evidence"]["summary"]["lane_count"] == 19
    assert result["evidence"]["summary"]["states"]["proposal"] == 11
