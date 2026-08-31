"""Reversible MAK convergence primitives.

This package is deliberately not wired into cron or the live services yet.
It provides the durable queue, idempotency helpers, audit queries, and one
cross-process GPU arbiter needed for the shadow phase of the MAK convergence
plan.
"""

from .conductor import Conductor
from .gpu_arbiter import GpuArbiter, GpuBudgetExceeded, GpuBusy
from .queue_store import QueueStore
from .queue_worker import QueueWorker

__all__ = ["Conductor", "GpuArbiter", "GpuBudgetExceeded", "GpuBusy",
           "QueueStore", "QueueWorker"]
