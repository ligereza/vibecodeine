#!/usr/bin/env python3
"""Derived MobileCLIP/FAISS index for the existing portfolio catalog.

The Hub only reads ``neighbors.json`` through the small read-only helpers in
this module.  The expensive imports (torch, MobileCLIP, PIL and faiss) live
inside ``build_index`` so this file is safe to import in mak-hub.service.

The index is a projection, never a source of truth.  A carousel is one visual
unit, videos are represented by a temporary midpoint frame, and all outputs
retain the source identity needed to return to the portfolio inbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
import time
import uuid
from collections import defaultdict
from pathlib import Path

try:
    import instagram_source as _instagram_source
except Exception:  # noqa: BLE001 - source adapter is optional for the worker
    try:
        from . import instagram_source as _instagram_source
    except Exception:  # pragma: no cover - minimal standalone import
        _instagram_source = None


VISUAL_INDEX_SCHEMA = "faro-portfolio-visual-index-v1"
VISUAL_NEIGHBORS_SCHEMA = "faro-portfolio-visual-neighbors-v1"
MODEL_NAME = "MobileCLIP-S0"
MODEL_ARCH = "mobileclip_s0"
MODEL_VERSION = "mobileclip_s0.pt"
DEFAULT_INDEX_ROOT = Path(os.path.expanduser(
    os.environ.get("MAK_VISUAL_INDEX_ROOT",
                   "~/plataforma/derived/visual-index")))
DEFAULT_MEDIA_ROOT = Path(os.path.expanduser(
    os.environ.get("MAK_PORTFOLIO_MEDIA_ROOT", "~/portfolio_media/media")))
DEFAULT_INBOX = Path(os.path.expanduser(
    os.environ.get("MAK_PORTFOLIO_INBOX",
                   "~/plataforma/director_runs/portfolio-editor-20260808/"
                   "PORTFOLIO_INBOX.json")))
DEFAULT_MODEL_PATH = Path(os.path.expanduser(
    os.environ.get("MAK_MOBILECLIP_MODEL", "~/models/mobileclip/mobileclip_s0.pt")))
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".m4v"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DEFAULT_NEIGHBORS = 8
MIN_SCORE = float(os.environ.get("MAK_VISUAL_MIN_SCORE", "0.50"))
MIN_MARGIN = float(os.environ.get("MAK_VISUAL_MIN_MARGIN", "0.010"))


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _json_write(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def _jsonl_read(path: Path):
    if not path.is_file():
        return []
    rows = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except (TypeError, ValueError):
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        return []
    return rows


def _jsonl_write(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(temporary, path)


def file_sha256(path: Path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_asset(value):
    value = str(value or "").split("?", 1)[0].strip()
    for prefix in ("/portfolio-media/", "portfolio-media/"):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value.lstrip("/")


def resolve_asset(item, media_root=DEFAULT_MEDIA_ROOT):
    """Resolve an inbox asset without allowing it to escape the media root."""
    relative = _safe_relative_asset(item.get("asset_path"))
    if not relative or ".." in Path(relative).parts:
        return None, ""
    root = Path(media_root).expanduser().resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, ""
    if not candidate.is_file():
        return None, relative.replace("\\", "/")
    return candidate, relative.replace("\\", "/")


def _is_video(path):
    return Path(str(path).split("?", 1)[0]).suffix.lower() in VIDEO_EXTENSIONS


def _is_image(path):
    return Path(str(path).split("?", 1)[0]).suffix.lower() in IMAGE_EXTENSIONS


def _unit_key(item):
    publication = str(item.get("publicacion_id") or "").strip()
    return "publication:" + publication if publication else "item:" + str(item.get("id") or "")


def group_portfolio_items(items, media_root=DEFAULT_MEDIA_ROOT):
    """Return one indexable unit per publication, preserving source members."""
    grouped = defaultdict(list)
    for item in items or []:
        if not isinstance(item, dict) or not str(item.get("id") or "").strip():
            continue
        asset, relative = resolve_asset(item, media_root)
        if asset is None:
            continue
        member = dict(item)
        member["id"] = str(member["id"])
        member["_asset"] = str(asset)
        member["_relative_path"] = relative
        member["_is_video"] = _is_video(asset)
        grouped[_unit_key(member)].append(member)

    units = []
    for unit_id, members in grouped.items():
        members.sort(key=lambda row: (
            int(row.get("medio_indice") or 0), str(row.get("id") or "")))
        first = members[0]
        # When the archive reference and the legacy inbox share a member,
        # ordering alone can leave the old record first. Preserve Instagram
        # provenance if any member of the canonical unit carries it.
        source_member = next((row for row in members
                              if row.get("source_kind") == "instagram_export"), first)
        publication_id = str(source_member.get("publicacion_id") or
                             first.get("publicacion_id") or "").strip()
        declared_total = max(int(first.get("medio_total") or 0), 0)
        is_carousel = len(members) > 1 or declared_total > 1
        units.append({
            "unit_id": unit_id,
            "work_id": source_member.get("work_id") or first.get("work_id") or
                       "portfolio:" + (publication_id or first["id"]),
            "source_id": first["id"],
            "source_ids": [member["id"] for member in members],
            "publication_id": publication_id,
            "date": source_member.get("fecha") or first.get("fecha") or "",
            "media_count": len(members),
            "is_carousel": is_carousel,
            "has_video": any(member["_is_video"] for member in members),
            "members": members,
            "relative_path": first["_relative_path"],
            "relative_paths": [member["_relative_path"] for member in members],
            "source_kind": source_member.get("source_kind", "portfolio_inbox"),
            "source_ref": source_member.get("source_ref", ""),
            "source_file": source_member.get("source_file", ""),
            "record_kind": source_member.get("record_kind", "media_candidate"),
            "description": source_member.get("descripcion_original") or
                           source_member.get("description") or
                           first.get("descripcion_original") or first.get("description", ""),
        })
    return sorted(units, key=lambda row: (str(row.get("date") or ""), row["unit_id"]))


def select_sample(units, limit=100):
    """Select a deterministic mixed sample without touching unselected media."""
    limit = max(1, int(limit))
    source_units = sorted(
        [unit for unit in units if unit.get("source_kind") == "instagram_export"],
        key=lambda row: hashlib.sha256(row["unit_id"].encode("utf-8")).hexdigest())
    if len(source_units) >= limit:
        return source_units[:limit]
    buckets = {"carousel": [], "video": [], "image": [], "other": []}
    for unit in units:
        if unit.get("source_kind") == "instagram_export":
            continue
        if unit.get("is_carousel"):
            bucket = "carousel"
        elif unit.get("has_video"):
            bucket = "video"
        elif any(_is_image(member.get("_asset"))
                 for member in unit.get("members", [])):
            bucket = "image"
        else:
            bucket = "other"
        buckets[bucket].append(unit)
    for rows in buckets.values():
        rows.sort(key=lambda row: hashlib.sha256(
            row["unit_id"].encode("utf-8")).hexdigest())
        # A bounded archive catalog is an explicit source slice. Prefer its
        # references inside the same mixed bucket so the visual index actually
        # carries the archive provenance, while the remaining capacity keeps
        # the existing portfolio fallback available.
        rows.sort(key=lambda row: (
            0 if row.get("source_kind") == "instagram_export" else 1,
            hashlib.sha256(row["unit_id"].encode("utf-8")).hexdigest()))

    selected = list(source_units)
    order = ("carousel", "video", "image", "other")
    while len(selected) < limit:
        progressed = False
        for bucket in order:
            if buckets[bucket]:
                selected.append(buckets[bucket].pop(0))
                progressed = True
                if len(selected) >= limit:
                    break
        if not progressed:
            break
    return selected


def group_hash(unit):
    parts = []
    for member in unit.get("members", []):
        path = Path(member["_asset"])
        parts.append("%s:%s" % (member["id"], file_sha256(path)))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def stable_index_id(unit_id):
    """Fit a stable unsigned hash into signed int64 for FAISS IDs."""
    value = int(hashlib.sha256(unit_id.encode("utf-8")).hexdigest()[:15], 16)
    return value or 1


def _probe_duration(path):
    try:
        from percepcion import ffprobe_duracion
        duration = ffprobe_duracion(str(path), timeout=30)
        if duration is not None:
            return max(0.0, float(duration))
    except Exception:  # noqa: BLE001 - worker has a subprocess fallback
        pass
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=30, check=False)
        return max(0.0, float((result.stdout or "").strip()))
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _temporary_video_frame(path, directory):
    duration = _probe_duration(path)
    midpoint = max(0.0, (duration or 0.0) / 2.0)
    output = Path(directory) / (hashlib.sha256(str(path).encode()).hexdigest()[:20] + ".jpg")
    command = ["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % midpoint,
               "-i", str(path), "-frames:v", "1", "-vf", "scale=768:-1",
               str(output)]
    try:
        subprocess.run(command, capture_output=True, timeout=90, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("video_frame_failed:%s" % str(exc)[:120]) from exc
    if not output.is_file():
        raise RuntimeError("video_frame_failed:%s" % str(path))
    return output, {"evidence_kind": "video_representative_frame",
                    "frame_seconds": round(midpoint, 3),
                    "source_path": str(path)}


def _load_encoder(model_path, device):
    try:
        import torch
        import mobileclip
    except ImportError as exc:
        raise RuntimeError("visual_runtime_missing:%s" % exc.name) from exc
    model, _, preprocess = mobileclip.create_model_and_transforms(
        MODEL_ARCH, pretrained=str(model_path), device=device)
    model.eval()
    model_hash = file_sha256(Path(model_path)) if Path(model_path).is_file() else ""
    return torch, model, preprocess, model_hash


def _encode_member(path, torch, model, preprocess, device, temporary_directory):
    from PIL import Image
    source_path = path
    evidence = {"evidence_kind": "still_image"}
    if _is_video(path):
        source_path, evidence = _temporary_video_frame(path, temporary_directory)
    if not _is_image(source_path):
        raise RuntimeError("unsupported_visual_asset:%s" % path)
    with Image.open(source_path) as image:
        image = image.convert("RGB")
        tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        vector = model.encode_image(tensor)
    vector = vector.detach().float().cpu().numpy()[0]
    norm = float((vector * vector).sum() ** 0.5)
    if not math.isfinite(norm) or norm <= 0:
        raise RuntimeError("empty_visual_vector:%s" % path)
    return vector / norm, evidence


def _encode_unit(unit, torch, model, preprocess, device, temporary_directory):
    vectors = []
    evidence = []
    for member in unit["members"]:
        vector, item_evidence = _encode_member(
            Path(member["_asset"]), torch, model, preprocess, device,
            temporary_directory)
        vectors.append(vector)
        evidence.append(item_evidence)
    vector = sum(vectors) / max(1, len(vectors))
    norm = float((vector * vector).sum() ** 0.5)
    return vector / norm, evidence


def _read_previous(root):
    rows = _jsonl_read(root / "vectors.jsonl")
    previous_vectors = {}
    vector_path = root / "vectors.npy"
    if rows and vector_path.is_file():
        try:
            import numpy as np
            matrix = np.load(vector_path)
            if len(matrix) == len(rows):
                previous_vectors = {
                    str(row.get("unit_id")): matrix[index]
                    for index, row in enumerate(rows)
                    if row.get("unit_id")
                }
        except (ImportError, OSError, ValueError):
            previous_vectors = {}
    return {str(row.get("unit_id")): row for row in rows if row.get("unit_id")}, previous_vectors


def _model_metadata(model_hash):
    return {"model": MODEL_NAME, "model_version": MODEL_VERSION,
            "model_hash": model_hash, "dimension": 512}


def _make_record(unit, digest, model_hash, evidence):
    metadata = _model_metadata(model_hash)
    return {
        "schema": VISUAL_INDEX_SCHEMA,
        "unit_id": unit["unit_id"],
        "work_id": unit["work_id"],
        "source_id": unit["source_id"],
        "source_ids": unit["source_ids"],
        "publication_id": unit["publication_id"],
        "relative_path": unit["relative_path"],
        "relative_paths": unit["relative_paths"],
        "source_kind": unit.get("source_kind", "portfolio_inbox"),
        "source_ref": unit.get("source_ref", ""),
        "source_file": unit.get("source_file", ""),
        "record_kind": unit.get("record_kind", "media_candidate"),
        "source_description": unit.get("description", ""),
        "hash": digest,
        "model": metadata["model"],
        "model_version": metadata["model_version"],
        "model_hash": metadata["model_hash"],
        "date": unit.get("date") or "",
        "indexed_at": _now(),
        "dimension": metadata["dimension"],
        "media_count": unit["media_count"],
        "carousel": bool(unit["is_carousel"]),
        "has_video": bool(unit["has_video"]),
        "evidence": evidence,
        "index_id": stable_index_id(unit["unit_id"]),
    }


def _neighbor_payload(records, matrix, faiss_module, index, limit):
    import numpy as np
    id_to_record = {int(row["index_id"]): row for row in records}
    scores, found_ids = index.search(np.asarray(matrix, dtype="float32"), min(limit + 1, len(records)))
    result = {}
    for row, row_scores, row_ids in zip(records, scores, found_ids):
        candidates = []
        for score, found_id in zip(row_scores, row_ids):
            found_id = int(found_id)
            if found_id <= 0 or found_id == int(row["index_id"]):
                continue
            target = id_to_record.get(found_id)
            if not target:
                continue
            candidates.append((float(score), target))
        eligible = []
        for position, (score, target) in enumerate(candidates):
            next_score = candidates[position + 1][0] if position + 1 < len(candidates) else 0.0
            margin = score - next_score
            accepted = score >= MIN_SCORE and margin >= MIN_MARGIN
            eligible.append({
                "item_id": target["source_id"],
                "unit_id": target["unit_id"],
                "work_id": target["work_id"],
                "source_ids": target.get("source_ids", []),
                "publication_id": target.get("publication_id", ""),
                "relative_path": target.get("relative_path", ""),
                "media_count": target.get("media_count", 1),
                "source_kind": target.get("source_kind", "portfolio_inbox"),
                "source_ref": target.get("source_ref", ""),
                "record_kind": target.get("record_kind", "media_candidate"),
                "score": round(max(-1.0, min(1.0, score)), 6),
                "margin": round(max(0.0, margin), 6),
                "eligible": accepted,
                "abstention_reason": "" if accepted else (
                    "score_insuficiente" if score < MIN_SCORE else "margen_insuficiente"),
                "model": target.get("model", MODEL_NAME),
                "model_version": target.get("model_version", MODEL_VERSION),
                "evidence_kind": "visual_similarity",
                "reason": "vecindad visual MobileCLIP sobre la unidad editorial",
            })
        result[row["unit_id"]] = {
            "source_id": row["source_id"],
            "source_ids": row.get("source_ids", []),
            "publication_id": row.get("publication_id", ""),
            "neighbors": eligible,
        }
    return result


def _merge_source_catalog(items, catalog):
    """Overlay archive provenance without replacing human inbox decisions."""
    by_id = {str(item.get("id")): dict(item) for item in items or []
             if isinstance(item, dict) and item.get("id")}
    for item in (catalog or {}).get("items", []):
        if not isinstance(item, dict) or not item.get("id"):
            continue
        item_id = str(item["id"])
        merged = dict(by_id.get(item_id, {}))
        for key, value in item.items():
            if key in {"selection", "classification", "consent_status", "public_status"}:
                continue
            merged[key] = value
        by_id[item_id] = merged
    return list(by_id.values())


def _read_source_catalog(path):
    if not path:
        return None
    try:
        payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict) or payload.get("schema") != "faro-instagram-source-v1":
        return None
    return payload


def build_index(inbox_path=DEFAULT_INBOX, media_root=DEFAULT_MEDIA_ROOT,
                output_root=DEFAULT_INDEX_ROOT, limit=100,
                model_path=DEFAULT_MODEL_PATH, device="cuda", neighbors=DEFAULT_NEIGHBORS,
                instagram_catalog=None):
    """Build or incrementally update the derived index for a bounded sample."""
    started = time.perf_counter()
    output_root = Path(output_root).expanduser()
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = "visual-index-%s-%s" % (time.strftime("%Y%m%d%H%M%S"), uuid.uuid4().hex[:8])
    run_dir = output_root / "runs"
    previous, previous_vectors = _read_previous(output_root)
    payload = json.loads(Path(inbox_path).expanduser().read_text(encoding="utf-8"))
    source_catalog = _read_source_catalog(instagram_catalog)
    catalog_items = _merge_source_catalog(payload.get("items", []), source_catalog)
    units = select_sample(group_portfolio_items(catalog_items, media_root), limit)
    if not units:
        raise RuntimeError("visual_sample_empty")

    torch, model, preprocess, model_hash = _load_encoder(model_path, device)
    metadata = _model_metadata(model_hash)
    encoded = 0
    reused = 0
    failed = []
    media_inputs = 0
    video_frames = 0
    records = []
    vectors = []
    with tempfile.TemporaryDirectory(prefix="mak-visual-frame-") as temporary_directory:
        for unit in units:
            media_inputs += len(unit["members"])
            digest = group_hash(unit)
            old = previous.get(unit["unit_id"])
            reusable = bool(old and previous_vectors.get(unit["unit_id"]) is not None
                             and old.get("hash") == digest
                             and old.get("model_hash") == model_hash
                             and old.get("dimension") == metadata["dimension"])
            try:
                if reusable:
                    vector = previous_vectors[unit["unit_id"]]
                    record = dict(old)
                    record.update(_make_record(
                        unit, digest, model_hash, old.get("evidence", [])))
                    reused += 1
                else:
                    vector, evidence = _encode_unit(
                        unit, torch, model, preprocess, device, temporary_directory)
                    record = _make_record(unit, digest, model_hash, evidence)
                    encoded += 1
                    video_frames += sum(1 for item in unit["members"] if item["_is_video"])
                records.append(record)
                vectors.append(vector)
            except Exception as exc:  # noqa: BLE001 - preserve per-unit failures
                failed.append({"unit_id": unit["unit_id"], "source_id": unit["source_id"],
                               "error": str(exc)[:240]})

    if not vectors:
        raise RuntimeError("visual_index_no_vectors")
    import numpy as np
    matrix = np.asarray(vectors, dtype="float32")
    faiss = __import__("faiss")
    index = faiss.IndexIDMap2(faiss.IndexFlatIP(int(matrix.shape[1])))
    ids = np.asarray([int(row["index_id"]) for row in records], dtype="int64")
    index.add_with_ids(matrix, ids)
    faiss.write_index(index, str(output_root / "index.faiss"))
    with (output_root / "vectors.npy").open("wb") as handle:
        np.save(handle, matrix)
    _jsonl_write(output_root / "vectors.jsonl", records)
    neighbors_payload = _neighbor_payload(records, matrix, faiss, index, neighbors)
    neighbors_document = {
        "schema": VISUAL_NEIGHBORS_SCHEMA,
        "index_schema": VISUAL_INDEX_SCHEMA,
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "model_hash": model_hash,
        "dimension": int(matrix.shape[1]),
        "updated_at": _now(),
        "thresholds": {"min_score": MIN_SCORE, "min_margin": MIN_MARGIN},
        "items": neighbors_payload,
        "source_catalog": {
            "schema": (source_catalog or {}).get("schema", ""),
            "source_kind": (source_catalog or {}).get("source_kind", ""),
            "selected_units": (source_catalog or {}).get("selected_units", 0),
            "selected_items": (source_catalog or {}).get("selected_items", 0),
        },
    }
    _json_write(output_root / "neighbors.json", neighbors_document)
    try:
        index_bytes = (output_root / "index.faiss").stat().st_size
    except OSError:
        index_bytes = 0
    manifest = {
        "schema": VISUAL_INDEX_SCHEMA,
        "run_id": run_id,
        "status": "ok",
        "created_at": _now(),
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "model_hash": model_hash,
        "dimension": int(matrix.shape[1]),
        "sample_units": len(units),
        "indexed_units": len(records),
        "encoded_units": encoded,
        "reused_units": reused,
        "removed_units": len(set(previous) - {row["unit_id"] for row in records}),
        "failed_units": failed,
        "media_inputs": media_inputs,
        "video_frames": video_frames,
        "carousel_units": sum(1 for unit in units if unit["is_carousel"]),
        "image_units": sum(1 for unit in units if not unit["has_video"]),
        "neighbor_count": neighbors,
        "eligible_neighbors": sum(
            sum(1 for neighbor in row["neighbors"] if neighbor["eligible"])
            for row in neighbors_payload.values()),
        "index_bytes": index_bytes,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "output_root": str(output_root),
        "source_catalog": {
            "schema": (source_catalog or {}).get("schema", ""),
            "source_kind": (source_catalog or {}).get("source_kind", ""),
            "metadata_items_seen": (source_catalog or {}).get("metadata_items_seen", 0),
            "selected_units": (source_catalog or {}).get("selected_units", 0),
            "selected_items": (source_catalog or {}).get("selected_items", 0),
        },
    }
    _json_write(output_root / "manifest.json", manifest)
    _json_write(run_dir / (run_id + ".json"), manifest)
    try:
        del model
        torch.cuda.empty_cache()
    except Exception:  # noqa: BLE001 - cleanup must not hide a completed run
        pass
    return manifest


def read_surface(root=DEFAULT_INDEX_ROOT):
    """Read only lightweight derived neighbor data for the Hub."""
    root = Path(root).expanduser()
    path = root / "neighbors.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"available": False, "schema": VISUAL_NEIGHBORS_SCHEMA,
                "reason": "visual_index_unavailable", "items": {}}
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), dict):
        return {"available": False, "schema": VISUAL_NEIGHBORS_SCHEMA,
                "reason": "visual_index_invalid", "items": {}}
    payload = dict(payload)
    payload["available"] = True
    payload["root"] = str(root)
    return payload


def _source_to_unit(surface):
    mapping = {}
    for unit_id, row in (surface.get("items") or {}).items():
        for source_id in [row.get("source_id"), *(row.get("source_ids") or [])]:
            if source_id:
                mapping[str(source_id)] = str(unit_id)
    return mapping


def visual_relations(source_id, surface=None, limit=8):
    """Return eligible candidates for one source, never facts or metadata."""
    surface = surface or read_surface()
    if not surface.get("available"):
        return []
    unit_id = _source_to_unit(surface).get(str(source_id))
    if not unit_id:
        return []
    row = (surface.get("items") or {}).get(unit_id) or {}
    result = []
    for neighbor in row.get("neighbors") or []:
        if not neighbor.get("eligible"):
            continue
        if str(neighbor.get("item_id") or "") == str(source_id):
            continue
        result.append(dict(neighbor))
        if len(result) >= max(1, int(limit)):
            break
    return result


def surface_profile(surface=None):
    surface = surface or read_surface()
    if not surface.get("available"):
        return {"available": False, "schema": VISUAL_INDEX_SCHEMA,
                "reason": surface.get("reason", "visual_index_unavailable"),
                "indexed_units": 0, "eligible_neighbors": 0}
    rows = list((surface.get("items") or {}).values())
    neighbors = [neighbor for row in rows for neighbor in row.get("neighbors", [])]
    return {
        "available": True,
        "schema": surface.get("index_schema", VISUAL_INDEX_SCHEMA),
        "model": surface.get("model", MODEL_NAME),
        "model_version": surface.get("model_version", MODEL_VERSION),
        "dimension": surface.get("dimension", 0),
        "indexed_units": len(rows),
        "eligible_neighbors": sum(1 for row in neighbors if row.get("eligible")),
        "abstained_neighbors": sum(1 for row in neighbors if not row.get("eligible")),
        "updated_at": surface.get("updated_at", ""),
        "thresholds": surface.get("thresholds", {}),
        "source_catalog": surface.get("source_catalog", {}),
    }


def _load_inbox(path):
    payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("portfolio_inbox_invalid")
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--inbox", default=str(DEFAULT_INBOX))
    build.add_argument("--media-root", default=str(DEFAULT_MEDIA_ROOT))
    build.add_argument("--output-root", default=str(DEFAULT_INDEX_ROOT))
    build.add_argument("--model-path", default=str(DEFAULT_MODEL_PATH))
    build.add_argument("--device", default="cuda")
    build.add_argument("--limit", type=int, default=100)
    build.add_argument("--neighbors", type=int, default=DEFAULT_NEIGHBORS)
    build.add_argument("--instagram-catalog", default="")
    status = subparsers.add_parser("status")
    status.add_argument("--output-root", default=str(DEFAULT_INDEX_ROOT))
    args = parser.parse_args(argv)
    if args.command == "status":
        print(json.dumps(surface_profile(read_surface(args.output_root)), ensure_ascii=False))
        return 0
    try:
        result = build_index(args.inbox, args.media_root, args.output_root,
                             args.limit, args.model_path, args.device, args.neighbors,
                             args.instagram_catalog or None)
    except Exception as exc:  # noqa: BLE001 - CLI emits durable failure evidence
        root = Path(args.output_root).expanduser()
        run_id = "visual-index-failed-%s-%s" % (time.strftime("%Y%m%d%H%M%S"), uuid.uuid4().hex[:8])
        failure = {"schema": VISUAL_INDEX_SCHEMA, "run_id": run_id,
                   "status": "error", "created_at": _now(),
                   "error": str(exc)[:400], "output_root": str(root)}
        _json_write(root / "runs" / (run_id + ".json"), failure)
        print(json.dumps(failure, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
