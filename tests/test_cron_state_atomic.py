import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_latido_state_and_index_are_atomic(tmp_path):
    module = _load("latido_atomic", "cultura/mak_plataforma/latido.py")
    module.STATE = str(tmp_path / "state.json")
    module.IDX = str(tmp_path / "idx")
    module._save({"count": 2})
    assert json.loads(Path(module.STATE).read_text()) == {"count": 2}
    assert not list(tmp_path.glob(".latido-*.tmp"))
    assert module.prox_idx(3) == 0
    assert Path(module.IDX).read_text() == "1"


def test_red_watch_state_is_atomic(tmp_path):
    module = _load("red_watch_atomic", "cultura/mak_plataforma/red_watch.py")
    path = tmp_path / "red.json"
    module._atomic_write(str(path), '{"up":true}')
    assert json.loads(path.read_text()) == {"up": True}
    assert not list(tmp_path.glob(".red-state-*.tmp"))


def test_junta_adjustments_are_atomic(tmp_path):
    module = _load("junta_atomic", "cultura/mak_plataforma/junta.py")
    module.AJUSTES_PATH = str(tmp_path / "ajustes.json")
    module.escribir_ajustes({"ts": "now"},
                            {"proveedor": "local", "decision": {"ok": True}})
    assert json.loads(Path(module.AJUSTES_PATH).read_text())["proveedor"] == "local"
    assert not list(tmp_path.glob(".junta-*.tmp"))


def test_repo_sync_versioning_remains_paused():
    cron = (ROOT / "cultura" / "mak_plataforma" / "crontab.mak").read_text(
        encoding="utf-8")
    lines = [line for line in cron.splitlines() if "MAK-REPO-SYNC" in line]
    assert len(lines) == 1
    assert lines[0].lstrip().startswith("# PAUSED-FARO")
    assert "/home/mak/bin/mak_sync_safe.py" in lines[0]
    assert "reset -q --hard origin/main" not in lines[0]
    assert "reset -q --hard origin/main" not in lines[0]
