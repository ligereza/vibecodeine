from pathlib import Path

from flujo.index.code_index import build_index, make_brief


def _files(index):
    return {item["path"]: item for item in index["files"]}


def test_code_index_extracts_structure_effects_and_consumers(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("from .worker import run\n", encoding="utf-8")
    (package / "worker.py").write_text(
        "import sqlite3\n"
        "from pathlib import Path\n\n"
        "def run():\n"
        "    Path('out.txt').write_text('ok')\n"
        "    return sqlite3.connect('data.db')\n\n"
        "if __name__ == '__main__':\n"
        "    run()\n",
        encoding="utf-8",
    )
    (package / "consumer.py").write_text(
        "from .worker import run\n\n"
        "def consume():\n"
        "    return run()\n",
        encoding="utf-8",
    )

    index = build_index(tmp_path)
    files = _files(index)
    worker = files["pkg/worker.py"]

    assert index["schema"] == "mak-code-structure-v1"
    assert index["summary"]["python_files"] == 3
    assert {item["name"] for item in worker["symbols"]} == {"run"}
    assert worker["entrypoints"] == ["__main__"]
    assert "database" in worker["effects"]
    assert "filesystem_write" in worker["effects"]
    assert "pkg" in worker["imported_by"]
    assert "pkg.consumer" in worker["imported_by"]
    assert "source" not in worker

    brief = make_brief(index, "worker database")
    assert brief["schema"] == "mak-code-brief-v1"
    assert brief["source_text_included"] is False
    assert "pkg/worker.py" in brief["candidate_paths"]


def test_code_index_reports_syntax_errors_without_stopping(tmp_path):
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "ok.py").write_text("VALUE = 1\n", encoding="utf-8")

    index = build_index(tmp_path)
    files = _files(index)

    assert index["summary"]["syntax_errors"] == 1
    assert files["broken.py"]["syntax_error"]["line"] == 1
    assert files["ok.py"]["syntax_error"] is None
