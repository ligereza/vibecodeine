#!/usr/bin/env python3
"""Ingesta derivada, repetible y de solo lectura para archivos creativos.

Este modulo une las piezas que ya existen en MAK: inventario determinista,
``percepcion.py`` (OCR + vision) y ``extraccion_db.py`` (candidatos de
identidad).  La raiz es siempre de solo lectura: el unico estado que crea es
una proyeccion SQLite y sus artefactos bajo ``--out``.

No pretende decidir que una imagen *es* una productora, un venue o una
sustancia.  Conserva cada observacion con su fuente, separa las tareas de
resolver evento/productora/venue/logo, y deja un fallo de una etapa como una
tarea reintentable, no como una conclusion negativa.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from collections import Counter
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import unicodedata

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional sensor
    Image = None


SCHEMA = "mak-creative-intake-v1"
CHUNK = 1024 * 1024
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".exr"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
PDF_EXTENSIONS = {".pdf"}
STRUCTURAL_EXTENSIONS = {
    ".psd", ".psb", ".ai", ".blend", ".blend1", ".aep", ".svg",
    ".obj", ".mtl", ".fbx", ".glb", ".gltf", ".vdb", ".uasset", ".toe",
}
REPO_ROOT = Path(__file__).resolve().parents[2]
CITY_ALIASES = {
    "santiago": "Santiago",
    "valparaiso": "Valparaíso",
    "vina del mar": "Viña del Mar",
    "concepcion": "Concepción",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_stream(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raster_metadata(path: Path) -> dict:
    """Read cheap, deterministic raster metadata without visual inference.

    Blender PNG exports commonly carry ``File`` and ``Date`` in PNG text
    chunks. Those fields are valuable lineage evidence, but they do not prove
    authorship or event identity. Binary metadata is represented by length and
    hash so the derived database remains JSON-safe and bounded.
    """
    if Image is None or not hasattr(Image, "open"):
        return {"status": "DEFERRED_TOOL", "reason": "pillow_unavailable"}
    try:
        with Image.open(path) as image:
            info = {}
            for key, value in (image.info or {}).items():
                name = str(key)
                if isinstance(value, bytes):
                    info[name] = {"bytes": len(value),
                                  "sha256": hashlib.sha256(value).hexdigest()}
                elif isinstance(value, (str, int, float, bool)):
                    info[name] = str(value)[:4096]
                else:
                    info[name] = str(value)[:4096]
            exif = {}
            try:
                for tag, value in image.getexif().items():
                    if isinstance(value, (str, int, float, bool)):
                        exif[str(tag)] = str(value)[:1024]
            except (AttributeError, ValueError, OSError):
                pass
            return {"status": "OBSERVED", "format": image.format,
                    "mode": image.mode, "width": image.width,
                    "height": image.height, "info": info, "exif": exif,
                    "observer": "Pillow"}
    except (OSError, ValueError, SyntaxError) as exc:
        return {"status": "RETRY", "reason": str(exc)[:240]}


def sample_fingerprint(path: Path, size: int) -> str:
    """A cheap *non-identity* fingerprint, explicit about its limitation.

    It lets the first pass detect likely repeats without pretending that a
    3 GB video was fully hashed.  ``full_sha256`` is only populated after a
    streaming hash and is the only value used for exact duplicate relations.
    """
    digest = hashlib.sha256()
    digest.update(str(size).encode("ascii"))
    with path.open("rb") as handle:
        digest.update(handle.read(CHUNK))
        if size > CHUNK:
            handle.seek(max(0, size - CHUNK))
            digest.update(handle.read(CHUNK))
    return digest.hexdigest()


def media_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in PDF_EXTENSIONS:
        return "pdf"
    if ext in STRUCTURAL_EXTENSIONS:
        return "structural"
    return "other"


def source_key(root: Path) -> str:
    return hashlib.sha256(str(root.resolve()).encode("utf-8")).hexdigest()[:20]


def asset_key(root_key: str, relative_path: str) -> str:
    return hashlib.sha256((root_key + "\0" + relative_path).encode("utf-8")).hexdigest()


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def connect(out: Path) -> sqlite3.Connection:
    out.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(out / "archivo_index.sqlite")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS runs (
          run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT,
          root TEXT NOT NULL, schema_name TEXT NOT NULL, summary_json TEXT
        );
        CREATE TABLE IF NOT EXISTS assets (
          asset_id TEXT PRIMARY KEY, source_key TEXT NOT NULL, relative_path TEXT NOT NULL,
          extension TEXT NOT NULL, media_kind TEXT NOT NULL, bytes INTEGER NOT NULL,
          mtime_ns INTEGER NOT NULL, sample_sha256 TEXT, full_sha256 TEXT,
          hash_state TEXT NOT NULL, hash_error TEXT, indexed_at TEXT NOT NULL,
          UNIQUE(source_key, relative_path)
        );
        CREATE INDEX IF NOT EXISTS assets_full_sha ON assets(full_sha256)
          WHERE full_sha256 IS NOT NULL;
        CREATE INDEX IF NOT EXISTS assets_sample_sha ON assets(sample_sha256);
        CREATE TABLE IF NOT EXISTS jobs (
          job_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(asset_id),
          stage TEXT NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
          last_error TEXT, updated_at TEXT NOT NULL, UNIQUE(asset_id, stage)
        );
        CREATE TABLE IF NOT EXISTS observations (
          observation_id INTEGER PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(asset_id),
          observer TEXT NOT NULL, field TEXT NOT NULL, value_json TEXT NOT NULL,
          status TEXT NOT NULL, observed_at TEXT NOT NULL,
          UNIQUE(asset_id, observer, field)
        );
        CREATE TABLE IF NOT EXISTS candidates (
          candidate_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(asset_id),
          kind TEXT NOT NULL, value TEXT NOT NULL, confidence REAL,
          evidence_json TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
          UNIQUE(asset_id, kind, value)
        );
        CREATE TABLE IF NOT EXISTS relations (
          relation_id TEXT PRIMARY KEY, left_id TEXT NOT NULL, relation TEXT NOT NULL,
          right_id TEXT NOT NULL, evidence_json TEXT NOT NULL, confidence REAL,
           status TEXT NOT NULL, UNIQUE(left_id, relation, right_id)
        );
        CREATE TABLE IF NOT EXISTS source_roots (
          source_key TEXT PRIMARY KEY, root_path TEXT NOT NULL,
          source_role TEXT NOT NULL, read_policy TEXT NOT NULL,
          observed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cartel_modules (
          module_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(asset_id),
          module_index INTEGER NOT NULL, x0 INTEGER NOT NULL, y0 INTEGER NOT NULL,
          x1 INTEGER NOT NULL, y1 INTEGER NOT NULL, crop_path TEXT,
          ocr_text TEXT NOT NULL, evidence_json TEXT NOT NULL,
          status TEXT NOT NULL, observed_at TEXT NOT NULL,
          UNIQUE(asset_id, module_index)
        );
        CREATE TABLE IF NOT EXISTS cartel_module_candidates (
          candidate_id TEXT PRIMARY KEY, module_id TEXT NOT NULL,
          kind TEXT NOT NULL, value TEXT NOT NULL, confidence REAL,
          evidence_json TEXT NOT NULL, status TEXT NOT NULL,
          observed_at TEXT NOT NULL, UNIQUE(module_id, kind, value)
        );
        """
    )
    return conn


def set_job(conn: sqlite3.Connection, asset_id: str, stage: str, status: str,
            error: str | None = None, increment: bool = False) -> None:
    job_id = hashlib.sha256((asset_id + "\0" + stage).encode("ascii")).hexdigest()
    conn.execute(
        """INSERT INTO jobs(job_id, asset_id, stage, status, attempts, last_error, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(asset_id, stage) DO UPDATE SET
             status=excluded.status,
             attempts=jobs.attempts + excluded.attempts,
             last_error=excluded.last_error,
             updated_at=excluded.updated_at""",
        (job_id, asset_id, stage, status, 1 if increment else 0, error, now()),
    )


def ensure_job(conn: sqlite3.Connection, asset_id: str, stage: str,
               status: str = "ready") -> None:
    """Schedule missing work without resetting a completed checkpoint."""
    job_id = hashlib.sha256((asset_id + "\0" + stage).encode("ascii")).hexdigest()
    conn.execute(
        """INSERT INTO jobs(job_id, asset_id, stage, status, attempts, last_error, updated_at)
           VALUES (?, ?, ?, ?, 0, NULL, ?)
           ON CONFLICT(asset_id, stage) DO NOTHING""",
        (job_id, asset_id, stage, status, now()),
    )


def store_observation(conn: sqlite3.Connection, asset_id: str, observer: str,
                      field: str, value, status: str = "observed") -> None:
    conn.execute(
        """INSERT INTO observations(asset_id, observer, field, value_json, status, observed_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(asset_id, observer, field) DO UPDATE SET
             value_json=excluded.value_json, status=excluded.status,
             observed_at=excluded.observed_at""",
        (asset_id, observer, field, json.dumps(value, ensure_ascii=False), status, now()),
    )


