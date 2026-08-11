import json
import threading
import time

from cultura.mak_plataforma import revision
from cultura.mak_plataforma import revision_episodios


def test_visual_review_record_is_idempotent_across_concurrent_retries(
        tmp_path, monkeypatch):
    root = tmp_path / "review-root"
    root.mkdir()
    reviews = root / "human_reviews.jsonl"
    monkeypatch.setattr(revision, "ROOT", root)
    monkeypatch.setattr(revision, "REVIEWS", reviews)
    original_read = revision._review_map
    state = {"active": 0, "max_active": 0}
    state_lock = threading.Lock()

    def slow_read():
        with state_lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.05)
        rows = original_read()
        with state_lock:
            state["active"] -= 1
        return rows

    monkeypatch.setattr(revision, "_review_map", slow_read)
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        revision.record("123_mp4", "accept"))) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    rows = [json.loads(line) for line in reviews.read_text(encoding="utf-8").splitlines()]
    assert state["max_active"] == 1
    assert len(rows) == 1
    assert sum(1 for result in results if result.get("duplicate")) == 1


def test_episode_review_record_is_idempotent_across_concurrent_retries(
        tmp_path, monkeypatch):
    run = tmp_path / "episode-run"
    reviews = run / "episode_reviews.jsonl"
    monkeypatch.setattr(revision_episodios, "RUN", run)
    monkeypatch.setattr(revision_episodios, "REVIEWS", reviews)
    monkeypatch.setattr(revision_episodios, "rows", lambda: [{
        "episodio": "episode-a", "human": None,
    }])
    original_read = revision_episodios._review_map
    state = {"active": 0, "max_active": 0}
    state_lock = threading.Lock()

    def slow_read():
        with state_lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.05)
        rows = original_read()
        with state_lock:
            state["active"] -= 1
        return rows

    monkeypatch.setattr(revision_episodios, "_review_map", slow_read)
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        revision_episodios.record("episode-a", "reject"))) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    rows = [json.loads(line) for line in reviews.read_text(encoding="utf-8").splitlines()]
    assert state["max_active"] == 1
    assert len(rows) == 1
    assert sum(1 for result in results if result.get("duplicate")) == 1
