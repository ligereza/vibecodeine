#!/usr/bin/env python3
"""Build a chronological, provenance-aware MAK knowledge index.

Read-only scanner. It indexes physical evidence without copying it. Git is used
only for provenance of files already found on disk.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sqlite3
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ACTIVE_SKIP = {
    ".cache", ".codex", ".config", ".local", ".npm", ".ollama", ".lmstudio",
    ".venvs", "venvs", "venv-providers", "models", "WIN", "node_modules",
    "__pycache__",
    # `consolidate_static_duplicates.PROTECTED_TOPS` already names these four
    # together with WIN; only WIN was listed here. Two of them, GoogleDrive and
    # OneDrive, are `fuse.rclone` mounts: walking them hashes every file, and
    # hashing a file on an rclone mount downloads it. On the operator's box
    # processes have been observed stuck in FUSE wait for hours, so the default
    # `--active-root /home/mak` would both stall the scan and pull the whole
    # cloud through it.
    "GoogleDrive", "OneDrive", "curatoria_inbox",
}
HISTORY_SKIP = {
    ".git", ".cache", "node_modules", "__pycache__", ".venv", "venv",
    "assets", "media", "renders", "render", "captures", "models", "data",
    "dist", "build",
}
TEXT_EXTS = {
    ".py", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".csv", ".html", ".htm", ".css", ".js", ".ts", ".tsx",
    ".jsx", ".sh", ".ps1", ".sql", ".svg", ".xml", ".env",
}
MEDIA_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".blend",
    ".wav", ".mp3", ".pdf", ".odt", ".docx", ".zip", ".tar", ".gz",
}
EFFORT_DIRS = {
    "informes", "paneles", "cadenas", "refutaciones", "grafos",
    "correlaciones", "fusiones",
}
META_READ_KEYS = {
    "llmCalls", "errors", "queries", "query_history", "timeouts",
    "sources", "seen_urls", "duration_ms", "duration", "ms",
    "iterations", "iteration",
}
META_KNOWN_UNUSED = {
    "ts", "t", "job_id", "topic", "tema", "model", "modelo", "modo",
    "tipo", "densidad", "sin_marco", "temperature", "max_tokens",
    "successes", "relevance", "search_depth", "queries_por_iteracion",
    "version",
}
ACTIVE_ROOT_NAMES = {
    "flujo", "plataforma", "research", "curatoria", "curatoria_inbox",
    "post", "RD", "xio_puente", "src", "apps", "labs", "n8n-local",
    "workspace", "trazos", "vibecodeine", "vigia", "bucle",
    "actions-runner", "searxng", "state", "indexes",
}
HISTORY_ROOT_NAMES = {
    "flujo", "claude_sesiones", "codex/archived_sessions",
    "codex/sessions", "incoming-20260813", "updates-20260813",
}
DATE_PATTERNS = (
    re.compile(r"(?P<value>20\d{2}-\d{2}-\d{2}[T _-]\d{2}[:_-]\d{2}(?::[:_-]?\d{2})?)"),
    re.compile(r"(?P<value>20\d{2}[-_]\d{2}[-_]\d{2})"),
    re.compile(r"(?P<value>20\d{6}[-_]\d{4,6})"),
)
SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS scan_runs (
    run_id INTEGER PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    active_root TEXT NOT NULL,
    history_root TEXT NOT NULL,
    repo_root TEXT NOT NULL,
    files_seen INTEGER NOT NULL DEFAULT 0,
    files_indexed INTEGER NOT NULL DEFAULT 0,
    text_hashed INTEGER NOT NULL DEFAULT 0,
    git_status TEXT NOT NULL DEFAULT 'pending',
    effort_status TEXT NOT NULL DEFAULT 'pending',
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    root_kind TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    name TEXT NOT NULL,
    suffix TEXT NOT NULL,
    artifact_kind TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    mode TEXT NOT NULL,
    mtime_ns INTEGER,
    ctime_ns INTEGER,
    birthtime_ns INTEGER,
    sha256 TEXT,
    text_title TEXT,
    declared_status TEXT,
    declared_work_id TEXT,
    declared_purpose TEXT,
    first_run_id INTEGER NOT NULL,
    last_run_id INTEGER NOT NULL,
    FOREIGN KEY(first_run_id) REFERENCES scan_runs(run_id),
    FOREIGN KEY(last_run_id) REFERENCES scan_runs(run_id)
);
CREATE TABLE IF NOT EXISTS temporal_events (
    event_id INTEGER PRIMARY KEY,
    artifact_id INTEGER,
    event_type TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    source_path TEXT NOT NULL,
    confidence TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    run_id INTEGER NOT NULL,
    UNIQUE(artifact_id, event_type, observed_at, source_path, detail),
    FOREIGN KEY(artifact_id) REFERENCES artifacts(artifact_id),
    FOREIGN KEY(run_id) REFERENCES scan_runs(run_id)
);
CREATE TABLE IF NOT EXISTS entities (
    entity_id INTEGER PRIMARY KEY,
    entity_kind TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    path TEXT,
    status TEXT NOT NULL DEFAULT 'unclassified',
    purpose TEXT,
    idea TEXT,
    origin TEXT,
    confidence TEXT NOT NULL DEFAULT 'low',
    UNIQUE(entity_kind, canonical_name, path)
);
CREATE TABLE IF NOT EXISTS entity_artifacts (
    entity_id INTEGER NOT NULL,
    artifact_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    confidence TEXT NOT NULL DEFAULT 'medium',
    PRIMARY KEY(entity_id, artifact_id, role),
    FOREIGN KEY(entity_id) REFERENCES entities(entity_id),
    FOREIGN KEY(artifact_id) REFERENCES artifacts(artifact_id)
);
CREATE TABLE IF NOT EXISTS entity_relations (
    relation_id INTEGER PRIMARY KEY,
    source_entity_id INTEGER NOT NULL,
    relation_kind TEXT NOT NULL,
    target_entity_id INTEGER NOT NULL,
    confidence TEXT NOT NULL DEFAULT 'low',
    evidence_artifact_id INTEGER,
    detail TEXT NOT NULL DEFAULT '',
    UNIQUE(source_entity_id, relation_kind, target_entity_id, evidence_artifact_id),
    FOREIGN KEY(source_entity_id) REFERENCES entities(entity_id),
    FOREIGN KEY(target_entity_id) REFERENCES entities(entity_id),
    FOREIGN KEY(evidence_artifact_id) REFERENCES artifacts(artifact_id)
);
CREATE TABLE IF NOT EXISTS python_imports (
    artifact_id INTEGER NOT NULL,
    import_name TEXT NOT NULL,
    import_kind TEXT NOT NULL,
    PRIMARY KEY(artifact_id, import_name, import_kind),
    FOREIGN KEY(artifact_id) REFERENCES artifacts(artifact_id)
);
CREATE TABLE IF NOT EXISTS effort_metrics (
    artifact_id INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    is_present INTEGER NOT NULL,
    meta_keys_json TEXT NOT NULL DEFAULT '[]',
    unknown_meta_keys_json TEXT NOT NULL DEFAULT '[]',
    method_source TEXT NOT NULL,
    PRIMARY KEY(artifact_id, metric_name),
    FOREIGN KEY(artifact_id) REFERENCES artifacts(artifact_id)
);
CREATE TABLE IF NOT EXISTS classification_queue (
    queue_id INTEGER PRIMARY KEY,
    artifact_id INTEGER NOT NULL,
    candidate_kind TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    evidence_packet TEXT NOT NULL DEFAULT '',
    UNIQUE(artifact_id, candidate_kind),
    FOREIGN KEY(artifact_id) REFERENCES artifacts(artifact_id)
);
CREATE TABLE IF NOT EXISTS method_sources (
    method_id INTEGER PRIMARY KEY,
    method_name TEXT NOT NULL UNIQUE,
    source_kind TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    status TEXT NOT NULL,
    contract_summary TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
    audit_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    event_kind TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    status TEXT NOT NULL,
    detail TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES scan_runs(run_id)
);
CREATE INDEX IF NOT EXISTS idx_artifacts_root_kind ON artifacts(root_kind);
CREATE INDEX IF NOT EXISTS idx_artifacts_suffix ON artifacts(suffix);
CREATE INDEX IF NOT EXISTS idx_events_artifact ON temporal_events(artifact_id);
CREATE INDEX IF NOT EXISTS idx_events_time ON temporal_events(observed_at);
CREATE INDEX IF NOT EXISTS idx_entities_kind ON entities(entity_kind);
CREATE INDEX IF NOT EXISTS idx_queue_status ON classification_queue(status);
CREATE VIEW IF NOT EXISTS chronology_ranked AS
SELECT a.artifact_id,a.path,a.root_kind,a.artifact_kind,
       t.event_type,t.observed_at,t.confidence,t.detail,
       CASE t.event_type
         WHEN 'git_first_commit' THEN 1
         WHEN 'filename_timestamp' THEN 2
         WHEN 'filesystem_mtime' THEN 3
         WHEN 'filesystem_ctime' THEN 4
         WHEN 'content_date_reference' THEN 5
         ELSE 99
       END AS evidence_rank
FROM artifacts a JOIN temporal_events t ON t.artifact_id=a.artifact_id;
"""


