"""Tests offline de commit_ai (sin llamadas a Gemini, sin commitear nada)."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "vibo_voz"))
import commit_ai  # noqa: E402


def _repo_con_diff(tmp_path, contenido):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "f.txt").write_text(contenido, encoding="utf-8")
    subprocess.run(["git", "add", "f.txt"], cwd=tmp_path, check=True)
    return tmp_path


def test_diff_staged_scrubbea_secretos(tmp_path):
    # clave FALSA armada por concatenacion: el archivo de test no debe
    # contener el patron contiguo o el hook pre-commit del repo lo bloquea
    clave_falsa = "AIza" + "SyABCDEFGHIJKLMNOPQRSTUV123456"
    repo = _repo_con_diff(tmp_path, f"config\napi_key = '{clave_falsa}'\n")
    diff = commit_ai.diff_staged(str(repo))
    assert clave_falsa not in diff
    assert "[REDACTADO]" in diff


def test_diff_staged_vacio_sin_stage(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    assert commit_ai.diff_staged(str(tmp_path)) == ""


def test_diff_staged_trunca(tmp_path, monkeypatch):
    monkeypatch.setattr(commit_ai, "_MAX_DIFF", 100)
    repo = _repo_con_diff(tmp_path, "x" * 5000)
    diff = commit_ai.diff_staged(str(repo))
    assert len(diff) < 200
    assert "truncado" in diff


def test_armar_prompt():
    p = commit_ai.armar_prompt("DIFFCONTENT")
    assert "Conventional Commits" in p and p.endswith("DIFFCONTENT")
    ppr = commit_ai.armar_prompt("DIFFCONTENT", pr=True)
    assert "Pull Request" in ppr and ppr.endswith("DIFFCONTENT")


def test_pedir_mensaje_sin_keys(monkeypatch):
    for var in list(commit_ai.os.environ):
        if var.startswith("GEMINI_API_KEY"):
            monkeypatch.delenv(var, raising=False)
    with pytest.raises(SystemExit):
        commit_ai.pedir_mensaje("x")
