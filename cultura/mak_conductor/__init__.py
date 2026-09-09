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
from .handler_registry import (HANDLERS, build_handler_registry,
                               handler_for_stage)
from .source_bridge import (import_codex_backlog, import_legacy_sources,
                            import_material, import_research_backlog)
from .producer_catalog import (CRONTAB_PRODUCER_HINTS, PRODUCER_CATALOG,
                               catalog_by_producer, uncovered_entries)

__all__ = ["Conductor", "GpuArbiter", "GpuBudgetExceeded", "GpuBusy",
           "QueueStore", "QueueWorker", "CRONTAB_PRODUCER_HINTS",
           "PRODUCER_CATALOG", "catalog_by_producer", "uncovered_entries",
           "HANDLERS", "build_handler_registry", "handler_for_stage",
           "import_material", "import_codex_backlog", "import_research_backlog",
           "import_legacy_sources"]