def store_candidate(conn: sqlite3.Connection, asset_id: str, kind: str, value: str,
                    evidence: dict, confidence: float | None = None,
                    status: str = "candidate") -> None:
    if not value:
        return
    candidate_id = hashlib.sha256((asset_id + "\0" + kind + "\0" + value).encode("utf-8")).hexdigest()
    conn.execute(
        """INSERT INTO candidates(candidate_id, asset_id, kind, value, confidence,
           evidence_json, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(asset_id, kind, value) DO UPDATE SET
             confidence=excluded.confidence, evidence_json=excluded.evidence_json,
             status=excluded.status""",
        (candidate_id, asset_id, kind, value, confidence,
         json.dumps(evidence, ensure_ascii=False), status, now()),
    )


def store_relation(conn: sqlite3.Connection, left_id: str, relation: str, right_id: str,
                   evidence: dict, confidence: float | None, status: str) -> None:
    relation_id = hashlib.sha256((left_id + "\0" + relation + "\0" + right_id).encode("utf-8")).hexdigest()
    conn.execute(
        """INSERT INTO relations(relation_id,left_id,relation,right_id,evidence_json,confidence,status)
           VALUES(?,?,?,?,?,?,?)
           ON CONFLICT(left_id,relation,right_id) DO UPDATE SET evidence_json=excluded.evidence_json,
             confidence=excluded.confidence,status=excluded.status""",
        (relation_id, left_id, relation, right_id, json.dumps(evidence, ensure_ascii=False),
        confidence, status),
    )


def register_source_root(conn: sqlite3.Connection, root: Path,
                         source_role: str = "external_evidence",
                         read_policy: str = "read_only_observation") -> str:
    """Register a mounted/local root without copying or changing its files."""
    key = source_key(root)
    conn.execute(
        """INSERT INTO source_roots(source_key,root_path,source_role,read_policy,observed_at)
           VALUES(?,?,?,?,?) ON CONFLICT(source_key) DO UPDATE SET
             root_path=excluded.root_path,source_role=excluded.source_role,
             read_policy=excluded.read_policy,observed_at=excluded.observed_at""",
        (key, str(Path(root).resolve()), str(source_role), str(read_policy), now()),
    )
    return key


def store_cartel_module_candidate(conn: sqlite3.Connection, module_id: str,
                                  kind: str, value: str, evidence: dict,
                                  confidence: float | None = None,
                                  status: str = "candidate") -> None:
    """Store a module-level candidate without pretending the whole image is one event."""
    module_id, kind, value = str(module_id or "").strip(), str(kind or "").strip(), str(value or "").strip()
    if not module_id or not kind or not value:
        return
    candidate_id = hashlib.sha256((module_id + "\0" + kind + "\0" + value).encode("utf-8")).hexdigest()
    conn.execute(
        """INSERT INTO cartel_module_candidates
           (candidate_id,module_id,kind,value,confidence,evidence_json,status,observed_at)
           VALUES (?,?,?,?,?,?,?,?)
           ON CONFLICT(module_id,kind,value) DO UPDATE SET
             confidence=excluded.confidence,evidence_json=excluded.evidence_json,
             status=excluded.status,observed_at=excluded.observed_at""",
        (candidate_id, module_id, kind, value, confidence,
         json.dumps(evidence, ensure_ascii=False), status, now()),
    )


def _ensure_composite_schema(conn: sqlite3.Connection) -> None:
    """Add the composite-cartel projection to an existing derived index."""
    conn.executescript(
        """CREATE TABLE IF NOT EXISTS cartel_modules (
          module_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(asset_id),
          module_index INTEGER NOT NULL, x0 INTEGER NOT NULL, y0 INTEGER NOT NULL,
          x1 INTEGER NOT NULL, y1 INTEGER NOT NULL, crop_path TEXT,
          ocr_text TEXT NOT NULL, evidence_json TEXT NOT NULL,
          status TEXT NOT NULL, observed_at TEXT NOT NULL,
          UNIQUE(asset_id, module_index)
        );
        CREATE TABLE IF NOT EXISTS cartel_module_candidates (
          candidate_id TEXT PRIMARY KEY, module_id TEXT NOT NULL,
          kind TEXT NOT NULL, value TEXT NOT NULL, confidence REAL,
          evidence_json TEXT NOT NULL, status TEXT NOT NULL,
          observed_at TEXT NOT NULL, UNIQUE(module_id, kind, value)
        );"""
    )


def _ensure_folder_research_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """CREATE TABLE IF NOT EXISTS cartel_folder_research (
          research_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(asset_id),
          token TEXT NOT NULL, matched_asset_id TEXT, matched_path TEXT,
          match_basis TEXT NOT NULL, evidence_json TEXT NOT NULL,
          status TEXT NOT NULL, observed_at TEXT NOT NULL,
          UNIQUE(asset_id, token, matched_asset_id, match_basis)
        );"""
    )


