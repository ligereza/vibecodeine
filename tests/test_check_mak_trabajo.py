"""`tools/mak_ops/check_mak_trabajo.py` used to exit 0 no matter what.

Fixed defect: the SSH probe to the (often unreachable) MAK box could fail
outright -- connection timed out, host down, `ssh` missing -- and the tool
still `return 0`ed. The markdown it writes names the SSH exit code, but the
process exit code did not, so a caller that only checks `$?` (a script, a
cron wrapper, `check_mak_trabajo.py && do_something`) saw success for a
measurement that never happened. Same family as `flujo doctor` reporting
`airdrop pendiente: OK` for a directory that did not exist.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "tools" / "mak_ops" / "check_mak_trabajo.py"
    spec = importlib.util.spec_from_file_location("check_mak_trabajo", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_completed(returncode: int, stdout: str = "", stderr: str = ""):
    return type("Completed", (), {
        "returncode": returncode, "stdout": stdout, "stderr": stderr})()


def test_dead_ssh_leg_exits_nonzero_not_zero(tmp_path, monkeypatch):
    module = _load()
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: _fake_completed(
            255, "", "ssh: connect to host 192.168.50.2 port 22: "
                     "Connection timed out\n"))
    out = tmp_path / "report.md"
    monkeypatch.setattr("sys.argv", ["check_mak_trabajo.py", "--output", str(out)])

    exit_code = module.main()

    assert exit_code != 0, "a dead SSH leg must not report success"
    assert "255" in out.read_text(encoding="utf-8"), (
        "the ssh exit code is still named in the report")


def test_successful_ssh_leg_exits_zero(tmp_path, monkeypatch):
    module = _load()
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: _fake_completed(0, "@@ STATE @@\nMISSING\n", ""))
    out = tmp_path / "report.md"
    monkeypatch.setattr("sys.argv", ["check_mak_trabajo.py", "--output", str(out)])

    assert module.main() == 0
