"""Static ratchets for the Windows launchers and MAK mirror tooling."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_windows_launchers_anchor_the_repo_and_use_current_app_command():
    batch = _text("launch-flujo.bat").lower()
    powershell = _text("launch-flujo.ps1").lower()
    opener = _text("abrir_hub.bat").lower()

    assert 'cd /d "%~dp0"' in batch
    assert "py -m flujo app --desktop" in batch
    assert "set-location $psscriptroot" in powershell
    assert "-m flujo app --desktop" in powershell
    assert 'call "%~dp0launch-flujo.bat"' in opener
    assert "--open" not in opener


def test_installer_uses_editable_install_instead_of_copying_source_trees():
    installer = _text("instalar.bat").lower()
    assert 'pip install -e ".[dev]"' in installer
    assert "xcopy" not in installer
    assert "py -m flujo doctor" in installer


def _load_mirror_module():
    path = ROOT / "tools" / "mak_ops" / "check_mak_mirror.py"
    spec = importlib.util.spec_from_file_location("check_mak_mirror", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mak_mirror_check_covers_curatoria_and_fails_on_mismatch(tmp_path, monkeypatch):
    module = _load_mirror_module()
    assert "mak_curatoria" in module.FILES
    assert {"percepcion.py", "curatoria_guardia.sh", "extraccion_db.py"}.issubset(
        module.FILES["mak_curatoria"])

    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(module, "remote_hashes", lambda: ({}, 0, ""))
    monkeypatch.setattr("sys.argv", ["check_mak_mirror.py", "--output", str(tmp_path / "report.md")])
    assert module.main() == 1


def test_repair_script_installs_fourth_mirror():
    repair = _text("tools/mak_ops/repair_mak_sync.py")
    assert "cultura/mak_curatoria/." in repair
    assert '"$HOME/curatoria/"' in repair
