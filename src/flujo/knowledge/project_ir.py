"""Open Project IR and append-only learning ledger for MAK.

This module is deliberately conservative.  It records references, metadata,
hashes and outcomes; it never copies a source tree and it never promotes an
unknown input to active truth without evidence.  The SQLite schema is an
extension point for the existing ``data/mak_knowledge.db`` database, but the
caller must explicitly choose the database path.

The first learning target is operational policy: remember what was tried,
what evidence was produced and when the system abstained.  Model weights are
not changed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "mak-project-ir-v1"
LEARNING_SCHEMA = "mak-learning-ledger-v1"

PROJECT_STATES = (
    "candidate",
    "unknown",
    "review_required",
    "active",
    "verified",
    "stale",
    "contradicted",
    "historical",
    "quarantined",
)
EPISODE_STATES = (
    "proposed",
    "running",
    "succeeded",
    "failed",
    "abstained",
    "needs_evidence",
    "rejected",
    "verified",
)
RULE_STATUSES = ("candidate", "promoted", "stale", "rejected")
RULE_VERDICTS = ("support", "contradict", "neutral")
EVIDENCE_STATES = ("unverified", "observed", "verified", "contradicted")

FORMAT_FAMILIES = {
    ".py": "code", ".js": "code", ".ts": "code", ".html": "web",
    ".css": "web", ".svg": "vector", ".json": "data", ".jsonl": "data",
    ".yaml": "data", ".yml": "data", ".toml": "data", ".csv": "data",
    ".db": "database", ".sqlite": "database", ".sqlite3": "database",
    ".md": "text", ".txt": "text", ".odt": "document", ".pdf": "document",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image",
    ".gif": "image", ".mp4": "video", ".mov": "video", ".webm": "video",
    ".mkv": "video", ".wav": "audio", ".mp3": "audio", ".blend": "3d",
    ".obj": "3d", ".fbx": "3d", ".gltf": "3d", ".glb": "3d",
    ".zip": "archive", ".7z": "archive", ".tar": "archive", ".gz": "archive",
}

SKIP_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules", ".venv", "venv", "trash", "$recycle.bin",
}

ALLOWED_TRANSITIONS = {
    "candidate": {"unknown", "review_required", "active", "quarantined", "historical"},
    "unknown": {"candidate", "review_required", "quarantined", "historical"},
    "review_required": {"candidate", "active", "verified", "quarantined", "contradicted"},
    "active": {"verified", "stale", "contradicted", "review_required", "historical"},
    "verified": {"stale", "contradicted", "review_required", "historical"},
    "stale": {"active", "review_required", "historical", "quarantined"},
    "contradicted": {"review_required", "historical", "quarantined"},
    "historical": {"candidate", "review_required"},
    "quarantined": {"candidate", "review_required", "historical"},
}


class ProjectIRError(ValueError):
    """Invalid Project IR or unsafe bounded inventory request."""


class InventoryLimitError(ProjectIRError):
    """The requested source exceeds the explicit bounded inventory limit."""


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str, fallback: str = "project") -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value or "").casefold()).strip("-")
    return text[:80] or fallback


def _text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def _list_text(values: Any, limit: int = 48) -> list[str]:
    if values is None:
        return []
    if isinstance(values, (str, bytes)):
        values = [values]
    if not isinstance(values, Sequence):
        return []
    return [_text(item, 400) for item in values[:limit] if _text(item, 400)]


def format_family(path: str | Path) -> str:
    suffix = Path(path).suffix.casefold()
    return FORMAT_FAMILIES.get(suffix, "unknown")


def media_type(path: str | Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


def _hash_file(path: Path, max_bytes: int) -> tuple[str, str]:
    if path.stat().st_size > max_bytes:
        return "", "skipped_size_limit"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest(), "full"


def inventory_source(
    source_root: str | Path,
    *,
    max_files: int = 5000,
    max_hash_bytes: int = 32 * 1024 * 1024,
) -> list[dict[str, Any]]:
    """Inventory one bounded source directory without copying it.

    File contents are read only for bounded SHA-256 hashing.  Large files
    remain traceable through size and mtime, with an explicit hash status.
    Symlinks and skipped system/cache directories are not followed.
    """
    root = Path(source_root).expanduser()
    if not root.is_dir():
        raise FileNotFoundError(f"source_root_not_directory: {root}")
    rows: list[dict[str, Any]] = []
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if name.casefold() not in SKIP_DIRS)
        for name in sorted(filenames):
            if len(rows) >= max_files:
                raise InventoryLimitError(f"max_files_exceeded: {max_files}")
            path = Path(current) / name
            if path.is_symlink():
                continue
            try:
                stat = path.stat()
                digest, hash_status = _hash_file(path, max_hash_bytes)
            except OSError as exc:
                rows.append({
                    "relative_path": path.relative_to(root).as_posix(),
                    "availability": "unreadable",
                    "error": type(exc).__name__,
                })
                continue
            relative = path.relative_to(root).as_posix()
            basis = f"{relative}\0{stat.st_size}\0{stat.st_mtime_ns}\0{digest}"
            rows.append({
                "artifact_id": "artifact_" + hashlib.sha256(basis.encode()).hexdigest()[:32],
                "relative_path": relative,
                "name": path.name,
                "suffix": path.suffix.casefold(),
                "format_family": format_family(path),
                "media_type": media_type(path),
                "size_bytes": int(stat.st_size),
                "mtime_ns": int(stat.st_mtime_ns),
                "sha256": digest,
                "hash_status": hash_status,
                "availability": "present",
            })
    return sorted(rows, key=lambda item: item.get("relative_path", ""))


def build_project_ir(
    *,
    project_id: str,
    title: str,
    source_root: str | Path,
    artifacts: Iterable[Mapping[str, Any]] = (),
    domains: Iterable[str] = (),
    purpose: str = "",
    state: str = "candidate",
    evidence: Iterable[Mapping[str, Any]] = (),
    unknowns: Iterable[str] = (),
    relations: Iterable[Mapping[str, Any]] = (),
    source_kind: str = "folder",
    source_ref: str = "",
) -> dict[str, Any]:
    """Build a portable project record from references, never source copies."""
    normalized_id = slug(project_id)
    normalized_state = _text(state, 40).casefold() or "candidate"
    if normalized_state not in PROJECT_STATES:
        raise ProjectIRError(f"project_bad_state: {normalized_state}")
    rows = [dict(item) for item in artifacts]
    normalized_artifacts = []
    for item in rows:
        relative = _text(item.get("relative_path") or item.get("source_path"), 1000)
        if not relative:
            raise ProjectIRError("artifact_missing_relative_path")
        normalized_artifacts.append({
            "artifact_id": _text(item.get("artifact_id"), 100) or "artifact_" + hashlib.sha256(relative.encode()).hexdigest()[:32],
            "relative_path": relative,
            "name": _text(item.get("name") or Path(relative).name, 240),
            "suffix": _text(item.get("suffix") or Path(relative).suffix, 40).casefold(),
            "format_family": _text(item.get("format_family") or format_family(relative), 40),
            "media_type": _text(item.get("media_type") or media_type(relative), 160),
            "size_bytes": int(item.get("size_bytes") or 0),
            "mtime_ns": int(item.get("mtime_ns") or 0),
            "sha256": _text(item.get("sha256"), 64),
            "hash_status": _text(item.get("hash_status") or "not_computed", 40),
            "availability": _text(item.get("availability") or "present", 40),
            "role": _text(item.get("role") or "source", 80),
        })
    record = {
        "schema": SCHEMA,
        "project_id": normalized_id,
        "title": _text(title, 300) or normalized_id,
        "state": normalized_state,
        "source": {
            "kind": _text(source_kind, 80) or "folder",
            "root_ref": _text(source_ref or str(source_root), 1000),
            "root_exists": Path(source_root).is_dir(),
        },
        "purpose": _text(purpose, 1200),
        "domains": sorted(set(_list_text(domains, 24))),
        "artifacts": sorted(normalized_artifacts, key=lambda item: item["relative_path"]),
        "relations": [dict(item) for item in relations],
        "evidence": [dict(item) for item in evidence],
        "unknowns": _list_text(unknowns, 48),
        "next_action": "review_evidence" if normalized_state in {"unknown", "review_required"} else "select_consumer",
        "provenance": {
            "producer": "flujo.knowledge.project_ir",
            "method": "bounded_reference_inventory",
            "created_at": now_iso(),
        },
    }
    errors = validate_project_ir(record)
    if errors:
        raise ProjectIRError("invalid_project_ir: " + ",".join(errors))
    return record


def project_ir_from_application_package(
    package: Mapping[str, Any], *, source_ref: str = "application-package"
) -> dict[str, Any]:
    """Adapt an existing application draft into Project IR.

    Application drafts are evidence-bearing candidates, not proof of a
    finished project.  Their explicit gaps become ``unknowns`` and their
    MAK links become relations; source assets remain references.
    """
    if package.get("schema") != "mak-application-package-v1":
        raise ProjectIRError("application_bad_schema")
    project = package.get("project")
    if not isinstance(project, Mapping):
        raise ProjectIRError("application_missing_project")
    project_id = _text(project.get("project_id"), 100) or _text(package.get("application_id"), 100)
    if not project_id:
        raise ProjectIRError("application_missing_project_id")
    evidence_block = package.get("evidence") if isinstance(package.get("evidence"), Mapping) else {}
    source_root = _text(project.get("path") or source_ref, 1000)
    source_index_ref = _text(evidence_block.get("source_index"), 1000)
    if source_index_ref:
        try:
            index_path = Path(source_index_ref).expanduser()
            if index_path.is_file():
                index = json.loads(index_path.read_text(encoding="utf-8"))
                indexed_root = _text(index.get("source_root"), 1000) if isinstance(index, Mapping) else ""
                if indexed_root:
                    source_root = indexed_root
        except (OSError, ValueError, TypeError):
            pass
    assets = evidence_block.get("representative_assets", [])
    if not isinstance(assets, list):
        assets = []
    artifacts = []
    for item in assets[:48]:
        if not isinstance(item, Mapping):
            continue
        reference = _text(item.get("relative_path") or item.get("path") or item.get("mak_path"), 1000)
        if not reference:
            continue
        family = format_family(reference)
        if _text(item.get("media_kind"), 40).casefold() in {"structural", "3d"}:
            family = "3d"
        artifacts.append({
            "relative_path": reference,
            "name": Path(reference).name,
            "format_family": family,
            "media_type": media_type(reference),
            "size_bytes": int(item.get("bytes") or 0),
            "sha256": _text(item.get("full_sha256"), 64),
            "hash_status": "full" if item.get("full_sha256") else "not_computed",
            "availability": _text(item.get("availability") or "referenced", 40),
            "role": "representative_asset",
        })
    links = evidence_block.get("mak_links", [])
    if not isinstance(links, list):
        links = []
    relations = []
    for item in links[:48]:
        if not isinstance(item, Mapping):
            continue
        mak_path = _text(item.get("mak_path"), 1000)
        if mak_path:
            normalized_path = mak_path.replace("\\", "/").casefold()
            plane = "historical_win" if "/win/" in normalized_path or "/actions-runner/" in normalized_path else "active_mak"
            relations.append({
                "subject": project_id,
                "predicate": _text(item.get("relation") or "consumer_link", 120),
                "object": mak_path,
                "confidence": item.get("confidence", "unknown"),
                "plane": plane,
            })
    gaps = package.get("gaps", [])
    unknowns = []
    if isinstance(gaps, list):
        for gap in gaps[:48]:
            if isinstance(gap, Mapping):
                field = _text(gap.get("field"), 160)
                reason = _text(gap.get("reason"), 300)
                if field:
                    unknowns.append(f"{field}: {reason}" if reason else field)
    dimensionality = _text(project.get("dimensionality"), 80)
    fund = package.get("fund") if isinstance(package.get("fund"), Mapping) else {}
    fund_name = _text(fund.get("name") or fund.get("id"), 160)
    evidence = [{
        "kind": "application_package",
        "source_ref": source_ref,
        "application_id": _text(package.get("application_id"), 160),
        "status": "observed",
        "readiness": package.get("readiness"),
    }]
    record = build_project_ir(
        project_id=project_id,
        title=_text(project.get("title"), 300) or project_id,
        source_root=source_root,
        artifacts=artifacts,
        domains=[item for item in ("mak", "funding", dimensionality) if item],
        purpose=f"application_candidate:{fund_name}" if fund_name else "application_candidate",
        state="review_required",
        evidence=evidence,
        unknowns=unknowns,
        relations=relations,
        source_kind="application_package",
        source_ref=source_root,
    )
    record["application"] = {
        "application_id": _text(package.get("application_id"), 160),
        "fund": fund_name,
        "status": _text(package.get("status"), 120),
        "readiness": package.get("readiness"),
        "source_index": source_index_ref,
        "project_path": _text(project.get("path"), 1000),
    }
    return record


def load_application_package(path: str | Path) -> dict[str, Any]:
    package_path = Path(path).expanduser()
    package = json.loads(package_path.read_text(encoding="utf-8"))
    if not isinstance(package, dict):
        raise ProjectIRError("application_package_not_object")
    return project_ir_from_application_package(package, source_ref=str(package_path))


def validate_project_ir(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("schema", "project_id", "title", "state", "source", "purpose",
                "domains", "artifacts", "relations", "evidence", "unknowns",
                "next_action", "provenance")
    errors.extend("missing_" + key for key in required if key not in record)
    if record.get("schema") != SCHEMA:
        errors.append("bad_schema")
    if not _text(record.get("project_id"), 100):
        errors.append("missing_project_id")
    if record.get("state") not in PROJECT_STATES:
        errors.append("bad_state")
    for key in ("domains", "artifacts", "relations", "evidence", "unknowns"):
        if key in record and not isinstance(record[key], list):
            errors.append(key + "_not_list")
    source = record.get("source")
    if not isinstance(source, Mapping) or not _text(source.get("root_ref"), 1000):
        errors.append("bad_source")
    provenance = record.get("provenance")
    if not isinstance(provenance, Mapping) or not _text(provenance.get("producer"), 200):
        errors.append("bad_provenance")
    if record.get("state") in {"active", "verified"} and not record.get("evidence"):
        errors.append("active_requires_evidence")
    for index, artifact in enumerate(record.get("artifacts", [])):
        if not isinstance(artifact, Mapping) or not _text(artifact.get("relative_path"), 1000):
            errors.append(f"artifact_{index}_bad_reference")
    return errors


def _json(value: Any) -> str:
    return stable_json(value if value is not None else {})


def _record_fingerprint(record: Mapping[str, Any]) -> str:
    """Hash semantic content while ignoring volatile creation/update times."""
    snapshot = json.loads(json.dumps(record, ensure_ascii=False))
    provenance = snapshot.get("provenance")
    if isinstance(provenance, dict):
        provenance.pop("created_at", None)
        provenance.pop("updated_at", None)
    return hashlib.sha256(stable_json(snapshot).encode("utf-8")).hexdigest()


class LearningStore:
    """SQLite persistence for Project IR, episodes and explicit transitions."""

    def __init__(self, database: str | Path):
        self.database = Path(database).expanduser()

    def connect(self) -> sqlite3.Connection:
        self.database.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def ensure_schema(self, connection: sqlite3.Connection | None = None) -> None:
        own = connection is None
        con = connection or self.connect()
        try:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS project_records (
                    project_id TEXT PRIMARY KEY,
                    schema_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    state TEXT NOT NULL,
                    source_root_ref TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    ir_json TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS project_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES project_records(project_id),
                    relative_path TEXT NOT NULL,
                    format_family TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL DEFAULT 0,
                    mtime_ns INTEGER NOT NULL DEFAULT 0,
                    sha256 TEXT NOT NULL DEFAULT '',
                    hash_status TEXT NOT NULL,
                    availability TEXT NOT NULL,
                    role TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    UNIQUE(project_id, relative_path)
                );
                CREATE TABLE IF NOT EXISTS project_episodes (
                    episode_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES project_records(project_id),
                    objective TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    action_json TEXT NOT NULL,
                    observation_json TEXT NOT NULL,
                    outcome_json TEXT NOT NULL,
                    validation_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    cost_json TEXT NOT NULL,
                    parent_episode_id TEXT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT
                );
                CREATE TABLE IF NOT EXISTS project_transitions (
                    transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL REFERENCES project_records(project_id),
                    from_state TEXT NOT NULL,
                    to_state TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS semantic_rules (
                    rule_id TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL UNIQUE,
                    trigger_json TEXT NOT NULL,
                    action_json TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    support_count INTEGER NOT NULL DEFAULT 0,
                    contradiction_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    promoted_at TEXT
                );
                CREATE TABLE IF NOT EXISTS project_contracts (
                    contract_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    contract_key TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    status TEXT NOT NULL,
                    fingerprint TEXT NOT NULL UNIQUE,
                    updated_at TEXT NOT NULL,
                    UNIQUE(kind, contract_key)
                );
                CREATE TABLE IF NOT EXISTS rule_observations (
                    observation_id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL REFERENCES semantic_rules(rule_id),
                    episode_id TEXT NOT NULL REFERENCES project_episodes(episode_id),
                    verdict TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(rule_id, episode_id, verdict)
                );
                CREATE INDEX IF NOT EXISTS idx_project_artifacts_project
                    ON project_artifacts(project_id);
                CREATE INDEX IF NOT EXISTS idx_project_episodes_project
                    ON project_episodes(project_id, status);
                CREATE INDEX IF NOT EXISTS idx_project_transitions_project
                    ON project_transitions(project_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_rule_observations_rule
                    ON rule_observations(rule_id, verdict);
                """
            )
            if own:
                con.commit()
        finally:
            if own:
                con.close()

    def save_project(self, record: Mapping[str, Any]) -> str:
        errors = validate_project_ir(record)
        if errors:
            raise ProjectIRError("invalid_project_ir: " + ",".join(errors))
        project_id = str(record["project_id"])
        encoded = stable_json(dict(record))
        fingerprint = _record_fingerprint(record)
        now = now_iso()
        with self.connect() as con:
            self.ensure_schema(con)
            previous = con.execute(
                "SELECT version, created_at, fingerprint FROM project_records WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if previous and previous["fingerprint"] == fingerprint:
                return fingerprint
            version = int(previous["version"]) + 1 if previous else 1
            created = previous["created_at"] if previous else now
            con.execute(
                """INSERT INTO project_records
                   (project_id,schema_name,title,state,source_root_ref,fingerprint,ir_json,version,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(project_id) DO UPDATE SET
                   schema_name=excluded.schema_name,title=excluded.title,state=excluded.state,
                   source_root_ref=excluded.source_root_ref,fingerprint=excluded.fingerprint,
                   ir_json=excluded.ir_json,version=excluded.version,updated_at=excluded.updated_at""",
                (project_id, SCHEMA, record["title"], record["state"],
                 record["source"]["root_ref"], fingerprint, encoded, version, created, now),
            )
            current_paths = {str(artifact["relative_path"]) for artifact in record["artifacts"]}
            if current_paths:
                placeholders = ",".join("?" for _ in current_paths)
                con.execute(
                    f"UPDATE project_artifacts SET availability='stale',observed_at=? WHERE project_id=? AND relative_path NOT IN ({placeholders})",
                    (now, project_id, *sorted(current_paths)),
                )
            else:
                con.execute(
                    "UPDATE project_artifacts SET availability='stale',observed_at=? WHERE project_id=?",
                    (now, project_id),
                )
            for artifact in record["artifacts"]:
                con.execute(
                    """INSERT INTO project_artifacts
                       (artifact_id,project_id,relative_path,format_family,media_type,size_bytes,mtime_ns,sha256,hash_status,availability,role,observed_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(project_id,relative_path) DO UPDATE SET
                       artifact_id=excluded.artifact_id,format_family=excluded.format_family,
                       media_type=excluded.media_type,size_bytes=excluded.size_bytes,mtime_ns=excluded.mtime_ns,
                       sha256=excluded.sha256,hash_status=excluded.hash_status,availability=excluded.availability,
                       role=excluded.role,observed_at=excluded.observed_at""",
                    (artifact["artifact_id"], project_id, artifact["relative_path"],
                     artifact["format_family"], artifact["media_type"], artifact["size_bytes"],
                     artifact["mtime_ns"], artifact["sha256"], artifact["hash_status"],
                     artifact["availability"], artifact["role"], now),
                )
        return fingerprint

    def record_episode(
        self,
        *,
        project_id: str,
        objective: str,
        phase: str,
        action: Mapping[str, Any],
        observation: Mapping[str, Any],
        outcome: Mapping[str, Any],
        validation: Mapping[str, Any],
        status: str,
        provider: str = "local",
        model: str = "",
        cost: Mapping[str, Any] | None = None,
        parent_episode_id: str | None = None,
        episode_id: str | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
    ) -> str:
        if status not in EPISODE_STATES:
            raise ProjectIRError(f"episode_bad_status: {status}")
        episode_id = episode_id or "episode_" + uuid.uuid4().hex
        start = started_at or now_iso()
        payload = (
            project_id, _text(objective, 1200), _text(phase, 120),
            _json(action), _json(observation), _json(outcome), _json(validation),
            status, _text(provider, 160) or "local", _text(model, 160), _json(cost),
            _text(parent_episode_id, 120),
        )
        with self.connect() as con:
            self.ensure_schema(con)
            if not con.execute("SELECT 1 FROM project_records WHERE project_id=?", (project_id,)).fetchone():
                raise ProjectIRError(f"episode_unknown_project: {project_id}")
            existing = con.execute(
                """SELECT project_id,objective,phase,action_json,observation_json,
                   outcome_json,validation_json,status,provider,model,cost_json,parent_episode_id
                   FROM project_episodes WHERE episode_id=?""",
                (episode_id,),
            ).fetchone()
            if existing:
                if tuple(existing) == payload:
                    return episode_id
                raise ProjectIRError(f"episode_id_conflict: {episode_id}")
            con.execute(
                """INSERT INTO project_episodes
                (episode_id,project_id,objective,phase,action_json,observation_json,outcome_json,validation_json,status,provider,model,cost_json,parent_episode_id,started_at,finished_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (episode_id, *payload, start, finished_at),
            )
        return episode_id

    def transition_project(
        self, project_id: str, to_state: str, *, reason: str,
        evidence: Iterable[Mapping[str, Any]] = (), actor: str = "system",
    ) -> None:
        if to_state not in PROJECT_STATES:
            raise ProjectIRError(f"project_bad_state: {to_state}")
        evidence_rows = [dict(item) for item in evidence]
        with self.connect() as con:
            self.ensure_schema(con)
            row = con.execute("SELECT state, ir_json FROM project_records WHERE project_id=?", (project_id,)).fetchone()
            if not row:
                raise ProjectIRError(f"unknown_project: {project_id}")
            from_state = str(row["state"])
            if to_state == from_state:
                return
            if to_state not in ALLOWED_TRANSITIONS.get(from_state, set()):
                raise ProjectIRError(f"transition_not_allowed: {from_state}->{to_state}")
            record = json.loads(row["ir_json"])
            record["state"] = to_state
            record["evidence"] = list(record.get("evidence", [])) + evidence_rows
            record["provenance"]["updated_at"] = now_iso()
            errors = validate_project_ir(record)
            if errors:
                raise ProjectIRError("invalid_transition_record: " + ",".join(errors))
            encoded = stable_json(record)
            con.execute(
                "UPDATE project_records SET state=?, fingerprint=?, ir_json=?, version=version+1, updated_at=? WHERE project_id=?",
                (to_state, hashlib.sha256(encoded.encode()).hexdigest(), encoded, now_iso(), project_id),
            )
            con.execute(
                "INSERT INTO project_transitions(project_id,from_state,to_state,reason,evidence_json,actor,created_at) VALUES (?,?,?,?,?,?,?)",
                (project_id, from_state, to_state, _text(reason, 1200), _json(evidence_rows), _text(actor, 160), now_iso()),
            )

    def upsert_rule(
        self, *, trigger: Mapping[str, Any], action: Mapping[str, Any],
        evidence: Iterable[Mapping[str, Any]] = (), rule_id: str | None = None,
    ) -> str:
        """Register a candidate semantic rule without promoting it."""
        fingerprint = hashlib.sha256(
            stable_json({"trigger": dict(trigger), "action": dict(action)}).encode("utf-8")
        ).hexdigest()
        rule_id = rule_id or "rule_" + fingerprint[:24]
        now = now_iso()
        with self.connect() as con:
            self.ensure_schema(con)
            con.execute(
                """INSERT INTO semantic_rules
                   (rule_id,fingerprint,trigger_json,action_json,evidence_json,status,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(fingerprint) DO UPDATE SET
                   trigger_json=excluded.trigger_json, action_json=excluded.action_json,
                   evidence_json=excluded.evidence_json, updated_at=excluded.updated_at""",
                (rule_id, fingerprint, _json(trigger), _json(action), _json(list(evidence)), "candidate", now, now),
            )
            actual = con.execute("SELECT rule_id FROM semantic_rules WHERE fingerprint=?", (fingerprint,)).fetchone()
            if actual:
                rule_id = str(actual["rule_id"])
        return rule_id

    def observe_rule(
        self, *, rule_id: str, episode_id: str, verdict: str,
        evidence: Iterable[Mapping[str, Any]] = (), observation_id: str | None = None,
    ) -> str:
        """Append one support/contradiction observation to a rule candidate."""
        if verdict not in RULE_VERDICTS:
            raise ProjectIRError(f"rule_bad_verdict: {verdict}")
        observation_id = observation_id or "observation_" + uuid.uuid4().hex
        with self.connect() as con:
            self.ensure_schema(con)
            rule = con.execute("SELECT rule_id FROM semantic_rules WHERE rule_id=?", (rule_id,)).fetchone()
            episode = con.execute("SELECT status FROM project_episodes WHERE episode_id=?", (episode_id,)).fetchone()
            if not rule:
                raise ProjectIRError(f"unknown_rule: {rule_id}")
            if not episode:
                raise ProjectIRError(f"unknown_episode: {episode_id}")
            con.execute(
                """INSERT INTO rule_observations(observation_id,rule_id,episode_id,verdict,evidence_json,created_at)
                   VALUES (?,?,?,?,?,?)""",
                (observation_id, rule_id, episode_id, verdict, _json(list(evidence)), now_iso()),
            )
            if verdict == "support":
                column = "support_count"
            elif verdict == "contradict":
                column = "contradiction_count"
            else:
                return observation_id
            con.execute(f"UPDATE semantic_rules SET {column}={column}+1,updated_at=? WHERE rule_id=?", (now_iso(), rule_id))
        return observation_id

    def promote_rule(self, rule_id: str, *, min_support: int = 2) -> None:
        """Promote only a rule supported by independently verified episodes.

        Promotion is intentionally strict.  A failed/unknown episode may be
        recorded, but it cannot teach the active router.  Contradictions
        always block promotion until an explicit future review changes state.
        """
        if min_support < 1:
            raise ProjectIRError("min_support_must_be_positive")
        with self.connect() as con:
            self.ensure_schema(con)
            rule = con.execute("SELECT * FROM semantic_rules WHERE rule_id=?", (rule_id,)).fetchone()
            if not rule:
                raise ProjectIRError(f"unknown_rule: {rule_id}")
            if int(rule["support_count"]) < min_support:
                raise ProjectIRError("rule_insufficient_support")
            if int(rule["contradiction_count"]) > 0:
                raise ProjectIRError("rule_has_contradictions")
            supports = con.execute(
                """SELECT e.status, e.validation_json
                   FROM rule_observations o JOIN project_episodes e ON e.episode_id=o.episode_id
                   WHERE o.rule_id=? AND o.verdict='support'""", (rule_id,),
            ).fetchall()
            if len(supports) < min_support:
                raise ProjectIRError("rule_support_observations_missing")
            for episode in supports:
                if episode["status"] not in {"succeeded", "verified"}:
                    raise ProjectIRError("rule_support_episode_not_verified")
                try:
                    validation = json.loads(episode["validation_json"])
                except json.JSONDecodeError as exc:
                    raise ProjectIRError("rule_support_validation_invalid") from exc
                if str(validation.get("status", "")).casefold() not in {"ok", "passed", "verified"}:
                    raise ProjectIRError("rule_support_validation_not_passed")
            con.execute(
                "UPDATE semantic_rules SET status='promoted',promoted_at=?,updated_at=? WHERE rule_id=?",
                (now_iso(), now_iso(), rule_id),
            )

    def rules(self, *, status: str | None = None) -> list[dict[str, Any]]:
        with self.connect() as con:
            self.ensure_schema(con)
            if status is None:
                rows = con.execute("SELECT * FROM semantic_rules ORDER BY updated_at, rule_id").fetchall()
            else:
                rows = con.execute("SELECT * FROM semantic_rules WHERE status=? ORDER BY updated_at, rule_id", (status,)).fetchall()
            return [dict(row) for row in rows]

    def summary(self, project_id: str | None = None) -> dict[str, Any]:
        with self.connect() as con:
            self.ensure_schema(con)
            where = " WHERE project_id=?" if project_id else ""
            args = (project_id,) if project_id else ()
            projects = con.execute("SELECT state, COUNT(*) AS count FROM project_records" + where + " GROUP BY state", args).fetchall()
            episodes = con.execute("SELECT status, COUNT(*) AS count FROM project_episodes" + where + " GROUP BY status", args).fetchall()
            rules = con.execute("SELECT status, COUNT(*) AS count FROM semantic_rules GROUP BY status").fetchall()
            return {
                "schema": LEARNING_SCHEMA,
                "projects": {row["state"]: row["count"] for row in projects},
                "episodes": {row["status"]: row["count"] for row in episodes},
                "rules": {row["status"]: row["count"] for row in rules},
                "project_id": project_id or "",
            }


def inspect_learning_target(database: str | Path) -> dict[str, Any]:
    """Inspect a potential target without creating tables or changing bytes."""
    path = Path(database).expanduser()
    expected = {
        "project_records", "project_artifacts", "project_episodes",
        "project_transitions", "semantic_rules", "rule_observations",
        "project_contracts",
    }
    if not path.is_file():
        return {
            "schema": LEARNING_SCHEMA,
            "database": path.name,
            "exists": False,
            "read_only": True,
            "compatible": True,
            "present": [],
            "missing": sorted(expected),
        }
    try:
        con = sqlite3.connect("file:" + str(path) + "?mode=ro", uri=True)
        present = {
            row[0] for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ) if row[0] in expected
        }
        con.close()
        present_names = sorted(present)
        if not present:
            materialization = "not_applied"
        elif present == expected:
            materialization = "already_applied"
        else:
            materialization = "partial"
        return {
            "schema": LEARNING_SCHEMA,
            "database": path.name,
            "exists": True,
            "read_only": True,
            "compatible": True,
            "present": present_names,
            "missing": sorted(expected - present),
            "materialization": materialization,
        }
    except (OSError, sqlite3.Error) as exc:
        return {
            "schema": LEARNING_SCHEMA,
            "database": path.name,
            "exists": True,
            "read_only": True,
            "compatible": False,
            "error": type(exc).__name__,
        }


def migration_dry_run(
    database: str | Path, *, application_dir: str | Path | None = None,
    max_packages: int = 200,
) -> dict[str, Any]:
    """Build a machine-readable migration impact report without applying it."""
    target = inspect_learning_target(database)
    report: dict[str, Any] = {
        "schema": "mak-learning-migration-dry-run-v1",
        "target": target,
        "writes_performed": False,
        "migration": "not_needed" if target.get("materialization") == "already_applied" else "not_applied",
        "collisions": [],
        "compatible": bool(target.get("compatible")),
        "action": target.get("materialization", "not_applied"),
        "intake": {"available": False, "packages": 0, "projects": [], "review_required": 0, "unknowns": 0},
    }
    if application_dir is None:
        return report
    root = Path(application_dir).expanduser()
    if not root.is_dir():
        report["intake"] = {"available": False, "reason": "directory_missing", "directory": root.name}
        return report
    packages = sorted(root.glob("*.json"))
    if len(packages) > max_packages:
        report["intake"] = {"available": False, "reason": "max_packages_exceeded", "max_packages": max_packages}
        return report
    project_ids: list[str] = []
    unknowns = 0
    review_required = 0
    for path in packages:
        try:
            record = load_application_package(path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
        project_ids.append(str(record["project_id"]))
        unknowns += len(record.get("unknowns", []))
        review_required += record.get("state") == "review_required"
    report["intake"] = {
        "available": True,
        "directory": root.name,
        "packages": len(project_ids),
        "projects": sorted(set(project_ids)),
        "review_required": review_required,
        "unknowns": unknowns,
    }
    return report


def _cli(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="MAK Project IR and learning ledger")
    parser.add_argument("--db", required=True, help="explicit SQLite path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    ingest = sub.add_parser("ingest")
    ingest.add_argument("--source-root", required=True)
    ingest.add_argument("--project-id", required=True)
    ingest.add_argument("--title", default="")
    ingest.add_argument("--state", choices=PROJECT_STATES, default="candidate")
    ingest.add_argument("--domain", action="append", default=[])
    application = sub.add_parser("import-application")
    application.add_argument("--package", required=True)
    summary = sub.add_parser("summary")
    summary.add_argument("--project-id")
    sub.add_parser("inspect")
    migration = sub.add_parser("migration-report")
    migration.add_argument("--intake-dir")
    args = parser.parse_args(list(argv))
    store = LearningStore(args.db)
    if args.command == "init":
        store.ensure_schema()
        print(json.dumps({"schema": LEARNING_SCHEMA, "database": str(store.database), "status": "ready"}, ensure_ascii=False))
        return 0
    if args.command == "ingest":
        artifacts = inventory_source(args.source_root)
        record = build_project_ir(
            project_id=args.project_id, title=args.title or args.project_id,
            source_root=args.source_root, artifacts=artifacts, domains=args.domain,
            state=args.state, source_kind="folder",
        )
        fingerprint = store.save_project(record)
        print(json.dumps({"project_id": record["project_id"], "artifacts": len(artifacts), "fingerprint": fingerprint}, ensure_ascii=False))
        return 0
    if args.command == "import-application":
        record = load_application_package(args.package)
        fingerprint = store.save_project(record)
        print(json.dumps({"project_id": record["project_id"], "state": record["state"], "unknowns": len(record["unknowns"]), "fingerprint": fingerprint}, ensure_ascii=False))
        return 0
    if args.command == "inspect":
        print(json.dumps(inspect_learning_target(store.database), ensure_ascii=False))
        return 0
    if args.command == "migration-report":
        print(json.dumps(migration_dry_run(store.database, application_dir=args.intake_dir), ensure_ascii=False))
        return 0
    print(json.dumps(store.summary(args.project_id), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