def scan_folder_identity_history(conn: sqlite3.Connection, root: Path,
                                 asset_id: str, tokens: list[str],
                                 limit: int = 200) -> dict:
    """Search the whole indexed folder for bounded historical candidates."""
    _ensure_folder_research_schema(conn)
    clean = []
    for token in tokens:
        normalized = _cartel_norm(token)
        if normalized and normalized not in clean:
            clean.append(normalized)
    hits = 0
    rows = conn.execute("SELECT asset_id,relative_path FROM assets").fetchall()
    for row in rows:
        path_norm = _cartel_norm(row["relative_path"])
        observations = conn.execute(
            "SELECT value_json FROM observations WHERE asset_id=? AND observer='percepcion'",
            (row["asset_id"],)).fetchall()
        perception_norm = _cartel_norm(" ".join(str(item["value_json"] or "") for item in observations))
        for token in clean:
            basis = "relative_path" if token in path_norm else (
                "prior_perception" if token in perception_norm else "")
            if not basis:
                continue
            evidence = {"token": token, "basis": basis,
                        "policy": "historical_candidate_not_identity",
                        "source_root": str(root)}
            research_id = hashlib.sha256(
                (asset_id + "\0" + token + "\0" + str(row["asset_id"]) + "\0" + basis).encode("utf-8")
            ).hexdigest()
            conn.execute(
                """INSERT OR REPLACE INTO cartel_folder_research
                   (research_id,asset_id,token,matched_asset_id,matched_path,match_basis,evidence_json,status,observed_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (research_id, asset_id, token, row["asset_id"], row["relative_path"],
                 basis, json.dumps(evidence, ensure_ascii=False), "candidate", now()),
            )
            hits += 1
            if hits >= limit:
                conn.commit()
                return {"status": "PROJECTED", "tokens": clean, "hits": hits, "truncated": True}
    conn.commit()
    return {"status": "PROJECTED", "tokens": clean, "hits": hits, "truncated": False}


def _cartel_norm(value: str) -> str:
    folded = unicodedata.normalize("NFKD", str(value or ""))
    folded = "".join(char for char in folded if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", folded.casefold())


def _cartel_tsv(path: Path, timeout: int) -> list[dict]:
    """Read bounded OCR boxes. Missing OCR is an explicit sensor state."""
    try:
        completed = subprocess.run(
            ["tesseract", str(path), "stdout", "--psm", "11", "tsv"],
            check=False, capture_output=True, text=True,
            timeout=max(5, min(int(timeout), 180)),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [{"sensor_error": str(exc)[:240]}]
    if completed.returncode != 0:
        return [{"sensor_error": (completed.stderr or "tesseract_failed")[:240]}]
    rows = []
    for row in csv.DictReader(completed.stdout.splitlines(), delimiter="\t"):
        text = str(row.get("text") or "").strip()
        if not text:
            continue
        try:
            confidence = float(row.get("conf") or -1)
            x, y = int(row.get("left") or 0), int(row.get("top") or 0)
            width, height = int(row.get("width") or 0), int(row.get("height") or 0)
        except (TypeError, ValueError):
            continue
        rows.append({"text": text, "confidence": confidence, "x": x, "y": y,
                     "width": width, "height": height})
    return rows


def _cartel_date_anchors(boxes: list[dict]) -> list[dict]:
    anchors = []
    for box in boxes:
        text = str(box.get("text") or "").strip().rstrip(".,;:")
        if re.fullmatch(r"\d{1,2}[./-]\d{1,2}", text) and float(box.get("confidence") or 0) >= 35:
            candidate = dict(box, text=text)
            if not anchors or abs(candidate["y"] - anchors[-1]["y"]) > 80:
                anchors.append(candidate)
            elif candidate["confidence"] > anchors[-1]["confidence"]:
                anchors[-1] = candidate
    return anchors


def _cartel_catalog_candidates(text: str) -> tuple[list[dict], list[dict]]:
    try:
        from cultura.mak_curatoria.extraccion_db import (
            cargar_catalogo_productoras, cargar_catalogo_venues,
        )
    except ImportError:
        return [], []
    normalized = _cartel_norm(text)
    def matches(catalog):
        found = []
        for entry in catalog:
            variants = [entry.get("canonico", ""), *(entry.get("variantes") or [])]
            # Two-letter aliases such as ``TY`` are too weak for a visual
            # identity claim: they occur in ordinary words and make a
            # Techno Youth module look like a TY Circle module.  Keep the
            # alias in the catalog, but require a useful lexical anchor here.
            exact = [value for value in variants
                     if len(_cartel_norm(value)) >= 4 and _cartel_norm(value) in normalized]
            if exact:
                found.append({"canonical": entry.get("canonico"), "matched": exact[0]})
        return found
    producers = matches(cargar_catalogo_productoras())
    venues = matches(cargar_catalogo_venues())
    for item in ("Dame", "Techno Youth", "TY Circle", "Street Machine"):
        if _cartel_norm(item) in normalized:
            producers.append({"canonical": item, "matched": item, "catalog_source": "rd_catalog"})
    if "metronomo" in normalized:
        venues.append({"canonical": "Sala Metrónomo", "matched": "METRONOMO", "catalog_source": "rd_primary"})
    if "caupolican" in normalized:
        venues.append({"canonical": "Teatro Caupolicán", "matched": "CAUPOLICAN", "catalog_source": "web_candidate"})
    deduped = {}
    for venue in venues:
        deduped[_cartel_norm(venue.get("canonical"))] = venue
    producers_by_name = {}
    for producer in producers:
        producers_by_name[_cartel_norm(producer.get("canonical"))] = producer
    return list(producers_by_name.values()), list(deduped.values())


def _cartel_raw_venue_lines(text: str) -> list[str]:
    lines = []
    known = {"PRODUCE", "FECHA", "MUESTRA", "SUSTANCIA", "EXPERIMENTO", "CARTELERA"}
    for raw in str(text or "").splitlines():
        line = re.sub(r"[^\wÀ-ÿ ]+", " ", raw, flags=re.UNICODE).strip()
        compact = _cartel_norm(line)
        if (len(compact) < 5 or compact.upper() in known or
                "@" in raw or re.fullmatch(r"\d{1,2}[./-]\d{1,2}", line or "")):
            continue
        if any(token in compact for token in ("caupol", "metron", "riesc", "espacio", "sala", "teatro", "venue")):
            if line not in lines:
                lines.append(line)
    return lines


def _cartel_join_venue_words(lines: list[str]) -> list[str]:
    """Join OCR fragments such as ``ESPACIO`` + ``RIESCO`` into one candidate."""
    joined = []
    for index, line in enumerate(lines):
        if index + 1 < len(lines):
            pair = "%s %s" % (line, lines[index + 1])
            if _cartel_norm(pair) in {"espacioriesco", "salametronomo", "teatrocaupolican"}:
                joined.append(pair)
    return list(dict.fromkeys(joined + lines))


def _local_logo_assets(producer: str) -> list[dict]:
    """Inventory logo assets already in the repo without treating filenames as proof."""
    token = _cartel_norm(producer)
    if not token:
        return []
    logo_root = REPO_ROOT / "knowledge" / "logos"
    found = []
    for path in sorted(logo_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".svg", ".webp"}:
            continue
        stem = _cartel_norm(path.stem)
        if token in stem or stem in token:
            stat = path.stat()
            dimensions = None
            if Image is not None and path.suffix.lower() != ".svg":
                try:
                    with Image.open(path) as image:
                        dimensions = list(image.size)
                except (OSError, ValueError):
                    dimensions = None
            found.append({"path": str(path.relative_to(REPO_ROOT)),
                          "exists": True, "bytes": stat.st_size,
                          "sha256": sha256_stream(path), "dimensions": dimensions,
                          "match_basis": "normalized_logo_filename",
                          "inventory_status": "observed"})
    return found


def _rd_primary_catalog_snapshot() -> dict:
    """Read canonical RD SQLite as an external primary branch, never write it."""
    db_path = REPO_ROOT / "data" / "rd.db"
    if not db_path.is_file():
        return {"status": "UNAVAILABLE", "reason": "rd_db_missing"}
    try:
        import sqlite3 as _sqlite3
        connection = _sqlite3.connect("file:%s?mode=ro" % db_path, uri=True)
        connection.row_factory = _sqlite3.Row
        data = {
            "productoras": [dict(row) for row in connection.execute(
                "SELECT slug,nombre,aliases,confirmado,notas FROM productoras")],
            "venues": [dict(row) for row in connection.execute(
                "SELECT id,nombre,tipo,escala,capacidad,preset_reco,notas FROM venues")],
            "producer_venues": [dict(row) for row in connection.execute(
                "SELECT productora_slug,venue_nombre,venue_id,preferido,estado,notas FROM productora_venues")],
            "producer_events": [dict(row) for row in connection.execute(
                "SELECT productora_slug,nombre,fecha,venue,estado,fuente FROM productora_eventos")],
        }
        connection.close()
        return {"status": "OBSERVED", "db": str(db_path), "data": data}
    except Exception as exc:
        return {"status": "RETRY", "reason": str(exc)[:240]}


def _primary_catalog_matches(value: str, snapshot: dict, key: str = "venues") -> list[dict]:
    normalized = _cartel_norm(value)
    if not normalized or snapshot.get("status") != "OBSERVED":
        return []
    rows = snapshot.get("data", {}).get(key, [])
    result = []
    for row in rows:
        candidate = _cartel_norm(row.get("nombre") or row.get("venue_nombre") or "")
        # A fragment from OCR (``ESPACIO`` or ``RIESCO``) is retained as raw
        # evidence, but cannot become a primary-catalog match.  Only exact
        # normalized labels, or a long unambiguous label embedded in a line,
        # are eligible for this branch.
        if candidate and (candidate == normalized or
                          (len(normalized) >= 8 and normalized in candidate) or
                          (len(candidate) >= 8 and candidate in normalized)):
            result.append(row)
    return result


def _cartel_city_candidates(text: str) -> list[str]:
    """Extract city labels separately from venue labels."""
    normalized = _cartel_norm(text)
    return list(dict.fromkeys(canonical for alias, canonical in CITY_ALIASES.items()
                              if _cartel_norm(alias) in normalized))


def _cartel_historical_hits(conn: sqlite3.Connection, module_id: str,
                            asset_id: str, tokens: list[str], limit: int = 32) -> int:
    """Find prior RD evidence by path or existing perception text, never basename-only identity."""
    normalized_tokens = [_cartel_norm(token) for token in tokens if _cartel_norm(token)]
    if not normalized_tokens:
        return 0
    rows = conn.execute("SELECT asset_id,relative_path FROM assets WHERE asset_id<>?", (asset_id,)).fetchall()
    hits = 0
    for row in rows:
        path_norm = _cartel_norm(row["relative_path"])
        evidence = []
        if any(token in path_norm for token in normalized_tokens):
            evidence.append({"source": "relative_path", "value": row["relative_path"]})
        if len(evidence) < 1:
            observations = conn.execute(
                "SELECT value_json FROM observations WHERE asset_id=? AND observer='percepcion'",
                (row["asset_id"],)).fetchall()
            for observation in observations:
                value_norm = _cartel_norm(observation["value_json"])
                if any(token in value_norm for token in normalized_tokens):
                    evidence.append({"source": "prior_perception", "asset_id": row["asset_id"]})
                    break
        if evidence:
            store_relation(conn, module_id, "historical_asset_candidate",
                           "asset:" + str(row["asset_id"]),
                           {"tokens": tokens, "matches": evidence,
                            "policy": "history_candidate_not_event_identity"},
                           None, "candidate")
            hits += 1
            if hits >= limit:
                break
    return hits


def project_composite_cartel(conn: sqlite3.Connection, root: Path, out: Path,
                             asset_id: str, timeout: int = 90,
                             max_modules: int = 12) -> dict:
    """Split a composite flyer into repeated modules and project RD candidates.

    The detector is layout-agnostic at the semantic layer: repeated date boxes
    provide anchors, while all extracted producer/venue/logo relations remain
    candidates. It is a collection/index stage, never a flyer generator.
    """
    _ensure_composite_schema(conn)
    row = conn.execute("SELECT relative_path,media_kind FROM assets WHERE asset_id=?", (asset_id,)).fetchone()
    if row is None:
        return {"status": "ASSET_NOT_FOUND", "modules": 0, "promotion": "none"}
    source = root / row["relative_path"]
    if row["media_kind"] != "image" or not source.is_file():
        return {"status": "NOT_AN_IMAGE", "modules": 0, "promotion": "none"}
    if Image is None:
        return {"status": "DEFERRED_TOOL", "reason": "pillow_unavailable", "modules": 0, "promotion": "none"}
    try:
        image = Image.open(source)
        width, height = image.size
    except (OSError, ValueError) as exc:
        return {"status": "RETRY", "reason": str(exc)[:240], "modules": 0, "promotion": "none"}
    boxes = _cartel_tsv(source, timeout)
    if boxes and boxes[0].get("sensor_error"):
        return {"status": "DEFERRED_TOOL", "reason": boxes[0]["sensor_error"], "modules": 0, "promotion": "none"}
    anchors = _cartel_date_anchors(boxes)[:max(1, int(max_modules))]
    if len(anchors) < 2:
        return {"status": "NOT_COMPOSITE", "date_anchors": len(anchors), "modules": 0, "promotion": "none"}
    modules_dir = Path(out) / "cartel_modules"
    modules_dir.mkdir(parents=True, exist_ok=True)
    primary_catalog = _rd_primary_catalog_snapshot()
    result = {"status": "PROJECTED", "date_anchors": len(anchors), "modules": 0,
              "promotion": "none", "source": str(source), "sensor": "tesseract_tsv",
              "primary_catalog": {"status": primary_catalog.get("status"),
                                  "db": primary_catalog.get("db")}}
    for index, anchor in enumerate(anchors, 1):
        y0 = max(0, int(anchor["y"]) - 50)
        next_y = int(anchors[index]["y"]) if index < len(anchors) else int(anchor["y"] + (anchor["y"] - anchors[index - 2]["y"]))
        y1 = min(height, max(y0 + 1, next_y - 35))
        crop = image.crop((0, y0, width, y1))
        crop_path = modules_dir / ("module-%02d.png" % index)
        crop.save(crop_path)
        module_id = hashlib.sha256((asset_id + "\0module\0" + str(index)).encode("utf-8")).hexdigest()
        module_boxes = _cartel_tsv(crop_path, timeout)
        module_text = "\n".join(box["text"] for box in module_boxes if box.get("text"))
        producers, venues = _cartel_catalog_candidates(module_text)
        raw_venues = _cartel_join_venue_words(_cartel_raw_venue_lines(module_text))
        evidence = {"anchor": anchor, "bounds": [0, y0, width, y1],
                    "sensor": "tesseract_tsv", "crop_path": str(crop_path),
                    "policy": "module_candidates_not_claims"}
        conn.execute(
            """INSERT INTO cartel_modules(module_id,asset_id,module_index,x0,y0,x1,y1,crop_path,ocr_text,evidence_json,status,observed_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(asset_id,module_index) DO UPDATE SET
                 x0=excluded.x0,y0=excluded.y0,x1=excluded.x1,y1=excluded.y1,
                 crop_path=excluded.crop_path,ocr_text=excluded.ocr_text,
                 evidence_json=excluded.evidence_json,status=excluded.status,observed_at=excluded.observed_at""",
            (module_id, asset_id, index, 0, y0, width, y1, str(crop_path), module_text,
             json.dumps(evidence, ensure_ascii=False), "observed", now()),
        )
        # Keep the parent-child edge explicit: a module is derived evidence
        # from this asset, never a replacement for it.
        store_relation(conn, module_id, "cartel_module_of", "asset:" + asset_id,
                       evidence, 1.0, "observed")
        store_cartel_module_candidate(conn, module_id, "date", str(anchor["text"]), evidence, 1.0, "observed")
        for producer in producers:
            canonical = str(producer.get("canonical") or "")
            producer_evidence = dict(evidence, matched=producer.get("matched"), canonical=canonical)
            store_cartel_module_candidate(conn, module_id, "producer", canonical, producer_evidence, 1.0, "candidate")
            store_relation(conn, module_id, "advertises_producer_candidate", "catalog:producer:" + _cartel_norm(canonical), producer_evidence, 1.0, "candidate")
            record = canonical_producer(canonical)
            logos = (record or {}).get("record", {}).get("logos") or []
            if logos:
                for logo in logos:
                    logo_evidence = dict(producer_evidence, logo=logo)
                    logo_status = "catalogued" if logo.get("estado") == "encontrado" else "catalog_missing_asset"
                    store_cartel_module_candidate(conn, module_id, "logo_catalog", str(logo.get("id") or canonical), logo_evidence, 1.0, logo_status)
                    store_relation(conn, module_id, "has_catalogued_logo_candidate", "catalog:logo:" + str(logo.get("id") or canonical), logo_evidence, 1.0, logo_status)
            else:
                store_cartel_module_candidate(conn, module_id, "logo_catalog", canonical, dict(producer_evidence, reason="no_logo_record"), None, "unresolved")
            for local_logo in _local_logo_assets(canonical):
                local_evidence = dict(producer_evidence, local_logo=local_logo,
                                       policy="local_asset_presence_not_logo_identity")
                store_cartel_module_candidate(conn, module_id, "logo_local_asset",
                                              local_logo["path"], local_evidence, None,
                                              "candidate")
                store_relation(conn, module_id, "local_logo_asset_candidate",
                               "file:" + local_logo["path"], local_evidence, None,
                               "candidate")
            _cartel_historical_hits(conn, module_id, asset_id, [canonical, producer.get("matched", "")])
        for venue in venues:
            canonical = str(venue.get("canonical") or "")
            venue_evidence = dict(evidence, matched=venue.get("matched"), canonical=canonical)
            store_cartel_module_candidate(conn, module_id, "venue", canonical, venue_evidence, 1.0, "candidate")
            store_relation(conn, module_id, "has_candidate_venue", "catalog:venue:" + _cartel_norm(canonical), venue_evidence, 1.0, "candidate")
        for raw_venue in raw_venues:
            primary_matches = _primary_catalog_matches(raw_venue, primary_catalog)
            raw_status = "candidate" if primary_matches else "unresolved"
            raw_evidence = dict(evidence, raw=raw_venue,
                                primary_catalog_matches=primary_matches,
                                location_kind="venue_not_city")
            store_cartel_module_candidate(conn, module_id, "venue_raw", raw_venue, raw_evidence, 1.0 if primary_matches else None, raw_status)
            for match in primary_matches:
                store_relation(conn, module_id, "primary_catalog_venue_candidate",
                               "rd:venue:" + str(match.get("id") or match.get("nombre")),
                               raw_evidence, 1.0, "candidate")
        for city in _cartel_city_candidates(module_text):
            city_evidence = dict(evidence, city=city, location_kind="city_not_venue")
            store_cartel_module_candidate(conn, module_id, "city", city, city_evidence, 1.0, "candidate")
            store_relation(conn, module_id, "has_candidate_city", "catalog:city:" + _cartel_norm(city),
                           city_evidence, 1.0, "candidate")
        if not raw_venues and not venues:
            store_cartel_module_candidate(conn, module_id, "venue", "unknown", dict(evidence, reason="no_venue_signal"), None, "unresolved")
        # Preserve a bounded visual surface for later logo matching. This is
        # an evidence crop, not a generated design asset and never overwrites
        # anything under the source root.
        logo_y0 = min(y1 - 1, y0 + max(1, int((y1 - y0) * 0.12)))
        logo_y1 = max(logo_y0 + 1, y1 - max(1, int((y1 - y0) * 0.08)))
        logo_x0, logo_x1 = max(0, int(width * 0.08)), max(1, int(width * 0.50))
        logo_crop_path = modules_dir / ("logo-%02d.png" % index)
        image.crop((logo_x0, logo_y0, min(width, logo_x1), logo_y1)).save(logo_crop_path)
        logo_evidence = dict(evidence, region="left_visual_panel", bounds=[logo_x0, logo_y0, logo_x1, logo_y1],
                             policy="derived_visual_evidence_only")
        store_cartel_module_candidate(conn, module_id, "visible_logo_surface", str(logo_crop_path), logo_evidence, None, "candidate")
        result["modules"] += 1
    conn.commit()
    result["module_ids"] = [row["module_id"] for row in conn.execute(
        "SELECT module_id FROM cartel_modules WHERE asset_id=? ORDER BY module_index", (asset_id,)).fetchall()]
    return result


def project_folder_brand_queue(conn: sqlite3.Connection, root: Path,
                               out: Path, brands: list[str], limit: int = 200) -> dict:
    """Build a bounded brand/event research queue from the whole folder.

    This is intentionally useful when a future cartel names a brand but not
    its producer (KLANG is the motivating case): historical paths, perception
    observations, logo assets, and existing RD primary rows are separate
    evidence branches. No provider call or identity promotion occurs here.
    """
    _ensure_folder_research_schema(conn)
    queue = []
    primary = _rd_primary_catalog_snapshot()
    for brand in brands:
        label = str(brand or "").strip()
        token = _cartel_norm(label)
        if not token:
            continue
        local_assets = _local_logo_assets(label)
        anchor_row = conn.execute(
            "SELECT asset_id FROM assets WHERE lower(relative_path) LIKE ? ORDER BY relative_path LIMIT 1",
            ("%" + token + "%",),
        ).fetchone()
        history = (scan_folder_identity_history(conn, root, anchor_row["asset_id"], [label], limit=limit)
                   if anchor_row else {"status": "PROJECTED", "tokens": [token], "hits": 0, "truncated": False})
        producer_rows = _primary_catalog_matches(label, primary, "productoras")
        events = [row for row in primary.get("data", {}).get("producer_events", [])
                  if token in _cartel_norm(row.get("productora_slug")) or token in _cartel_norm(row.get("nombre"))]
        queue.append({"brand": label, "token": token,
                      "local_logo_assets": local_assets,
                      "primary_producer_rows": producer_rows,
                      "primary_event_rows": events,
                      "folder_history": history,
                      "status": "candidate_research" if (local_assets or history.get("hits") or producer_rows or events)
                      else "unresolved_not_negative",
                      "promotion": "none"})
    path = Path(out) / "brand_research_queue.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": "mak-rd-brand-research-v1",
                                "source_root": str(root), "brands": queue,
                                "promotion": "none"}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    return {"status": "PROJECTED", "brands": len(queue), "path": str(path), "promotion": "none"}


def project_external_root(conn: sqlite3.Connection, root: Path, out: Path,
                          source_role: str = "external_evidence",
                          full_hash_mb: int = 64, limit: int = 200) -> dict:
    """Index a mounted secondary root into the same derived organism.

    Google Drive/OneDrive are treated as evidence roots, not as trusted
    canonical storage. The root is registered and its files are inventoried
    under the existing ``assets`` table; no source copy, rename, upload or
    provider call happens here. ``limit`` bounds the optional visual stage,
    while inventory remains deterministic and resumable.
    """
    root, out = Path(root).resolve(), Path(out).resolve()
    if not root.is_dir():
        return {"status": "ROOT_UNAVAILABLE", "root": str(root), "promotion": "none"}
    if is_within(out, root):
        return {"status": "SOURCE_SURFACE_RISK", "root": str(root), "promotion": "none"}
    conn.execute("CREATE TABLE IF NOT EXISTS source_roots (source_key TEXT PRIMARY KEY, root_path TEXT NOT NULL, source_role TEXT NOT NULL, read_policy TEXT NOT NULL, observed_at TEXT NOT NULL)")
    root_key = register_source_root(conn, root, source_role=source_role,
                                    read_policy="mounted_read_only_expected")
    measured = inventory(conn, root, int(full_hash_mb) * 1024 * 1024,
                         source_role=source_role,
                         read_policy="mounted_read_only_expected")
    conn.commit()
    return {"status": "PROJECTED", "root": str(root), "source_key": root_key,
            "source_role": source_role, "inventory": measured,
            "visual_stage": "deferred", "promotion": "none"}


STRUCTURE_LINEAGE_RELATIONS = {
    "has_document_id", "has_original_document_id", "has_derived_document_id",
}


def project_structure_evidence(conn: sqlite3.Connection, asset_id: str,
                               structure: dict | None) -> dict:
    """Project one deterministic structure manifest into the derived graph.

    This is deliberately a projection, not a triangulator.  Exact XMP keys
    can create a neutral cross-asset lineage edge, but the function never
    assigns an artist, client, venue, producer, or authorship.  The caller
    owns the transaction so a worker can atomically persist the manifest and
    its edges with the rest of the family evidence.
    """
    if not isinstance(structure, dict):
        return {"status": "NO_MANIFEST", "edges_written": 0,
                "lineage_edges_written": 0, "promotion": "none"}
    asset_id = str(asset_id or "").strip()
    if not asset_id:
        return {"status": "NO_ASSET", "edges_written": 0,
                "lineage_edges_written": 0, "promotion": "none"}
    manifest_status = str(structure.get("status") or "unknown")
    store_observation(conn, asset_id, "structure", "manifest", structure,
                       "observed" if manifest_status == "OBSERVED" else manifest_status.casefold())
    edges = structure.get("evidence_edges")
    if not isinstance(edges, list):
        edges = []
    written = 0
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        relation = str(edge.get("relation") or "").strip()
        right_id = str(edge.get("right_id") or "").strip()
        if not relation or not right_id:
            continue
        evidence = edge.get("evidence") if isinstance(edge.get("evidence"), dict) else {}
        evidence = dict(evidence, source_observer=structure.get("tool"),
                        structure_status=manifest_status)
        store_relation(conn, asset_id, relation, right_id, evidence,
                       None, str(edge.get("status") or "candidate"))
        written += 1

    # Reconcile only exact, repeated lineage keys. This is an evidence edge
    # for the organism's judge, not a claim that the assets share an owner.
    grouped: defaultdict[str, set[str]] = defaultdict(set)
    for row in conn.execute(
            "SELECT left_id,right_id,relation FROM relations "
            "WHERE relation IN (?,?,?) AND status IN ('candidate','observed')",
            tuple(sorted(STRUCTURE_LINEAGE_RELATIONS))):
        grouped[str(row["right_id"])].add(str(row["left_id"]))
    lineage_written = 0
    conflict_written = 0
    for key, members in grouped.items():
        members = sorted(member for member in members if member)
        # A pathological shared key must not turn the projection into an
        # O(n^2) fan-out. The full membership remains visible in evidence.
        if len(members) < 2:
            continue
        for left_id, right_id in combinations(members[:128], 2):
            evidence = {
                "shared_key": key,
                "members": members[:128],
                "relation_basis": "exact_embedded_lineage_key",
                "policy": "lineage_candidate_not_identity",
            }
            store_relation(conn, left_id, "same_embedded_lineage_key", right_id,
                           evidence, None, "candidate")
            lineage_written += 1
        contexts = {}
        for member in members[:128]:
            context_rows = conn.execute(
                "SELECT relation,right_id FROM relations WHERE left_id=? "
                "AND relation IN ('embedded_date_candidate','creator_tool_observed')",
                (member,)).fetchall()
            contexts[member] = sorted({str(row["right_id"]) for row in context_rows})
        distinct_context = sorted({value for values in contexts.values() for value in values})
        if len(distinct_context) > 1:
            for left_id, right_id in combinations(members[:128], 2):
                left_context = contexts.get(left_id, [])
                right_context = contexts.get(right_id, [])
                if left_context == right_context:
                    continue
                store_relation(
                    conn, left_id, "lineage_context_divergence_candidate", right_id,
                    {"shared_key": key, "left_context": left_context,
                     "right_context": right_context,
                     "policy": "divergence_candidate_requires_organism_judge"},
                    None, "candidate")
                conflict_written += 1
    return {
        "status": "PROJECTED",
        "manifest_status": manifest_status,
        "edges_written": written,
        "lineage_edges_written": lineage_written,
        "conflict_edges_written": conflict_written,
        "lineage_keys_seen": sum(len(members) >= 2 for members in grouped.values()),
        "promotion": "none",
    }


def project_visual_surface_evidence(conn: sqlite3.Connection, asset_id: str,
                                    source_id: str, surface_path: str | Path,
                                    limit: int = 16) -> dict:
    """Project existing visual-index neighbors without running an encoder.

    The visual index is an evidence surface, not an identity graph. Eligible
    and abstained neighbors are both retained so a later organism judge can
    see score, margin, model version, and the reason for abstention. A missing
    source mapping is explicitly not a negative visual conclusion.
    """
    asset_id = str(asset_id or "").strip()
    source_id = str(source_id or "").strip()
    if not asset_id or not source_id:
        return {"status": "NO_SOURCE_MAPPING", "neighbors_written": 0,
                "promotion": "none"}
    try:
        from cultura.mak_plataforma.visual_index import read_surface
    except ImportError as exc:
        return {"status": "DEFERRED_TOOL", "reason": str(exc)[:240],
                "neighbors_written": 0, "promotion": "none"}
    surface = read_surface(Path(surface_path).expanduser())
    if not surface.get("available"):
        return {"status": "DEFERRED_SURFACE", "reason": surface.get("reason", "unavailable"),
                "neighbors_written": 0, "promotion": "none"}
    target = None
    for row in (surface.get("items") or {}).values():
        if not isinstance(row, dict):
            continue
        ids = [row.get("source_id"), *(row.get("source_ids") or [])]
        if source_id in {str(value) for value in ids if value}:
            target = row
            break
    if target is None:
        return {"status": "NO_SOURCE_MAPPING", "source_id": source_id,
                "neighbors_written": 0, "promotion": "none"}
    neighbors = list(target.get("neighbors") or [])[:max(1, int(limit))]
    store_observation(conn, asset_id, "visual_index", "neighbors", {
        "source_id": source_id,
        "unit_id": target.get("unit_id"),
        "model": surface.get("model"),
        "model_version": surface.get("model_version"),
        "thresholds": surface.get("thresholds"),
        "neighbor_count": len(neighbors),
    })
    written = 0
    eligible = 0
    abstained = 0
    for neighbor in neighbors:
        if not isinstance(neighbor, dict):
            continue
        item_id = str(neighbor.get("item_id") or neighbor.get("unit_id") or "").strip()
        if not item_id:
            continue
        accepted = bool(neighbor.get("eligible"))
        relation = "visual_similarity_candidate" if accepted else "visual_similarity_abstained"
        evidence = dict(neighbor)
        evidence.update({
            "source_id": source_id,
            "surface": str(Path(surface_path).expanduser()),
            "policy": "visual_similarity_not_identity",
        })
        store_relation(conn, asset_id, relation, "visual:%s" % item_id,
                       evidence, None, "candidate" if accepted else "abstain")
        written += 1
        eligible += int(accepted)
        abstained += int(not accepted)
    return {
        "status": "PROJECTED",
        "source_id": source_id,
        "neighbors_written": written,
        "eligible": eligible,
        "abstained": abstained,
        "promotion": "none",
    }


def project_sequence_coverage(conn: sqlite3.Connection, asset_id: str,
                              family_id: str, family_stats: dict | None,
                              structure: dict | None) -> dict:
    """Compare a representative video's measured frames with its family.

    This only tests whether a video could cover a numbered-frame family. It
    does not assert that the images came from that video, that both are one
    work, or that either has an owner. Missing frame metadata remains
    `UNRESOLVED` so the organism can choose a bounded fallback.
    """
    stats = family_stats if isinstance(family_stats, dict) else {}
    expected = int(stats.get("frame_count") or 0)
    video_count = int(stats.get("video_count") or 0)
    if expected <= 0 or video_count <= 0:
        return {"status": "NOT_APPLICABLE", "expected_frames": expected,
                "promotion": "none"}
    if not isinstance(structure, dict) or structure.get("status") != "OBSERVED":
        return {"status": "UNRESOLVED", "reason": "video_structure_not_observed",
                "expected_frames": expected, "promotion": "none"}
    metadata = structure.get("metadata") if isinstance(structure.get("metadata"), dict) else {}
    streams = metadata.get("streams") if isinstance(metadata.get("streams"), list) else []
    measured = []
    fps_values = []
    durations = []
    for stream in streams:
        if not isinstance(stream, dict):
            continue
        raw_frames = stream.get("nb_frames")
        try:
            if raw_frames not in (None, "", "N/A"):
                measured.append(int(raw_frames))
        except (TypeError, ValueError):
            pass
        rate = str(stream.get("r_frame_rate") or "")
        try:
            if "/" in rate:
                num, den = rate.split("/", 1)
                fps_values.append(float(num) / float(den))
            elif rate:
                fps_values.append(float(rate))
        except (TypeError, ValueError, ZeroDivisionError):
            pass
        try:
            if stream.get("duration") not in (None, "", "N/A"):
                durations.append(float(stream["duration"]))
        except (TypeError, ValueError):
            pass
    format_data = metadata.get("format") if isinstance(metadata.get("format"), dict) else {}
    try:
        if format_data.get("duration") not in (None, "", "N/A"):
            durations.append(float(format_data["duration"]))
    except (TypeError, ValueError):
        pass
    if not measured and durations and fps_values:
        measured.append(round(max(durations) * max(fps_values)))
    if not measured:
        return {"status": "UNRESOLVED", "reason": "video_frame_count_missing",
                "expected_frames": expected, "promotion": "none"}
    observed = max(measured)
    relation = ("video_covers_sequence_candidate" if observed >= expected else
                "video_sequence_coverage_insufficient")
    evidence = {
        "family_id": str(family_id or ""),
        "expected_frame_count": expected,
        "observed_video_frames": observed,
        "all_measured_frame_counts": measured,
        "policy": "coverage_candidate_not_same_work_proof",
    }
    store_relation(conn, asset_id, relation, "family:%s" % str(family_id or ""),
                   evidence, None, "candidate")
    store_observation(conn, asset_id, "sequence_coverage", "comparison", evidence)
    return {"status": "PROJECTED", "relation": relation,
            "expected_frames": expected, "observed_frames": observed,
            "promotion": "none"}


def build_evidence_gate(conn: sqlite3.Connection, asset_id: str) -> dict:
    """Route evidence to the organism without resolving an identity.

    `ROUTE_TO_JUDGE` means that independent evidence branches are available for
    comparison; it is not approval. `ABSTAIN` preserves contradictions or an
    incomplete identity quorum, while `DEFERRED` means the organism needs a
    bounded sensor before asking a model or researcher. The gate never writes
    a public claim and never treats a model description as a source.
    """
    asset_id = str(asset_id or "").strip()
    if not asset_id:
        return {"schema": "mak-organism-evidence-gate-v1", "route": "DEFERRED",
                "reason": "asset_missing", "promotion": "none"}
    observations = []
    try:
        observations = [dict(row) for row in conn.execute(
            "SELECT observer,field,status,value_json FROM observations WHERE asset_id=?",
            (asset_id,)).fetchall()]
    except sqlite3.OperationalError:
        observations = []
    relations = []
    try:
        relations = [dict(row) for row in conn.execute(
            "SELECT relation,status,left_id,right_id,evidence_json FROM relations "
            "WHERE left_id=? OR (right_id=? AND relation IN "
            "('same_embedded_lineage_key','lineage_context_divergence_candidate'))",
            (asset_id, asset_id)).fetchall()]
    except sqlite3.OperationalError:
        relations = []
    relation_names = {str(row.get("relation") or "") for row in relations}
    observed_observers = {
        str(row.get("observer") or "") for row in observations
        if str(row.get("status") or "").casefold() in {"observed", "done", "projected"}
    }
    branches = {}
    branches["structure"] = (
        "structure" in observed_observers or
        bool(relation_names & {"contains_scene", "references_external_asset",
                               "has_document_id", "has_original_document_id",
                               "archive_contains", "show_control_context"})
    )
    branches["visual"] = any(
        str(row.get("relation") or "") == "visual_similarity_candidate" and
        str(row.get("status") or "") == "candidate"
        for row in relations
    )
    branches["sequence"] = any(
        str(row.get("relation") or "") == "video_covers_sequence_candidate" and
        str(row.get("status") or "") == "candidate"
        for row in relations
    )
    branches["lineage"] = "same_embedded_lineage_key" in relation_names
    branches["temporal"] = any(
        str(row.get("relation") or "") == "embedded_date_candidate"
        for row in relations
    )
    coverage = {"status": "unmeasured", "match_type": ""}
    try:
        row = conn.execute(
            "SELECT status,match_type FROM asset_coverage WHERE asset_id=? "
            "ORDER BY rowid DESC LIMIT 1", (asset_id,)).fetchone()
        if row is not None:
            coverage = {"status": str(row[0] or ""),
                        "match_type": str(row[1] or "")}
    except sqlite3.OperationalError:
        pass
    branches["coverage"] = coverage["status"] == "strong"

    conflicts = []
    abstentions = []
    for row in relations:
        relation = str(row.get("relation") or "")
        status = str(row.get("status") or "")
        if "divergence" in relation or "insufficient" in relation:
            conflicts.append({"relation": relation, "right_id": row.get("right_id")})
        if status in {"abstain", "retry"} or "abstained" in relation:
            abstentions.append({"relation": relation, "right_id": row.get("right_id"),
                                "status": status})
    identity_candidates = []
    try:
        identity_candidates = [dict(row) for row in conn.execute(
            "SELECT kind,value,status,evidence_json FROM candidates WHERE asset_id=?",
            (asset_id,)).fetchall()
        ]
    except sqlite3.OperationalError:
        pass
    identity_kinds = {str(row.get("kind") or "") for row in identity_candidates
                      if str(row.get("status") or "") in {"candidate", "catalogued"}}
    active_branches = sorted(name for name, active in branches.items() if active)
    if conflicts:
        route, reason = "ABSTAIN", "evidence_conflict_requires_judge"
    elif identity_candidates:
        # A candidate from one pipeline is not a second independent source.
        route, reason = "ABSTAIN", "identity_quorum_not_proven"
    elif len(active_branches) >= 2:
        route, reason = "ROUTE_TO_JUDGE", "independent_evidence_branches_available"
    else:
        route, reason = "DEFERRED", "insufficient_independent_evidence_branches"
    result = {
        "schema": "mak-organism-evidence-gate-v1",
        "route": route,
        "reason": reason,
        "branches": branches,
        "active_branches": active_branches,
        "coverage": coverage,
        "identity_candidate_count": len(identity_candidates),
        "identity_candidate_kinds": sorted(identity_kinds),
        "conflicts": conflicts[:100],
        "abstentions": abstentions[:100],
        "minimum_independent_branches": 2,
        "identity_resolution": "candidate_only_until_two_independent_sources_agree",
        "promotion": "none",
    }
    store_observation(conn, asset_id, "organism_gate", "routing", result,
                      "observed")
    return result


def canonical_producer(name: str) -> dict | None:
    """Return a local RD catalog record only on an exact normalized identity."""
    normalized = "".join(c for c in name.casefold() if c.isalnum())
    if not normalized:
        return None
    for path in (REPO_ROOT / "data" / "productoras").glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        names = [record.get("name", "")] + list(record.get("aliases") or [])
        if any("".join(c for c in str(value).casefold() if c.isalnum()) == normalized
               for value in names):
            return {"record": record, "path": str(path.relative_to(REPO_ROOT))}
    return None


def split_venue_and_city(value: str) -> tuple[str, str]:
    """Keep geographic city distinct from a venue name in a raw flyer field."""
    pieces = [piece.strip() for piece in re.split(r"[,|]", value or "") if piece.strip()]
    if not pieces:
        return "", ""
    candidate_city = "".join(c for c in pieces[-1].casefold() if c.isalnum() or c.isspace()).strip()
    city = CITY_ALIASES.get(candidate_city, "")
    return ", ".join(pieces[:-1]) if city else ", ".join(pieces), city


def producer_venue_candidate(producer: str, raw_venue: str) -> dict | None:
    """Resolve a venue only through the matched producer's local catalog.

    A partial OCR string such as ``RIESCO`` can name ``Espacio Riesco`` when
    that relationship is already catalogued for the producer.  The result is
    deliberately still a *candidate*; it does not confirm this particular
    event occurred there.
    """
    found = canonical_producer(producer)
    raw_norm = "".join(c for c in raw_venue.casefold() if c.isalnum())
    if not found or not raw_norm:
        return None
    for venue in found["record"].get("venues") or []:
        name = str(venue.get("nombre") or "")
        name_norm = "".join(c for c in name.casefold() if c.isalnum())
        if raw_norm == name_norm or (len(raw_norm) >= 5 and raw_norm in name_norm):
            return {"name": name, "venue_id": venue.get("venue_id"),
                    "catalog": found["path"], "catalog_status": venue.get("estado"),
                    "notes": venue.get("notas")}
    return None


def project_local_logo(conn: sqlite3.Connection, asset_id: str, producer: str) -> bool:
    """Resolve an already-catalogued logo; never searches or creates one."""
    found = canonical_producer(producer)
    if not found:
        return False
    record, catalog_path = found["record"], found["path"]
    store_observation(conn, asset_id, "rd_catalog", "producer", {
        "name": record.get("name"), "catalog": catalog_path,
    })
    for logo in record.get("logos") or []:
        if logo.get("estado") != "encontrado":
            continue
        vector = str(logo.get("archivo") or "")
        raster = str(logo.get("raster") or "")
        # The catalog can retain a source even if a historical local raster is
        # missing.  It is a reference, not proof that the asset is usable.
        evidence = {
            "catalog": catalog_path, "logo_id": logo.get("id"),
            "vector": vector, "vector_exists": bool(vector and (REPO_ROOT / vector).is_file()),
            "raster": raster, "raster_exists": bool(raster and (REPO_ROOT / raster).is_file()),
            "source": logo.get("fuente"), "obtained": logo.get("obtenido"),
        }
        value = str(logo.get("id") or vector or raster)
        if value:
            store_candidate(conn, asset_id, "logo_reference", value, evidence, 1.0, "catalogued")
            store_relation(conn, asset_id, "has_catalogued_logo",
                           "catalog:logo:" + value, evidence, 1.0, "catalogued")
            return True
    return False


def schedule_asset_stages(conn: sqlite3.Connection, asset_id: str, kind: str,
                          hash_state: str) -> None:
    if hash_state != "full":
        ensure_job(conn, asset_id, "full_hash")
    if kind == "structural":
        ensure_job(conn, asset_id, "extract_structure")
        ensure_job(conn, asset_id, "render_preview")
    elif kind in {"image", "video", "pdf"}:
        ensure_job(conn, asset_id, "perception")


def reconcile_perception_jobs(conn: sqlite3.Connection) -> None:
    """Recover a job checkpoint from its already durable observation."""
    rows = conn.execute(
        """SELECT asset_id, value_json FROM observations
           WHERE observer='percepcion' AND field='ficha'"""
    ).fetchall()
    for row in rows:
        try:
            record = json.loads(row["value_json"])
        except (TypeError, json.JSONDecodeError):
            continue
        set_job(conn, row["asset_id"], "perception",
                "retry" if record.get("error") else "done",
                record.get("error"), False)


def inventory(conn: sqlite3.Connection, root: Path, full_hash_limit: int,
              source_role: str = "indexed_source",
              read_policy: str = "read_only_observation") -> dict:
    """Read every regular file deterministically.  Never opens source writable."""
    root_key = source_key(root)
    register_source_root(conn, root, source_role=source_role,
                         read_policy=read_policy)
    counts = Counter()
    for directory, directories, names in os.walk(root, followlinks=False):
        directories.sort()
        for name in sorted(names):
            path = Path(directory) / name
            try:
                if not path.is_file() or path.is_symlink():
                    continue
                stat = path.stat()
            except OSError as exc:
                counts["unreadable"] += 1
                continue
            relative = path.relative_to(root).as_posix()
            identity = asset_key(root_key, relative)
            kind = media_kind(path)
            previous = conn.execute(
                "SELECT bytes, mtime_ns, full_sha256, hash_state FROM assets WHERE asset_id=?",
                (identity,),
            ).fetchone()
            same = previous and previous["bytes"] == stat.st_size and previous["mtime_ns"] == stat.st_mtime_ns
            sample = None
            full = previous["full_sha256"] if same else None
            state = previous["hash_state"] if same else "pending"
            error = None
            try:
                sample = sample_fingerprint(path, stat.st_size)
                if not full and stat.st_size <= full_hash_limit:
                    full = sha256_stream(path)
                    state = "full"
                elif not full:
                    state = "pending"
            except OSError as exc:
                state, error = "failed", str(exc)[:500]
                counts["hash_failed"] += 1
            conn.execute(
                """INSERT INTO assets(asset_id, source_key, relative_path, extension, media_kind,
                   bytes, mtime_ns, sample_sha256, full_sha256, hash_state, hash_error, indexed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(asset_id) DO UPDATE SET extension=excluded.extension,
                     media_kind=excluded.media_kind, bytes=excluded.bytes, mtime_ns=excluded.mtime_ns,
                     sample_sha256=excluded.sample_sha256, full_sha256=excluded.full_sha256,
                     hash_state=excluded.hash_state, hash_error=excluded.hash_error,
                     indexed_at=excluded.indexed_at""",
                (identity, root_key, relative, path.suffix.lower(), kind, stat.st_size,
                 stat.st_mtime_ns, sample, full, state, error, now()),
            )
            schedule_asset_stages(conn, identity, kind, state)
            if kind == "image":
                metadata = raster_metadata(path)
                store_observation(conn, identity, "raster_metadata", "metadata",
                                  metadata, "failed" if metadata.get("status") == "RETRY" else "observed")
            counts["assets"] += 1
            counts["bytes"] += stat.st_size
            counts["kind_" + kind] += 1
            counts["hash_" + state] += 1
    # Exact equality only: partial fingerprints are deliberately excluded.
    duplicates = conn.execute(
        "SELECT full_sha256 FROM assets WHERE full_sha256 IS NOT NULL GROUP BY full_sha256 HAVING COUNT(*) > 1"
    ).fetchall()
    for row in duplicates:
        members = conn.execute("SELECT asset_id FROM assets WHERE full_sha256=? ORDER BY asset_id",
                               (row["full_sha256"],)).fetchall()
        head = members[0]["asset_id"]
        for member in members[1:]:
            relation_id = hashlib.sha256((head + "\0exact_duplicate\0" + member["asset_id"]).encode("ascii")).hexdigest()
            conn.execute(
                """INSERT OR REPLACE INTO relations(relation_id,left_id,relation,right_id,evidence_json,confidence,status)
                   VALUES(?,?,?,?,?,?,?)""",
                (relation_id, head, "exact_duplicate", member["asset_id"],
                 json.dumps({"full_sha256": row["full_sha256"]}), 1.0, "measured"),
            )
            counts["exact_duplicate_relations"] += 1
    return dict(counts)


def selected_for_perception(conn: sqlite3.Connection, root: Path, limit: int,
                            asset_ids: list[str] | None = None) -> list[dict]:
    """Stable triage: supports every visual type, path hints only set priority."""
    params: list[str | int] = []
    asset_filter = ""
    if asset_ids:
        clean_ids = [str(value).strip() for value in asset_ids if str(value).strip()]
        if clean_ids:
            asset_filter = " AND asset_id IN (%s)" % ",".join("?" for _ in clean_ids)
            params.extend(clean_ids)
    rows = conn.execute(
        """SELECT asset_id, relative_path, media_kind FROM assets
           WHERE media_kind IN ('image','video','pdf')
           AND NOT EXISTS (
             SELECT 1 FROM jobs AS completed
             WHERE completed.asset_id=assets.asset_id
               AND completed.stage='perception' AND completed.status='done'
           )""" + asset_filter +
        " ORDER BY relative_path", params,
    ).fetchall()
    def priority(row):
        path = row["relative_path"].casefold()
        hint = 0 if any(word in path for word in ("flyer", "entrega", "evento", "afiche")) else 1
        return (hint, hashlib.sha256(row["relative_path"].encode("utf-8")).hexdigest())
    return [dict(row) for row in sorted(rows, key=priority)[:max(0, limit)]]


def run_perception(conn: sqlite3.Connection, root: Path, out: Path, limit: int,
                   timeout: int, asset_ids: list[str] | None = None,
                   source_name: str = "rd") -> dict:
    if limit <= 0:
        return {"requested": 0, "processed": 0, "failed": 0, "skipped": 0}
    try:
        from percepcion import construir_ficha, escribir_ficha
    except ImportError:
        from cultura.mak_curatoria.percepcion import construir_ficha, escribir_ficha
    skipped = 0
    if asset_ids:
        clean_ids = [str(value).strip() for value in asset_ids if str(value).strip()]
        if clean_ids:
            placeholders = ",".join("?" for _ in clean_ids)
            skipped = conn.execute(
                """SELECT COUNT(*) FROM jobs
                   WHERE stage='perception' AND status='done'
                     AND asset_id IN (%s)""" % placeholders, clean_ids).fetchone()[0]
    targets = selected_for_perception(conn, root, limit, asset_ids=asset_ids)
    records_dir = out / "perception" / "fichas"
    tmp = out / "perception" / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    done = failed = 0
    for target in targets:
        path = root / target["relative_path"]
        # ``percepcion`` predates this generic projection and uses the Spanish
        # classifier labels (imagen/video/pdf).  Keep that legacy contract at
        # the boundary; passing our storage label ``image`` silently made the
        # measurement "no_intentado" for every PNG.
        perception_kind = {"image": "imagen", "video": "video", "pdf": "pdf"}[target["media_kind"]]
        entry = {"fuente": source_name, "ruta_rel": target["relative_path"], "ruta_abs": str(path),
                 "tipo": perception_kind, "bytes": path.stat().st_size,
                 "mtime": path.stat().st_mtime}
        try:
            record = construir_ficha(entry, tmp, timeout)
            escribir_ficha(records_dir, record)
            store_observation(conn, target["asset_id"], "percepcion", "ficha", record,
                              "failed" if record.get("error") else "observed")
            if record.get("error"):
                failed += 1
                set_job(conn, target["asset_id"], "perception", "retry", record["error"], True)
            else:
                done += 1
                set_job(conn, target["asset_id"], "perception", "done", None, True)
        except Exception as exc:  # per-file failure cannot abort the corpus
            failed += 1
            set_job(conn, target["asset_id"], "perception", "retry", str(exc)[:500], True)
        # A vision call can take minutes or crash independently of SQLite.
        # Persist each completed/failing item, so a stopped batch resumes from
        # durable evidence instead of holding the whole corpus transaction.
        conn.commit()
    return {"requested": len(targets) + skipped, "processed": done, "failed": failed,
            "skipped": skipped}


def project_candidates(conn: sqlite3.Connection, out: Path,
                       source_name: str = "rd") -> dict:
    records_path = out / "perception" / "fichas" / "fichas.jsonl"
    if not records_path.is_file():
        return {"candidates": 0, "reason": "no_perception_output"}
    try:
        from extraccion_db import procesar
    except ImportError:
        from cultura.mak_curatoria.extraccion_db import procesar
    result = procesar(records_path, out / "candidates", fuente=source_name)
    assets = {row["relative_path"]: row["asset_id"] for row in conn.execute(
        "SELECT asset_id, relative_path FROM assets").fetchall()}
    candidate_file = out / "candidates" / "candidatos_db.jsonl"
    projected = 0
    if candidate_file.is_file():
        for line in candidate_file.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            source = assets.get(row.get("ruta_rel", ""))
            if not source:
                continue
            evidence = {"pipeline": "extraccion_db", "obra_id": row.get("obra_id"),
                        "route": row.get("ruta_rel"), "signal": row.get("calidad_senal")}
            for field, stage in (("fecha_cruda", "resolve_event"),
                                 ("productora_cruda", "resolve_producer"),
                                 ("venue_crudo", "resolve_venue")):
                value = str(row.get(field) or "").strip()
                if value:
                    store_candidate(conn, source, field, value, evidence,
                                    float(row.get("match_ratio") or 0) if field == "productora_cruda" else None)
                    # Independent branches: venue can proceed when producer fails, etc.
                    set_job(conn, source, stage, "ready")
                    if field == "productora_cruda":
                        set_job(conn, source, "resolve_logo", "ready")
                    projected += 1
            canonical = str(row.get("productora_canonica") or "").strip()
            if canonical:
                set_job(conn, source, "resolve_producer", "done")
                if project_local_logo(conn, source, canonical):
                    set_job(conn, source, "resolve_logo", "done")
            raw_venue, city = split_venue_and_city(str(row.get("venue_crudo") or ""))
            if city:
                evidence_city = dict(evidence, raw_venue=row.get("venue_crudo"))
                store_candidate(conn, source, "city", city, evidence_city, 1.0, "candidate")
            venue = producer_venue_candidate(canonical, raw_venue) if canonical else None
            if venue:
                evidence_venue = dict(evidence, raw_venue=row.get("venue_crudo"),
                                      city=city, catalog=venue["catalog"],
                                      catalog_status=venue["catalog_status"], notes=venue["notes"])
                venue_id = str(venue.get("venue_id") or venue["name"])
                store_candidate(conn, source, "venue_reference", venue_id,
                                evidence_venue, 1.0, "candidate")
                store_relation(conn, source, "has_candidate_venue",
                               "catalog:venue:" + venue_id, evidence_venue, 1.0, "candidate")
    return {"candidates": projected, "extractor": result}


def summary(conn: sqlite3.Connection) -> dict:
    def grouped(sql):
        return {row[0]: row[1] for row in conn.execute(sql)}
    return {
        "schema": SCHEMA,
        "assets_by_kind": grouped("SELECT media_kind, COUNT(*) FROM assets GROUP BY media_kind"),
        "hash_state": grouped("SELECT hash_state, COUNT(*) FROM assets GROUP BY hash_state"),
        "jobs": grouped("SELECT stage || ':' || status, COUNT(*) FROM jobs GROUP BY stage, status"),
        "candidates": grouped("SELECT kind, COUNT(*) FROM candidates GROUP BY kind"),
        "relations": grouped("SELECT relation, COUNT(*) FROM relations GROUP BY relation"),
    }


def run(root: Path, out: Path, full_hash_mb: int, perception_limit: int,
        timeout: int) -> dict:
    root, out = root.resolve(), out.resolve()
    if not root.is_dir():
        raise ValueError("root no es un directorio: %s" % root)
    if is_within(out, root):
        raise ValueError("--out debe estar fuera de la raiz fuente (solo lectura)")
    conn = connect(out)
    run_id = hashlib.sha256((str(root) + now()).encode("utf-8")).hexdigest()[:20]
    conn.execute("INSERT INTO runs(run_id,started_at,root,schema_name) VALUES(?,?,?,?)",
                 (run_id, now(), str(root), SCHEMA))
    try:
        inventory_result = inventory(conn, root, full_hash_mb * 1024 * 1024)
        reconcile_perception_jobs(conn)
        # The inventory is useful even when a later provider never answers.
        conn.commit()
        perception_result = run_perception(conn, root, out, perception_limit, timeout)
        candidates_result = project_candidates(conn, out)
        result = {"run_id": run_id, "root": str(root), "out": str(out),
                  "inventory": inventory_result, "perception": perception_result,
                  "candidates": candidates_result, "summary": summary(conn)}
        conn.execute("UPDATE runs SET finished_at=?, summary_json=? WHERE run_id=?",
                     (now(), json.dumps(result, ensure_ascii=False), run_id))
        conn.commit()
        (out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
        return result
    finally:
        conn.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="carpeta fuente (nunca se escribe)")
    parser.add_argument("--out", required=True, help="proyeccion derivada fuera de --root")
    parser.add_argument("--full-hash-mb", type=int, default=64,
                        help="hash SHA-256 completo por archivo hasta este tamano; grandes quedan en cola")
    parser.add_argument("--perception-limit", type=int, default=0,
                        help="maximo de visuales a procesar automatico en esta tanda")
    parser.add_argument("--timeout", type=int, default=90, help="timeout por archivo perceptual")
    args = parser.parse_args(argv)
    try:
        result = run(Path(args.root), Path(args.out), args.full_hash_mb,
                     args.perception_limit, args.timeout)
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
