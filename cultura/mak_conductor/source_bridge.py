"""Bounded, read-only import of legacy JSONL task sources into SQLite.

The bridge is for shadow measurement first. It never changes the source
JSONL, never claims the task was executed, and uses a stable source identity
as the queue idempotency key. A later active cutover can acknowledge a source
row only after its queue job has completed and passed validation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .idempotency import canonical_json
from .queue_store import QueueStore


_ACTIVE_STATUSES = {"ENQUEUED", "CLAIMED", "RUNNING", "VALIDATING"}


def _collect_job(job: dict[str, Any], jobs: list[str], *,
                 counters: dict[str, int]) -> None:
    if job.get("created"):
        counters["created"] += 1
    else:
        counters["deduplicated"] += 1
    # Terminal source jobs are evidence of already-handled work. Do not return
    # them to the cron drain, otherwise a completed row at the top of a legacy
    # file would starve every later row.
    if str(job.get("status")) in _ACTIVE_STATUSES:
        jobs.append(str(job["job_id"]))
    else:
        counters["terminal"] += 1


def _source_key(source: str, identity: str) -> str:
    raw = ("legacy|%s|%s" % (source, identity)).encode("utf-8")
    return "legacy:%s" % hashlib.sha256(raw).hexdigest()


def _payload_of(job: dict[str, Any]) -> dict[str, Any]:
    try:
        value = json.loads(str(job.get("payload_json") or "{}"))
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _route(department: str, handler: str, mode: str, text: str,
           *, source: str, record_id: str, revision: str | None,
           line: int, density: str = "medio") -> dict[str, Any]:
    return {
        "source": source,
        "source_record_id": record_id,
        "source_revision": revision,
        "source_line": line,
        "department": department,
        "handler": handler,
        "mode": mode,
        "text": text,
        "density": density,
    }


def legacy_projection(source: str, record: Any, line: int
                      ) -> dict[str, Any] | None:
    """Project one untouched legacy record into its old execution contract."""
    if source == "material":
        if not isinstance(record, dict) or record.get("estado") != "pendiente":
            return None
        revision = hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()
        task = record
        department = "codex" if task.get("depto") == "codex" else "research"
        return _route(
            department, "run_pedido" if department == "codex" else "run_tema",
            str(task.get("modo") or ("generar" if department == "codex"
                                      else "research")),
            str(task.get("texto") or "").strip(), source="material.jsonl",
            record_id=str(task.get("id") or "anonymous"), revision=revision,
            line=line,
        )
    if source == "codex-backlog":
        text = str(record or "").strip()
        if not text or text.startswith("#"):
            return None
        identity = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return _route("codex", "run_pedido", "generar", text,
                      source="backlog_codex.txt", record_id=identity,
                      revision=None, line=line)
    if source == "research-backlog":
        if not isinstance(record, dict) or record.get("estado") != "pendiente":
            return None
        topic = str(record.get("pregunta") or record.get("tema") or "").strip()
        if not topic:
            return None
        revision = hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()
        return _route("research", "run_tema",
                      "research", topic, source="backlog.jsonl",
                      record_id=str(record.get("id") or "anonymous"),
                      revision=revision, line=line)
    return None


def durable_projection(job: dict[str, Any]) -> dict[str, Any] | None:
    """Project an imported durable job into the legacy execution contract."""
    payload = _payload_of(job)
    source = str(payload.get("source") or "")
    line = int(payload.get("source_line") or 0)
    record_id = str(payload.get("source_record_id") or "anonymous")
    revision = payload.get("source_revision")
    if source == "material.jsonl":
        task = payload.get("task")
        if not isinstance(task, dict):
            return None
        department = "codex" if task.get("depto") == "codex" else "research"
        return _route(
            department, "run_pedido" if department == "codex" else "run_tema",
            str(task.get("modo") or ("generar" if department == "codex"
                                      else "research")),
            str(task.get("texto") or "").strip(), source=source,
            record_id=record_id, revision=revision, line=line)
    if source == "backlog_codex.txt":
        return _route("codex", "run_pedido", str(payload.get("mode") or "generar"),
                      str(payload.get("text") or "").strip(), source=source,
                      record_id=record_id, revision=None, line=line,
                      density=str(payload.get("density") or "medio"))
    if source == "backlog.jsonl":
        return _route("research", "run_tema", str(payload.get("mode") or "research"),
                      str(payload.get("topic") or "").strip(), source=source,
                      record_id=record_id, revision=revision, line=line,
                      density=str(payload.get("density") or "medio"))
    return None


def _record_at(source: str, path: str | Path, line: int) -> Any:
    if source == "codex-backlog":
        try:
            rows = Path(path).expanduser().read_text(
                encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return None
        return rows[line - 1] if 0 < line <= len(rows) else None
    for number, row in _read_jsonl(path):
        if number == line:
            return row
    return None


def compare_imported_jobs(store: QueueStore,
                          imported: dict[str, Any]) -> dict[str, Any]:
    """Compare durable jobs with the exact source records they represent.

    The comparison is read-only with respect to legacy files. It writes only
    auditable comparison artifacts/events into the supplied queue database.
    """
    comparisons = []
    artifact_ids = []
    mismatches = []
    for source_name, details in imported.items():
        if not isinstance(details, dict):
            continue
        source = {"material": "material", "codex": "codex-backlog",
                  "research": "research-backlog"}.get(source_name)
        for job_id in details.get("jobs") or []:
            job = store.get_job(str(job_id))
            if not job:
                mismatches.append({"job_id": job_id, "error": "missing_job"})
                continue
            payload = _payload_of(job)
            raw = _record_at(source or "", payload.get("source_path", ""),
                             int(payload.get("source_line") or 0))
            legacy = legacy_projection(source or "", raw,
                                       int(payload.get("source_line") or 0))
            durable = durable_projection(job)
            legacy_hash = hashlib.sha256(
                canonical_json(legacy or {}).encode("utf-8")).hexdigest()
            durable_hash = hashlib.sha256(
                canonical_json(durable or {}).encode("utf-8")).hexdigest()
            match = bool(legacy is not None and durable is not None and
                         legacy_hash == durable_hash)
            comparison = {"job_id": job_id, "source": source,
                          "match": match, "legacy_hash": legacy_hash,
                          "durable_hash": durable_hash,
                          "source_line": payload.get("source_line")}
            content = canonical_json({"comparison": comparison,
                                      "legacy": legacy,
                                      "durable": durable})
            artifact = store.record_artifact(
                str(job_id), "shadow_input_comparison", content)
            store.record_event(
                "shadow_input_comparison", job_id=str(job_id),
                artifact_id=artifact["artifact_id"],
                status="MATCH" if match else "MISMATCH", payload=comparison)
            comparison["artifact_id"] = artifact["artifact_id"]
            comparisons.append(comparison)
            artifact_ids.append(artifact["artifact_id"])
            if not match:
                mismatches.append(comparison)
    return {"ok": not mismatches, "checked": len(comparisons),
            "matched": sum(1 for row in comparisons if row["match"]),
            "mismatched": len(mismatches), "artifact_ids": artifact_ids,
            "mismatches": mismatches, "comparisons": comparisons}


def _read_jsonl(path: str | Path):
    try:
        with Path(path).expanduser().open(encoding="utf-8",
                                           errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                text = line.strip()
                if not text:
                    continue
                try:
                    value = json.loads(text)
                except (TypeError, ValueError):
                    yield number, None
                    continue
                yield number, value
    except OSError:
        return


def import_material(path: str | Path, store: QueueStore, *,
                    limit: int = 20) -> dict[str, Any]:
    """Import pending material rows without consuming or rewriting them."""
    counters = {"created": 0, "deduplicated": 0, "terminal": 0}
    invalid = seen = 0
    jobs = []
    for number, row in _read_jsonl(path):
        if len(jobs) >= max(0, int(limit)):
            break
        if not isinstance(row, dict):
            invalid += 1
            continue
        if row.get("estado") != "pendiente":
            continue
        seen += 1
        revision = hashlib.sha256(canonical_json(row).encode("utf-8")).hexdigest()
        identity = "%s:%s" % (str(row.get("id") or "anonymous"), revision)
        payload = {"source": "material.jsonl", "source_path": str(path),
                   "source_record_id": str(row.get("id") or "anonymous"),
                   "source_revision": revision, "source_line": number,
                   "task": row}
        job = store.enqueue(
            "legacy_material_task", payload,
            idempotency_key=_source_key("material", identity),
            template_version="legacy-material-v1",
        )
        _collect_job(job, jobs, counters=counters)
    return {"source": "material", "created": counters["created"],
            "deduplicated": counters["deduplicated"],
            "terminal": counters["terminal"], "seen": seen,
            "invalid": invalid, "jobs": jobs}


def import_codex_backlog(path: str | Path, store: QueueStore, *,
                         limit: int = 20) -> dict[str, Any]:
    """Import non-comment backlog lines without removing or marking them."""
    counters = {"created": 0, "deduplicated": 0, "terminal": 0}
    seen = 0
    jobs = []
    try:
        lines = Path(path).expanduser().read_text(encoding="utf-8",
                                                   errors="replace").splitlines()
    except OSError:
        lines = []
    for number, line in enumerate(lines, 1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if len(jobs) >= max(0, int(limit)):
            break
        seen += 1
        identity = hashlib.sha256(text.encode("utf-8")).hexdigest()
        payload = {"source": "backlog_codex.txt", "source_path": str(path),
                   "source_record_id": identity, "source_line": number,
                   "text": text, "mode": "generar", "density": "medio"}
        job = store.enqueue(
            "legacy_codex_task", payload,
            idempotency_key=_source_key("codex-backlog", identity),
            template_version="legacy-codex-backlog-v1",
        )
        _collect_job(job, jobs, counters=counters)
    return {"source": "codex-backlog", "created": counters["created"],
            "deduplicated": counters["deduplicated"],
            "terminal": counters["terminal"], "seen": seen, "jobs": jobs}


def import_research_backlog(path: str | Path, store: QueueStore, *,
                            limit: int = 20) -> dict[str, Any]:
    """Import pending research questions without marking the JSONL rows."""
    counters = {"created": 0, "deduplicated": 0, "terminal": 0}
    invalid = seen = 0
    jobs = []
    for number, row in _read_jsonl(path):
        if len(jobs) >= max(0, int(limit)):
            break
        if not isinstance(row, dict):
            invalid += 1
            continue
        if row.get("estado") != "pendiente":
            continue
        seen += 1
        topic = str(row.get("pregunta") or row.get("tema") or "").strip()
        if not topic:
            invalid += 1
            continue
        revision = hashlib.sha256(canonical_json(row).encode("utf-8")).hexdigest()
        identity = "%s:%s" % (str(row.get("id") or "anonymous"), revision)
        payload = {"source": "backlog.jsonl", "source_path": str(path),
                   "source_record_id": str(row.get("id") or "anonymous"),
                   "source_revision": revision, "source_line": number,
                   "task": row, "mode": "research", "topic": topic,
                   "density": "medio"}
        job = store.enqueue(
            "legacy_research_task", payload,
            idempotency_key=_source_key("research-backlog", identity),
            template_version="legacy-research-backlog-v1",
        )
        _collect_job(job, jobs, counters=counters)
    return {"source": "research-backlog", "created": counters["created"],
            "deduplicated": counters["deduplicated"],
            "terminal": counters["terminal"], "seen": seen,
            "invalid": invalid, "jobs": jobs}


def import_legacy_sources(store: QueueStore, *, material_path: str | Path,
                          backlog_path: str | Path,
                          research_path: str | Path | None = None,
                          limit: int = 20
                          ) -> dict[str, Any]:
    """Import the explicitly selected legacy source files, read-only.

    ``research_path`` is intentionally opt-in.  Older code silently fell back
    to ``~/plataforma/backlog.jsonl`` when the caller omitted it; that made a
    test or an isolated checkout ingest the live deployment backlog and made
    the result depend on the machine's home directory.  Production entry
    points pass ``MAK_RESEARCH_BACKLOG_PATH`` explicitly (see the cron and
    shadow runtime callers), while isolated callers receive a durable
    ``NOT_CONFIGURED`` result until they provide a source.
    """
    research = (import_research_backlog(research_path, store, limit=limit)
                if research_path is not None else {
                    "source": "research-backlog", "created": 0,
                    "deduplicated": 0, "terminal": 0, "seen": 0,
                    "invalid": 0, "jobs": [],
                    "status": "NOT_CONFIGURED",
                    "reason": "research_path_not_provided",
                })
    return {
        "material": import_material(material_path, store, limit=limit),
        "codex": import_codex_backlog(backlog_path, store, limit=limit),
        "research": research,
    }
