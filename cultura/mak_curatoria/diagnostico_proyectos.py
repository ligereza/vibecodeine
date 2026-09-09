#!/usr/bin/env python3
"""Diagnostico automatico antes de percibir una carpeta creativa.

La unidad de trabajo es el proyecto y su familia de obra, no cada PNG.  Lee
la proyeccion de ``ingesta_archivo.py`` y agrega un plan derivado en la misma
SQLite: anclas editables, secuencias, videos representativos, tipo 2D/3D/
motion, rol de almacenamiento y colas de estrategia. Nunca abre la fuente
original para escribirla y nunca promueve artista/cliente como identidad
confirmada: esos campos son candidatos con evidencia de ruta.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

try:
    from cultura.mak_plataforma.ledger import (build_work_envelope,
                                                validate_work_envelope)
except ImportError:  # pragma: no cover - MAK mirror imports cultura flat
    try:
        from mak_plataforma.ledger import (build_work_envelope,
                                           validate_work_envelope)
    except ImportError:  # pragma: no cover - diagnostic remains standalone
        build_work_envelope = validate_work_envelope = None


SCHEMA = "mak-project-diagnostic-v1"
ORGANISM_PLAN_SCHEMA = "mak-family-triangulation-plan-v1"
ANCHOR_EXTENSIONS = {".blend", ".aep", ".psd", ".psb", ".ai", ".prproj", ".c4d", ".toe"}
EDITABLE_EXTENSIONS = ANCHOR_EXTENSIONS | {".svg"}
THREE_D_EXTENSIONS = {
    ".blend", ".blend1", ".obj", ".fbx", ".glb", ".gltf", ".vdb", ".uasset", ".c4d",
}
TWO_D_EXTENSIONS = {
    ".psd", ".psb", ".ai", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".heic",
    ".tif", ".tiff", ".exr", ".pdf",
}
MOTION_EXTENSIONS = {".aep", ".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"}
ADOBE_METADATA_EXTENSIONS = {".aep", ".aet", ".psd", ".psb", ".ai", ".indd", ".idml"}
NON_CONTENT_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
TRIANGULATION_BRANCHES = (
    "coverage", "structure", "visual", "identity", "claim_safety",
)
GENERATED_DIRS = {
    "assets", "asset", "source", "sources", "textures", "texture", "obj", "fbx", "vdb",
    "renders", "render", "frames", "frame", "output", "outputs", "export", "exports",
    "preview", "previews", "cache", "caches", "autosave", "backup", "backups", "tmp",
    "temp", "alquiler", "materiales", "materials", "almacenamiento automatico de adobe after effects",
}
ARCHIVE_TOKENS = {"backup", "backups", "respaldo", "respaldo", "icloud", "archive", "archivo",
                  "archives", "descargas", "downloads", "recovery", "recover", "autosave"}
CLIENT_TOKENS = {"cliente", "client", "encargo", "commission", "brief", "cotizacion", "presupuesto"}
PERSONAL_TOKENS = {"personal", "obra", "autoral", "portfolio", "portafolio", "isвкw", "iskvw"}
# These patterns are deliberately non-nested.  A nested repeated group turns
# long camera/export names such as Instagram numeric IDs into catastrophic
# backtracking and can stall the whole diagnosis before it emits a plan.
VERSION_RE = re.compile(r"(?:^|[_ -])(?:v|ver|version|final|copy|copia|export|render|output)(?:[_ -]*\d*)?", re.I)
TRAILING_NUMBER_RE = re.compile(r"[_ -]\d{2,}$")


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def compact(value: str) -> str:
    return normalize(value).replace(" ", "")


def stable_id(prefix: str, value: str) -> str:
    return prefix + "_" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def dir_is_generated(name: str) -> bool:
    value = normalize(name)
    return value in GENERATED_DIRS or value.startswith("almacenamiento automatico")


def clean_anchor_dir(parts: tuple[str, ...]) -> tuple[str, ...]:
    """Move a project anchor out of source/cache/render directories."""
    parts = tuple(parts)
    while len(parts) > 1 and dir_is_generated(parts[-1]):
        parts = parts[:-1]
    return parts or ("[root]",)


def path_dirs(rel: str) -> list[tuple[str, ...]]:
    parts = PurePosixPath(rel).parts
    return [parts[:i] for i in range(1, len(parts))]


def frame_like(stem: str) -> bool:
    value = normalize(stem)
    if value.isdigit():
        return True
    if TRAILING_NUMBER_RE.search(stem):
        return True
    return any(token in value.split() for token in ("frame", "frames", "render", "output", "img", "image", "comp"))


def is_non_content_path(value: str) -> bool:
    """Identify filesystem sidecars/cache markers, not visual content."""
    name = PurePosixPath(str(value or "").replace("\\", "/")).name.casefold()
    return name.startswith("._") or name in NON_CONTENT_NAMES


def family_stem(stem: str) -> str:
    value = VERSION_RE.sub(" ", stem)
    value = TRAILING_NUMBER_RE.sub("", value)
    value = normalize(value)
    return value or "sin_nombre"


def project_root_for(rel: str, anchor_dirs: set[tuple[str, ...]]) -> tuple[str, ...]:
    candidates = [d for d in path_dirs(rel) if d in anchor_dirs]
    if candidates:
        return max(candidates, key=len)
    parts = PurePosixPath(rel).parts
    return parts[:1] or ("[root]",)


def dimensionality(rows: list[sqlite3.Row]) -> tuple[str, dict]:
    counts = Counter(row["extension"] for row in rows)
    three = sum(counts[e] for e in THREE_D_EXTENSIONS)
    two = sum(counts[e] for e in TWO_D_EXTENSIONS)
    motion = sum(counts[e] for e in MOTION_EXTENSIONS)
    # A source project is stronger evidence than its rendered derivatives:
    # one .blend plus 800 PNG frames remains a 3D project.  Raw counts stay
    # in the diagnostic for audit; scores choose the next instrument.
    three_score = three + 10 * sum(counts[e] for e in {".blend", ".c4d"})
    two_score = two + 10 * sum(counts[e] for e in {".psd", ".psb", ".ai"})
    motion_score = motion + 10 * counts[".aep"]
    source_dimensions = set()
    if any(counts[e] for e in {".blend", ".c4d"}):
        source_dimensions.add("3d")
    if any(counts[e] for e in {".psd", ".psb", ".ai", ".svg"}):
        source_dimensions.add("2d")
    if counts[".aep"]:
        source_dimensions.add("motion")
    signals = {"3d": three, "2d": two, "motion": motion,
               "scores": {"3d": three_score, "2d": two_score, "motion": motion_score},
               "source_dimensions": sorted(source_dimensions)}
    active = [name for name, count in {"3d": three, "2d": two, "motion": motion}.items() if count]
    if len(active) == 1:
        label = active[0]
    elif not active:
        label = "unknown"
    elif len(source_dimensions) > 1:
        # Competing editable sources are evidence of a mixed project even if
        # exported PNGs dominate the byte/count volume.
        label = "mixto"
    elif len(source_dimensions) == 1:
        label = next(iter(source_dimensions))
    elif three_score >= max(two_score, motion_score) * 1.25:
        label = "3d"
    elif motion_score >= max(two_score, three_score) * 1.25:
        label = "motion"
    elif two_score >= max(three_score, motion_score) * 1.25:
        label = "2d"
    else:
        label = "mixto"
    return label, signals


def role_from_path(project_path: str, container_root: str) -> tuple[str, list[dict], str]:
    """Return candidate role, evidence, and storage role; never identity truth."""
    tokens = set(normalize(project_path + " " + container_root).split())
    role_evidence = []
    for token in sorted(tokens & CLIENT_TOKENS):
        role_evidence.append({"signal": token, "candidate": "client"})
    for token in sorted(tokens & PERSONAL_TOKENS):
        role_evidence.append({"signal": token, "candidate": "personal"})
    if any(item["candidate"] == "client" for item in role_evidence):
        role = "client_candidate"
    elif any(item["candidate"] == "personal" for item in role_evidence):
        role = "personal_candidate"
    else:
        role = "unknown"
    storage = "backup_or_archive_candidate" if tokens & ARCHIVE_TOKENS else "working_or_mixed"
    return role, role_evidence, storage


def representative(rows: list[sqlite3.Row]) -> tuple[sqlite3.Row, str]:
    def score(row: sqlite3.Row) -> tuple[int, int, str]:
        if is_non_content_path(row["relative_path"]):
            return 0, 0, row["relative_path"]
        ext = row["extension"]
        if ext in VIDEO_EXTENSIONS:
            rank = 500
            reason = "video_completo"
        elif ext in EDITABLE_EXTENSIONS:
            rank = 400
            reason = "fuente_editable"
        elif ext == ".pdf":
            rank = 300
            reason = "documento_exportado"
        elif row["media_kind"] == "image":
            rank = 200
            reason = "muestra_visual"
        else:
            rank = 100
            reason = "metadata_unica"
        return rank, int(row["bytes"] or 0), row["relative_path"]
    row = max(rows, key=score)
    ext = row["extension"]
    reason = "metadata_sidecar" if is_non_content_path(row["relative_path"]) else (
        "video_completo" if ext in VIDEO_EXTENSIONS else (
        "fuente_editable" if ext in EDITABLE_EXTENSIONS else (
            "documento_exportado" if ext == ".pdf" else (
                "muestra_visual" if row["media_kind"] == "image" else "metadata_unica"))))
    return row, reason


def family_strategy(rows: list[sqlite3.Row]) -> tuple[str, str, int, int]:
    video_count = sum(row["extension"] in VIDEO_EXTENSIONS for row in rows)
    frame_count = sum(row["media_kind"] == "image" and frame_like(PurePosixPath(row["relative_path"]).stem)
                      for row in rows)
    editable = any(row["extension"] in EDITABLE_EXTENSIONS for row in rows)
    transient = sum(any(token in normalize(row["relative_path"]).split() for token in ("cache", "autosave", "tmp"))
                    for row in rows)
    if rows and all(is_non_content_path(row["relative_path"]) for row in rows):
        return "metadata_only_deferred", "familia_de_sidecars_no_contenido", frame_count, video_count
    if transient == len(rows):
        return "metadata_only_deferred", "familia_de_cache_o_autoguardado", frame_count, video_count
    if video_count and frame_count >= 5:
        return "video_first_frames_deferred", "video_cubre_secuencia", frame_count, video_count
    if frame_count >= 20:
        return "sample_frames_deferred", "secuencia_larga_sin_video", frame_count, video_count
    if editable:
        return "inspect_editable_first", "fuente_editable_disponible", frame_count, video_count
    if len(rows) >= 100:
        return "sample_visuals", "volumen_visual_alto", frame_count, video_count
    if video_count:
        return "inspect_video", "video_disponible", frame_count, video_count
    return "metadata_then_visual_sample", "sin_representante_fuerte", frame_count, video_count


def structure_adapter_for_path(path: str, media_kind: str = "") -> str:
    """Return a deterministic reader, never a semantic judge.

    The fallback names are organism sensors, not claims that a package is
    installed.  They intentionally include bounded readers (XMP window and
    standard-library XML/ZIP paths) so an absent optional package becomes a
    visible capability decision rather than an empty negative.
    """
    suffix = Path(str(path)).suffix.casefold()
    kind = str(media_kind or "").casefold()
    if kind == "video" or suffix in VIDEO_EXTENSIONS:
        return "ffprobe" if shutil.which("ffprobe") else ""
    if kind == "pdf" or suffix == ".pdf":
        return "pdfinfo" if shutil.which("pdfinfo") else ""
    if suffix in ADOBE_METADATA_EXTENSIONS:
        if importlib.util.find_spec("psd_tools") and suffix in {".psd", ".psb"}:
            return "psd-tools+xmp_window"
        return "xmp_window"
    if kind == "image" or suffix in TWO_D_EXTENSIONS - {".pdf"}:
        return "Pillow" if importlib.util.find_spec("PIL") else ""
    if suffix in {".blend", ".blend1"}:
        blender = os.environ.get("MAK_BLENDER", "")
        if (shutil.which("blender") or
                (blender and Path(blender).is_file()) or
                Path("/home/mak/blender/blender").is_file()):
            return "blender_headless_manifest"
        return ""
    if suffix in ARCHIVE_EXTENSIONS:
        return "7z_manifest" if (shutil.which("7z") or shutil.which("7za")) else (
            "zipfile_manifest" if suffix == ".zip" else "")
    if suffix == ".xml":
        return "resolume_xml_probe"
    if suffix in {".ai", ".eps"}:
        if shutil.which("pdfinfo"):
            return "pdfinfo"
        if importlib.util.find_spec("psd_tools"):
            return "psd-tools"
    if suffix in EDITABLE_EXTENSIONS or suffix in THREE_D_EXTENSIONS:
        return ""
    return "stat"


def organism_plan(family: dict, representative_path: str = "",
                  coverage: dict | None = None,
                  job_states: dict | None = None) -> dict:
    """Create the organism's bounded work contract for one family.

    This is routing, not interpretation. The plan tells the organism which
    evidence branches may run, what is the single representative, and when it
    must abstain. It never claims an artist, client, venue, producer or logo.
    The plan is deliberately emitted as a derived sidecar so the source tree
    and the live MAK queues remain untouched.
    """
    family_id = str(family.get("family_id") or "").strip()
    project_id = str(family.get("project_id") or "").strip()
    strategy = str(family.get("strategy") or "metadata_then_visual_sample")
    representative = str(family.get("representative_asset_id") or "").strip()
    path = str(representative_path or "").strip()
    coverage = coverage if isinstance(coverage, dict) else {}
    job_states = job_states if isinstance(job_states, dict) else {}
    coverage_status = str(coverage.get("status") or "not_measured")
    deferred = strategy == "metadata_only_deferred"
    visual_allowed = not deferred and bool(representative)
    structure_allowed = strategy in {
        "inspect_editable_first", "diagnose_editable_structure",
        "diagnose_editable_and_video", "inspect_video",
    }
    video_first = strategy in {"video_first_frames_deferred", "inspect_video",
                               "diagnose_video_first", "diagnose_editable_and_video"}
    # The organism may use a branch result as a candidate only. A relation is
    # never promoted from a single model answer or from visual similarity.
    branches = [
        {"name": "coverage", "stage": "deterministic_match", "required": True,
         "policy": "exact_hash_then_path_size_mtime_then_family_context"},
        {"name": "structure", "stage": "extract_structure", "required": structure_allowed,
         "policy": "read_editable_metadata_without_rendering_every_derivative"},
        {"name": "visual", "stage": "curatoria_vision", "required": visual_allowed,
         "policy": "representative_only;video_or_editable_precedes_frames"},
        {"name": "identity", "stage": "investigacion", "required": not deferred,
         "policy": "primary_sources_only;candidate_relations_with_citations"},
        {"name": "claim_safety", "stage": "ollama_judge", "required": True,
         "policy": "abstain_on_conflict_or_missing_evidence"},
    ]
    if coverage_status == "already_reviewed":
        plan_status = "already_reviewed"
        work_status = "covered_no_enqueue"
        next_action = "reuse_existing_observation"
    elif coverage_status == "partially_reviewed":
        plan_status = "partially_reviewed"
        work_status = "coverage_partial"
        next_action = "reconcile_representative"
    elif coverage_status == "ambiguous":
        plan_status = "ambiguous"
        work_status = "coverage_ambiguous"
        next_action = "disambiguate_coverage"
    elif coverage_status == "unreviewed":
        plan_status = "unreviewed"
        work_status = "coverage_passed"
        next_action = "route_representative"
    else:
        plan_status = "deferred" if deferred else "awaiting_coverage"
        work_status = "coverage_deferred" if deferred else "coverage_pending"
        next_action = "archive_metadata_only" if deferred else "coverage_gate"
    # A source observation can suppress duplicate provider work, but never
    # suppresses the claim-safety branch or promotes a relation.
    if coverage_status in {"already_reviewed", "partially_reviewed", "ambiguous"}:
        for branch in branches:
            if branch["name"] in {"visual", "identity"}:
                branch["required"] = False
                branch["policy"] += ";coverage_requires_reconciliation_first"

    representative_ext = Path(path).suffix.casefold()
    structural = representative_ext in EDITABLE_EXTENSIONS or representative_ext in {
        ".blend1", ".obj", ".mtl", ".fbx", ".glb", ".gltf", ".vdb", ".uasset",
    }
    execution = {
        "asset_id": representative,
        "ready": [],
        "deferred": [],
        "dependencies": [
            ["coverage", "structure"], ["coverage", "visual"],
            ["structure", "visual"], ["visual", "identity"],
            ["identity", "claim_safety"],
        ],
    }
    for branch in branches:
        name = branch["name"]
        if not branch["required"]:
            execution["deferred"].append({"branch": name, "reason": "not_required_by_strategy"})
            continue
        if name == "coverage":
            execution["ready"].append({"branch": name, "stage": "coverage_gate",
                                        "status": coverage_status})
        elif name == "structure":
            stage = "extract_structure"
            status = job_states.get((representative, stage), "not_scheduled")
            adapter = structure_adapter_for_path(
                representative_path, family.get("media_kind", ""))
            if not adapter and status in {"not_scheduled", "ready", "retry"}:
                status = "deferred_tool"
            elif status == "not_scheduled" and adapter:
                status = "ready"
            execution["ready" if status in {"ready", "retry", "done", "observed"} else "deferred"].append(
                {"branch": name, "stage": stage, "status": status,
                 "adapter": adapter})
        elif name == "visual":
            stage = "render_preview" if structural else "perception"
            status = job_states.get((representative, stage), "not_scheduled")
            execution["ready" if status in {"ready", "retry", "done", "observed"} else "deferred"].append(
                {"branch": name, "stage": stage, "status": status,
                 "follow_up": "perception" if structural else ""})
        elif name == "identity":
            execution["deferred"].append({
                "branch": name,
                "stages": ["resolve_event", "resolve_producer", "resolve_venue",
                           "resolve_logo", "investigacion"],
                "reason": "requires_observation_and_candidate_evidence",
            })
        elif name == "claim_safety":
            execution["deferred"].append({
                "branch": name, "stage": "ollama_judge",
                "reason": "requires_identity_evidence_and_conflict_check",
            })

    work_kwargs = {
        "work_id": "creative-family:%s" % family_id,
        "parent_task": "creative-project:%s" % project_id,
        "lane": "obra",
        "purpose": "triangulate one creative family without reopening derived members",
        "format": str(family.get("family_kind") or "asset_family"),
        "provider": "deterministic_router",
        "sources": [path] if path else [],
        "status": work_status,
        "owner": "MAK",
        "next_action": next_action,
        "evidence_required": [
            "family_structure", "coverage_result", "representative_observation",
            "independent_identity_source",
        ],
        "fallback_chain": [
            "deterministic_metadata", "editable_or_video_representative",
            "representative_visual", "primary_source_research", "abstain",
        ],
        "identity": {
            "schema": "mak-identity-v1", "kind": "work",
            "source_id": "family:%s" % family_id,
            "parent_id": "project:%s" % project_id,
            "entities": {
                "artist": [], "username": [], "client": [], "collab": [],
                "event": [], "festival": [], "venue": [], "location": [],
                "source": ["portable_ssd"],
            },
            "event_date": "", "published_at": "",
        },
    }
    work = (build_work_envelope(**work_kwargs)
            if build_work_envelope is not None else {
                "schema": "mak-work-v1", **work_kwargs,
                "allowed_decisions": ["hacer", "revisar", "refutar", "archivar", "descartar"],
                "created_at": "",
            })
    valid, errors = (validate_work_envelope(work)
                     if validate_work_envelope is not None else (True, []))
    return {
        "schema": ORGANISM_PLAN_SCHEMA,
        "unit": "family",
        "status": plan_status,
        "family_id": family_id,
        "project_id": project_id,
        "family_kind": str(family.get("family_kind") or "asset_family"),
        "strategy": strategy,
        "coverage": {
            "status": coverage_status,
            "match_type": str(coverage.get("match_type") or ""),
            "matched_assets": int(coverage.get("matched_assets") or 0),
            "ambiguous_assets": int(coverage.get("ambiguous_assets") or 0),
        },
        "representative": {
            "asset_id": representative,
            "path": path,
            "reason": str(family.get("representative_reason") or ""),
            "video_first": video_first,
        },
        "family_stats": {
            "member_count": int(family.get("member_count") or 0),
            "frame_count": int(family.get("frame_count") or 0),
            "video_count": int(family.get("video_count") or 0),
            "family_kind": str(family.get("family_kind") or "asset_family"),
        },
        "scope": {
            "process_representative_first": bool(representative) and not deferred,
            "defer_frames_until_video_or_representative_fails": True,
            "metadata_only_for_cache_or_autosave": deferred,
        },
        "branches": branches,
        "join_policy": {
            "minimum_independent_evidence": 2,
            "identity_resolution": "candidate_only_until_two_independent_sources_agree",
            "conflict": "abstain_and_preserve_each_observation",
            "basename_alone": "never_sufficient",
        },
        "execution": execution,
        "work": work,
        "work_contract_valid": bool(valid),
        "work_contract_errors": list(errors),
        "promotion": "none",
    }


def validate_organism_plan(plan: object) -> tuple[bool, list[str]]:
    """Validate the routing envelope before the conductor can observe it."""
    if not isinstance(plan, dict):
        return False, ["plan_not_object"]
    errors = []
    if plan.get("schema") != ORGANISM_PLAN_SCHEMA:
        errors.append("plan_bad_schema")
    if plan.get("unit") != "family":
        errors.append("plan_bad_unit")
    for field in ("family_id", "project_id", "strategy", "branches", "execution", "work"):
        if not plan.get(field):
            errors.append("plan_missing_%s" % field)
    if plan.get("promotion") != "none":
        errors.append("plan_promotion_not_none")
    branch_names = [str(row.get("name") or "") for row in plan.get("branches", [])
                    if isinstance(row, dict)]
    missing = [name for name in TRIANGULATION_BRANCHES if name not in branch_names]
    if missing:
        errors.append("plan_missing_branches:%s" % ",".join(missing))
    join = plan.get("join_policy")
    try:
        quorum = int(join.get("minimum_independent_evidence") or 0) if isinstance(join, dict) else 0
    except (TypeError, ValueError):
        quorum = 0
    if quorum < 2:
        errors.append("plan_evidence_quorum_too_low")
    execution = plan.get("execution")
    if isinstance(execution, dict):
        if str(execution.get("asset_id") or "") != str(
                (plan.get("representative") or {}).get("asset_id") or ""):
            errors.append("execution_asset_mismatch")
        for key in ("ready", "deferred", "dependencies"):
            if not isinstance(execution.get(key), list):
                errors.append("execution_%s_not_list" % key)
    if validate_work_envelope is not None:
        valid_work, work_errors = validate_work_envelope(plan.get("work"))
        if not valid_work:
            errors.extend("work:" + error for error in work_errors)
    return not errors, errors


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS diagnostic_runs (
          run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, schema_name TEXT NOT NULL,
          summary_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS projects (
          project_id TEXT PRIMARY KEY, project_path TEXT UNIQUE NOT NULL,
          container_root TEXT NOT NULL, dimensionality TEXT NOT NULL,
          owner_status TEXT NOT NULL, owner_evidence_json TEXT NOT NULL,
          storage_role TEXT NOT NULL, asset_count INTEGER NOT NULL, bytes INTEGER NOT NULL,
          anchor_count INTEGER NOT NULL, strategy TEXT NOT NULL, confidence REAL NOT NULL,
          diagnostic_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS families (
          family_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          family_key TEXT NOT NULL, family_kind TEXT NOT NULL, member_count INTEGER NOT NULL,
          bytes INTEGER NOT NULL, representative_asset_id TEXT, representative_reason TEXT NOT NULL,
          strategy TEXT NOT NULL, frame_count INTEGER NOT NULL, video_count INTEGER NOT NULL,
          diagnostic_json TEXT NOT NULL, UNIQUE(project_id, family_key)
        );
        CREATE TABLE IF NOT EXISTS project_members (
          asset_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          family_id TEXT NOT NULL REFERENCES families(family_id), member_role TEXT NOT NULL,
          is_representative INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS projects_strategy ON projects(strategy);
        CREATE INDEX IF NOT EXISTS families_strategy ON families(strategy);
        CREATE TABLE IF NOT EXISTS coverage_runs (
          run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
          source_paths_json TEXT NOT NULL, summary_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS asset_coverage (
          run_id TEXT NOT NULL REFERENCES coverage_runs(run_id),
          asset_id TEXT NOT NULL REFERENCES assets(asset_id),
          status TEXT NOT NULL, match_type TEXT NOT NULL,
          source_count INTEGER NOT NULL DEFAULT 0,
          match_paths_json TEXT NOT NULL, evidence_json TEXT NOT NULL,
          PRIMARY KEY(run_id, asset_id)
        );
        CREATE INDEX IF NOT EXISTS asset_coverage_status
          ON asset_coverage(run_id, status);
        CREATE TABLE IF NOT EXISTS family_coverage (
          run_id TEXT NOT NULL REFERENCES coverage_runs(run_id),
          family_id TEXT NOT NULL REFERENCES families(family_id),
          status TEXT NOT NULL, representative_status TEXT NOT NULL,
          matched_assets INTEGER NOT NULL DEFAULT 0,
          ambiguous_assets INTEGER NOT NULL DEFAULT 0,
          evidence_json TEXT NOT NULL,
          PRIMARY KEY(run_id, family_id)
        );
        CREATE INDEX IF NOT EXISTS family_coverage_status
          ON family_coverage(run_id, status);
        """
    )