def utc_iso(epoch_ns):
    if not epoch_ns:
        return None
    return datetime.fromtimestamp(epoch_ns / 1_000_000_000, timezone.utc).isoformat()


def parse_date(value):
    value = value.replace("_", "-").replace(" ", "T")
    value = value.replace("T-", "T").replace("T_", "T")
    for fmt in ("%Y-%m-%dT%H-%M-%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H-%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(
                tzinfo=timezone.utc).isoformat()
        except ValueError:
            pass
    return None


def dates_in(text, limit=5):
    found = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            parsed = parse_date(match.group("value"))
            if parsed and parsed not in found:
                found.append(parsed)
            if len(found) >= limit:
                return found
    return found


def is_virtual_environment(path):
    """A directory Python itself marks as a virtual environment.

    The name lists below are names, and a name list only catches the names
    someone thought of. Measured: 1463 of the 8273 rows in
    ``classification_queue`` -- 17.7% of the whole queue -- came from ONE
    directory, ``/home/mak/curatoria_inbox/3d/NEW/env``, a Windows virtualenv
    copied onto this box. ``ACTIVE_SKIP`` holds ``venvs``, ``.venvs`` and
    ``venv-providers`` and misses both ``env`` and the Windows layout
    ``env/Lib/site-packages``.

    ``pyvenv.cfg`` is not a naming convention: PEP 405 requires the interpreter
    to write it at the environment root, and ``sys.prefix`` is derived from it.
    Testing for the file is a definition instead of a guess, and it holds for a
    directory called anything at all.
    """
    return (path / "pyvenv.cfg").is_file()


