#!/usr/bin/env python3
"""Provider-free shadow import probe for legacy MAK task stores."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cultura.mak_conductor.queue_store import QueueStore
from cultura.mak_conductor.queue_worker import QueueWorker
from cultura.mak_conductor.source_bridge import (compare_imported_jobs,
                                                  durable_projection,
                                                  import_legacy_sources)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", required=True)
    parser.add_argument("--backlog", required=True)
    parser.add_argument("--research", required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--execute-contract-shadow", action="store_true",
                        help="execute imported jobs with deterministic contract handlers only")
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="mak-source-probe-"))
    store = QueueStore(root / "shadow.db")
    first = import_legacy_sources(
        store, material_path=args.material, backlog_path=args.backlog,
        research_path=args.research,
        limit=args.limit)
    expected = (first["material"]["created"] + first["codex"]["created"] +
                first["research"]["created"])
    comparison = compare_imported_jobs(store, first)
    second = import_legacy_sources(
        store, material_path=args.material, backlog_path=args.backlog,
        research_path=args.research,
        limit=args.limit)
    contract_execution = None
    if args.execute_contract_shadow:
        def contract_handler(job):
            projection = durable_projection(job)
            if projection is None:
                return {"validated": False, "error": "invalid durable projection"}
            encoded = json.dumps(projection, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":"))
            return {
                "validated": True,
                "shadow_execution": "contract-only",
                "output_hash": hashlib.sha256(
                    encoded.encode("utf-8")).hexdigest(),
                "artifacts": [{"kind": "contract_shadow_output",
                               "content": encoded}],
            }

        worker = QueueWorker(
            store,
            {stage: contract_handler for stage in (
                "legacy_material_task", "legacy_codex_task",
                "legacy_research_task")},
            gpu_lock=root / "gpu.lock", worker_id="contract-shadow",
            lease_seconds=30.0,
        )
        execution_results = worker.run_batch(
            max_jobs=expected,
            stages=["legacy_material_task", "legacy_codex_task",
                    "legacy_research_task"],
        )
        execution_jobs = [store.get_job(job_id) for details in first.values()
                          if isinstance(details, dict)
                          for job_id in details.get("jobs") or []]
        contract_execution = {
            "mode": "contract-only",
            "attempted": len(execution_results),
            "completed": sum(1 for job in execution_jobs
                              if job and job.get("status") == "COMPLETED"),
            "results": execution_results,
            "events": len(store.list_events(event_type="job_completed")),
        }
    jobs = store.list_jobs()
    result = {"ok": (expected > 0 and comparison["ok"] and
                      first["material"]["created"] == second["material"]["deduplicated"]
                      and first["codex"]["created"] == second["codex"]["deduplicated"]
                      and first["research"]["created"] == second["research"]["deduplicated"]
                      and len(jobs) == expected),
              "db": str(root / "shadow.db"), "first": first, "second": second,
              "jobs": len(jobs), "statuses": sorted({j["status"] for j in jobs}),
              "comparison": comparison, "contract_execution": contract_execution}
    if args.execute_contract_shadow:
        result["ok"] = bool(result["ok"] and contract_execution and
                             contract_execution["attempted"] == expected and
                             contract_execution["completed"] == expected)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
