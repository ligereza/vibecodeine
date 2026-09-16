from __future__ import annotations

from pathlib import Path

from tools.contexto_repo import _live_context


def test_live_context_returns_git_independent_python_facts(tmp_path: Path) -> None:
    (tmp_path / "demo.py").write_text(
        "import sqlite3\n\n"
        "def run():\n"
        "    \"\"\"Open a temporary database.\"\"\"\n"
        "    return sqlite3.connect(':memory:')\n",
        encoding="utf-8",
    )

    payload = _live_context(tmp_path, "run")

    assert payload["schema"] == "mak-repo-context-v1"
    assert payload["git"]["available"] is False
    python = payload["python"]
    assert python["available"] is True
    assert python["summary"]["python_files"] == 1
    assert python["summary"]["symbols"] == 1
    assert python["summary"]["syntax_errors"] == 0
    assert python["files"][0]["symbols"][0]["name"] == "run"
    assert python["files"][0]["symbols"][0]["purpose"] == "Open a temporary database."
    assert python["files"][0]["effects"] == ["database"]
    assert payload["query"]["candidate_paths"] == ["demo.py"]