def should_skip_dir(path, root_kind):
    # Name-based decisions come first because they cost nothing. The
    # `pyvenv.cfg` test below stats the directory, and two of the names in
    # ACTIVE_SKIP are `fuse.rclone` mounts: asking the cloud whether it holds a
    # virtualenv marker, in order to decide never to read the cloud, is one
    # network round trip -- or one hang -- per mount.
    if path.name.startswith("."):
        return True
    if path.name in (ACTIVE_SKIP if root_kind == "active" else HISTORY_SKIP):
        return True
    if path.name in {"site-packages", "dist-packages"}:
        # Reached when the environment root is above the scan root, so the
        # pyvenv.cfg test never sees it.
        return True
    return is_virtual_environment(path)


def iter_files(root, root_kind):
    if root.is_file():
        yield root
        return
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        for entry in entries:
            path = Path(entry.path)
            try:
                if entry.is_dir(follow_symlinks=False):
                    if not should_skip_dir(path, root_kind):
                        stack.append(path)
                elif entry.is_file(follow_symlinks=False):
                    yield path
            except OSError:
                continue


def read_text(path, max_bytes):
    if path.suffix.lower() not in TEXT_EXTS:
        return None, "binary"
    try:
        raw = path.read_bytes()
    except OSError:
        return None, "unreadable"
    if len(raw) > max_bytes:
        return None, "too_large"
    try:
        return raw.decode("utf-8"), "utf8"
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace"), "utf8_repaired"


def document_fields(text):
    if not text:
        return {"title": None, "status": None, "work_id": None, "purpose": None}
    title = next((line[2:].strip() for line in text.splitlines()[:160]
                  if line.startswith("# ")), None)
    front = {}
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:120]:
            if line.strip() == "---":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                front[key.strip().lower()] = value.strip().strip("'").strip('"')
    return {
        "title": title,
        "status": front.get("status"),
        "work_id": front.get("work_id"),
        "purpose": front.get("purpose"),
    }