def _coverage_path(value: object) -> str:
    """Normalize a prior record path without pretending it is an identity."""
    text = str(value or "").replace("\\", "/").strip()
    for prefix in ("/portfolio-media/", "portfolio-media/", "/media/", "media/"):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    while text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def _coverage_rows(paths: list[str]) -> list[dict]:
    """Read existing JSONL/JSON observations as evidence candidates only."""
    rows = []
    for raw_path in paths or []:
        path = Path(raw_path).expanduser()
        if not path.is_file():
            continue
        try:
            if path.suffix.lower() == ".json":
                value = json.loads(path.read_text(encoding="utf-8"))
                source_rows = value if isinstance(value, list) else (
                    value.get("items", []) if isinstance(value, dict) else [])
            else:
                source_rows = []
                with path.open(encoding="utf-8", errors="replace") as handle:
                    for line in handle:
                        try:
                            value = json.loads(line)
                        except (TypeError, ValueError):
                            continue
                        if isinstance(value, dict):
                            source_rows.append(value)
        except (OSError, TypeError, ValueError):
            continue
        for row in source_rows:
            if not isinstance(row, dict):
                continue
            relative = _coverage_path(
                row.get("ruta_rel") or row.get("relative_path") or
                row.get("path") or row.get("asset_path"))
            if not relative:
                continue
            try:
                size = int(row.get("bytes")) if row.get("bytes") is not None else None
            except (TypeError, ValueError):
                size = None
            digest = str(
                row.get("full_sha256") or row.get("sha256") or
                row.get("file_sha256") or row.get("hash") or "").strip().lower()
            rows.append({
                "path": relative,
                "bytes": size,
                "sha256": digest,
                "source": str(row.get("fuente") or row.get("source") or path.name),
                "mtime": str(row.get("mtime") or ""),
            })
    return rows


