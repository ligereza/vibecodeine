"""Fructification is measured by MAK and granted only by a human."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "cultura" / "mak_research" / "fructificacion.py"


def _load():
    spec = importlib.util.spec_from_file_location("fructificacion", PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_presion_solo_sugiere_primordio():
    f = _load()
    nodes = [
        {"id": "ideas/a.md", "dir": "ideas", "chunks": 4},
        {"id": "corpus/b.md", "dir": "corpus", "chunks": 2},
        {"id": "codex/c.md", "dir": "codex", "chunks": 4},
    ]
    edges = [
        {"a": "ideas/a.md", "b": "corpus/b.md", "clase": "procedencia"},
        {"a": "ideas/a.md", "b": "codex/c.md", "clase": "afinidad"},
    ]
    out = {n["id"]: n for n in f.evaluar(nodes, edges, registro={})}
    assert out["ideas/a.md"]["presion"] >= 0.6
    assert out["ideas/a.md"]["estatuto"] == "primordio"
    assert out["ideas/a.md"]["decision_humana"] is False
    assert all(n["estatuto"] != "fructifero" for n in out.values())


def test_solo_registro_humano_fructifica(tmp_path):
    f = _load()
    registry = tmp_path / "frutos.json"
    result = f.decidir("ideas/a.md", "fructificar", "adquiere forma", registry)
    assert result["ok"] is True
    out = f.evaluar([{"id": "ideas/a.md", "dir": "ideas", "chunks": 1}], [],
                    registro=f.cargar(registry))[0]
    assert out["estatuto"] == "fructifero"
    assert out["decision_humana"] is True
    assert out["nota_estatuto"] == "adquiere forma"


def test_devolver_no_borra_el_registro(tmp_path):
    f = _load()
    registry = tmp_path / "frutos.json"
    f.decidir("corpus/x.md", "fructificar", "primero", registry)
    f.decidir("corpus/x.md", "devolver", "todavía no", registry)
    data = f.cargar(registry)["corpus/x.md"]
    assert data["estatuto"] == "sustrato"
    assert data["nota"] == "todavía no"