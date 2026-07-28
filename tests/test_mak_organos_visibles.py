"""The common body exposes live organs as transformations, not tabs."""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "cultura" / "mak_research" / "interfaz.py"


def _load(monkeypatch):
    # interfaz imports Linux worker/fcntl; organ inventory itself is portable.
    monkeypatch.syspath_prepend(str(PATH.parent))
    worker = types.ModuleType("worker")
    worker.run_tema = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "worker", worker)
    spec = importlib.util.spec_from_file_location("interfaz_organos", PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_organos_exponen_transformacion_y_no_departamentos_vacios(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    module = _load(monkeypatch)
    monkeypatch.setattr(module.os.path, "expanduser", lambda value: value.replace("~", str(tmp_path)))
    monkeypatch.setattr(
        module, "_procesos_vivos",
        lambda: "interfaz.py interfaz_codex.py trabajo.py percepcion.py")
    (tmp_path / "plataforma").mkdir()
    (tmp_path / "plataforma" / "ideas.jsonl").write_text("{}\n", encoding="utf-8")
    module.DIRS = {name: str(tmp_path / "research" / name) for name in module.DIRS}
    for path in module.DIRS.values():
        Path(path).mkdir(parents=True, exist_ok=True)
    (Path(module.DIRS["corpus"]) / "obra.md").write_text("obra", encoding="utf-8")
    (tmp_path / "plataforma" / "material.jsonl").write_text(
        json.dumps({"estado": "pendiente"}) + "\n" +
        json.dumps({"estado": "despachada"}) + "\n", encoding="utf-8")
    data = module._organos()["organos"]
    assert [x["id"] for x in data] == [
        "entrada", "curatoria", "research", "codex", "plataforma", "emerge"]
    assert [x["verbo"] for x in data] == [
        "recibe", "percibe / extrae", "busca / debate", "implementa / prueba",
        "coordina / entrega", "publica / devuelve"]
    assert next(x for x in data if x["id"] == "research")["vivo"] is True
    assert next(x for x in data if x["id"] == "plataforma")["vivo"] is True
    assert next(x for x in data if x["id"] == "codex")["vivo"] is True
    assert next(x for x in data if x["id"] == "curatoria")["vivo"] is True
    assert next(x for x in data if x["id"] == "entrada")["cantidad"] == 2
    assert next(x for x in data if x["id"] == "plataforma")["cantidad"] == 1


def test_interfaz_contiene_tuberia_y_filtro_sobre_el_mismo_cuerpo():
    text = PATH.read_text(encoding="utf-8")
    assert 'class="organ-line"' in text
    assert "function mapOrgano" in text
    assert 'fetch(\'/api/organos\')' in text
    assert 'if u.path == "/api/organos"' in text
    assert '<div id="map-view" class="show">' in text
    assert "ORGANOS_PLACEHOLDER" in text
    assert "MAPA.lente='cultivo'" in text
    assert "@media(max-width:800px)" in text
