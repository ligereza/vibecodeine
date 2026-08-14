"""Runtime bridge for the reversible MAK shadow phase.

The bridge is intentionally fail-safe for legacy producers: when shadow mode
is disabled it is a no-op, and when the evidence store is unavailable the
legacy operation continues while the caller can keep its own result status.
GPU arbitration is opt-in and fail-closed when explicitly enabled.
"""

from __future__ import annotations

import os
import hashlib
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from .gpu_arbiter import GpuArbiter
from .queue_store import QueueStore


_GPU_LOCAL = threading.local()
_RUNTIME_LOCAL = threading.local()


def _truthy(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in {
        "1", "true", "yes", "on"
    }


def shadow_enabled() -> bool:
    return _truthy("MAK_CONDUCTOR_SHADOW")


def active_enabled() -> bool:
    """Return whether a producer may route execution through the queue."""
    return (_truthy("MAK_CONDUCTOR_ACTIVE") and
            not bool(getattr(_RUNTIME_LOCAL, "legacy_execution", False)))


def queue_execution_enabled() -> bool:
    """Return whether the current call is executing inside a queue handler."""
    return bool(getattr(_RUNTIME_LOCAL, "queue_execution", False))


def gpu_arbiter_enabled() -> bool:
    # Active execution must never bypass the common GPU arbiter. The explicit
    # GPU flag remains useful for shadow-only contention experiments.
    return _truthy("MAK_CONDUCTOR_GPU") or active_enabled()


def store_path() -> Path:
    return Path(os.path.expanduser(
        os.environ.get("MAK_DB_PATH", "~/mak/state/mak.db")))


def gpu_lock_path() -> Path:
    return Path(os.path.expanduser(
        os.environ.get("MAK_GPU_LOCK_PATH", "~/mak/locks/gpu.lock")))


def gpu_capacity_mb() -> int:
    return int(os.environ.get("MAK_GPU_VRAM_MB", "4096"))


def _store() -> QueueStore:
    return QueueStore(store_path(), max_retries=int(
        os.environ.get("MAK_MAX_RETRIES", "3")))


def file_content_hash(path: str | os.PathLike[str], *, chunk_size: int = 1024 * 1024
                      ) -> str | None:
    """Return a bounded-memory SHA-256 for a produced file, if it exists."""
    digest = hashlib.sha256()
    try:
        with Path(path).expanduser().open("rb") as handle:
            for chunk in iter(lambda: handle.read(chunk_size), b""):
                digest.update(chunk)
    except (OSError, TypeError):
        return None
    return digest.hexdigest()


def enqueue_shadow(stage: str, payload: Mapping[str, Any], *,
                   producer: str, parent_job_id: str | None = None,
                   priority: int = 0, estimated_vram_mb: int = 0,
                   model: str = "", template_version: str = ""
                   ) -> dict[str, Any] | None:
    """Create or reuse an evidence job without taking control of execution."""
    # A queue-owned handler already has a durable parent job. Do not create a
    # second shadow record when legacy code calls another adapted producer.
    if not shadow_enabled() or queue_execution_enabled():
        return None
    body = dict(payload)
    body.setdefault("producer", producer)
    try:
        return _store().enqueue(
            stage, body, parent_job_id=parent_job_id, priority=priority,
            estimated_vram_mb=estimated_vram_mb, model=model,
            template_version=template_version,
        )
    except Exception:
        return None


def enqueue_active(stage: str, payload: Mapping[str, Any], *,
                   producer: str, parent_job_id: str | None = None,
                   priority: int = 0, estimated_vram_mb: int = 0,
                   model: str = "", template_version: str = "active-v1"
                   ) -> dict[str, Any] | None:
    """Enqueue production work only behind the explicit active flag."""
    if not active_enabled():
        return None
    return _store().enqueue(
        stage, dict(payload), parent_job_id=parent_job_id, priority=priority,
        estimated_vram_mb=estimated_vram_mb, model=model,
        template_version=template_version,
    )


def dispatch_sync(stage: str, payload: Mapping[str, Any], *,
                  producer: str, handler, estimated_vram_mb: int = 0,
                  model: str = "", template_version: str = "active-v1",
                  priority: int = 0,
                  parent_job_id: str | None = None) -> dict[str, Any] | None:
    """Route one synchronous caller through the durable queue when active.

    The queue remains the source of truth; inline dispatch preserves the
    existing caller contract until a bounded queue worker is deployed.
    """
    if not active_enabled():
        return None
    from .conductor import Conductor
    from .handler_registry import handler_for_stage
    job_store = _store()
    job = job_store.enqueue(
        stage, dict(payload), parent_job_id=parent_job_id, priority=priority,
        estimated_vram_mb=estimated_vram_mb, model=model,
        template_version=template_version,)
    if job.get("status") in {"COMPLETED", "FAILED", "DEAD", "OBSERVED"}:
        saved = job_store.get_result(job["job_id"])
        if saved is not None:
            saved.setdefault("job_id", job["job_id"])
            saved.setdefault("queue_status", job["status"])
            return saved
        return {"job_id": job["job_id"], "queue_status": job["status"]}
    canonical_handler = handler_for_stage(stage)
    selected_handler = canonical_handler or handler
    conductor = Conductor(
        job_store,
        GpuArbiter(gpu_lock_path(), capacity_mb=gpu_capacity_mb()),
        worker_id="inline-%s-%s" % (producer, os.getpid()),
        lease_seconds=float(os.environ.get("MAK_QUEUE_LEASE_SECONDS", "600")),
    )
    wait_seconds = max(0.1, float(os.environ.get(
        "MAK_QUEUE_WAIT_SECONDS", "900")))
    deadline = time.monotonic() + wait_seconds
    result = None
    while True:
        status = job_store.get_job(job["job_id"])
        if status and status["status"] in {"COMPLETED", "FAILED", "DEAD"}:
            saved = job_store.get_result(job["job_id"])
            if saved is not None:
                saved.setdefault("job_id", job["job_id"])
                saved.setdefault("queue_status", status["status"])
                return saved
            return {"job_id": job["job_id"],
                    "queue_status": status["status"],
                    "error": status.get("last_error") or "queue terminal without result"}
        result = conductor.dispatch_once(selected_handler, stages=[stage],
                                         job_id=job["job_id"])
        if result and result.get("status") == "WAITING_HUMAN":
            return result
        if time.monotonic() >= deadline:
            return result or {"job_id": job["job_id"], "queued": True,
                              "queue_status": "WAITING"}
        time.sleep(0.05 if not result or result.get("status") == "WAITING_GPU"
                   else 0.1)


@contextmanager
def legacy_execution_context() -> Iterator[None]:
    """Run a legacy handler without recursively re-routing it to the queue."""
    previous = getattr(_RUNTIME_LOCAL, "legacy_execution", False)
    _RUNTIME_LOCAL.legacy_execution = True
    try:
        yield
    finally:
        _RUNTIME_LOCAL.legacy_execution = previous


@contextmanager
def queue_execution_context() -> Iterator[None]:
    """Keep queue-owned resource accounting active inside legacy handlers."""
    previous = getattr(_RUNTIME_LOCAL, "queue_execution", False)
    _RUNTIME_LOCAL.queue_execution = True
    try:
        yield
    finally:
        _RUNTIME_LOCAL.queue_execution = previous


def observe_shadow(job: Mapping[str, Any] | None, *, producer: str,
                   result_status: str, validated: bool = False,
                   payload: Mapping[str, Any] | None = None,
                   started_at: float | None = None,
                   owner_pid: int | None = None,
                   artifact_id: str | None = None,
                   output_hash: str | None = None) -> None:
    """Attach legacy execution evidence to its shadow job when available."""
    if not job or not shadow_enabled():
        return
    try:
        _store().record_observation(
            job["job_id"], producer, result_status=result_status,
            validated=validated, payload=payload, started_at=started_at,
            owner_pid=owner_pid, artifact_id=artifact_id,
            output_hash=output_hash,
        )
    except Exception:
        return


def import_legacy_sources_shadow(*, limit: int | None = None
                                 ) -> dict[str, Any] | None:
    """Import legacy task rows into SQLite without consuming their sources."""
    if not shadow_enabled() or queue_execution_enabled():
        return None
    try:
        from .source_bridge import import_legacy_sources
        cap = int(limit if limit is not None else os.environ.get(
            "MAK_CONDUCTOR_SOURCE_LIMIT", "20"))
        return import_legacy_sources(
            _store(),
            material_path=os.path.expanduser(os.environ.get(
                "MAK_MATERIAL_PATH", "~/plataforma/material.jsonl")),
            backlog_path=os.path.expanduser(os.environ.get(
                "MAK_CODEX_BACKLOG_PATH", "~/plataforma/backlog_codex.txt")),
            research_path=os.path.expanduser(os.environ.get(
                "MAK_RESEARCH_BACKLOG_PATH", "~/plataforma/backlog.jsonl")),
            limit=max(0, cap),
        )
    except Exception as exc:
        return {"error": str(exc)[:300]}


@contextmanager
def shared_gpu_lease(*, job_id: str, estimated_vram_mb: int,
                     timeout_s: float | None = None,
                     priority: int = 0) -> Iterator[None]:
    """Use the common GPU lease only when the migration flag is enabled."""
    if not gpu_arbiter_enabled():
        yield
        return
    held = getattr(_GPU_LOCAL, "held", None)
    if held is not None:
        held_path, held_arbiter = held
        if held_path == str(gpu_lock_path().resolve()):
            # Nested calls in one producer (for example reindex -> embed) do
            # not compete with themselves; the outer owner still serializes
            # the whole process against every other MAK process.
            yield
            return
    timeout = (float(os.environ.get("MAK_GPU_WAIT_SECONDS", "30"))
               if timeout_s is None else float(timeout_s))
    arbiter = GpuArbiter(gpu_lock_path(), capacity_mb=gpu_capacity_mb())
    arbiter.acquire(job_id=job_id, estimated_vram_mb=estimated_vram_mb,
                    timeout_s=timeout, priority=priority)
    _GPU_LOCAL.held = (str(gpu_lock_path().resolve()), arbiter)
    try:
        yield
    finally:
        _GPU_LOCAL.held = None
        arbiter.release()


@contextmanager
def adopt_gpu_lease(arbiter: GpuArbiter) -> Iterator[None]:
    """Expose a conductor-held lease to nested legacy GPU helpers."""
    previous = getattr(_GPU_LOCAL, "held", None)
    _GPU_LOCAL.held = (str(arbiter.lock_path.resolve()), arbiter)
    try:
        yield
    finally:
        _GPU_LOCAL.held = previous


def reserve_external_call(provider: str, *, limit_count: int,
                          window: str = "hour") -> bool:
    """Record a bounded call; reject only during explicit enforcement."""
    if not (shadow_enabled() or active_enabled() or queue_execution_enabled()):
        return True
    try:
        allowed = _store().reserve_budget(provider, limit_count=limit_count,
                                           window=window)
        if not _truthy("MAK_CONDUCTOR_ENFORCE_BUDGET"):
            return True
        return allowed
    except Exception:
        return not _truthy("MAK_CONDUCTOR_ENFORCE_BUDGET")


def external_budget_limit(provider: str, default: int = 20) -> int:
    """Read a bounded hourly allowance without exposing provider credentials."""
    key = "MAK_%s_HOURLY_LIMIT" % str(provider).upper()
    try:
        return max(0, int(os.environ.get(key, str(default))))
    except ValueError:
        return max(0, int(default))


def conductor_import_hint() -> str:
    """Return the deployment path for diagnostics without mutating sys.path."""
    return os.environ.get("MAK_CONDUCTOR_PATH", str(Path(__file__).parent))


def install_live_import_path() -> None:
    """Allow mirrored scripts to import this package from the MAK checkout."""
    candidate = Path(os.path.expanduser(
        os.environ.get("MAK_CONDUCTOR_PATH", "~/flujo/cultura")))
    if candidate.is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
