#!/usr/bin/env python3
"""Run one bounded, provider-free MAK conductor shadow probe.

The probe proves concurrent idempotent enqueue, observation, and expired lease
recovery against the selected SQLite path. It never calls a model or network
provider and never touches a canonical branch or README/SVG.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import nullcontext
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
for _module_root in ("mak_research", "mak_plataforma", "mak_curatoria", "mak_codex"):
    _path = REPO_ROOT / "cultura" / _module_root
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size=-1):
        return json.dumps(self.payload).encode("utf-8")


def _producer_matrix(db: Path, lock: Path, root: Path) -> dict:
    """Exercise adapted producer boundaries without network or model calls."""
    from cultura.mak_conductor.queue_store import QueueStore

    from cultura.mak_curatoria import percepcion
    import cultura.mak_plataforma.trabajo as trabajo
    import cultura.mak_plataforma.puente_issues as puente_issues
    import cultura.mak_plataforma.visual_index as visual_index
    from cultura.mak_plataforma import discernment, mineria_rd, providers
    from cultura.mak_research import memoria, research_lib

    results = {}
    providers._call_unobserved = lambda *_args, **_kwargs: "provider-ok"
    results["providers.call"] = providers.call("cerebras", "matrix prompt")

    original_urlopen = discernment.urllib.request.urlopen
    discernment.urllib.request.urlopen = lambda *_args, **_kwargs: _FakeResponse(
        {"response": "judge-ok"})
    try:
        results["discernment.call_ollama"] = discernment.call_ollama(
            "matrix judge prompt")
    finally:
        discernment.urllib.request.urlopen = original_urlopen

    results["percepcion.vision_imagen"] = percepcion.vision_imagen(
        str(root / "missing-image.png"))
    results["mineria_rd.vision_flyer"] = mineria_rd.vision_flyer(
        str(root / "missing-flyer.png"))

    memoria._index_unlocked = lambda **_kwargs: {
        "archivos": 0, "chunks": 0, "nuevos": 0}
    memoria._exclusive_index_lock = lambda: nullcontext()
    results["memoria.indexar"] = memoria.indexar()

    results["visual_index.build_index"] = None
    try:
        visual_index.build_index(
            inbox_path=root / "missing-inbox.json",
            media_root=root / "media", output_root=root / "index")
    except FileNotFoundError:
        results["visual_index.build_index"] = "expected_missing_input"

    puente_issues.config = lambda: {"activo": False, "etiqueta": "matrix"}
    results["puente_issues.una_pasada"] = puente_issues.una_pasada()

    trabajo.STATE = str(root / "trabajo-state.json")
    trabajo._main_unlocked = lambda: {"matrix": True}
    results["trabajo.main"] = trabajo.main()

    llm = research_lib.LLM(order="cerebras")
    llm._has_key = lambda _name: True
    llm._cerebras = lambda *_args: "llm-ok"
    results["research.LLM.call"] = llm.call("system", "user")

    skipped = []
    try:
        from cultura.mak_codex import codex_lib
        coder = codex_lib.CoderLLM(chain=[("win", "matrix-model")])
        coder._win = lambda *_args: "coder-ok"
        results["codex.CoderLLM.call"] = coder.call("system", "user")
    except (ImportError, ModuleNotFoundError) as exc:
        skipped.append({"producer": "codex.CoderLLM.call",
                        "reason": str(exc)[:200]})

    store = QueueStore(db)
    jobs = store.list_jobs()
    observations = store.list_observations()
    statuses = {job["status"] for job in jobs}
    expected = {
        "platform.providers.call", "platform.discernment.call_ollama",
        "curatoria.percepcion.vision_imagen", "platform.mineria_rd.vision_flyer",
        "research.memoria.indexar", "platform.visual_index.build_index",
        "platform.puente_issues.una_pasada", "platform.trabajo.main",
        "research.LLM.call",
    }
    observed_producers = {row["producer"] for row in observations}
    missing = sorted(expected - observed_producers)
    matrix_job_ids = {row["job_id"] for row in observations
                      if row["producer"] in expected}
    matrix_unobserved = [job["job_id"] for job in jobs
                         if job["job_id"] in matrix_job_ids
                         and job["status"] != "OBSERVED"]
    return {
        "ok": not missing and not matrix_unobserved,
        "jobs": len(jobs), "observations": len(observations),
        "observed_producers": sorted(observed_producers),
        "missing_producers": missing, "matrix_unobserved": matrix_unobserved,
        "skipped": skipped,
        "statuses": sorted(statuses), "results": results,
    }


def _gpu_contention_probe(lock: Path) -> dict:
    """Prove exclusive GPU admission without starting a model."""
    from cultura.mak_conductor.gpu_arbiter import GpuBudgetExceeded, GpuBusy
    from cultura.mak_conductor.runtime import shared_gpu_lease

    os.environ["MAK_CONDUCTOR_GPU"] = "1"
    holder_ready = threading.Event()
    release_holder = threading.Event()
    state = {"active": 0, "max_active": 0, "busy_rejected": False,
             "budget_rejected": False}
    lock_state = threading.Lock()

    def holder() -> None:
        with shared_gpu_lease(job_id="gpu-holder", estimated_vram_mb=3000,
                              timeout_s=1.0):
            with lock_state:
                state["active"] += 1
                state["max_active"] = max(state["max_active"], state["active"])
            holder_ready.set()
            release_holder.wait(2.0)
            with lock_state:
                state["active"] -= 1

    thread = threading.Thread(target=holder, daemon=True)
    thread.start()
    if not holder_ready.wait(2.0):
        return {"ok": False, "error": "gpu_holder_not_ready"}
    try:
        with shared_gpu_lease(job_id="gpu-contender", estimated_vram_mb=3000,
                              timeout_s=0.0):
            with lock_state:
                state["active"] += 1
                state["max_active"] = max(state["max_active"], state["active"])
                state["active"] -= 1
    except GpuBusy:
        state["busy_rejected"] = True
    try:
        with shared_gpu_lease(job_id="gpu-too-large", estimated_vram_mb=4097,
                              timeout_s=0.0):
            pass
    except GpuBudgetExceeded:
        state["budget_rejected"] = True
    finally:
        release_holder.set()
        thread.join(timeout=2.0)
    state["ok"] = (state["busy_rejected"] and state["budget_rejected"] and
                    state["max_active"] == 1)
    return state


def _crash_recovery_probe(db: Path) -> dict:
    """Claim a job in a child that exits abruptly, then recover its lease."""
    from cultura.mak_conductor.queue_store import ENQUEUED, QueueStore

    store = QueueStore(db, max_retries=2)
    job = store.enqueue("crash-recovery", {"probe": "process-crash"})
    code = (
        "import os, sys; "
        "from cultura.mak_conductor.queue_store import QueueStore; "
        "s=QueueStore(sys.argv[1], max_retries=2); "
        "j=s.claim_next('crashed-worker', lease_seconds=0.1, job_id=sys.argv[2]); "
        "os._exit(17 if j else 18)"
    )
    child = subprocess.run(
        [sys.executable, "-c", code, str(db), job["job_id"]],
        cwd=str(REPO_ROOT), env=dict(os.environ),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        check=False,
    )
    time.sleep(0.2)
    recovered = store.recover_expired_leases()
    status = store.get_job(job["job_id"])["status"]
    event_count = len(store.list_events(job_id=job["job_id"],
                                        event_type="lease_expired"))
    return {"ok": child.returncode == 17 and recovered == 1 and
            status == ENQUEUED and event_count == 1,
            "child_returncode": child.returncode, "recovered": recovered,
            "status": status, "lease_expired_events": event_count}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="", help="SQLite path for the probe")
    parser.add_argument("--lock", default="", help="GPU lock path")
    parser.add_argument("--producer-matrix", action="store_true",
                        help="also exercise adapted producers with fakes")
    parser.add_argument("--gpu-contention", action="store_true",
                        help="prove exclusive GPU admission without a model")
    parser.add_argument("--crash-recovery", action="store_true",
                        help="prove a dead worker lease is recoverable")
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="mak-conductor-probe-"))
    db = Path(args.db).expanduser() if args.db else root / "shadow.db"
    lock = Path(args.lock).expanduser() if args.lock else root / "gpu.lock"
    os.environ["MAK_CONDUCTOR_SHADOW"] = "1"
    os.environ["MAK_CONDUCTOR_ACTIVE"] = "0"
    os.environ["MAK_CONDUCTOR_GPU"] = "0"
    os.environ["MAK_DB_PATH"] = str(db)
    os.environ["MAK_GPU_LOCK_PATH"] = str(lock)

    try:
        from cultura.mak_conductor.runtime import enqueue_shadow, observe_shadow
        from cultura.mak_conductor.queue_store import ENQUEUED, OBSERVED, QueueStore
    except ImportError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2

    jobs = []
    errors = []

    def produce(index: int) -> None:
        try:
            jobs.append(enqueue_shadow(
                "probe", {"text": "same bounded concept"},
                producer="probe-%d" % index, template_version="probe-v1"))
        except Exception as exc:  # pragma: no cover - process boundary report
            errors.append(repr(exc))

    threads = [threading.Thread(target=produce, args=(i,)) for i in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if errors or not jobs or not all(jobs):
        print(json.dumps({"ok": False, "errors": errors,
                          "none_jobs": sum(job is None for job in jobs)}))
        return 1
    if len({job["job_id"] for job in jobs}) != 1:
        print(json.dumps({"ok": False, "error": "duplicate_jobs",
                          "job_ids": [job["job_id"] for job in jobs]}))
        return 1

    observe_shadow(jobs[0], producer="bounded-probe", result_status="READY",
                   validated=True, payload={"probe": True}, owner_pid=os.getpid())
    store = QueueStore(db)
    if store.get_job(jobs[0]["job_id"])["status"] != OBSERVED:
        print(json.dumps({"ok": False, "error": "observation_not_terminal"}))
        return 1

    orphan = store.enqueue("orphan", {"text": "lease"})
    store.claim_next("probe-dead-worker", lease_seconds=0.1)
    time.sleep(0.2)
    recovered = store.recover_expired_leases()
    orphan_status = store.get_job(orphan["job_id"])["status"]
    result = {"ok": recovered == 1 and orphan_status == ENQUEUED,
              "jobs_created": 1, "enqueue_callers": len(jobs),
              "observed_status": OBSERVED, "orphan_recovered": recovered,
              "orphan_status": orphan_status, "summary": store.summary(),
              "db": str(db)}
    if args.producer_matrix:
        matrix = _producer_matrix(db, lock, root)
        result["producer_matrix"] = matrix
        result["ok"] = result["ok"] and bool(matrix.get("ok"))
    if args.gpu_contention:
        gpu = _gpu_contention_probe(lock)
        result["gpu_contention"] = gpu
        result["ok"] = result["ok"] and bool(gpu.get("ok"))
    if args.crash_recovery:
        crash = _crash_recovery_probe(root / "crash-recovery.db")
        result["crash_recovery"] = crash
        result["ok"] = result["ok"] and bool(crash.get("ok"))
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
