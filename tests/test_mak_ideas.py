import json
import threading
import time

from cultura.mak_plataforma import ideas
from cultura.mak_plataforma import material


def test_anotar_is_idempotent_across_concurrent_http_workers(tmp_path, monkeypatch):
    path = tmp_path / "ideas.jsonl"
    monkeypatch.setattr(ideas, "IDEAS", str(path))
    state = {"active": 0, "max_active": 0}
    state_lock = threading.Lock()

    def slow_relation(*_args, **_kwargs):
        with state_lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.05)
        with state_lock:
            state["active"] -= 1
        return []

    monkeypatch.setattr(ideas, "relacionar", slow_relation)
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        ideas.anotar("idea concurrente"))) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert state["max_active"] == 1
    assert len(rows) == 1
    assert sum(1 for result in results if result.get("ok")) == 1
    assert sum(1 for result in results if "ya estaba anotada" in result.get("error", "")) == 1


def test_material_pop_is_atomic_across_concurrent_workers(tmp_path, monkeypatch):
    path = tmp_path / "material.jsonl"
    path.write_text(json.dumps({
        "id": "task-a", "texto": "tarea", "estado": "pendiente",
    }) + "\n", encoding="utf-8")
    monkeypatch.setattr(material, "COLA", str(path))
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        material.pop_pendiente())) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert sum(result is not None for result in results) == 1
    assert sum(result is None for result in results) == 1
    stored = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert stored[0]["estado"] == "despachada"


def test_material_enqueue_is_idempotent_across_concurrent_workers(tmp_path, monkeypatch):
    path = tmp_path / "material.jsonl"
    monkeypatch.setattr(material, "COLA", str(path))
    task = {"id": "idea-a", "texto": "idea", "estado": "pendiente"}
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        material.enqueue_front(task))) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert results.count(True) == 1
    assert results.count(False) == 1
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1
