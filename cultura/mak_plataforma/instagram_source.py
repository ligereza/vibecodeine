"""Bounded adapter from the real Instagram export to ``mak-work-v1``.

The export remains the source archive. This module creates only references and
portfolio-shaped metadata; it never copies/moves media and never decides that
a post or reel is an artwork. Stories stay ``story_record`` records.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    import ledger as _ledger
except Exception:  # pragma: no cover - package/import mode differs on MAK
    try:
        from . import ledger as _ledger
    except Exception:  # pragma: no cover - standalone fixture use
        _ledger = None


SCHEMA = "faro-instagram-source-v1"
MEDIA_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".mp4", ".mov", ".webm", ".m4v"}
SOURCE_FILES = (
    "posts_1.json", "posts.json", "reels.json", "stories.json",
    "archived_posts.json", "igtv_videos.json",
)


def _rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                return value
    return []


def _media_nodes(value):
    """Find export media records without treating subtitles as media."""
    found = []
    if isinstance(value, dict):
        uri = str(value.get("uri") or "").strip()
        suffix = Path(uri.split("?", 1)[0]).suffix.lower()
        if uri.startswith("media/") and suffix in MEDIA_EXTENSIONS:
            found.append(value)
        for child in value.values():
            found.extend(_media_nodes(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_media_nodes(child))
    return found


def _date(timestamp):
    try:
        return datetime.fromtimestamp(float(timestamp), tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return ""


def _safe_id(uri):
    return Path(uri.split("?", 1)[0]).name


def _mentions(text):
    return sorted(set(re.findall(r"@[A-Za-z0-9_.]+", str(text or ""))))


def _kind(stem, row):
    if stem == "stories":
        return "story"
    if stem in {"reels", "igtv_videos"}:
        return "reel"
    return "post"


def _unit_selection(units, limit):
    limit = max(1, int(limit))
    buckets = {"carousel": [], "video": [], "image": []}
    for unit in units:
        if unit["grouping"]["member_count"] > 1:
            bucket = "carousel"
        elif unit["media_kind"] in {"reel", "story"} or Path(
            unit["members"][0]["asset_path"]
        ).suffix.lower() in {".mp4", ".mov", ".webm", ".m4v"}:
            bucket = "video"
        else:
            bucket = "image"
        buckets[bucket].append(unit)
    for rows in buckets.values():
        rows.sort(key=lambda row: hashlib.sha256(row["unit_id"].encode()).hexdigest())
    selected = []
    while len(selected) < limit:
        progressed = False
        for bucket in ("carousel", "video", "image"):
            if buckets[bucket]:
                selected.append(buckets[bucket].pop(0))
                progressed = True
                if len(selected) >= limit:
                    break
        if not progressed:
            break
    return selected


def _work_ref(unit):
    first = unit["members"][0]
    record_kind = "story_record" if unit["media_kind"] == "story" else "media_candidate"
    story = record_kind == "story_record"
    work_id = unit["work_id"]
    sources = [member["source_ref"] for member in unit["members"]]
    identity = {
        "kind": "record",
        "source_id": work_id,
        "entities": {"source": sources},
        "event_date": first.get("date") or "",
    }
    if _ledger is not None:
        work = _ledger.build_work_envelope(
            work_id=work_id,
            parent_task="instagram-archive-reference",
            lane="obra",
            purpose=("preservar story como registro audiovisual" if story else
                     "catalogar media Instagram como candidato revisable"),
            format="registro" if story else "media",
            provider="instagram_export",
            sources=sources,
            status="candidate",
            identity=identity,
            owner="human",
            next_action="human_review",
            evidence_required=["instagram_export", "source_media", "human_kind_decision"],
            fallback_chain=["metadata_only", "human_review"],
        )
    else:
        work = {"schema": "mak-work-v1", "work_id": work_id, "status": "candidate"}
    frame = {
        "policy": "temporary_midpoint_frame" if first["is_video"] else "source_image",
        "status": "pending_visual_index" if first["is_video"] else "source_media",
        "seconds": None,
        "path": None if first["is_video"] else first["relative_path"],
    }
    work["evidence"] = {
        "source_kind": "instagram_export",
        "media_kind": unit["media_kind"],
        "post": first["source_ref"],
        "carousel": unit["publication_id"] if unit["grouping"]["member_count"] > 1 else "",
        "date": first.get("date") or "",
        "description": first.get("description") or "",
        "path": first["relative_path"],
        "frame": frame,
        "grouping": dict(unit["grouping"]),
        "record_kind": record_kind,
        "stories_are_not_works": story,
    }
    return work


def load_catalog(info_root, media_root, limit=100):
    """Read export metadata and return a deterministic mixed reference sample."""
    info_root = Path(info_root).expanduser()
    media_root = Path(media_root).expanduser()
    units = []
    metadata_items = 0
    source_files = []
    for filename in SOURCE_FILES:
        path = info_root / filename
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        source_files.append("info/your_instagram_activity/media/" + filename)
        stem = path.stem
        for row_index, row in enumerate(_rows(payload)):
            nodes = _media_nodes(row)
            if not nodes:
                continue
            # A story is a record per media item; post/reel entries retain a
            # publication boundary so carousels become one visual unit.
            media_kind = _kind(stem, row)
            # Match the canonical inbox publication boundary so the derived
            # visual index can reuse vectors instead of creating a parallel
            # unit namespace. A story remains one audiovisual record.
            publication_id = "%s.json:%s" % (stem, row_index)
            members = []
            for member_index, node in enumerate(nodes):
                uri = str(node.get("uri") or "").strip()
                relative = uri[len("media/"):]
                media_path = media_root / relative
                description = str(node.get("title") or row.get("title") or "").strip()
                timestamp = node.get("creation_timestamp") or row.get("creation_timestamp") or row.get("timestamp")
                source_ref = "instagram://%s#%s:%s" % (filename, row_index, member_index)
                members.append({
                    "id": _safe_id(uri),
                    "asset_path": "/portfolio-media/" + relative.replace("\\", "/"),
                    "asset_available": media_path.is_file(),
                    "publicacion_id": publication_id,
                    "medio_indice": member_index,
                    "medio_total": len(nodes),
                    "fecha": _date(timestamp),
                    "descripcion_original": description,
                    "tipo_contenido": media_kind,
                    "format": "registro" if media_kind == "story" else "media",
                    "record_kind": "story_record" if media_kind == "story" else "media_candidate",
                    "source_kind": "instagram_export",
                    "source_ref": source_ref,
                    "source_file": "info/your_instagram_activity/media/" + filename,
                    "relative_path": relative.replace("\\", "/"),
                    "description": description,
                    "mentions": _mentions(description),
                    "is_video": Path(relative).suffix.lower() in {".mp4", ".mov", ".webm", ".m4v"},
                })
            if not members:
                continue
            metadata_items += len(members)
            unit_id = publication_id or "instagram:%s:%s" % (stem, row_index)
            units.append({
                "unit_id": unit_id,
                "work_id": "instagram:" + unit_id,
                "publication_id": publication_id,
                "media_kind": media_kind,
                "members": members,
                "grouping": {
                    "unit_id": unit_id,
                    "publication_id": publication_id,
                    "member_count": len(members),
                    "member_ids": [member["id"] for member in members],
                    "is_carousel": len(members) > 1,
                },
            })
            for member in members:
                member["unit_id"] = unit_id
                member["work_id"] = "instagram:" + unit_id
    selected = _unit_selection(units, limit)
    items = [member for unit in selected for member in unit["members"]]
    works = [_work_ref(unit) for unit in selected]
    return {
        "schema": SCHEMA,
        "source_kind": "instagram_export",
        "source_files": source_files,
        "metadata_items_seen": metadata_items,
        "catalog_units_seen": len(units),
        "selected_units": len(selected),
        "selected_items": len(items),
        "items": items,
        "works": works,
        "units": selected,
    }


def write_catalog(path, catalog):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return path
