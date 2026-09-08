import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cultura" /
                        "mak_plataforma"))
from cultura.mak_plataforma import trabajo


def test_work_serializes_ticks_and_state_atomically(tmp_path, monkeypatch):
    state_path = tmp_path / "trabajo_state.json"
    monkeypatch.setattr(trabajo, "STATE", str(state_path))
    monkeypatch.setattr(trabajo.roles, "GAP_MIN", 999)
    monkeypatch.setattr(trabajo.roles, "MAX_DIA", 10)
    monkeypatch.setattr(trabajo, "load1", lambda: 0.0)
    monkeypatch.setattr(trabajo, "red_ok", lambda: True)
    monkeypatch.setattr(trabajo, "_tarea",
                        lambda _verbo, _state: ("local", {"modo": "memory_audit"}))
    monkeypatch.setattr(trabajo, "_run_local_idle", lambda _payload: {"ok": True})
    monkeypatch.setattr(trabajo, "_resp_ok", lambda _response: (True, ""))
    monkeypatch.setattr(trabajo, "_audit_idle_decision", lambda *args, **kwargs: None)
    monkeypatch.setattr(trabajo, "log", lambda _message: None)

    threads = [threading.Thread(target=trabajo.main) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["count"] == 1
    assert not list(Path(tmp_path).glob(".trabajo-state-*.tmp"))
