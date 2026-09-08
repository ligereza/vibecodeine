import json
import threading
import time

from cultura.mak_plataforma import entregar


def test_delivery_main_serializes_concurrent_ticks(tmp_path, monkeypatch):
    monkeypatch.setattr(entregar, "STATE", str(tmp_path / "state.json"))
    state = {"active": 0, "max_active": 0}
    state_lock = threading.Lock()

    def slow_run():
        with state_lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.05)
        with state_lock:
            state["active"] -= 1
        return 0

    monkeypatch.setattr(entregar, "_main_unlocked", slow_run)
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        entregar.main())) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert state["max_active"] == 1
    assert results == [0, 0]


def test_delivery_state_installs_atomically(tmp_path, monkeypatch):
    path = tmp_path / "codex_delivered.json"
    monkeypatch.setattr(entregar, "STATE", str(path))
    entregar.guardar_estado({"job-2", "job-1"}, {"slug-b", "slug-a"})

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {"entregados": ["job-1", "job-2"],
                   "slugs": ["slug-a", "slug-b"]}
    assert not list(tmp_path.glob(".codex-delivered-*.tmp"))
