"""Ideas are matter in the micelio, not a separate inbox."""
from __future__ import annotations

import importlib.util
import json
import threading
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
        "relacionadas": [{"titulo": "Obra 1", "carpeta": "corpus",
                   "score": 0.81, "id": "corpus/obra-1.md"}],
        "origen": {"id": "corpus/obra-0.md", "dir": "corpus"},
    }
    origen.write_text(json.dumps(idea, ensure_ascii=False) + "\n", encoding="utf-8")

    resultado = module.sincronizar(origen, destino)

    assert resultado["ideas"] == 1
    text = (destino / "idea-abc123.md").read_text(encoding="utf-8")
    assert "La cámara como proyector de preguntas" in text
    assert "Obra 1 [corpus; 0.810; id=corpus/obra-1.md]" in text
    assert '"origen_materia": {"id": "corpus/obra-0.md"' in text
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


def test_concurrent_sync_preserves_adapters(tmp_path):
    module = _load()
    origen = tmp_path / "ideas.jsonl"
    destino = tmp_path / "ideas"
    ideas = [
        {"id": "a", "texto": "idea A", "estado": "anotada"},
        {"id": "b", "texto": "idea B", "estado": "anotada"},
    ]
    origen.write_text("".join(json.dumps(idea) + "\n" for idea in ideas),
                      encoding="utf-8")
    threads = [threading.Thread(target=module.sincronizar,
                                args=(origen, destino)) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert (destino / "idea-a.md").exists()
    assert (destino / "idea-b.md").exists()


def test_interfaz_ofrece_operaciones_sobre_la_materia():
    interfaz = (ROOT / "cultura" / "mak_research" / "interfaz.py").read_text(
        encoding="utf-8")
    assert "Idea desde aquí" in interfaz
    assert "mapDebatir" in interfaz
    assert "mapExperimentar" in interfaz
    assert "setView('mapa');" in interfaz
    assert '<div id="map-view" class="show">' in interfaz
    assert "tubería clara" in interfaz
    assert "e.clase === 'procedencia'" in interfaz
    assert "mapLente('compost')" in interfaz
    assert "mapFusionar" in interfaz
    assert "mapEstatuto" in interfaz
    assert 'self.path == "/api/fusion"' in interfaz
    assert 'data-lente="frutos"' in interfaz
    assert 'self.path == "/api/codex/experimentar"' in interfaz
    assert 'self.path == "/api/ideas/anotar"' in interfaz
    assert '"corpus": os.path.expanduser("~/research/corpus")' in interfaz
    assert '"ideas": os.path.expanduser("~/research/ideas")' in interfaz
    assert '"codex": os.path.expanduser("~/research/codex")' in interfaz
    assert '"fusiones": os.path.expanduser("~/research/fusiones")' in interfaz


def test_endpoints_historicos_no_quedan_dentro_de_fusion():
    interfaz = (ROOT / "cultura" / "mak_research" / "interfaz.py").read_text(
        encoding="utf-8")
    fusion = interfaz.index('if self.path == "/api/fusion"')
    workflow = interfaz.index('if self.path == "/api/workflow"', fusion)
    between = interfaz[fusion:workflow]
    assert 'return self._json_response({"ok": True, "primordio": primordio})' in between
    workflow_line = interfaz[workflow:].splitlines()[0]
    fusion_line = interfaz[fusion:].splitlines()[0]
    assert len(workflow_line) - len(workflow_line.lstrip()) == \
        len(fusion_line) - len(fusion_line.lstrip())
    assert 'memoria.invalidate_grafo_cache()' in between
    assert between.index('memoria.invalidate_grafo_cache()') < \
        between.index('_lanzar("panel"')


def test_memoria_declara_afinidad_y_procedencia():
    memoria = (ROOT / "cultura" / "mak_research" / "memoria.py").read_text(
        encoding="utf-8")
    assert '"clase": "afinidad"' in memoria
    assert '"clase": "procedencia"' in memoria
    assert "GRAFO_SCHEMA_VERSION" in memoria
    assert '"calidad": calidad.get' in memoria
    assert '"ideas"' in memoria
    assert '"fusiones"' in memoria
    assert 'def invalidate_grafo_cache()' in memoria
    assert 'def _exclusive_grafo_lock()' in memoria
