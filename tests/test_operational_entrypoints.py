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
    assert 'pip install -e ".[dev,web]"' in installer
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
    assert module.ROOT == ROOT
    assert "Path(__file__).resolve().parents[2]" in _text("tools/mak_ops/check_mak_mirror.py")
    assert "mak_curatoria" in module.FILES
    assert {"percepcion.py", "curatoria_guardia.sh", "extraccion_db.py"}.issubset(
        module.FILES["mak_curatoria"])
    assert {"interfaz.py", "memoria.py", "research_lib.py"}.issubset(
        module.FILES["mak_research"])
    assert {"pausa.py", "worker.py"}.issubset(module.FILES["mak_research"])
    assert {"interfaz_codex.py", "agente_libre.py"}.issubset(
        module.FILES["mak_codex"])
    assert "vigia.py" in module.FILES["mak_vigia"]
    assert {"energia_log.py", "mineria_rd.py"}.issubset(
        module.FILES["mak_plataforma"])
    assert {"backup.sh", "watchdog_mak.sh", "vigilar_red.py", "revisor.py"}.issubset(
        module.FILES["mak_plataforma"])
    assert {"corpus_a_micelio.py", "micelio_guardia.sh", "retencion.py", "watchdog.sh"}.issubset(
        module.FILES["mak_research"])
    assert module.FILES["mak_lenguaje"] == ["hook_barrido.py", "cron_lexicon.sh"]
    assert "vigia_guardia.sh" in module.FILES["mak_vigia"]
    assert module.UNIT_FILES == {
        "cultura/mak_plataforma/mak-hub.service":
            "/home/mak/.config/systemd/user/mak-hub.service",
        "cultura/mak_codex/mak-codex.service":
            "/home/mak/.config/systemd/user/mak-codex.service",
        "cultura/mak_plataforma/mak-xio.service":
            "/home/mak/.config/systemd/user/mak-xio.service",
        "cultura/mak_research/interfaz.service":
            "/home/mak/.config/systemd/user/mak-research.service",
        "cultura/mak_research/cola.service":
            "/home/mak/.config/systemd/user/mak-research-queue.service",
    }

    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(module, "remote_hashes", lambda: ({}, 0, ""))
    monkeypatch.setattr("sys.argv", ["check_mak_mirror.py", "--output", str(tmp_path / "report.md")])
    assert module.main() == 1


def test_repair_script_installs_fourth_mirror():
    repair = _text("tools/mak_ops/repair_mak_sync.py")
    safe = _text("tools/mak_ops/sync_mak_safe.py")
    assert "cultura/mak_curatoria" in safe
    assert "$HOME/flujo-deploy" in repair
    assert "reset -q --hard origin/main" not in repair
    assert "checkout -q -B main origin/main" not in repair


def test_safe_sync_separates_human_checkout_and_records_deploy_provenance():
    safe = _text("tools/mak_ops/sync_mak_safe.py")
    assert "DEPLOY_REPO" in safe
    assert "/home/mak/flujo-deploy" in safe
    assert "USER_REPO" in safe
    assert "deploy worktree must not be the human checkout" in safe
    assert "flock" in safe
    assert '"schema": "mak-deploy-v1"' in safe
    assert '"status": status' in safe
    assert "backup_live_drift" in safe


def test_curatoria_guard_reconciles_before_declaring_corpus_done():
    guard = _text("cultura/mak_curatoria/curatoria_guardia.sh")
    reconcile = guard.index('percepcion.py" reconciliar')
    decide = guard.index("FUENTE=$(python3")
    assert reconcile < decide
    assert 'estado.get("firma") == firma_actual' in guard


def test_single_human_hub_contract_has_no_direct_service_docs():
    active_docs = [
        _text("MAPA.md"),
        _text("cultura/mak_plataforma/GENESIS.md"),
        _text("cultura/mak_research/MAK_RESEARCH.md"),
        _text("xio/FACES.md"),
    ]
    joined = "\n".join(active_docs)
    assert "192.168.50.2:8890" not in joined
    assert "192.168.50.2:8891" not in joined
    assert "http://192.168.50.2:8900/research/" in joined
    assert "http://192.168.50.2:8900/codex/" in joined

    mirror = _load_mirror_module()
    assert "panel.py" not in mirror.FILES["mak_curatoria"]
    assert "queue_store.py" in mirror.CONDUCTOR_FILES
    assert "queue_worker.py" in mirror.CONDUCTOR_FILES
