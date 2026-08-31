"""SQLite WAL queue and append-only evidence store for MAK."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Iterable, Mapping

from .idempotency import (SCHEMA_VERSION, artifact_content_hash,
                          canonical_json, job_idempotency_key)


ENQUEUED = "ENQUEUED"
CLAIMED = "CLAIMED"
RUNNING = "RUNNING"
VALIDATING = "VALIDATING"
COMPLETED = "COMPLETED"
FAILED = "FAILED"
DEAD = "DEAD"
OBSERVED = "OBSERVED"

_LEASED = (CLAIMED, RUNNING, VALIDATING)


class QueueStore:
    """Small transactional store; each operation uses its own connection."""

    _init_lock = threading.RLock()

    def __init__(self, db_path: str | os.PathLike[str], *,
                 max_retries: int = 3) -> None:
        self.db_path = Path(db_path).expanduser()
        self.max_retries = max(0, int(max_retries))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0,
                               isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    def _initialize(self) -> None:
        # Several producers can first touch the shadow store at once. Serialize
        # schema setup inside one MAK process before SQLite handles the writes.
        with type(self)._init_lock:
            for attempt in range(6):
                try:
                    self._initialize_locked()
                    return
                except sqlite3.OperationalError as exc:
                    if "locked" not in str(exc).lower() or attempt >= 5:
                        raise
                    time.sleep(0.05 * (attempt + 1))

    def _initialize_locked(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    parent_job_id TEXT REFERENCES jobs(job_id),
                    idempotency_key TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    owner_id TEXT,
                    lease_expires_at REAL,
                    priority INTEGER NOT NULL DEFAULT 0,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    estimated_vram_mb INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    result_json TEXT
                );
                CREATE INDEX IF NOT EXISTS jobs_claim_idx
                    ON jobs(status, priority DESC, created_at ASC);
                CREATE INDEX IF NOT EXISTS jobs_lease_idx
                    ON jobs(status, lease_expires_at);
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    kind TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    staging_path TEXT,
                    canonical_path TEXT,
                    created_at REAL NOT NULL,
                    UNIQUE(kind, content_hash)
                );
                CREATE TABLE IF NOT EXISTS artifact_links (
                    job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
                    relation TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    PRIMARY KEY (job_id, artifact_id, relation)
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    job_id TEXT REFERENCES jobs(job_id),
                    event_type TEXT NOT NULL,
                    cron_id TEXT,
                    provider TEXT,
                    model TEXT,
                    artifact_id TEXT,
                    decision_id TEXT,
                    vram_mb INTEGER,
                    duration_ms INTEGER,
                    status TEXT,
                    payload_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    producer TEXT NOT NULL,
                    owner_pid INTEGER,
                    result_status TEXT NOT NULL,
                    validated INTEGER NOT NULL DEFAULT 0,
                    artifact_id TEXT REFERENCES artifacts(artifact_id),
                    output_hash TEXT,
                    started_at REAL,
                    finished_at REAL NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS observations_job_idx
                    ON observations(job_id, finished_at);
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    status TEXT NOT NULL,
                    actor TEXT,
                    approved INTEGER,
                    note TEXT,
                    estimated_cost REAL,
                    created_at REAL NOT NULL,
                    decided_at REAL
                );
                CREATE INDEX IF NOT EXISTS decisions_job_idx
                    ON decisions(job_id, status, created_at);
                CREATE TABLE IF NOT EXISTS external_budget (
                    provider TEXT NOT NULL,
                    window TEXT NOT NULL,
                    window_start INTEGER NOT NULL,
                    used INTEGER NOT NULL DEFAULT 0,
                    limit_count INTEGER NOT NULL,
                    PRIMARY KEY (provider, window, window_start)
                );
                CREATE TABLE IF NOT EXISTS store_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            conn.execute(
                """INSERT INTO store_meta(key, value) VALUES (?, ?)
                   ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
                ("schema_version", SCHEMA_VERSION),
            )
            columns = {row[1] for row in conn.execute(
                "PRAGMA table_info(jobs)")}
            if "result_json" not in columns:
                conn.execute("ALTER TABLE jobs ADD COLUMN result_json TEXT")

    def _event_unlocked(self, conn: sqlite3.Connection, event_type: str,
                        *, job_id: str | None = None,
                        status: str | None = None,
                        payload: Mapping[str, Any] | None = None) -> None:
        conn.execute(
            """INSERT INTO events
               (event_id, job_id, event_type, status, payload_json,
                created_at) VALUES (?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), job_id, event_type, status,
             canonical_json(payload or {}), time.time()),
        )

    @staticmethod
    def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row is not None else None

    def enqueue(self, stage: str, payload: Mapping[str, Any], *,
                idempotency_key: str | None = None,
                parent_job_id: str | None = None, priority: int = 0,
                estimated_vram_mb: int = 0, model: str = "",
                template_version: str = "") -> dict[str, Any]:
        key = idempotency_key or job_idempotency_key(
            stage, payload, parent_job_id=parent_job_id, model=model,
            template_version=template_version)
        now = time.time()
        job_id = str(uuid.uuid4())
        payload_json = canonical_json(dict(payload))
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT * FROM jobs WHERE idempotency_key = ?", (key,)
            ).fetchone()
            if existing is not None:
                self._event_unlocked(
                    conn, "job_deduplicated", job_id=existing["job_id"],
                    status=existing["status"],
                    payload={"idempotency_key": key, "stage": stage},
                )
                conn.commit()
                result = self._row(existing) or {}
                result["created"] = False
                return result
            conn.execute(
                """INSERT INTO jobs
                   (job_id, stage, parent_job_id, idempotency_key,
                    payload_json, status, priority, estimated_vram_mb,
                    created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (job_id, stage, parent_job_id, key, payload_json, ENQUEUED,
                 int(priority), max(0, int(estimated_vram_mb)), now, now),
            )
            self._event_unlocked(conn, "job_enqueued", job_id=job_id,
                                 status=ENQUEUED,
                                 payload={"stage": stage})
            conn.commit()
        result = self.get_job(job_id) or {}
        result["created"] = True
        return result

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id = ?",
                               (job_id,)).fetchone()
        return self._row(row)

    def list_jobs(self, *, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM jobs"
        args: list[Any] = []
        if status is not None:
            query += " WHERE status = ?"
            args.append(status)
        query += " ORDER BY created_at ASC"
        with self._connect() as conn:
            rows = conn.execute(query, args).fetchall()
        return [dict(row) for row in rows]

    def list_events(self, *, job_id: str | None = None,
                    event_type: str | None = None) -> list[dict[str, Any]]:
        """Return append-only events in creation order for audit tooling."""
        query = "SELECT * FROM events"
        clauses: list[str] = []
        args: list[Any] = []
        if job_id is not None:
            clauses.append("job_id = ?")
            args.append(job_id)
        if event_type is not None:
            clauses.append("event_type = ?")
            args.append(event_type)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at ASC, event_id ASC"
        with self._connect() as conn:
            rows = conn.execute(query, args).fetchall()
        return [dict(row) for row in rows]

    def summary(self) -> dict[str, Any]:
        """Return compact queue and observation counts without mutating state."""
        with self._connect() as conn:
            jobs = {
                row["status"]: int(row["count"])
                for row in conn.execute(
                    "SELECT status, COUNT(*) AS count FROM jobs GROUP BY status"
                )
            }
            observations = int(conn.execute(
                "SELECT COUNT(*) FROM observations").fetchone()[0])
            events = int(conn.execute(
                "SELECT COUNT(*) FROM events").fetchone()[0])
        return {"jobs": jobs, "observations": observations, "events": events,
                "schema_version": SCHEMA_VERSION}

    def _recover_expired_unlocked(self, conn: sqlite3.Connection,
                                  now: float) -> int:
        placeholders = ",".join("?" for _ in _LEASED)
        expired = conn.execute(
            f"""SELECT job_id, status, owner_id, retry_count
                FROM jobs
                WHERE status IN ({placeholders})
                  AND lease_expires_at IS NOT NULL
                  AND lease_expires_at < ?""",
            [*_LEASED, now],
        ).fetchall()
        requeued = 0
        for row in expired:
            retry = int(row["retry_count"])
            next_status = ENQUEUED if retry < self.max_retries else DEAD
            retry += 1
            reason = ("lease expired" if next_status == ENQUEUED else
                      "lease expired; retry limit reached")
            conn.execute(
                """UPDATE jobs SET status = ?, owner_id = NULL,
                    lease_expires_at = NULL, retry_count = ?,
                    updated_at = ?, last_error = ? WHERE job_id = ?""",
                (next_status, retry, now, reason, row["job_id"]),
            )
            self._event_unlocked(
                conn, "lease_expired", job_id=row["job_id"],
                status=next_status,
                payload={"previous_status": row["status"],
                         "previous_owner": row["owner_id"],
                         "retry_count": retry, "reason": reason},
            )
            if next_status == ENQUEUED:
                requeued += 1
        return requeued

    def recover_expired_leases(self, *, now: float | None = None) -> int:
        stamp = time.time() if now is None else float(now)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            count = self._recover_expired_unlocked(conn, stamp)
            conn.commit()
        return count

    def claim_next(self, worker_id: str, *, stages: Iterable[str] | None = None,
                   lease_seconds: float = 600.0,
                   now: float | None = None,
                   job_id: str | None = None) -> dict[str, Any] | None:
        stamp = time.time() if now is None else float(now)
        allowed = list(stages or [])
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self._recover_expired_unlocked(conn, stamp)
            query = "SELECT * FROM jobs WHERE status = ?"
            args: list[Any] = [ENQUEUED]
            if job_id is not None:
                query += " AND job_id = ?"
                args.append(job_id)
            if allowed:
                query += " AND stage IN (%s)" % ",".join("?" for _ in allowed)
                args.extend(allowed)
            query += " ORDER BY priority DESC, created_at ASC LIMIT 1"
            row = conn.execute(query, args).fetchone()
            if row is None:
                conn.commit()
                return None
            expires = stamp + max(0.1, float(lease_seconds))
            conn.execute(
                """UPDATE jobs SET status = ?, owner_id = ?,
                   lease_expires_at = ?, updated_at = ? WHERE job_id = ?""",
                (CLAIMED, worker_id, expires, stamp, row["job_id"]),
            )
            self._event_unlocked(
                conn, "job_claimed", job_id=row["job_id"], status=CLAIMED,
                payload={"owner_id": worker_id},
            )
            conn.commit()
            claimed = conn.execute("SELECT * FROM jobs WHERE job_id = ?",
                                   (row["job_id"],)).fetchone()
        return self._row(claimed)

    def record_result(self, job_id: str, owner_id: str,
                      result: Mapping[str, Any]) -> bool:
        """Persist the bounded handler result while the worker owns the lease."""
        stamp = time.time()
        safe = dict(result)
        encoded = canonical_json(safe)
        if len(encoded) > 20000:
            safe = {"truncated": True, "result_preview": encoded[:19000]}
            encoded = canonical_json(safe)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                """UPDATE jobs SET result_json = ?, updated_at = ?
                   WHERE job_id = ? AND owner_id = ?
                   AND status IN (?, ?, ?)""",
                (encoded, stamp, job_id, owner_id, CLAIMED, RUNNING, VALIDATING),
            )
            if cur.rowcount == 1:
                self._event_unlocked(
                    conn, "job_result_recorded", job_id=job_id,
                    status="RECORDED", payload={"keys": sorted(safe)[:40]},
                )
            conn.commit()
        return cur.rowcount == 1

    def get_result(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT result_json FROM jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        if row is None or not row["result_json"]:
            return None
        try:
            value = json.loads(row["result_json"])
        except (TypeError, ValueError):
            return {"error": "invalid_result_json"}
        return value if isinstance(value, dict) else {"result": value}

    def _owned_update(self, job_id: str, owner_id: str, from_status: str,
                      to_status: str, *, lease_seconds: float = 600.0,
                      now: float | None = None) -> bool:
        stamp = time.time() if now is None else float(now)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                """UPDATE jobs SET status = ?, lease_expires_at = ?,
                   updated_at = ? WHERE job_id = ? AND owner_id = ?
                   AND status = ?""",
                (to_status, stamp + max(0.1, float(lease_seconds)), stamp,
                 job_id, owner_id, from_status),
            )
            if cur.rowcount == 1:
                event_type = "job_started" if to_status == RUNNING else "job_validating"
                self._event_unlocked(
                    conn, event_type, job_id=job_id, status=to_status,
                    payload={"owner_id": owner_id},
                )
            conn.commit()
        return cur.rowcount == 1

    def start(self, job_id: str, owner_id: str, *,
              lease_seconds: float = 600.0) -> bool:
        return self._owned_update(job_id, owner_id, CLAIMED, RUNNING,
                                  lease_seconds=lease_seconds)

    def heartbeat(self, job_id: str, owner_id: str, *,
                  lease_seconds: float = 600.0) -> bool:
        stamp = time.time()
        with self._connect() as conn:
            cur = conn.execute(
                """UPDATE jobs SET lease_expires_at = ?, updated_at = ?
                   WHERE job_id = ? AND owner_id = ? AND status IN (?, ?, ?)""",
                (stamp + max(0.1, float(lease_seconds)), stamp, job_id,
                 owner_id, CLAIMED, RUNNING, VALIDATING),
            )
            if cur.rowcount == 1:
                self._event_unlocked(
                    conn, "job_heartbeat", job_id=job_id, status="LEASED",
                    payload={"owner_id": owner_id},
                )
            conn.commit()
        return cur.rowcount == 1

    def begin_validation(self, job_id: str, owner_id: str) -> bool:
        return self._owned_update(job_id, owner_id, RUNNING, VALIDATING)

    def complete(self, job_id: str, owner_id: str, *,
                 artifact_ids: Iterable[str] = ()) -> bool:
        stamp = time.time()
        artifact_ids = list(artifact_ids)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            if artifact_ids:
                placeholders = ",".join("?" for _ in artifact_ids)
                linked = conn.execute(
                    """SELECT COUNT(DISTINCT artifact_id) FROM artifact_links
                       WHERE job_id = ? AND artifact_id IN (%s)"""
                    % placeholders,
                    [job_id, *artifact_ids],
                ).fetchone()[0]
                if linked != len(set(artifact_ids)):
                    conn.rollback()
                    return False
            cur = conn.execute(
                """UPDATE jobs SET status = ?, lease_expires_at = NULL,
                   owner_id = NULL, updated_at = ?, last_error = NULL
                   WHERE job_id = ? AND owner_id = ? AND status = ?""",
                (COMPLETED, stamp, job_id, owner_id, VALIDATING),
            )
            if cur.rowcount == 1:
                self._event_unlocked(
                    conn, "job_completed", job_id=job_id,
                    status=COMPLETED,
                    payload={"artifact_count": len(artifact_ids)},
                )
            conn.commit()
        return cur.rowcount == 1

    def fail(self, job_id: str, owner_id: str, reason: str, *,
             retriable: bool = True) -> str | None:
        stamp = time.time()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT retry_count FROM jobs
                   WHERE job_id = ? AND owner_id = ?
                   AND status IN (?, ?, ?)""",
                (job_id, owner_id, CLAIMED, RUNNING, VALIDATING),
            ).fetchone()
            if row is None:
                conn.rollback()
                return None
            next_status = (ENQUEUED if retriable and
                           row["retry_count"] < self.max_retries else
                           (DEAD if retriable else FAILED))
            retry = row["retry_count"] + (1 if next_status in (ENQUEUED, DEAD)
                                           else 0)
            conn.execute(
                """UPDATE jobs SET status = ?, owner_id = NULL,
                   lease_expires_at = NULL, retry_count = ?, last_error = ?,
                   updated_at = ? WHERE job_id = ?""",
                (next_status, retry, str(reason)[:2000], stamp, job_id),
            )
            self._event_unlocked(conn, "job_failed", job_id=job_id,
                                 status=next_status,
                                 payload={"reason": str(reason)[:2000]})
            conn.commit()
        return next_status

    def record_artifact(self, job_id: str, kind: str,
                        content: bytes | bytearray | memoryview | str, *,
                        staging_path: str | None = None,
                        canonical_path: str | None = None) -> dict[str, Any]:
        digest = artifact_content_hash(content)
        artifact_id = str(uuid.uuid4())
        stamp = time.time()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT * FROM artifacts WHERE kind = ? AND content_hash = ?",
                (kind, digest),
            ).fetchone()
            if existing is not None:
                conn.execute(
                    """INSERT OR IGNORE INTO artifact_links
                       (job_id, artifact_id, relation, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (job_id, existing["artifact_id"], "duplicate", stamp),
                )
                self._event_unlocked(
                    conn, "artifact_deduplicated", job_id=job_id,
                    status="DUPLICATE",
                    payload={"artifact_id": existing["artifact_id"],
                             "kind": kind, "content_hash": digest},
                )
                conn.commit()
                result = dict(existing)
                result["duplicate"] = True
                return result
            conn.execute(
                """INSERT INTO artifacts
                   (artifact_id, job_id, kind, content_hash, staging_path,
                    canonical_path, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (artifact_id, job_id, kind, digest, staging_path,
                 canonical_path, stamp),
            )
            conn.execute(
                """INSERT INTO artifact_links
                   (job_id, artifact_id, relation, created_at)
                   VALUES (?, ?, ?, ?)""",
                (job_id, artifact_id, "produced", stamp),
            )
            self._event_unlocked(
                conn, "artifact_recorded", job_id=job_id,
                payload={"artifact_id": artifact_id, "kind": kind,
                         "content_hash": digest},
            )
            conn.commit()
        return {"artifact_id": artifact_id, "job_id": job_id, "kind": kind,
                "content_hash": digest, "staging_path": staging_path,
                "canonical_path": canonical_path, "created_at": stamp,
                "duplicate": False}

    def record_observation(self, job_id: str, producer: str, *,
                           result_status: str, validated: bool = False,
                           payload: Mapping[str, Any] | None = None,
                           started_at: float | None = None,
                           finished_at: float | None = None,
                           owner_pid: int | None = None,
                           artifact_id: str | None = None,
                           output_hash: str | None = None) -> str:
        """Record an old-path execution without pretending the conductor ran it."""
        observation_id = str(uuid.uuid4())
        stamp = time.time() if finished_at is None else float(finished_at)
        with self._connect() as conn:
            job = conn.execute(
                "SELECT status FROM jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
            if job is None:
                raise ValueError("unknown job: %s" % job_id)
            conn.execute(
                """INSERT INTO observations
                   (observation_id, job_id, producer, owner_pid,
                    result_status, validated, artifact_id, output_hash,
                    started_at, finished_at, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (observation_id, job_id, producer, owner_pid, result_status,
                 int(bool(validated)), artifact_id, output_hash, started_at,
                 stamp, canonical_json(payload or {})),
            )
            self._event_unlocked(
                conn, "shadow_observation", job_id=job_id,
                status=result_status,
                payload={"observation_id": observation_id,
                         "producer": producer,
                         "validated": bool(validated),
                         "output_hash": output_hash},
            )
            moved = conn.execute(
                """UPDATE jobs SET status = ?, updated_at = ?,
                   owner_id = NULL, lease_expires_at = NULL
                   WHERE job_id = ? AND status = ?""",
                (OBSERVED, stamp, job_id, ENQUEUED),
            )
            if moved.rowcount == 1:
                self._event_unlocked(
                    conn, "shadow_observed", job_id=job_id,
                    status=OBSERVED,
                    payload={"producer": producer,
                             "result_status": result_status},
                )
            elif job["status"] not in {ENQUEUED, OBSERVED}:
                self._event_unlocked(
                    conn, "shadow_observation_late", job_id=job_id,
                    status=job["status"],
                    payload={"producer": producer,
                             "result_status": result_status},
                )
            conn.commit()
        return observation_id

    def list_observations(self, *, job_id: str | None = None
                          ) -> list[dict[str, Any]]:
        query = "SELECT * FROM observations"
        args: list[Any] = []
        if job_id is not None:
            query += " WHERE job_id = ?"
            args.append(job_id)
        query += " ORDER BY finished_at ASC"
        with self._connect() as conn:
            rows = conn.execute(query, args).fetchall()
        return [dict(row) for row in rows]

    def request_decision(self, job_id: str, *,
                         estimated_cost: float = 0.0,
                         note: str = "") -> str:
        decision_id = str(uuid.uuid4())
        stamp = time.time()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO decisions
                   (decision_id, job_id, status, note, estimated_cost,
                    created_at) VALUES (?, ?, 'PENDING', ?, ?, ?)""",
                (decision_id, job_id, note[:2000], float(estimated_cost), stamp),
            )
            self._event_unlocked(
                conn, "human_gate_requested", job_id=job_id,
                status="PENDING",
                payload={"decision_id": decision_id,
                         "estimated_cost": float(estimated_cost)},
            )
        return decision_id

    def ensure_human_gate(self, job_id: str, *,
                          estimated_cost: float = 0.0,
                          note: str = "") -> str:
        """Return the latest gate for a job, creating it if none exists."""
        decision_id = str(uuid.uuid4())
        stamp = time.time()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT decision_id FROM decisions
                   WHERE job_id = ? ORDER BY created_at DESC LIMIT 1""", (job_id,)
            ).fetchone()
            if row is not None:
                conn.commit()
                return str(row["decision_id"])
            conn.execute(
                """INSERT INTO decisions
                   (decision_id, job_id, status, note, estimated_cost,
                    created_at) VALUES (?, ?, 'PENDING', ?, ?, ?)""",
                (decision_id, job_id, note[:2000], float(estimated_cost), stamp),
            )
            self._event_unlocked(
                conn, "human_gate_requested", job_id=job_id,
                status="PENDING",
                payload={"decision_id": decision_id,
                         "estimated_cost": float(estimated_cost)},
            )
            conn.commit()
        return decision_id

    def human_gate_status(self, job_id: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT status FROM decisions WHERE job_id = ?
                   ORDER BY created_at DESC LIMIT 1""", (job_id,)
            ).fetchone()
        return str(row["status"]) if row is not None else None

    def human_gate_decision_id(self, job_id: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT decision_id FROM decisions WHERE job_id = ?
                   ORDER BY created_at DESC LIMIT 1""", (job_id,)
            ).fetchone()
        return str(row["decision_id"]) if row is not None else None

    def decision_belongs_to_job(self, decision_id: str, job_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM decisions WHERE decision_id = ? AND job_id = ?",
                (decision_id, job_id),
            ).fetchone()
        return row is not None

    def defer(self, job_id: str, owner_id: str, *, reason: str) -> bool:
        """Return a claimed job to the queue without consuming a retry."""
        stamp = time.time()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                """UPDATE jobs SET status = ?, owner_id = NULL,
                   lease_expires_at = NULL, updated_at = ?, last_error = ?
                   WHERE job_id = ? AND owner_id = ? AND status IN (?, ?, ?)""",
                (ENQUEUED, stamp, reason[:2000], job_id, owner_id,
                 CLAIMED, RUNNING, VALIDATING),
            )
            if cur.rowcount == 1:
                self._event_unlocked(
                    conn, "job_deferred", job_id=job_id, status=ENQUEUED,
                    payload={"owner_id": owner_id, "reason": reason[:2000]},
                )
            conn.commit()
        return cur.rowcount == 1

    def record_decision(self, decision_id: str, *, actor: str,
                        approved: bool, note: str = "") -> bool:
        stamp = time.time()
        status = "APPROVED" if approved else "REJECTED"
        with self._connect() as conn:
            decision = conn.execute(
                "SELECT job_id FROM decisions WHERE decision_id = ?",
                (decision_id,),
            ).fetchone()
            cur = conn.execute(
                """UPDATE decisions SET status = ?, actor = ?, approved = ?,
                   note = ?, decided_at = ?
                   WHERE decision_id = ? AND status = 'PENDING'""",
                (status, actor[:200], int(bool(approved)), note[:2000], stamp,
                 decision_id),
            )
            if cur.rowcount == 1:
                self._event_unlocked(
                    conn, "human_gate_decided",
                    job_id=decision["job_id"] if decision else None,
                    status=status,
                    payload={"decision_id": decision_id, "actor": actor,
                             "approved": bool(approved)},
                )
            conn.commit()
        return cur.rowcount == 1

    def decision_approved(self, decision_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT approved FROM decisions WHERE decision_id = ?",
                (decision_id,),
            ).fetchone()
        return bool(row and row["approved"] == 1)

    def reserve_budget(self, provider: str, *, limit_count: int,
                       window: str = "hour", now: float | None = None) -> bool:
        """Atomically reserve one bounded external call."""
        stamp = time.time() if now is None else float(now)
        duration = 3600 if window == "hour" else 86400
        start = int(stamp // duration * duration)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT used FROM external_budget
                   WHERE provider = ? AND window = ? AND window_start = ?""",
                (provider, window, start),
            ).fetchone()
            used = int(row["used"]) if row else 0
            if used >= int(limit_count):
                self._event_unlocked(
                    conn, "external_call_rejected", status="BUDGET_EXCEEDED",
                    payload={"provider": provider, "window": window,
                             "limit": int(limit_count)},
                )
                conn.commit()
                return False
            conn.execute(
                """INSERT INTO external_budget
                   (provider, window, window_start, used, limit_count)
                   VALUES (?, ?, ?, 1, ?)
                   ON CONFLICT(provider, window, window_start)
                   DO UPDATE SET used = used + 1, limit_count = excluded.limit_count""",
                (provider, window, start, int(limit_count)),
            )
            self._event_unlocked(
                conn, "external_call_reserved", status="RESERVED",
                payload={"provider": provider, "window": window,
                         "limit": int(limit_count), "used": used + 1},
            )
            conn.commit()
        return True

    def record_event(self, event_type: str, *, job_id: str | None = None,
                     cron_id: str | None = None, provider: str | None = None,
                     model: str | None = None, artifact_id: str | None = None,
                     decision_id: str | None = None, vram_mb: int | None = None,
                     duration_ms: int | None = None, status: str | None = None,
                     payload: Mapping[str, Any] | None = None) -> str:
        event_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO events
                   (event_id, job_id, event_type, cron_id, provider, model,
                    artifact_id, decision_id, vram_mb, duration_ms, status,
                    payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?)""",
                (event_id, job_id, event_type, cron_id, provider, model,
                 artifact_id, decision_id, vram_mb, duration_ms, status,
                 canonical_json(payload or {}), event_id and time.time()),
            )
        return event_id
