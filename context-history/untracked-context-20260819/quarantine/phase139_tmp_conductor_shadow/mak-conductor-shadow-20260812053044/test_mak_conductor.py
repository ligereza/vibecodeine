from __future__ import annotations

import threading
import time
import json

import pytest

from cultura.mak_conductor.conductor import Conductor
from cultura.mak_conductor.gpu_arbiter import GpuArbiter, GpuBudgetExceeded, GpuBusy
from cultura.mak_conductor.runtime import file_content_hash
from cultura.mak_conductor.queue_store import (COMPLETED, ENQUEUED, FAILED,
                                                OBSERVED, QueueStore)


def test_enqueue_is_idempotent_and_wal_store_is_reusable(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    first = store.enqueue("anexo_svg", {"text": "onda   violeta"})
    second = QueueStore(tmp_path / "mak.db").enqueue(
        "anexo_svg", {"text": "onda violeta"})

    assert first["created"] is True
    assert second["created"] is False
    assert second["job_id"] == first["job_id"]
    assert len(store.list_jobs()) == 1


def test_idempotency_keeps_semantic_payload_fields_distinct(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    first = store.enqueue("investigacion", {"text": "agua", "mode": "research"})
    second = store.enqueue("investigacion", {"text": "agua", "mode": "panel"})
    assert first["job_id"] != second["job_id"]


def test_file_content_hash_is_stable_and_missing_is_explicit(tmp_path):
    path = tmp_path / "artifact.bin"
    path.write_bytes(b"abc\x00def")
    assert file_content_hash(path) == file_content_hash(path)
    assert file_content_hash(tmp_path / "missing.bin") is None


def test_concurrent_enqueue_keeps_one_job_and_records_deduplication(tmp_path):
    db = tmp_path / "mak.db"
    stores = [QueueStore(db) for _ in range(4)]
    results = []
    errors = []

    def enqueue(store):
        try:
            results.append(store.enqueue("anexo_svg", {"text": "mismo"}))
        except Exception as exc:  # pragma: no cover - assertion below reports it
            errors.append(exc)

    threads = [threading.Thread(target=enqueue, args=(store,))
               for store in stores]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert len(results) == 4
    assert len({result["job_id"] for result in results}) == 1
    assert len(stores[0].list_jobs()) == 1
    with stores[0]._connect() as conn:
        event_types = [row[0] for row in conn.execute(
            "SELECT event_type FROM events ORDER BY created_at")]
    assert event_types.count("job_enqueued") == 1
    assert event_types.count("job_deduplicated") == 3


def test_shadow_observation_and_human_gate_are_distinct_from_job_completion(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    job = store.enqueue("publicacion", {"text": "pieza"})
    observation = store.record_observation(
        job["job_id"], "legacy-producer", result_status="listo",
        validated=False, payload={"path": "staging/pieza.svg"},
    )
    decision = store.request_decision(job["job_id"], estimated_cost=2.5)

    assert observation
    assert store.get_job(job["job_id"])["status"] == OBSERVED
    assert store.decision_approved(decision) is False
    assert store.record_decision(decision, actor="human", approved=True)
    assert store.decision_approved(decision) is True
    assert len(store.list_observations(job_id=job["job_id"])) == 1


def test_late_shadow_observation_is_audited_and_unknown_jobs_fail(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    job = store.enqueue("demo", {"text": "one"})
    claimed = store.claim_next("worker")
    assert claimed["job_id"] == job["job_id"]
    store.record_observation(job["job_id"], "legacy", result_status="READY")
    with pytest.raises(ValueError):
        store.record_observation("missing", "legacy", result_status="FAILED")
    assert any(event["event_type"] == "shadow_observation_late"
               for event in store.list_events(job_id=job["job_id"]))


def test_human_gate_creation_is_atomic_under_race(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    job = store.enqueue("publicacion", {"text": "pieza"})
    ids = []
    errors = []

    def request_gate():
        try:
            ids.append(store.ensure_human_gate(job["job_id"], note="gate"))
        except Exception as exc:  # pragma: no cover - assertion below reports it
            errors.append(exc)

    threads = [threading.Thread(target=request_gate) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert len(set(ids)) == 1
    with store._connect() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM decisions WHERE job_id = ?",
            (job["job_id"],),
        ).fetchone()[0] == 1
    assert store.summary()["events"] == 2


def test_external_budget_is_atomic_and_bounded(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    assert store.reserve_budget("watsonx", limit_count=2, now=100)
    assert store.reserve_budget("watsonx", limit_count=2, now=101)
    assert not store.reserve_budget("watsonx", limit_count=2, now=102)


def test_active_mode_records_and_enforces_external_budget_without_shadow(
        tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_CONDUCTOR_ACTIVE", "1")
    monkeypatch.setenv("MAK_CONDUCTOR_SHADOW", "0")
    monkeypatch.setenv("MAK_CONDUCTOR_ENFORCE_BUDGET", "1")
    monkeypatch.setenv("MAK_DB_PATH", str(tmp_path / "mak.db"))
    monkeypatch.setenv("MAK_WATSONX_HOURLY_LIMIT", "1")
    from cultura.mak_conductor.runtime import reserve_external_call

    assert reserve_external_call("watsonx", limit_count=1)
    assert not reserve_external_call("watsonx", limit_count=1)


def test_only_one_worker_can_claim_a_job(tmp_path):
    db = tmp_path / "mak.db"
    first_store = QueueStore(db)
    second_store = QueueStore(db)
    first_store.enqueue("investigacion", {"topic": "agua"})

    claimed_a = first_store.claim_next("worker-a")
    claimed_b = second_store.claim_next("worker-b")

    assert claimed_a is not None
    assert claimed_b is None
    assert claimed_a["status"] == "CLAIMED"
    assert first_store.start(claimed_a["job_id"], "worker-a")
    assert not second_store.heartbeat(claimed_a["job_id"], "worker-b")


def test_expired_lease_is_requeued_then_can_be_claimed(tmp_path):
    store = QueueStore(tmp_path / "mak.db", max_retries=2)
    job = store.enqueue("memoria_embedding", {"text": "registro"})
    claimed = store.claim_next("worker-a", lease_seconds=0.1)
    assert claimed["job_id"] == job["job_id"]
    time.sleep(0.15)

    assert store.recover_expired_leases() == 1
    recovered = store.get_job(job["job_id"])
    assert recovered["status"] == ENQUEUED
    assert recovered["retry_count"] == 1
    with store._connect() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM events WHERE job_id = ? AND event_type = 'lease_expired'",
            (job["job_id"],),
        ).fetchone()[0] == 1
    assert store.claim_next("worker-b") is not None


def test_artifact_hash_deduplicates_bytes_and_completion_requires_validation(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    job = store.enqueue("anexo_svg", {"text": "vaso"})
    claimed = store.claim_next("worker-a")
    assert store.start(claimed["job_id"], "worker-a")
    artifact_a = store.record_artifact(job["job_id"], "svg", b"<svg/>")
    artifact_b = store.record_artifact(job["job_id"], "svg", b"<svg/>")
    assert artifact_a["duplicate"] is False
    assert artifact_b["duplicate"] is True
    assert artifact_b["artifact_id"] == artifact_a["artifact_id"]
    assert not store.complete(job["job_id"], "worker-a",
                              artifact_ids=[artifact_a["artifact_id"]])
    assert store.begin_validation(job["job_id"], "worker-a")
    assert store.complete(job["job_id"], "worker-a",
                          artifact_ids=[artifact_a["artifact_id"]])
    assert store.get_job(job["job_id"])["status"] == COMPLETED
    with store._connect() as conn:
        links = conn.execute(
            "SELECT relation FROM artifact_links WHERE job_id = ?",
            (job["job_id"],),
        ).fetchall()
        events = conn.execute(
            "SELECT event_type FROM events WHERE job_id = ?",
            (job["job_id"],),
        ).fetchall()
    assert {row[0] for row in links} == {"produced", "duplicate"}
    assert "job_completed" in {row[0] for row in events}
    assert "artifact_deduplicated" in {row[0] for row in events}


def test_gpu_budget_and_timeout_are_explicit(tmp_path):
    path = tmp_path / "gpu.lock"
    first = GpuArbiter(path, capacity_mb=4096)
    second = GpuArbiter(path, capacity_mb=4096)
    with pytest.raises(GpuBudgetExceeded):
        first.acquire(job_id="too-large", estimated_vram_mb=4097)
    first.acquire(job_id="one", estimated_vram_mb=800)
    try:
        with pytest.raises(GpuBusy):
            second.acquire(job_id="two", estimated_vram_mb=800,
                          timeout_s=0.05)
    finally:
        first.release()


def test_conductor_never_marks_unvalidated_handler_complete(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    arbiter = GpuArbiter(tmp_path / "gpu.lock")
    conductor = Conductor(store, arbiter, worker_id="shadow")
    job = conductor.enqueue("anexo_svg", {"text": "prueba"})

    result = conductor.dispatch_once(lambda _: {"validated": False,
                                                  "error": "bad svg"})

    assert result["status"] == FAILED
    assert store.get_job(job["job_id"])["status"] == FAILED
    assert store.list_jobs(status=ENQUEUED) == []


def test_queue_worker_persists_result_before_completion(tmp_path):
    from cultura.mak_conductor.queue_worker import QueueWorker

    store = QueueStore(tmp_path / "mak.db")
    job = store.enqueue("demo", {"text": "one"})
    worker = QueueWorker(
        store, {"demo": lambda _job: {"validated": True, "value": 7}},
        gpu_lock=tmp_path / "gpu.lock", worker_id="demo-worker")
    result = worker.run_once()
    assert result["status"] == COMPLETED
    assert store.get_result(job["job_id"])["value"] == 7


def test_dispatch_sync_is_idempotent_and_returns_persisted_result(tmp_path,
                                                                  monkeypatch):
    monkeypatch.setenv("MAK_CONDUCTOR_ACTIVE", "1")
    monkeypatch.setenv("MAK_DB_PATH", str(tmp_path / "mak.db"))
    monkeypatch.setenv("MAK_GPU_LOCK_PATH", str(tmp_path / "gpu.lock"))
    from cultura.mak_conductor.runtime import dispatch_sync

    calls = []

    def handler(_job):
        calls.append(True)
        return {"validated": True, "value": "stable"}

    first = dispatch_sync("demo", {"text": "same"}, producer="test",
                          handler=handler)
    second = dispatch_sync("demo", {"text": "same"}, producer="test",
                           handler=handler)
    assert first["value"] == second["value"] == "stable"
    assert len(calls) == 1
    assert second["queue_status"] == COMPLETED


def test_active_gpu_handler_can_use_nested_shared_lease(tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_CONDUCTOR_ACTIVE", "1")
    monkeypatch.setenv("MAK_DB_PATH", str(tmp_path / "mak.db"))
    monkeypatch.setenv("MAK_GPU_LOCK_PATH", str(tmp_path / "gpu.lock"))
    from cultura.mak_conductor.runtime import dispatch_sync, shared_gpu_lease

    def handler(_job):
        with shared_gpu_lease(job_id="nested", estimated_vram_mb=900):
            return {"validated": True, "value": "nested-ok"}

    result = dispatch_sync(
        "gpu_demo", {"text": "same"}, producer="test",
        estimated_vram_mb=2500, handler=handler)
    assert result["value"] == "nested-ok"


def test_publication_waits_for_human_approval_and_then_runs(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    conductor = Conductor(store, GpuArbiter(tmp_path / "gpu.lock"),
                          worker_id="gate")
    job = conductor.enqueue("publicacion", {"text": "pieza"})

    waiting = conductor.dispatch_once(lambda _: {"validated": True})
    assert waiting["status"] == "WAITING_HUMAN"
    assert store.get_job(job["job_id"])["status"] == ENQUEUED
    decision = store.human_gate_decision_id(job["job_id"])
    assert decision and store.record_decision(decision, actor="artist",
                                              approved=True)

    done = conductor.dispatch_once(lambda _: {"validated": True})
    assert done["status"] == COMPLETED


def test_budget_error_is_terminal_not_retried(tmp_path):
    store = QueueStore(tmp_path / "mak.db")
    conductor = Conductor(store, GpuArbiter(tmp_path / "gpu.lock",
                                            capacity_mb=100),
                          worker_id="budget")
    job = conductor.enqueue("investigacion", {"text": "big"},
                            estimated_vram_mb=101)
    result = conductor.dispatch_once(lambda _: {"validated": True})
    assert result["status"] == FAILED
    assert store.get_job(job["job_id"])["status"] == FAILED


def test_bounded_shadow_batch_proves_dedup_race_and_orphan_recovery(tmp_path,
                                                                    monkeypatch):
    db = tmp_path / "shadow.db"
    monkeypatch.setenv("MAK_CONDUCTOR_SHADOW", "1")
    monkeypatch.setenv("MAK_CONDUCTOR_GPU", "1")
    monkeypatch.setenv("MAK_DB_PATH", str(db))
    monkeypatch.setenv("MAK_GPU_LOCK_PATH", str(tmp_path / "gpu.lock"))
    monkeypatch.setenv("MAK_GPU_WAIT_SECONDS", "0.05")

    from cultura.mak_conductor.runtime import enqueue_shadow, observe_shadow

    jobs = []
    errors = []

    def producer(index):
        try:
            job = enqueue_shadow(
                "anexo_svg", {"text": "same concept"},
                producer="bounded-producer-%d" % index,
                estimated_vram_mb=3000, template_version="shadow-test-v1")
            jobs.append(job)
        except Exception as exc:  # pragma: no cover - assertion below reports it
            errors.append(exc)

    threads = [threading.Thread(target=producer, args=(i,)) for i in range(6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert len({job["job_id"] for job in jobs}) == 1
    observe_shadow(jobs[0], producer="bounded-producer",
                   result_status="READY", validated=True,
                   payload={"bounded": True}, owner_pid=1234)
    store = QueueStore(db)
    assert store.get_job(jobs[0]["job_id"])["status"] == OBSERVED
    with store._connect() as conn:
        types = [row[0] for row in conn.execute(
            "SELECT event_type FROM events WHERE job_id = ?",
            (jobs[0]["job_id"],),
        )]
    assert "job_deduplicated" in types
    assert "shadow_observed" in types

    orphan = store.enqueue("investigacion", {"text": "orphan"})
    claimed = store.claim_next("dead-worker", lease_seconds=0.1)
    assert claimed["job_id"] == orphan["job_id"]
    time.sleep(0.15)
    assert store.recover_expired_leases() == 1
    assert store.get_job(orphan["job_id"])["status"] == ENQUEUED


def test_shadow_enqueue_initialization_is_safe_when_threads_start_together(
        tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_CONDUCTOR_SHADOW", "1")
    monkeypatch.setenv("MAK_DB_PATH", str(tmp_path / "shadow.db"))
    from cultura.mak_conductor.runtime import enqueue_shadow

    jobs = []
    errors = []

    def producer(index):
        try:
            jobs.append(enqueue_shadow(
                "investigacion", {"text": "same"},
                producer="producer-%d" % index,
                template_version="init-race-v1"))
        except Exception as exc:  # pragma: no cover - assertion below reports it
            errors.append(exc)

    threads = [threading.Thread(target=producer, args=(i,)) for i in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert all(jobs)
    assert len({job["job_id"] for job in jobs}) == 1
