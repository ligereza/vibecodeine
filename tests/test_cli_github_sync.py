"""Tests for `flujo github-sync`.

Includes a documented defect (see
test_status_on_a_broken_git_falsely_claims_a_clean_tree below): the doctrine
in this repo is that absence must be named, never read as health -- `flujo
doctor` had exactly this shape of bug with a directory check that always said
OK. `--status` has the same shape: when `git status --short` itself fails,
its empty stdout is indistinguishable from "no changes" and the command prints
"Working tree limpio" -- claiming a clean tree when the check never ran. This
test pins the CURRENT behavior as a known defect, not as something desired;
fixing it belongs to src/, which is out of scope for this suite.
"""
from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from flujo.cli import app
import flujo.paths

runner = CliRunner()


def _completed(returncode: int, stdout: str = "", stderr: str = ""):
    return type("Completed", (), {"returncode": returncode, "stdout": stdout, "stderr": stderr})()


def _fake_run_factory(responses: dict):
    """responses maps a git subcommand (args[1]) to a _completed(...)."""
    def fake_run(cmd, cwd=None, text=True, capture_output=True, check=False, encoding=None, errors=None):
        sub = cmd[1] if len(cmd) > 1 else ""
        return responses.get(sub, _completed(0, "", ""))
    return fake_run


def test_status_reports_dirty_tree_when_there_are_local_changes(monkeypatch):
    monkeypatch.setattr("subprocess.run", _fake_run_factory({
        "rev-parse": _completed(0, "main\n"),
        "remote": _completed(0, "https://example.invalid/repo.git\n"),
        "status": _completed(0, " M archivo.py\n"),
    }))
    result = runner.invoke(app, ["github-sync", "--status"])
    assert result.exit_code == 0
    assert "Cambios locales" in result.output
    assert "M archivo.py" in result.output


def test_status_on_a_broken_git_falsely_claims_a_clean_tree(monkeypatch, tmp_path: Path):
    """KNOWN DEFECT, documented not endorsed: rev-parse and status both fail
    (e.g. run from a directory that is not a git repo at all), and the
    command still prints '(check) Working tree limpio' plus 'Estado de
    GitHub preparado' with exit code 0 -- the failure of the check itself is
    never named. This is the same class of bug already found in `flujo
    doctor` (a directory-existence check that always read OK)."""
    monkeypatch.setattr("flujo.paths.repo_root", lambda: tmp_path)
    monkeypatch.setattr("subprocess.run", _fake_run_factory({
        "rev-parse": _completed(128, "", "fatal: not a git repository\n"),
        "remote": _completed(128, "", "fatal: not a git repository\n"),
        "status": _completed(128, "", "fatal: not a git repository\n"),
    }))
    result = runner.invoke(app, ["github-sync", "--status"])
    assert result.exit_code == 0, (
        "the command exits 0 even though every git call failed -- that is "
        "the defect, pinned here so a fix is a visible behavior change")
    assert "Working tree limpio" in result.output, (
        "empty stdout from a FAILED `git status` reads as 'no changes'; a "
        "fixed version should say the check could not run, not that the "
        "tree is clean")


def test_push_with_nothing_to_commit_still_attempts_the_push(monkeypatch):
    monkeypatch.setattr("subprocess.run", _fake_run_factory({
        "rev-parse": _completed(0, "main\n"),
        "remote": _completed(0, "https://example.invalid/repo.git\n"),
        "status": _completed(0, ""),
        "push": _completed(0, "Everything up-to-date\n"),
    }))
    result = runner.invoke(app, ["github-sync", "--push"])
    assert result.exit_code == 0
    assert "No hay cambios para commitear" in result.output
    assert "Sincronizado con GitHub" in result.output


def test_push_reports_a_commit_failure_and_exits_nonzero(monkeypatch):
    monkeypatch.setattr("subprocess.run", _fake_run_factory({
        "rev-parse": _completed(0, "main\n"),
        "remote": _completed(0, "https://example.invalid/repo.git\n"),
        "status": _completed(0, " M archivo.py\n"),
        "add": _completed(0, ""),
        "commit": _completed(1, "", "pre-commit hook failed\n"),
    }))
    result = runner.invoke(app, ["github-sync", "--push"])
    assert result.exit_code == 1
    assert "pre-commit hook failed" in result.output


def test_push_reports_a_push_failure_and_exits_nonzero(monkeypatch):
    monkeypatch.setattr("subprocess.run", _fake_run_factory({
        "rev-parse": _completed(0, "main\n"),
        "remote": _completed(0, "https://example.invalid/repo.git\n"),
        "status": _completed(0, ""),
        "push": _completed(1, "", "remote rejected\n"),
    }))
    result = runner.invoke(app, ["github-sync", "--push"])
    assert result.exit_code == 1
    assert "remote rejected" in result.output


def test_status_without_a_remote_warns_instead_of_crashing(monkeypatch):
    monkeypatch.setattr("subprocess.run", _fake_run_factory({
        "rev-parse": _completed(0, "main\n"),
        "remote": _completed(128, "", "No such remote 'origin'\n"),
        "status": _completed(0, ""),
    }))
    result = runner.invoke(app, ["github-sync", "--status"])
    assert result.exit_code == 0
    assert "No hay remote" in result.output