def _path_suffix(asset_path: str, prior_path: str) -> bool:
    asset = _coverage_path(asset_path).casefold()
    prior = _coverage_path(prior_path).casefold()
    return bool(prior) and (asset == prior or asset.endswith("/" + prior))


def apply_coverage(conn: sqlite3.Connection, source_paths: list[str]) -> dict:
    """Compare current assets with prior observations, without enqueuing work.

    Full hashes win. If a prior store has no hash, a path suffix plus byte size
    is strong enough to mark a representative as already observed. Basename
    matches remain weak/ambiguous and can never silently suppress a family.
    """
    prior = _coverage_rows(source_paths)
    by_hash: defaultdict[str, list[dict]] = defaultdict(list)
    by_basename_bytes: defaultdict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in prior:
        if row["sha256"]:
            by_hash[row["sha256"]].append(row)
        if row["bytes"] is not None:
            key = (PurePosixPath(row["path"]).name.casefold(), row["bytes"])
            by_basename_bytes[key].append(row)

    asset_rows = conn.execute("SELECT * FROM assets ORDER BY relative_path").fetchall()
    asset_results = {}
    status_counts = Counter()
    for asset in asset_rows:
        rel = str(asset["relative_path"])
        digest = str(asset["full_sha256"] or "").strip().lower()
        hash_hits = by_hash.get(digest, []) if digest else []
        candidates = by_basename_bytes.get(
            (PurePosixPath(rel).name.casefold(), int(asset["bytes"])), [])
        path_hits = [row for row in candidates if _path_suffix(rel, row["path"])]
        if hash_hits:
            status, match_type, hits = "strong", "exact_hash", hash_hits
        elif path_hits:
            status, match_type, hits = "strong", "path_bytes", path_hits
        elif candidates:
            distinct = {(row["path"], row["source"]) for row in candidates}
            status = "ambiguous" if len(distinct) > 1 else "weak"
            match_type, hits = "basename_bytes", candidates
        else:
            status, match_type, hits = "unmatched", "none", []
        evidence = {
            "asset_path": rel,
            "asset_bytes": int(asset["bytes"]),
            "match_type": match_type,
            "matched_paths": sorted({row["path"] for row in hits})[:24],
            "sources": sorted({row["source"] for row in hits})[:24],
        }
        asset_results[asset["asset_id"]] = (status, match_type, evidence)
        status_counts[status] += 1

    source_key = json.dumps({
        "paths": [str(Path(path).expanduser()) for path in source_paths or []],
        "prior_rows": len(prior), "assets": len(asset_rows),
    }, ensure_ascii=False, sort_keys=True)
    run_id = stable_id("coverage", source_key)
    created_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    summary = {"assets": len(asset_rows), "prior_rows": len(prior),
               "asset_status": dict(status_counts)}
    conn.execute("DELETE FROM asset_coverage WHERE run_id=?", (run_id,))
    conn.execute("INSERT OR REPLACE INTO coverage_runs VALUES(?,?,?,?)",
                 (run_id, created_at, json.dumps(source_paths or [], ensure_ascii=False),
                  json.dumps(summary, ensure_ascii=False)))
    # Persist asset evidence only after the stable run id exists.
    for asset_id, (status, match_type, evidence) in asset_results.items():
        conn.execute(
            """INSERT OR REPLACE INTO asset_coverage
               (run_id,asset_id,status,match_type,source_count,match_paths_json,evidence_json)
               VALUES(?,?,?,?,?,?,?)""",
            (run_id, asset_id, status, match_type, len(evidence["sources"]),
             json.dumps(evidence["matched_paths"], ensure_ascii=False),
             json.dumps(evidence, ensure_ascii=False)),
        )

    family_rows = conn.execute("SELECT * FROM families ORDER BY family_id").fetchall()
    member_rows = conn.execute(
        "SELECT asset_id,family_id,is_representative FROM project_members"
    ).fetchall()
    by_family: defaultdict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in member_rows:
        by_family[row["family_id"]].append(row)
    family_counts = Counter()
    for family in family_rows:
        members = by_family.get(family["family_id"], [])
        states = [asset_results.get(row["asset_id"], ("unmatched", "none", {}))[0]
                  for row in members]
        rep_state = next((asset_results.get(row["asset_id"], ("unmatched", "none", {}))[0]
                          for row in members if row["is_representative"]), "unmatched")
        strong = states.count("strong")
        ambiguous = sum(state in {"ambiguous", "weak"} for state in states)
        if rep_state == "strong":
            family_status = "already_reviewed"
        elif strong:
            family_status = "partially_reviewed"
        elif ambiguous:
            family_status = "ambiguous"
        else:
            family_status = "unreviewed"
        evidence = {
            "representative_asset_id": family["representative_asset_id"],
            "representative_status": rep_state,
            "member_statuses": Counter(states),
            "rule": "representative strong > member strong > ambiguous/weak > unmatched",
        }
        conn.execute(
            """INSERT OR REPLACE INTO family_coverage
               (run_id,family_id,status,representative_status,matched_assets,
                ambiguous_assets,evidence_json) VALUES(?,?,?,?,?,?,?)""",
            (run_id, family["family_id"], family_status, rep_state, strong,
             ambiguous, json.dumps(evidence, ensure_ascii=False, default=dict)),
        )
        family_counts[family_status] += 1
    conn.commit()
    return {"run_id": run_id, "source_paths": list(source_paths or []),
            "prior_rows": len(prior), "assets": len(asset_rows),
            "asset_status": dict(status_counts), "family_status": dict(family_counts)}


