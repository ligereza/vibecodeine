import importlib.util
import json
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cultura" / "mak_research"))


def _load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fruition_concurrent_records_preserve_distinct_decisions(tmp_path):
    module = _load("fructification_concurrent", "cultura/mak_research/fructificacion.py")
    path = tmp_path / "fructificaciones.json"
    barrier = threading.Barrier(8)

    def decide(index):
        barrier.wait(timeout=3)
        module.decidir("ideas/%d.md" % index, "fructificar",
                       "nota-%d" % index, path)

    threads = [threading.Thread(target=decide, args=(i,)) for i in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) == 8
    assert {value["nota"] for value in data.values()} == {
        "nota-%d" % index for index in range(8)}


def test_memory_serializes_indexers(tmp_path, monkeypatch):
    module = _load("memory_concurrent", "cultura/mak_research/memoria.py")
    monkeypatch.setattr(module, "RESEARCH", str(tmp_path / "research"))
    monkeypatch.setattr(module, "MEM_DIR", str(tmp_path / "research" / "memoria"))
    monkeypatch.setattr(module, "INDEX_FILE",
                        str(tmp_path / "research" / "memoria" / "index.jsonl"))
    monkeypatch.setattr(module, "FUENTES", ())
    state = {"active": 0, "max": 0}
    guard = threading.Lock()

    def save_records(records):
        with guard:
            state["active"] += 1
            state["max"] = max(state["max"], state["active"])
        time.sleep(0.03)
        with guard:
            state["active"] -= 1

    monkeypatch.setattr(module, "_guardar_index", save_records)
    threads = [threading.Thread(target=module.indexar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert state["max"] == 1


def test_memory_serializes_graph_rebuilds_and_exposes_invalidation(
        tmp_path, monkeypatch):
    module = _load("memory_graph_concurrent", "cultura/mak_research/memoria.py")
    monkeypatch.setattr(module, "GRAFO_CACHE",
                        str(tmp_path / "research" / "memoria" / "grafo.json"))
    state = {"active": 0, "max": 0}
    guard = threading.Lock()

    def rebuild_graph(**_kwargs):
        with guard:
            state["active"] += 1
            state["max"] = max(state["max"], state["active"])
        time.sleep(0.03)
        with guard:
            state["active"] -= 1
        return {"nodes": [], "edges": [], "meta": {}}

    monkeypatch.setattr(module, "_semantic_graph_unlocked", rebuild_graph)
    threads = [threading.Thread(target=module.grafo_semantico) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert state["max"] == 1
    cache = Path(module.GRAFO_CACHE)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("{}", encoding="utf-8")
    assert module.invalidate_grafo_cache() is True
    assert not cache.exists()
    assert module.invalidate_grafo_cache() is False
