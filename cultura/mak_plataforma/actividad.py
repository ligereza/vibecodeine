#!/usr/bin/env python3
"""mak activity inventory shared by MAK departments.

This is a small append-only telemetry utility, not a queue or a ledger. It
records the execution path that a product already has: trigger -> caller ->
queue -> model/resource. Product state remains in the department job files.
"""
import argparse
import json
import os
import tempfile
import time
import uuid


HOME = os.path.expanduser("~")
ACTIVITY_FILE = os.environ.get(
    "MAK_ACTIVITY_FILE", os.path.join(HOME, "plataforma", "actividad.jsonl"))
LOCK_FILE = ACTIVITY_FILE + ".lock"


def _append(row):
    """Append one JSON row without interleaving independent writers."""
    try:
        import fcntl
    except ImportError:  # pragma: no cover - Linux MAK owns this file
        fcntl = None
    parent = os.path.dirname(os.path.abspath(ACTIVITY_FILE))
    os.makedirs(parent, exist_ok=True)
    fd = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX)
        with open(ACTIVITY_FILE, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
    finally:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def record(kind, status, *, trigger="manual", caller="unknown", queue="",
           department="", job_id="", provider="", model="", resource="",
           activity_id="", started=None, ended=None, error="", extra=None):
    """Record one activity event and return its stable activity id."""
    activity_id = activity_id or ("act-%s-%s" % (
        time.strftime("%Y%m%d-%H%M%S"), uuid.uuid4().hex[:8]))
    row = {
        "schema": "mak-activity-v1",
        "activity_id": activity_id,
        "kind": kind,
        "status": status,
        "ts": int(time.time()),
        "trigger": str(trigger or "manual")[:120],
        "caller": str(caller or "unknown")[:160],
        "queue": str(queue or "")[:120],
        "department": str(department or "")[:80],
        "job_id": str(job_id or "")[:120],
        "provider": str(provider or "")[:100],
        "model": str(model or "")[:160],
        "resource": str(resource or "")[:80],
    }
    if started is not None:
        row["started"] = round(float(started), 3)
    if ended is not None:
        row["ended"] = round(float(ended), 3)
    if error:
        row["error"] = str(error)[:300]
    if isinstance(extra, dict):
        row.update({str(k): v for k, v in extra.items()})
    try:
        _append(row)
    except (OSError, ValueError):
        pass
    return activity_id


def read(limit=200):
    """Read the newest valid activity rows."""
    rows = []
    try:
        with open(ACTIVITY_FILE, encoding="utf-8") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except (TypeError, ValueError):
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        return []
    return rows[-max(0, int(limit)):]


def inventory(limit=200):
    """Return a compact inventory grouped by trigger/caller/queue/model."""
    rows = read(limit)
    groups = {}
    for row in rows:
        key = (row.get("trigger", ""), row.get("caller", ""),
               row.get("queue", ""), row.get("provider", ""),
               row.get("model", ""), row.get("resource", ""))
        item = groups.setdefault(key, {
            "trigger": key[0], "caller": key[1], "queue": key[2],
            "provider": key[3], "model": key[4], "resource": key[5],
            "attempts": 0, "finished": 0, "failed": 0,
            "last_status": "", "last_ts": 0,
        })
        item["attempts"] += 1
        status = row.get("status", "")
        if status in ("finished", "released", "ok"):
            item["finished"] += 1
        if status in ("failed", "rejected", "timeout", "busy"):
            item["failed"] += 1
        if row.get("ts", 0) >= item["last_ts"]:
            item["last_ts"] = row.get("ts", 0)
            item["last_status"] = status
    return {
        "schema": "mak-activity-inventory-v1",
        "ts": int(time.time()),
        "rows": len(rows),
        "groups": sorted(groups.values(), key=lambda x: x["last_ts"], reverse=True),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("read", "inventory"),
                        nargs="?", default="inventory")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    payload = read(args.limit) if args.command == "read" else inventory(args.limit)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
