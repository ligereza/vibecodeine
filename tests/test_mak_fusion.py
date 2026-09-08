"""Fusion creates a primordium and preserves every source."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "cultura" / "mak_research" / "fusion.py"


def _load():
    spec = importlib.util.spec_from_file_location("fusion", PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fusion_no_borra_y_declara_fuentes(tmp_path):
    f = _load()
    sources = ["corpus/obra.md", "ideas/idea-a.md", "codex/prueba.py"]
    result = f.crear("comparar forma y pérdida", sources, tmp_path)
    path = Path(result["path"])
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for source in sources:
        assert source in text
    meta = json.loads(next(line[6:] for line in text.splitlines()
                           if line.startswith("meta: ")))
    assert meta["tipo"] == "fusion"
    assert meta["fuentes"] == sources
    assert "esperando correlación y decisión humana" in text


def test_fusion_exige_dos_fuentes(tmp_path):
    f = _load()
    try:
        f.crear("tema", ["corpus/a.md"], tmp_path)
    except ValueError as exc:
        assert "dos fuentes" in str(exc)
    else:
        raise AssertionError("aceptó una fusión sin dos fuentes")