#!/usr/bin/env python3
"""Run a bounded batch from the canonical MAK conductor registry."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cultura.mak_conductor.queue_store import QueueStore
from cultura.mak_conductor.queue_worker import QueueWorker
from cultura.mak_conductor.source_bridge import (compare_imported_jobs,
                                                  import_legacy_sources)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-jobs", type=int, default=1)
    parser.add_argument("--stage", action="append", default=[])
    parser.add_argument("--db", default=os.environ.get("MAK_DB_PATH", ""))
    parser.add_argument("--gpu-lock", default=os.environ.get("MAK_GPU_LOCK_PATH", ""))
    parser.add_argument("--import-legacy", action="store_true",
                        help="read legacy sources into the durable queue first")
    parser.add_argument("--observe-only", action="store_true",
                        help="import and compare evidence without claiming jobs")
    parser.add_argument("--sentinel", default="",
                        help="required file that explicitly permits observe-only execution")
    parser.add_argument("--source-limit", type=int,
                        default=int(os.environ.get("MAK_CONDUCTOR_SOURCE_LIMIT", "1")))
    parser.add_argument("--material", default=os.environ.get(
        "MAK_MATERIAL_PATH", "~/plataforma/material.jsonl"))
    parser.add_argument("--backlog", default=os.environ.get(
        "MAK_CODEX_BACKLOG_PATH", "~/plataforma/backlog_codex.txt"))
    parser.add_argument("--research", default=os.environ.get(
        "MAK_RESEARCH_BACKLOG_PATH", "~/plataforma/backlog.jsonl"))
    args = parser.parse_args()
    if args.observe_only:
        sentinel_value = args.sentinel or os.environ.get(
            "MAK_CONDUCTOR_OBSERVE_SENTINEL", "")
        if not sentinel_value:
            print(__import__("json").dumps({
                "mode": "observe-only", "ok": False,
                "error": "sentinel_required",
            }, sort_keys=True))
            return 3
        sentinel = Path(sentinel_value).expanduser()
        if not sentinel.is_file():
            print(__import__("json").dumps({
                "mode": "observe-only", "ok": False,
                "error": "sentinel_missing", "sentinel": str(sentinel),
            }, sort_keys=True))
            return 3
        if not args.db and not os.environ.get("MAK_DB_PATH"):
            print(__import__("json").dumps({
                "mode": "observe-only", "ok": False,
                "error": "shadow_db_required",
            }, sort_keys=True))
            return 3
    db = Path(args.db).expanduser() if args.db else Path("~/mak/state/mak.db").expanduser()
    lock = (Path(args.gpu_lock).expanduser() if args.gpu_lock else
            Path("~/mak/locks/gpu.lock").expanduser())
    store = QueueStore(db)
    imported = None
    if args.import_legacy:
        imported = import_legacy_sources(
            store, material_path=Path(args.material).expanduser(),
            backlog_path=Path(args.backlog).expanduser(),
            research_path=Path(args.research).expanduser(),
            limit=max(0, args.source_limit),
        )
    if args.observe_only:
        comparison = compare_imported_jobs(store, imported or {})
        print(__import__("json").dumps({"mode": "observe-only",
                                        "imported": imported,
                                        "comparison": comparison,
                                        "summary": store.summary()},
                                       ensure_ascii=False, sort_keys=True))
        return 0 if comparison.get("ok", True) else 1
    worker = QueueWorker.canonical(
        store, gpu_lock=lock,
        gpu_capacity_mb=int(os.environ.get("MAK_GPU_VRAM_MB", "4096")),
        worker_id="mak-conductor-%s" % os.getpid(),
        lease_seconds=float(os.environ.get("MAK_QUEUE_LEASE_SECONDS", "600")),
    )
    results = worker.run_batch(max_jobs=max(0, args.max_jobs),
                              stages=args.stage or None)
    print(__import__("json").dumps({"imported": imported, "results": results},
                                   ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
