"""Ideas are matter in the micelio, not a separate inbox."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "cultura" / "mak_research" / "ideas_a_micelio.py"


def _load():
    spec = importlib.util.spec_from_file_location("ideas_a_micelio", MOD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_idea_se_materializa_como_documento_indexable(tmp_path):
    module = _load()
    origen = tmp_path / "ideas.jsonl"
    destino = tmp_path / "ideas"
    idea = {
        "id": "abc123", "texto": "La cámara como proyector de preguntas",
        "estado": "anotada", "ts": "2026-07-28T10:00:00",
        "relacionadas": [{"titulo": "Obra 1", "carpeta": "corpus", "score": 0.81}],
    }
    origen.write_text(json.dumps(idea, ensure_ascii=False) + "\n", encoding="utf-8")

    resultado = module.sincronizar(origen, destino)

    assert resultado["ideas"] == 1
    text = (destino / "idea-abc123.md").read_text(encoding="utf-8")
    assert "La cámara como proyector de preguntas" in text
    assert "Obra 1 [corpus; 0.810]" in text
    assert '"tipo": "idea"' in text
    assert '"origen": "usuario"' in text


def test_sincronizar_es_idempotente_y_retira_solo_adaptadores(tmp_path):
    module = _load()
    origen = tmp_path / "ideas.jsonl"
    destino = tmp_path / "ideas"
    destino.mkdir()
    (destino / "manual.md").write_text("no tocar", encoding="utf-8")
    origen.write_text(json.dumps({"id": "x", "texto": "idea"}) + "\n", encoding="utf-8")
    module.sincronizar(origen, destino)
    segundo = module.sincronizar(origen, destino)
    assert segundo["sin_cambio"] == 1

    origen.write_text("", encoding="utf-8")
    resultado = module.sincronizar(origen, destino)
    assert resultado["retiradas"] == 1
    assert (destino / "manual.md").read_text(encoding="utf-8") == "no tocar"


def test_interfaz_ofrece_operaciones_sobre_la_materia():
    interfaz = (ROOT / "cultura" / "mak_research" / "interfaz.py").read_text(
        encoding="utf-8")
    assert "Idea desde aquí" in interfaz
    assert "mapDebatir" in interfaz
    assert "mapExperimentar" in interfaz
    assert 'self.path == "/api/codex/experimentar"' in interfaz
    assert 'self.path == "/api/ideas/anotar"' in interfaz
