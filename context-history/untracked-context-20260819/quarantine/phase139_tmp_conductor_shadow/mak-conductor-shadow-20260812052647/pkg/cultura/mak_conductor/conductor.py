"""Generic shadow dispatcher for the MAK convergence plan."""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from .gpu_arbiter import GpuArbiter, GpuBudgetExceeded, GpuBusy
from .queue_store import QueueStore


class Conductor:
    """Claim, serialize, validate, and record one job without live wiring."""

    def __init__(self, store: QueueStore, arbiter: GpuArbiter, *,
                 worker_id: str | None = None, lease_seconds: float = 600.0):
        self.store = store
        self.arbiter = arbiter
        self.worker_id = worker_id or ("conductor-%s" % os.getpid())
        self.lease_seconds = float(lease_seconds)

    def enqueue(self, stage: str, payload: Mapping[str, Any], **kwargs: Any
                ) -> dict[str, Any]:
        return self.store.enqueue(stage, payload, **kwargs)

    def dispatch_once(
        self,
        handler: Callable[[dict[str, Any]], Mapping[str, Any]],
        *,
        stages: Iterable[str] | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Run one claimed job; completion requires explicit validation.

        The handler is deliberately dependency-free. Existing producers can
        be adapted later without changing queue semantics or publishing any
        artifact before the validation boundary.
        """
        job = self.store.claim_next(self.worker_id, stages=stages,
                                    lease_seconds=self.lease_seconds,
                                    job_id=job_id)
        if job is None:
            return None
        job_id = job["job_id"]
        started = time.monotonic()
        if self._requires_human_gate(job):
            payload = self._payload(job)
            requested_decision = str(payload.get("decision_id") or "").strip()
            if (requested_decision and
                    self.store.decision_belongs_to_job(requested_decision,
                                                       job_id)):
                decision_id = requested_decision
            else:
                decision_id = self.store.ensure_human_gate(
                    job_id,
                    estimated_cost=float(payload.get("estimated_cost") or 0),
                    note=str(payload.get("gate_note") or
                             "Human approval required before publication"))
            if not self.store.decision_approved(decision_id):
                gate_status = self.store.human_gate_status(job_id)
                if gate_status == "REJECTED":
                    self.store.fail(job_id, self.worker_id,
                                    "human gate rejected", retriable=False)
                    return {"job_id": job_id, "status": "REJECTED",
                            "decision_id": decision_id}
                self.store.defer(job_id, self.worker_id,
                                 reason="waiting for human gate")
                self.store.record_event(
                    "human_gate_wait", job_id=job_id, status="PENDING",
                    decision_id=decision_id,
                    payload={"decision_id": decision_id},
                )
                return {"job_id": job_id, "status": "WAITING_HUMAN",
                        "decision_id": decision_id}
        if not self.store.start(job_id, self.worker_id,
                                lease_seconds=self.lease_seconds):
            return {"job_id": job_id, "status": "LOST_CLAIM"}
        heartbeat_stop = threading.Event()

        def renew_lease():
            interval = min(30.0, max(0.1, self.lease_seconds / 3.0))
            while not heartbeat_stop.wait(interval):
                if not self.store.heartbeat(
                        job_id, self.worker_id,
                        lease_seconds=self.lease_seconds):
                    break

        heartbeat_thread = threading.Thread(target=renew_lease, daemon=True)
        heartbeat_thread.start()
        try:
            estimate = int(job.get("estimated_vram_mb") or 0)
            if estimate:
                self.arbiter.acquire(job_id=job_id,
                                     estimated_vram_mb=estimate,
                                     timeout_s=0.0)
            try:
                result = dict(handler(job))
                if not self.store.record_result(job_id, self.worker_id, result):
                    raise RuntimeError("result persistence lost")
            finally:
                if estimate:
                    self.arbiter.release()
            if not self.store.begin_validation(job_id, self.worker_id):
                self.store.fail(job_id, self.worker_id,
                                "validation transition lost", retriable=False)
                status = "FAILED"
            elif not bool(result.get("validated")):
                self.store.fail(job_id, self.worker_id,
                                str(result.get("error") or
                                    "handler did not validate output"),
                                retriable=False)
                status = "FAILED"
            else:
                artifact_ids = result.get("artifact_ids") or []
                completed = self.store.complete(
                    job_id, self.worker_id, artifact_ids=artifact_ids)
                if completed:
                    status = "COMPLETED"
                else:
                    self.store.fail(job_id, self.worker_id,
                                    "completion transition lost",
                                    retriable=False)
                    status = "FAILED"
            self.store.record_event(
                "job_end", job_id=job_id, status=status,
                duration_ms=int((time.monotonic() - started) * 1000),
                payload={"validated": bool(result.get("validated"))},
            )
            return {"job_id": job_id, "status": status, **result}
        except GpuBusy as exc:
            self.store.defer(job_id, self.worker_id, reason=str(exc))
            self.store.record_event("gpu_wait", job_id=job_id,
                                    status="WAITING_GPU",
                                    payload={"error": str(exc)[:2000]})
            return {"job_id": job_id, "status": "WAITING_GPU"}
        except GpuBudgetExceeded as exc:
            self.store.fail(job_id, self.worker_id, str(exc), retriable=False)
            self.store.record_event("job_error", job_id=job_id, status="FAILED",
                                    payload={"error": str(exc)[:2000],
                                             "retriable": False})
            return {"job_id": job_id, "status": "FAILED", "error": str(exc)}
        except Exception as exc:  # noqa: BLE001 - queue must record failures
            self.store.fail(job_id, self.worker_id, str(exc), retriable=True)
            self.store.record_event("job_error", job_id=job_id, status="FAILED",
                                    payload={"error": str(exc)[:2000]})
            return {"job_id": job_id, "status": "REQUEUED", "error": str(exc)}
        finally:
            heartbeat_stop.set()
            heartbeat_thread.join(timeout=1.0)

    @staticmethod
    def _payload(job: Mapping[str, Any]) -> dict[str, Any]:
        import json
        try:
            value = json.loads(str(job.get("payload_json") or "{}"))
        except (TypeError, ValueError):
            value = {}
        return value if isinstance(value, dict) else {}

    @classmethod
    def _requires_human_gate(cls, job: Mapping[str, Any]) -> bool:
        payload = cls._payload(job)
        return str(job.get("stage")) in {
            "publicacion", "promotion", "branch_write", "branch_mutation"
        } or bool(
            payload.get("requires_human"))
