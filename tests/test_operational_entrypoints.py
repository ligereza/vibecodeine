"""Static ratchets for MAK mirror tooling and active entrypoint boundaries."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


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
    monkeypatch.setattr("sys.argv", ["check_mak_mirror.py", "--output", str(tmp_path / "report.md")])

    # Until 2026-08-29 this asserted `main() == 1` while mocking `remote_hashes`
    # empty, because the checker asked two of its three hashes over SSH to a
    # machine that no longer answers: with the remote leg dead every row read
    # MISMATCH and the exit was always 1. It "passed" by pinning the broken
    # behaviour. The checker is now local, so silence means agreement -- and a
    # detector that only ever returns 0 has to prove it can return 1.
    assert module.main() == 0, "sin deriva, la salida es 0"

    organ = Path("/home/mak/xio_puente/monitor.py")
    if organ.is_file() and not organ.is_symlink():
        original = organ.read_bytes()
        try:
            organ.write_bytes(original + b"\n# drift injected by this test\n")
            assert module.main() == 1, "con deriva inyectada, la salida debe ser 1"
        finally:
            organ.write_bytes(original)
        assert module.main() == 0, "y vuelve a 0 al revertirla"


def test_legacy_repair_script_is_not_an_active_entrypoint():
    # The historical repair script performed SSH, Git reset/checkout, cron and
    # mirror-copy operations without an active consumer. It is quarantined as
    # evidence; keeping a test that requires it would resurrect a dangerous
    # mutator by treating its absence as a regression.
    assert not (ROOT / "tools" / "mak_ops" / "repair_mak_sync.py").exists()


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
    # RELEVO_MAK.md is a box-level projection, not part of this repo's
    # canonical source tree. Do not manufacture a stale copy just to satisfy
    # an inventory test; include it when a future active projection exists.
    relevo = ROOT / "cultura" / "mak_plataforma" / "RELEVO_MAK.md"
    if relevo.exists():
        active_docs.append(relevo.read_text(encoding="utf-8"))
    joined = "\n".join(active_docs)
    assert "192.168.50.2:8890" not in joined
    assert "192.168.50.2:8891" not in joined
    assert "http://127.0.0.1:8900/research/" in joined
    assert "http://127.0.0.1:8900/codex/" in joined

    mirror = _load_mirror_module()
    assert "panel.py" not in mirror.FILES["mak_curatoria"]
    assert "queue_store.py" in mirror.CONDUCTOR_FILES
    assert "queue_worker.py" in mirror.CONDUCTOR_FILES
