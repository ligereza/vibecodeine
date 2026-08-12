"""Durable MAK queue consumer.

This is an internal execution primitive, not a human-facing interface. It can
run one bounded batch or one job at a time; systemd/cron activation remains a
separate, explicit deployment decision.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from .conductor import Conductor
from .gpu_arbiter import GpuArbiter
from .queue_store import QueueStore


Handler = Callable[[dict[str, Any]], Mapping[str, Any]]


class QueueWorker:
    """Run bounded work from one durable store with one handler registry."""

    def __init__(self, store: QueueStore, handlers: Mapping[str, Handler], *,
                 gpu_lock: str | os.PathLike[str],
                 gpu_capacity_mb: int = 4096, worker_id: str | None = None,
                 lease_seconds: float = 600.0):
        self.store = store
        self.handlers = dict(handlers)
        self.conductor = Conductor(
            store, GpuArbiter(gpu_lock, capacity_mb=gpu_capacity_mb),
            worker_id=worker_id or ("queue-worker-%s" % os.getpid()),
            lease_seconds=lease_seconds,
        )

    @classmethod
    def canonical(cls, store: QueueStore, *,
                  gpu_lock: str | os.PathLike[str],
                  gpu_capacity_mb: int = 4096,
                  worker_id: str | None = None,
                  lease_seconds: float = 600.0) -> "QueueWorker":
        """Build the single lazy registry used by a deployed worker."""
        from .handler_registry import build_handler_registry
        return cls(store, build_handler_registry(), gpu_lock=gpu_lock,
                   gpu_capacity_mb=gpu_capacity_mb, worker_id=worker_id,
                   lease_seconds=lease_seconds)

    def run_once(self, *, stages: Iterable[str] | None = None,
                 job_id: str | None = None) -> dict[str, Any] | None:
        """Claim and execute at most one job."""
        return self.conductor.dispatch_once(
            self._handle, stages=stages, job_id=job_id)

    def run_batch(self, *, max_jobs: int = 1,
                  stages: Iterable[str] | None = None,
                  idle_sleep: float = 0.0) -> list[dict[str, Any]]:
        """Run a bounded batch; never become an unbounded daemon implicitly."""
        results = []
        for _ in range(max(0, int(max_jobs))):
            result = self.run_once(stages=stages)
            if result is None:
                break
            results.append(result)
            if idle_sleep:
                time.sleep(max(0.0, float(idle_sleep)))
        return results

    def _handle(self, job: dict[str, Any]) -> Mapping[str, Any]:
        handler = self.handlers.get(str(job.get("stage")))
        if handler is None:
            return {"validated": False,
                    "error": "no handler for stage %s" % job.get("stage")}
        result = handler(job)
        if not isinstance(result, Mapping):
            return {"validated": False, "error": "handler returned non-mapping"}
        return result