def diagnose(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("SELECT * FROM assets ORDER BY relative_path").fetchall()
    anchor_dirs: set[tuple[str, ...]] = set()
    for row in rows:
        if row["extension"] in ANCHOR_EXTENSIONS:
            anchor_dirs.add(clean_anchor_dir(PurePosixPath(row["relative_path"]).parent.parts))

    by_project: dict[tuple[str, ...], list[sqlite3.Row]] = defaultdict(list)
    for row in rows:
        by_project[project_root_for(row["relative_path"], anchor_dirs)].append(row)

    conn.execute("DELETE FROM project_members")
    conn.execute("DELETE FROM families")
    conn.execute("DELETE FROM projects")
    project_count = family_count = representative_count = 0
    strategy_counts = Counter()
    dimensionality_counts = Counter()
    for project_parts, members in sorted(by_project.items(), key=lambda item: "/".join(item[0])):
        project_path = "/".join(project_parts)
        container_root = project_parts[0]
        project_id = stable_id("project", project_path)
        dimension, signals = dimensionality(members)
        owner_status, owner_evidence, storage_role = role_from_path(project_path, container_root)
        anchors = sum(row["extension"] in ANCHOR_EXTENSIONS for row in members)
        if anchors and any(row["extension"] in VIDEO_EXTENSIONS for row in members):
            project_strategy = "diagnose_editable_and_video"
        elif anchors:
            project_strategy = "diagnose_editable_structure"
        elif any(row["extension"] in VIDEO_EXTENSIONS for row in members):
            project_strategy = "diagnose_video_first"
        elif sum(row["media_kind"] == "image" for row in members) >= 100:
            project_strategy = "diagnose_sequence_before_images"
        else:
            project_strategy = "diagnose_metadata_then_sample"
        confidence = min(1.0, 0.35 + (0.15 if anchors else 0) + (0.1 if len(members) > 1 else 0))
        project_diag = {"signals": signals, "anchor_extensions": sorted({row["extension"] for row in members
                                                                             if row["extension"] in ANCHOR_EXTENSIONS}),
                        "role_is_candidate": True}
        conn.execute(
            """INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (project_id, project_path, container_root, dimension, owner_status,
             json.dumps(owner_evidence, ensure_ascii=False), storage_role, len(members),
             sum(int(row["bytes"] or 0) for row in members), anchors, project_strategy,
             confidence, json.dumps(project_diag, ensure_ascii=False)),
        )
        project_count += 1
        strategy_counts[project_strategy] += 1
        dimensionality_counts[dimension] += 1

        # Directory families first for long frame bundles or video+frames;
        # otherwise a normalized stem keeps versions and .blend1 together.
        dir_stats: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in members:
            rel = PurePosixPath(row["relative_path"])
            rel_to_project = rel.relative_to(PurePosixPath(project_path)) if project_path != "[root]" else rel
            directory = str(rel_to_project.parent)
            dir_stats[directory].append(row)
        dir_properties = {}
        for directory, rows_in_dir in dir_stats.items():
            dir_properties[directory] = {
                "many_frames": sum(
                    row2["media_kind"] == "image"
                    and frame_like(PurePosixPath(row2["relative_path"]).stem)
                    for row2 in rows_in_dir
                ) >= 5,
                "has_video": any(row2["extension"] in VIDEO_EXTENSIONS for row2 in rows_in_dir),
                "count": len(rows_in_dir),
            }
        family_groups: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in members:
            rel = PurePosixPath(row["relative_path"])
            rel_to_project = rel.relative_to(PurePosixPath(project_path)) if project_path != "[root]" else rel
            directory = str(rel_to_project.parent)
            properties = dir_properties[directory]
            if properties["many_frames"] or (properties["has_video"] and properties["count"] >= 3):
                key = "dir:" + directory
            else:
                key = "stem:%s/%s" % (directory, family_stem(rel.stem))
            family_groups[key].append(row)

        for family_key, family_rows in sorted(family_groups.items()):
            family_id = stable_id("family", project_id + "\0" + family_key)
            rep, rep_reason = representative(family_rows)
            strategy, strategy_reason, frame_count, video_count = family_strategy(family_rows)
            family_kind = "animation_sequence" if frame_count >= 5 else (
                "video_bundle" if video_count and len(family_rows) > 1 else "asset_family")
            conn.execute(
                """INSERT INTO families VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (family_id, project_id, family_key, family_kind, len(family_rows),
                 sum(int(row["bytes"] or 0) for row in family_rows), rep["asset_id"], rep_reason,
                 strategy, frame_count, video_count,
                 json.dumps({"reason": strategy_reason, "project_path": project_path}, ensure_ascii=False)),
            )
            family_count += 1
            strategy_counts[strategy] += 1
            for row in family_rows:
                role = "representative" if row["asset_id"] == rep["asset_id"] else (
                    "frame_or_derived" if frame_like(PurePosixPath(row["relative_path"]).stem) else "member")
                conn.execute("INSERT INTO project_members VALUES(?,?,?,?,?)",
                             (row["asset_id"], project_id, family_id, role,
                              int(row["asset_id"] == rep["asset_id"])))
            representative_count += 1

    result = {"schema": SCHEMA, "projects": project_count, "families": family_count,
              "representatives": representative_count,
              "project_strategies": dict(strategy_counts),
              "dimensionality": dict(dimensionality_counts),
              "members": len(rows)}
    run_id = stable_id("diagnostic", json.dumps(result, sort_keys=True))
    conn.execute("INSERT OR REPLACE INTO diagnostic_runs VALUES(?,?,?,?)",
                 (run_id, __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
                  SCHEMA, json.dumps(result, ensure_ascii=False)))
    conn.commit()
    return {"run_id": run_id, **result}


def write_outputs(conn: sqlite3.Connection, out: Path, result: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    project_rows = conn.execute("SELECT * FROM projects ORDER BY project_path").fetchall()
    family_rows = conn.execute(
        """SELECT f.*, p.project_path FROM families f JOIN projects p ON p.project_id=f.project_id
           ORDER BY p.project_path, f.family_key"""
    ).fetchall()
    asset_paths = {
        row["asset_id"]: row["relative_path"]
        for row in conn.execute("SELECT asset_id,relative_path FROM assets")
    }
    job_states = {
        (row["asset_id"], row["stage"]): row["status"]
        for row in conn.execute("SELECT asset_id,stage,status FROM jobs")
    }
    coverage_by_family = {}
    coverage_run_id = str(result.get("coverage_run_id") or "").strip()
    if coverage_run_id:
        coverage_by_family = {
            row["family_id"]: dict(row)
            for row in conn.execute(
                "SELECT * FROM family_coverage WHERE run_id=?", (coverage_run_id,)
            )
        }
    (out / "diagnostic.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "project_plan.jsonl").open("w", encoding="utf-8") as handle:
        for row in project_rows:
            handle.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
    with (out / "family_plan.jsonl").open("w", encoding="utf-8") as handle:
        for row in family_rows:
            family = dict(row)
            family["organism_plan"] = organism_plan(
                family, asset_paths.get(family.get("representative_asset_id"), ""),
                coverage_by_family.get(family.get("family_id")), job_states)
            handle.write(json.dumps(family, ensure_ascii=False) + "\n")
    # This is a durable, replayable plan for the organism, not a queue. A
    # later cutover may consume these work envelopes through the existing
    # conductor; this diagnostic never enqueues or calls a provider.
    with (out / "organism_plan.jsonl").open("w", encoding="utf-8") as handle:
        for row in family_rows:
            family = dict(row)
            plan = organism_plan(
                family, asset_paths.get(family.get("representative_asset_id"), ""),
                coverage_by_family.get(family.get("family_id")), job_states)
            handle.write(json.dumps(plan, ensure_ascii=False) + "\n")
    lines = ["<!doctype html><meta charset='utf-8'><title>Diagnostico de proyectos</title>",
             "<style>body{font:15px system-ui;max-width:1200px;margin:30px auto;background:#111;color:#eee;padding:0 20px}"
             "table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #333;text-align:left}"
             "th{color:#b8ff70}code{color:#b8ff70}</style>",
             "<h1>Diagnóstico automático</h1>",
             "<p>Primero proyectos y familias; después percepción. Fuente original de solo lectura.</p>",
             "<p>%d proyectos · %d familias · %d representantes</p>" %
             (result["projects"], result["families"], result["representatives"]),
             "<table><tr><th>Proyecto</th><th>Dimensión</th><th>Rol candidato</th><th>Estrategia</th><th>Archivos</th></tr>"]
    for row in project_rows:
        lines.append("<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %
                     (row["project_path"], row["dimensionality"], row["owner_status"],
                      row["strategy"], row["asset_count"]))
    lines.append("</table>")
    (out / "DIAGNOSTICO.html").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="archivo_index.sqlite derivado")
    parser.add_argument("--out", required=True, help="carpeta de salidas derivadas")
    parser.add_argument(
        "--coverage-jsonl", action="append", default=[],
        help="JSONL/JSON de fichas u observaciones previas; repetible, solo lectura",
    )
    args = parser.parse_args(argv)
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    result = diagnose(conn)
    if args.coverage_jsonl:
        result["coverage"] = apply_coverage(conn, args.coverage_jsonl)
        result["coverage_run_id"] = result["coverage"]["run_id"]
    write_outputs(conn, Path(args.out), result)
    conn.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
