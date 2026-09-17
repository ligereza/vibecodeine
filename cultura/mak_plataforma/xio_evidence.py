"""Read-only XIO show-kit evidence adapter for the existing MAK scene.

This module reads only the small, authoritative setlist/cue/annotation files.
It does not ingest the event log, infer identity, append to the ledger, or
create a second work schema.  The returned envelope is ``mak-work-v1``.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:
    import ledger as _ledger
except Exception:  # pragma: no cover - standalone/local fixture use
    try:
        from . import ledger as _ledger
    except Exception:  # pragma: no cover - adapter fallback
        _ledger = None


SCHEMA = "faro-xio-evidence-v1"
# The show kit no longer lives in this repository: its source is the XIO
# checkout (`ligereza/XIO`), where these same files keep being edited. The
# copy under `/home/mak/xio` was a frozen tree and was retired; reading it
# meant reading July's show. `MAK_XIO_SHOW_ROOT` still overrides this, and
# this module is the single place where the path is declared.
DEFAULT_ROOT = Path(os.environ.get(
    "MAK_XIO_SHOW_ROOT", "/home/mak/XIO/xio/show_kit"))
# The FOH knowledge XIO publishes for this Hub: one envelope per subject
# (event, venue, artist, work), already written in this module's own
# `faro-xio-evidence-v1` shape, so nothing here re-implements XIO's reader.
# XIO builds it with `python -m xio.foh_knowledge --publish`; the directory is
# measured state living outside both repositories and is regenerated from the
# ledger, so its absence is normal and is reported as such.
KNOWLEDGE_ROOT = Path(os.environ.get(
    "MAK_XIO_KNOWLEDGE_DIR", "/home/mak/XIO/xio/data/foh_knowledge"))
KNOWLEDGE_SUBJECTS = ("event", "venue", "artist", "work")
MAX_SEGMENTS = 24


def _text(path: Path, limit: int = 160_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _json(path: Path):
    try:
        return json.loads(_text(path))
    except (json.JSONDecodeError, TypeError):
        return {}


def _source_name(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root.parent.parent).as_posix()
    except ValueError:
        return path.name


def _show_date(root: Path, annotation: str) -> str:
    match = re.search(r"20\d{2}[01]\d[0-3]\d", root.name)
    if match:
        value = match.group(0)
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    match = re.search(r"20\d{2}-[01]\d-[0-3]\d", annotation)
    return match.group(0) if match else ""


def _event_name(root: Path, show_doc: str) -> str:
    match = re.search(r"DREF\s+CHOCOLATE", show_doc, re.IGNORECASE)
    if match:
        return "DREF CHOCOLATE"
    match = re.search(r"show_([a-z0-9_-]+)", root.name, re.IGNORECASE)
    return match.group(1).replace("_", " ").upper() if match else ""


def _timecode_atoms(annotation: str, source: str):
    atoms = []
    for value in dict.fromkeys(re.findall(r"\b\d{2}:\d{2}:\d{2}:\d{2}\b", annotation)):
        atoms.append({
            "field": "timecode",
            "value": value,
            "status": "observed",
            "source": source,
        })
    return atoms


def _unknown(field: str, source: str):
    return {"field": field, "value": "", "status": "unknown", "source": source}


def load_foh_knowledge(subject, key=None, root=None):
    """Read the FOH knowledge envelope XIO published for one subject.

    This is a read of a file, not a second implementation: the envelope already
    carries `field/value/status/source` atoms in this module's schema, and the
    two layers XIO keeps apart -- what a source declared and what an instrument
    observed -- arrive labelled, so a venue somebody typed once never reads
    like a venue that was measured.

    An absent directory is reported, never treated as empty knowledge: the
    difference between "XIO has not published yet" and "there is nothing to
    know" is the whole point.
    """
    if subject not in KNOWLEDGE_SUBJECTS:
        return {"ok": False, "available": False, "schema": SCHEMA,
                "source": "xio/foh_knowledge",
                "reason": f"subject desconocido: {subject}"}
    base = Path(root or KNOWLEDGE_ROOT)
    path = base / f"{subject}.json"
    if not path.is_file():
        return {"ok": True, "available": False, "schema": SCHEMA,
                "source": "xio/foh_knowledge",
                "reason": f"XIO no ha publicado {path.name} todavia",
                "path": str(path), "evidence": [], "keys": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"ok": False, "available": False, "schema": SCHEMA,
                "source": "xio/foh_knowledge",
                "reason": f"envelope ilegible: {type(exc).__name__}",
                "path": str(path)}
    keys = payload.get("keys") or {}
    if key is None:
        return {"ok": True, "available": bool(keys), "schema": SCHEMA,
                "source": "xio/foh_knowledge", "subject": subject,
                "generated": payload.get("generated"),
                "keys": {name: envelope.get("evidence") or []
                         for name, envelope in keys.items()}}
    envelope = keys.get(key)
    if envelope is None:
        return {"ok": True, "available": False, "schema": SCHEMA,
                "source": "xio/foh_knowledge", "subject": subject, "key": key,
                "reason": "XIO no tiene evidencia publicada de este sujeto",
                "evidence": []}
    return {**envelope, "generated": payload.get("generated")}


def load_show_evidence(root=None, limit=MAX_SEGMENTS):
    """Return a bounded evidence surface from a local XIO show kit."""
    root = Path(root or DEFAULT_ROOT)
    setlist_path = root / "setlist_festival_sentir.txt"
    durations_path = root / "setlist_durations_dref.json"
    cue_path = root / "cue_map_dref.json"
    show_doc_path = root / "DIA_DEL_SHOW.md"
    annotation_path = root / "ANOTACIONES_SHOW_20260724.md"
    if not any(path.exists() for path in (setlist_path, durations_path, cue_path)):
        return {
            "ok": True, "available": False, "schema": SCHEMA,
            "source": "xio/show_kit", "reason": "show_kit_no_disponible",
            "evidence": [], "segments": [], "unknowns": ["event", "date", "artist", "venue", "producer"],
        }

    setlist_text = _text(setlist_path)
    show_doc = _text(show_doc_path)
    annotation = _text(annotation_path)
    cue_doc = _json(cue_path)
    duration_doc = _json(durations_path)
    event = _event_name(root, show_doc)
    event_date = _show_date(root, annotation)
    source_files = [
        _source_name(root, path) for path in
        (setlist_path, durations_path, cue_path, show_doc_path, annotation_path)
        if path.exists()
    ]
    primary_source = _source_name(root, show_doc_path) if show_doc_path.exists() else (
        source_files[0] if source_files else "xio/show_kit")
    evidence = []
    if event:
        evidence.append({"field": "event", "value": event,
                         "status": "declared", "source": primary_source})
    if event_date:
        evidence.append({"field": "date", "value": event_date,
                         "status": "declared", "source": _source_name(root, annotation_path)})
    evidence.extend(_timecode_atoms(
        annotation, _source_name(root, annotation_path)))
    for field in ("artist", "venue", "producer"):
        evidence.append(_unknown(field, primary_source))

    cues = cue_doc.get("cues", []) if isinstance(cue_doc, dict) else []
    setlist_rows = []
    for index, line in enumerate(setlist_text.splitlines()):
        match = re.match(r"^\s*(\d{2}:\d{2}:\d{2}:\d{2})\s+(.+?)\s*$", line)
        if match:
            setlist_rows.append({"index": index, "timecode": match.group(1), "tema": match.group(2)})
    durations = duration_doc.get("durations", []) if isinstance(duration_doc, dict) else []
    segments = []
    for index, row in enumerate(cues[:max(1, min(int(limit), MAX_SEGMENTS))]):
        if not isinstance(row, dict):
            continue
        segments.append({
            "segment_id": f"xio:{root.name}:cue:{index + 1}",
            "index": index,
            "timecode": str(row.get("timecode") or ""),
            "title": str(row.get("tema") or ""),
            "layer": row.get("layer"),
            "clip": row.get("clip"),
            "duration_s": durations[index] if index < len(durations) else None,
            "source": _source_name(root, cue_path),
            "status": "observed",
        })
    if not segments:
        segments = [
            {"segment_id": f"xio:{root.name}:setlist:{index}", **row,
             "source": _source_name(root, setlist_path), "status": "declared"}
            for index, row in enumerate(setlist_rows[:max(1, min(int(limit), MAX_SEGMENTS))])
        ]

    work_id = f"xio:show:{root.name}"
    if _ledger is not None:
        work = _ledger.build_work_envelope(
            work_id=work_id,
            parent_task="xio-show-evidence",
            lane="trabajo",
            purpose="preservar evidencia audiovisual separada del show kit",
            format="show_evidence",
            provider="xio_local",
            sources=source_files,
            status="candidate",
            identity={
                "kind": "work", "source_id": work_id,
                "entities": {"event": [event] if event else [], "source": source_files},
                "event_date": event_date,
            },
            owner="MAK",
            next_action="link manually to portfolio source",
            evidence_required=["xio_show_kit", "human_portfolio_link"],
            fallback_chain=["metadata_only", "human_review"],
        )
        valid, errors = _ledger.validate_work_envelope(work)
    else:
        work, valid, errors = {"schema": "mak-work-v1", "work_id": work_id}, False, ["ledger_unavailable"]
    return {
        "ok": True, "available": True, "schema": SCHEMA,
        "source": "xio/show_kit", "source_files": source_files,
        "work": work, "work_valid": valid, "work_errors": errors,
        "linked_to_source_id": False,
        "next_action": "link manually to portfolio source",
        "evidence": evidence, "segments": segments,
        "counts": {"setlist": len(setlist_rows), "cues": len(cues), "segments": len(segments)},
        "unknowns": [row["field"] for row in evidence if row.get("status") == "unknown"],
    }