def artifact_kind(path):
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix in {".md", ".txt", ".odt", ".docx"}:
        return "document"
    if suffix in {".html", ".htm", ".css", ".js", ".ts", ".tsx", ".jsx"}:
        return "interface_or_web"
    if suffix in {".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return "configuration_or_data"
    if suffix in MEDIA_EXTS:
        return "media_or_binary"
    return "file"


def is_interface_candidate(path, text):
    if path.suffix.lower() in {".html", ".htm"}:
        return True
    if path.name.lower() in {
        "hub.py", "interfaz.py", "serve.py", "server.py", "app.py",
        "web.py", "editor.py", "dashboard.py",
    }:
        return True
    if text:
        return any(marker in text for marker in (
            "BaseHTTPRequestHandler", "HTTPServer", "FastAPI",
            "@app.route", "NiceGUI", "<html",
        ))
    return False


def nearest_department(path, active_root, history_root):
    try:
        rel = path.relative_to(active_root)
        return rel.parts[0] if rel.parts else active_root.name
    except ValueError:
        try:
            rel = path.relative_to(history_root)
            return "WIN/" + (rel.parts[0] if rel.parts else "flujo")
        except ValueError:
            return "unknown"


def get_or_create_entity(conn, kind, name, path=None, status="unclassified",
                         purpose=None, idea=None, origin=None, confidence="low"):
    conn.execute(
        "INSERT OR IGNORE INTO entities(entity_kind,canonical_name,path,status,"
        "purpose,idea,origin,confidence) VALUES(?,?,?,?,?,?,?,?)",
        (kind, name, path, status, purpose, idea, origin, confidence),
    )
    row = conn.execute(
        "SELECT entity_id FROM entities WHERE entity_kind=? AND "
        "canonical_name=? AND path IS ?",
        (kind, name, path),
    ).fetchone()
    if row is None:
        raise RuntimeError("entity insert failed: %s/%s" % (kind, name))
    return int(row[0])


def add_event(conn, artifact_id, event_type, observed_at, source_path,
              confidence, detail, run_id):
    conn.execute(
        "INSERT OR IGNORE INTO temporal_events(artifact_id,event_type,"
        "observed_at,source_path,confidence,detail,run_id) VALUES(?,?,?,?,?,?,?)",
        (artifact_id, event_type, observed_at, source_path, confidence, detail, run_id),
    )


def add_imports(conn, artifact_id, text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                conn.execute("INSERT OR IGNORE INTO python_imports VALUES(?,?,?)",
                             (artifact_id, alias.name, "import"))
        elif isinstance(node, ast.ImportFrom):
            name = "." * node.level + (node.module or "")
            if name:
                conn.execute("INSERT OR IGNORE INTO python_imports VALUES(?,?,?)",
                             (artifact_id, name, "from"))


def effort_values(doc):
    """Read the esfuerzo.py contract; missing values remain missing."""
    meta = doc.get("meta") if isinstance(doc.get("meta"), dict) else {}

    def lookup(*keys):
        for key in keys:
            if key in meta and meta[key] is not None:
                return meta[key]
            if key in doc and doc[key] is not None:
                return doc[key]
        return None

    iterations = lookup("iterations", "iteration")
    calls = lookup("llmCalls")
    if isinstance(calls, dict):
        numeric = [v for v in calls.values()
                   if isinstance(v, int) and not isinstance(v, bool)]
        calls_total = sum(numeric) if numeric else None
        depth = len([v for v in numeric if v > 0]) if numeric else None
    else:
        calls_total, depth = None, None
    queries = lookup("queries", "query_history")
    sources = lookup("sources", "seen_urls")
    if sources is None and isinstance(doc.get("findings"), list):
        urls = {x.get("url") for x in doc["findings"]
                if isinstance(x, dict) and x.get("url")}
        sources = len(urls) or None
    errors = lookup("errors")
    timeouts = lookup("timeouts")
    values = {
        "iteraciones": iterations if isinstance(iterations, (int, float))
        else (len(iterations) if isinstance(iterations, (list, tuple, dict, str))
              else None),
        "llamadas_llm": calls_total,
        "profundidad_cadena": depth,
        "errores": len(errors) if isinstance(errors, list) else None,
        "timeouts": len(timeouts) if isinstance(timeouts, list) else timeouts,
        "consultas": len(queries) if isinstance(queries, list) else None,
        "fuentes": len(sources) if isinstance(sources, list) else sources,
        "duracion_ms": lookup("duration_ms", "duration", "ms"),
    }
    for key in ("report", "informe", "summary", "sintesis"):
        if isinstance(doc.get(key), str):
            values["largo_informe"] = len(doc[key])
            break
    query_values = []
    if isinstance(queries, list):
        for item in queries:
            if isinstance(item, str):
                query_values.append(item.strip())
            elif isinstance(item, dict):
                for key in ("query", "text", "q", "consulta"):
                    if isinstance(item.get(key), str):
                        query_values.append(item[key].strip())
                        break
    if len(query_values) >= 2:
        values["deriva_consultas"] = len(set(query_values)) / len(query_values)
    return {
        key: float(value) for key, value in values.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }, sorted(meta.keys()), sorted(set(meta) - META_READ_KEYS - META_KNOWN_UNUSED)


def load_git_provenance(conn, repo, by_path, run_id):
    command = [
        "git", "-C", str(repo), "log", "--all", "--date=iso-strict",
        "--format=__COMMIT__%x09%H%x09%aI%x09%s", "--name-only",
    ]
    try:
        proc = subprocess.run(command, check=False, capture_output=True,
                              text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return "unavailable:%s" % type(exc).__name__
    if proc.returncode != 0:
        return "error:%s" % proc.stderr.strip()[:200]
    commits = defaultdict(list)
    current = None
    for raw in proc.stdout.splitlines():
        if raw.startswith("__COMMIT__\t"):
            parts = raw.split("\t", 3)
            current = parts[1:4] if len(parts) == 4 else None
            continue
        rel = raw.strip()
        if not current or not rel:
            continue
        full = str((repo / rel).resolve())
        if full in by_path:
            commits[full].append((current[1], current[0], current[2]))
    for full, entries in commits.items():
        entries.sort(key=lambda row: row[0])
        first, last = entries[0], entries[-1]
        artifact_id = by_path[full]
        add_event(conn, artifact_id, "git_first_commit", first[0], str(repo),
                  "high", json.dumps({"commit": first[1],
                  "subject": first[2], "count": len(entries)}), run_id)
        add_event(conn, artifact_id, "git_last_commit", last[0], str(repo),
                  "high", json.dumps({"commit": last[1],
                  "subject": last[2], "count": len(entries)}), run_id)
    return "ok:files=%d" % len(commits)


def add_static_consumers(conn, repo_root, active_root, run_id):
    """Link selected importer files to Python tool candidates.

    This is static evidence only: an import is not proof that a runtime route
    executed. The low-confidence relation is deliberately reviewable.
    """
    module_to_artifacts = defaultdict(list)
    source_roots = [repo_root / "src", active_root / "src"]
    for source_root in source_roots:
        if not source_root.is_dir():
            continue
        for path in source_root.rglob("*.py"):
            try:
                rel = path.relative_to(source_root)
            except ValueError:
                continue
            parts = list(rel.parts)
            if parts[-1] == "__init__.py":
                parts = parts[:-1]
            else:
                parts[-1] = Path(parts[-1]).stem
            if parts:
                module_to_artifacts[".".join(parts)].append(str(path.resolve()))

    importer_rows = conn.execute(
        "SELECT DISTINCT a.artifact_id,a.path,a.root_kind,pi.import_name "
        "FROM python_imports pi JOIN artifacts a ON a.artifact_id=pi.artifact_id "
        "WHERE a.suffix='.py'"
    ).fetchall()
    relation_count = 0
    consumer_ids = set()
    for artifact_id, raw_path, root_kind, import_name in importer_rows:
        if import_name.startswith(".") or not import_name:
            continue
        path = Path(raw_path)
        parts = set(path.parts)
        is_consumer = (
            path.name != "__init__.py" and
            ({"web", "serve", "dashboard", "tests", "scripts", "projects",
              "cultura", "jobs", "intake", "eventos", "research", "rd"}
             & parts)
        )
        if not is_consumer:
            continue
        target_paths = module_to_artifacts.get(import_name, [])
        if not target_paths:
            continue
        consumer_id = get_or_create_entity(
            conn, "consumer_candidate", path.stem, str(path),
            status="historical" if root_kind == "historical" else "unclassified",
            purpose="static importer; runtime use not yet proven",
            origin=str(path.parent), confidence="low",
        )
        consumer_ids.add(consumer_id)
        conn.execute(
            "INSERT OR IGNORE INTO entity_artifacts VALUES(?,?,?,?)",
            (consumer_id, artifact_id, "consumer_source", "low"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO classification_queue"
            "(artifact_id,candidate_kind,reason,evidence_packet) VALUES(?,?,?,?)",
            (artifact_id, "consumer",
             "AST import indicates a possible consumer; runtime route needs validation",
             import_name),
        )
        for target_path in target_paths:
            target_row = conn.execute(
                "SELECT artifact_id FROM artifacts WHERE path=?", (target_path,)
            ).fetchone()
            if target_row is None:
                continue
            tool_rows = conn.execute(
                "SELECT e.entity_id FROM entity_artifacts ea JOIN entities e "
                "ON e.entity_id=ea.entity_id WHERE ea.artifact_id=? "
                "AND e.entity_kind='tool_candidate'",
                (target_row[0],),
            ).fetchall()
            for (tool_id,) in tool_rows:
                conn.execute(
                    "INSERT OR IGNORE INTO entity_relations"
                    "(source_entity_id,relation_kind,target_entity_id,confidence,"
                    "evidence_artifact_id,detail) VALUES(?,?,?,?,?,?)",
                    (tool_id, "possibly_consumed_by", consumer_id, "low",
                     artifact_id, "AST import: " + import_name),
                )
                relation_count += 1
    return len(consumer_ids), relation_count


def scan(args):
    active_root = Path(args.active_root).resolve()
    history_root = Path(args.history_root).resolve()
    repo_root = Path(args.repo_root).resolve()
    db_path = Path(args.db).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.executescript(SCHEMA)
    effort_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(effort_metrics)")
    }
    if "unknown_meta_keys_json" not in effort_columns:
        conn.execute(
            "ALTER TABLE effort_metrics ADD COLUMN "
            "unknown_meta_keys_json TEXT NOT NULL DEFAULT '[]'"
        )
    started = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO scan_runs(started_at,active_root,history_root,repo_root)"
        " VALUES(?,?,?,?)",
        (started, str(active_root), str(history_root), str(repo_root)),
    )
    run_id = int(cur.lastrowid)
    conn.execute(
        "INSERT OR REPLACE INTO method_sources(method_name,source_kind,"
        "source_ref,status,contract_summary) VALUES(?,?,?,?,?)",
        (
            "esfuerzo.py", "user_attachment",
            "attachment:d7e3f292-059c-4085-9aba-05eea8e73f3d/pasted-text.txt",
            "contract_read_not_physical",
            "discover metrics; preserve missing; report unknown meta keys; "
            "compute residuals by mode",
        ),
    )
    by_path = {}
    effort_found = False
    files_seen = files_indexed = text_hashed = 0
    active_paths = [active_root / name for name in sorted(ACTIVE_ROOT_NAMES)
                    if (active_root / name).exists()]
    active_paths += sorted(path for path in active_root.iterdir()
                           if path.is_file())
    history_paths = [history_root / name for name in sorted(HISTORY_ROOT_NAMES)
                     if (history_root / name).exists()]
    scan_specs = ([(path, "active") for path in active_paths] +
                  [(path, "historical") for path in history_paths])
    conn.execute(
        "INSERT INTO audit_events(run_id,event_kind,source_ref,status,detail) "
        "VALUES(?,?,?,?,?)",
        (run_id, "scan_scope", str(active_root), "bounded",
         json.dumps({"active": [str(p) for p in active_paths],
                     "historical": [str(p) for p in history_paths]},
                    ensure_ascii=True, sort_keys=True)),
    )
    limit_reached = False
    for root, kind in scan_specs:
        for path in iter_files(root, kind):
            files_seen += 1
            if args.max_files and files_seen > args.max_files:
                limit_reached = True
                break
            try:
                st = path.stat()
            except OSError:
                continue
            text, text_status = read_text(path, args.max_text_bytes)
            fields = document_fields(text)
            digest = None
            if text is not None:
                try:
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    text_hashed += 1
                except OSError:
                    pass
            rel_path = str(path.relative_to(root))
            conn.execute(
                "INSERT INTO artifacts(path,root_kind,relative_path,name,suffix,"
                "artifact_kind,size_bytes,mode,mtime_ns,ctime_ns,birthtime_ns,"
                "sha256,text_title,declared_status,declared_work_id,"
                "declared_purpose,first_run_id,last_run_id) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(path) DO UPDATE SET root_kind=excluded.root_kind,"
                "relative_path=excluded.relative_path,name=excluded.name,"
                "suffix=excluded.suffix,artifact_kind=excluded.artifact_kind,"
                "size_bytes=excluded.size_bytes,mode=excluded.mode,"
                "mtime_ns=excluded.mtime_ns,ctime_ns=excluded.ctime_ns,"
                "birthtime_ns=excluded.birthtime_ns,sha256=excluded.sha256,"
                "text_title=excluded.text_title,declared_status=excluded.declared_status,"
                "declared_work_id=excluded.declared_work_id,"
                "declared_purpose=excluded.declared_purpose,last_run_id=excluded.last_run_id",
                (
                    str(path), kind, rel_path, path.name, path.suffix.lower(),
                    artifact_kind(path), st.st_size, oct(st.st_mode & 0o777),
                    st.st_mtime_ns, st.st_ctime_ns,
                    getattr(st, "st_birthtime_ns", None), digest,
                    fields["title"], fields["status"], fields["work_id"],
                    fields["purpose"], run_id, run_id,
                ),
            )
            artifact_id = int(conn.execute(
                "SELECT artifact_id FROM artifacts WHERE path=?", (str(path),)
            ).fetchone()[0])
            by_path[str(path.resolve())] = artifact_id
            files_indexed += 1
            mtime = utc_iso(st.st_mtime_ns)
            ctime = utc_iso(st.st_ctime_ns)
            if mtime:
                add_event(conn, artifact_id, "filesystem_mtime", mtime,
                          str(path), "medium", text_status, run_id)
            if ctime:
                add_event(conn, artifact_id, "filesystem_ctime", ctime,
                          str(path), "low",
                          "inode metadata, not creation proof", run_id)
            for date in dates_in(path.name):
                add_event(conn, artifact_id, "filename_timestamp", date,
                          str(path), "medium", "timestamp-like filename token",
                          run_id)
            for date in dates_in(text or ""):
                add_event(conn, artifact_id, "content_date_reference", date,
                          str(path), "low",
                          "date found in content; not creation proof", run_id)
            if path.name.lower() == "esfuerzo.py":
                effort_found = True
            if path.suffix.lower() == ".py" and text is not None:
                add_imports(conn, artifact_id, text)
            dept_name = nearest_department(path, active_root, history_root)
            dept_id = get_or_create_entity(
                conn, "department", dept_name, dept_name,
                status="historical" if kind == "historical" else "active",
                origin=str(path), confidence="medium",
            )
            conn.execute(
                "INSERT OR IGNORE INTO entity_artifacts VALUES(?,?,?,?)",
                (dept_id, artifact_id, "located_under", "medium"),
            )
            if path.suffix.lower() == ".py":
                tool_id = get_or_create_entity(
                    conn, "tool_candidate", path.stem, str(path),
                    status=fields["status"] or (
                        "historical" if kind == "historical"
                        else "unclassified"
                    ),
                    purpose=fields["purpose"], idea=fields["title"],
                    origin=dept_name, confidence="medium",
                )
                conn.execute(
                    "INSERT OR IGNORE INTO entity_artifacts VALUES(?,?,?,?)",
                    (tool_id, artifact_id, "implementation", "medium"),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO entity_relations("
                    "source_entity_id,relation_kind,target_entity_id,confidence,"
                    "evidence_artifact_id,detail) VALUES(?,?,?,?,?,?)",
                    (tool_id, "located_in", dept_id, "medium", artifact_id,
                     dept_name),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO classification_queue("
                    "artifact_id,candidate_kind,reason,evidence_packet) VALUES(?,?,?,?)",
                    (artifact_id, "tool",
                     "python implementation requires purpose and consumer "
                     "classification", fields["title"] or ""),
                )
            if is_interface_candidate(path, text):
                int_id = get_or_create_entity(
                    conn, "interface_candidate", path.stem, str(path),
                    status=fields["status"] or (
                        "historical" if kind == "historical"
                        else "unclassified"
                    ),
                    purpose=fields["purpose"], idea=fields["title"],
                    origin=dept_name, confidence="medium",
                )
                conn.execute(
                    "INSERT OR IGNORE INTO entity_artifacts VALUES(?,?,?,?)",
                    (int_id, artifact_id, "interface", "medium"),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO entity_relations("
                    "source_entity_id,relation_kind,target_entity_id,confidence,"
                    "evidence_artifact_id,detail) VALUES(?,?,?,?,?,?)",
                    (int_id, "serves_department", dept_id, "low", artifact_id,
                     "interface route needs consumer audit"),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO classification_queue("
                    "artifact_id,candidate_kind,reason,evidence_packet) VALUES(?,?,?,?)",
                    (artifact_id, "interface",
                     "interface candidate requires route and consumer "
                     "classification", fields["title"] or ""),
                )
            if path.suffix.lower() == ".md" and any(
                part in {"dossiers", "projects", "curatoria_inbox",
                         "research", "funding-lab"} for part in path.parts
            ):
                idea_id = get_or_create_entity(
                    conn, "idea_candidate", fields["title"] or path.stem,
                    str(path), status=fields["status"] or (
                        "historical" if kind == "historical"
                        else "unclassified"
                    ),
                    purpose=fields["purpose"], idea=fields["title"],
                    origin=dept_name, confidence="low",
                )
                conn.execute(
                    "INSERT OR IGNORE INTO entity_artifacts VALUES(?,?,?,?)",
                    (idea_id, artifact_id, "dossier_or_context", "low"),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO classification_queue("
                    "artifact_id,candidate_kind,reason,evidence_packet) VALUES(?,?,?,?)",
                    (artifact_id, "idea",
                     "markdown candidate requires project and proposal "
                     "classification", fields["title"] or ""),
                )
            if path.suffix.lower() == ".json" and "/research/" in str(path) and text is not None:
                try:
                    doc = json.loads(text)
                except (TypeError, ValueError):
                    doc = None
                if isinstance(doc, dict) and (
                    isinstance(doc.get("meta"), dict)
                    or any(k in doc for k in ("report", "findings", "llmCalls"))
                ):
                    values, meta_keys, unknown_meta_keys = effort_values(doc)
                    metrics = (
                        "iteraciones", "llamadas_llm", "profundidad_cadena",
                        "errores", "timeouts", "consultas", "fuentes",
                        "duracion_ms", "largo_informe", "deriva_consultas",
                    )
                    for metric in metrics:
                        conn.execute(
                            "INSERT OR REPLACE INTO effort_metrics VALUES(?,?,?,?,?,?,?)",
                            (
                                artifact_id, metric, values.get(metric),
                                1 if metric in values else 0,
                                json.dumps(meta_keys, ensure_ascii=True),
                                json.dumps(unknown_meta_keys, ensure_ascii=True),
                                "esfuerzo.py:attachment-contract",
                            ),
                        )
        if limit_reached:
            break
    if limit_reached:
        conn.execute(
            "INSERT INTO audit_events(run_id,event_kind,source_ref,status,detail)"
            " VALUES(?,?,?,?,?)",
            (run_id, "scan_limit", str(active_root), "partial",
             "max_files reached; rerun with a larger limit"),
        )
    consumers, consumer_relations = add_static_consumers(
        conn, repo_root, active_root, run_id
    )
    git_status = load_git_provenance(conn, repo_root, by_path, run_id)
    effort_status = "found_in_scan" if effort_found else "not_found_in_physical_roots"
    conn.execute(
        "INSERT INTO audit_events(run_id,event_kind,source_ref,status,detail)"
        " VALUES(?,?,?,?,?)",
        (run_id, "method_source", "esfuerzo.py", effort_status,
         "user attachment contract registered; physical file search performed"),
    )
    conn.execute(
        "UPDATE scan_runs SET finished_at=?,files_seen=?,files_indexed=?,"
        "text_hashed=?,git_status=?,effort_status=?,notes=? WHERE run_id=?",
        (
            datetime.now(timezone.utc).isoformat(), files_seen, files_indexed,
            text_hashed, git_status, effort_status,
            "metadata first; semantic classification queued; no source copies",
            run_id,
        ),
    )
    conn.commit()
    summary = {
        "db": str(db_path),
        "run_id": run_id,
        "files_seen": files_seen,
        "files_indexed": files_indexed,
        "text_hashed": text_hashed,
        "git_status": git_status,
        "effort_status": effort_status,
        "tools": conn.execute(
            "SELECT count(*) FROM entities WHERE entity_kind='tool_candidate'"
        ).fetchone()[0],
        "consumers": consumers,
        "consumer_relations": consumer_relations,
        "interfaces": conn.execute(
            "SELECT count(*) FROM entities WHERE entity_kind='interface_candidate'"
        ).fetchone()[0],
        "ideas": conn.execute(
            "SELECT count(*) FROM entities WHERE entity_kind='idea_candidate'"
        ).fetchone()[0],
        "events": conn.execute(
            "SELECT count(*) FROM temporal_events"
        ).fetchone()[0],
        "imports": conn.execute(
            "SELECT count(*) FROM python_imports"
        ).fetchone()[0],
        "effort_rows": conn.execute(
            "SELECT count(*) FROM effort_metrics"
        ).fetchone()[0],
        "queue": conn.execute(
            "SELECT count(*) FROM classification_queue WHERE status='pending'"
        ).fetchone()[0],
    }
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    conn.close()
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--active-root", default="/home/mak")
    parser.add_argument("--history-root", default="/home/mak/WIN")
    parser.add_argument("--repo-root", default="/home/mak")
    parser.add_argument("--db", default="/home/mak/data/mak_knowledge.db")
    parser.add_argument("--max-text-bytes", type=int, default=4_000_000)
    parser.add_argument("--max-files", type=int, default=0)
    return scan(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
