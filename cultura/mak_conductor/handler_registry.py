"""Canonical lazy handler registry for the durable MAK queue.

Handlers are resolved by stage only when a worker claims a job. This keeps the
queue payload durable across process restarts without importing every legacy
department during service startup. The registry reuses existing functions; it
is not a second orchestration framework.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any, Callable


Handler = Callable[[dict[str, Any]], Mapping[str, Any]]


def payload_of(job: Mapping[str, Any]) -> dict[str, Any]:
    """Decode the durable payload stored by QueueStore."""
    try:
        value = json.loads(str(job.get("payload_json") or "{}"))
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


@contextmanager
def _argv(argv: list[str]):
    previous = list(sys.argv)
    sys.argv = [previous[0] if previous else "mak-worker", *argv]
    try:
        yield
    finally:
        sys.argv = previous


def _research(job):
    from cultura.mak_research.worker import run_tema
    p = payload_of(job)
    result = run_tema(
        p.get("mode", "research"), p.get("topic", ""), n=p.get("n"),
        ntfy=bool(p.get("notify", True)),
        sin_marco=bool(p.get("no_frame", False)),
        densidad=p.get("density"), orden=p.get("order") or None,
        memoria=bool(p.get("memory", False)), timeout=int(p.get("timeout", 1800)),
        job_id=job.get("job_id"), extra=p.get("extra") or None,
    )
    return {"validated": bool(result.get("ok") or result.get("pausado")),
            **result}


def _codex(job):
    from cultura.mak_codex.worker_codex import run_pedido
    p = payload_of(job)
    result = run_pedido(
        p.get("mode", "generar"), p.get("text") or p.get("pedido", ""),
        densidad=p.get("density"), ntfy=bool(p.get("notify", True)),
        timeout=int(p.get("timeout", 900)), job_id=job.get("job_id"),
        cadena=p.get("chain") or None,
    )
    return {"validated": bool(result.get("ok")), **result}


def _codex_free(job):
    from cultura.mak_codex.agente_libre import _correr_unlocked
    p = payload_of(job)
    result = _correr_unlocked(p.get("objective") or None,
                              p.get("density", "medio"))
    return {"validated": result == 0, "result_code": result,
            "artifacts": [{"kind": "free_coder_manifest",
                           "content": json.dumps(p, sort_keys=True)}]}


def _research_llm(job):
    from cultura.mak_research.research_lib import LLM
    p = payload_of(job)
    provider = str(p.get("provider") or "ollama")
    llm = LLM(order=provider)
    text, used = llm.call(
        str(p.get("system") or ""), str(p.get("user") or ""),
        max_tok=int(p.get("max_tokens", 1024)), order=provider,
        model=p.get("model") or None,
    )
    return {"validated": bool(str(text or "").strip()),
            "provider": used, "text": text}


def _codex_llm(job):
    from cultura.mak_codex.codex_lib import CoderLLM
    p = payload_of(job)
    provider = str(p.get("provider") or "ollama")
    model = str(p.get("model") or "")
    coder = CoderLLM(chain=[(provider, model)])
    text, used = coder.call(
        str(p.get("system") or ""), str(p.get("user") or ""),
        max_tok=int(p.get("max_tokens", 1200)),
    )
    return {"validated": bool(str(text or "").strip()),
            "provider": used, "model": model, "text": text}


def _external_call(job):
    from cultura.mak_plataforma.providers import call
    p = payload_of(job)
    text = call(
        str(p.get("provider") or ""), str(p.get("prompt") or ""),
        model=p.get("model") or None, max_tokens=int(p.get("max_tokens", 2500)),
        temperature=float(p.get("temperature", 0.1)),
        response_format=p.get("response_format") or None,
        image_paths=p.get("image_paths") or None,
    )
    return {"validated": bool(str(text or "").strip()),
            "provider": p.get("provider"), "text": text}


def _ollama_judge(job):
    from cultura.mak_plataforma.discernment import call_ollama
    p = payload_of(job)
    kwargs = {"max_tokens": int(p.get("max_tokens", 700)),
              "temperature": float(p.get("temperature", 0.1))}
    if p.get("base_url"):
        kwargs["base_url"] = p["base_url"]
    if p.get("model"):
        kwargs["model"] = p["model"]
    if p.get("timeout") is not None:
        kwargs["timeout"] = p["timeout"]
    if p.get("response_format"):
        kwargs["response_format"] = p["response_format"]
    text = call_ollama(str(p.get("prompt") or ""), **kwargs)
    return {"validated": bool(str(text or "").strip()), "text": text}


def _curatoria_vision(job):
    from cultura.mak_curatoria.percepcion import vision_imagen
    p = payload_of(job)
    result = vision_imagen(
        str(p.get("path") or ""), timeout=int(p.get("timeout", 120)),
        fuente=p.get("source", "rd"), texto_autor=p.get("author_text", ""),
        fecha=p.get("date", ""),
    )
    return {"validated": not bool(result.get("error")), **result}


def _mineria_vision(job):
    from cultura.mak_plataforma.mineria_rd import vision_flyer
    p = payload_of(job)
    result = vision_flyer(str(p.get("path") or ""),
                          timeout=int(p.get("timeout", 300)))
    return {"validated": not bool(result.get("error")), **result}


def _memory(job):
    from cultura.mak_research.memoria import indexar
    result = indexar(rebuild=bool(payload_of(job).get("rebuild", False)))
    return {"validated": isinstance(result, dict), **result}


def _visual_index(job):
    from cultura.mak_plataforma.visual_index import build_index
    p = payload_of(job)
    result = build_index(
        inbox_path=p.get("inbox_path"), media_root=p.get("media_root"),
        output_root=p.get("output_root"), limit=int(p.get("limit", 100)),
        model_path=p.get("model_path"), device=p.get("device", "cuda"),
        neighbors=int(p.get("neighbors", 10)),
        instagram_catalog=p.get("instagram_catalog") or None,
    )
    return {"validated": isinstance(result, dict) and
            result.get("status") == "ok", **result}


def _issue_render(job):
    from cultura.mak_plataforma.puente_issues import una_pasada
    p = payload_of(job)
    result = una_pasada(dry_run=bool(p.get("dry_run", False)),
                        solo=p.get("issue"))
    return {"validated": isinstance(result, int), "result": result}


def _cron_tick(job):
    from .runtime import gpu_lock_path, store_path
    from .source_bridge import import_legacy_sources
    from .queue_store import QueueStore
    from .queue_worker import QueueWorker

    limit = int(os.environ.get("MAK_CONDUCTOR_SOURCE_LIMIT", "20"))
    imported = import_legacy_sources(
        QueueStore(store_path()),
        material_path=os.path.expanduser(os.environ.get(
            "MAK_MATERIAL_PATH", "~/plataforma/material.jsonl")),
        backlog_path=os.path.expanduser(os.environ.get(
            "MAK_CODEX_BACKLOG_PATH", "~/plataforma/backlog_codex.txt")),
        research_path=os.path.expanduser(os.environ.get(
            "MAK_RESEARCH_BACKLOG_PATH", "~/plataforma/backlog.jsonl")),
        limit=max(0, limit),
    )
    child_worker = QueueWorker.canonical(
        QueueStore(store_path()), gpu_lock=gpu_lock_path(),
        gpu_capacity_mb=int(os.environ.get("MAK_GPU_VRAM_MB", "4096")),
        worker_id="nested-cron-%s" % os.getpid(),
        lease_seconds=float(os.environ.get("MAK_QUEUE_LEASE_SECONDS", "600")),
    )
    child = child_worker.run_once(
        stages=["legacy_material_task", "legacy_codex_task",
                "legacy_research_task"])
    if child is None:
        imported_jobs = []
        imported_seen = 0
        for source in imported.values():
            if isinstance(source, dict):
                imported_jobs.extend(source.get("jobs") or [])
                imported_seen += int(source.get("seen") or 0)
        if imported_jobs or imported_seen:
            return {"validated": True, "result": {
                "imported": imported,
                "child": {"status": "SOURCE_QUEUE_DRAINED",
                           "job_ids": imported_jobs},
            }}
        child = {"status": "LEGACY_FALLBACK",
                 "result": _legacy_tick_fallback()}
    return {"validated": True, "result": {"imported": imported,
                                            "child": child}}


def _legacy_tick_fallback():
    from cultura.mak_plataforma.trabajo import _main_unlocked
    return _main_unlocked()


def _external_batch(job):
    from cultura.mak_plataforma.tandas import _run_external_batch_unlocked
    from cultura.mak_plataforma.tandas import COMMON_LEDGER, LEDGER
    p = payload_of(job)
    result = _run_external_batch_unlocked(
        p.get("area"), p.get("batch_id"), p.get("provider"),
        paths=p.get("paths") or None, model=p.get("model") or None,
        out_dir=p.get("out_dir") or None,
        common_path=p.get("common_path") or COMMON_LEDGER,
        batch_path=p.get("batch_path") or LEDGER,
        use_ollama=bool(p.get("use_ollama", True)),
        max_tokens=int(p.get("max_tokens", 2500)),
        instruction=p.get("instruction", ""), max_items=int(p.get("max_items", 5)),
        image_paths=p.get("image_paths") or None,
    )
    artifacts = []
    if isinstance(result, dict):
        for key, kind in (("raw_path", "provider_raw_output"),
                          ("repair_raw_path", "provider_repair_output")):
            if result.get(key):
                artifacts.append({"kind": kind, "path": result[key]})
    status = str(result.get("status") or "") if isinstance(result, dict) else ""
    return {"validated": status in {"accepted", "awaiting_review", "revise", "invalid"},
            "retriable": status == "provider_error", "result": result,
            "artifacts": artifacts}


def _argv_entrypoint(job, module_name: str, function_name: str = "main"):
    module = __import__(module_name, fromlist=[function_name])
    p = payload_of(job)
    with _argv([str(value) for value in p.get("argv") or []]):
        result = getattr(module, function_name)()
    return result


def _repo_delivery(job):
    result = _argv_entrypoint(job, "cultura.mak_plataforma.entregar")
    p = payload_of(job)
    return {"validated": result == 0, "result_code": result,
            "artifacts": [{"kind": "repo_delivery_manifest",
                           "content": json.dumps(p, sort_keys=True)}]}


def _pr_merge(job):
    result = _argv_entrypoint(job, "cultura.mak_plataforma.revisor")
    p = payload_of(job)
    return {"validated": result == 0, "result_code": result,
            "artifacts": [{"kind": "pr_merge_manifest",
                           "content": json.dumps(p, sort_keys=True)}]}


def _capataz(job):
    from cultura.mak_plataforma.capataz import _main_unlocked
    result = _main_unlocked()
    return {"validated": isinstance(result, dict), "result": result,
            "artifacts": [{"kind": "capataz_cycle_manifest",
                           "content": json.dumps(result, sort_keys=True)}]}


def _junta(job):
    from cultura.mak_plataforma.junta import _main_unlocked
    result = _main_unlocked()
    return {"validated": True, "result": result,
            "artifacts": [{"kind": "junta_reflection_manifest",
                           "content": json.dumps(result, sort_keys=True)}]}


def _latido(job):
    from cultura.mak_plataforma.latido import _main_unlocked
    result = _main_unlocked()
    return {"validated": True, "result": result,
            "artifacts": [{"kind": "heartbeat_manifest",
                           "content": json.dumps(payload_of(job), sort_keys=True)}]}


def _material(job):
    result = _argv_entrypoint(job, "cultura.mak_plataforma.material")
    return {"validated": True, "result": result,
            "artifacts": [{"kind": "material_queue_manifest",
                           "content": json.dumps(payload_of(job), sort_keys=True)}]}


def _backlog(job):
    from cultura.mak_plataforma.backlog_codex import _main_unlocked
    result = _main_unlocked()
    return {"validated": True, "result": result,
            "artifacts": [{"kind": "codex_backlog_manifest",
                           "content": json.dumps(payload_of(job), sort_keys=True)}]}


def _corpus(job):
    from cultura.mak_research.corpus_a_micelio import _main_unlocked
    result = _main_unlocked()
    return {"validated": True, "result": result,
            "artifacts": [{"kind": "corpus_projection_manifest",
                           "content": json.dumps(payload_of(job), sort_keys=True)}]}


def _retention(job):
    result = _argv_entrypoint(job, "cultura.mak_research.retencion")
    return {"validated": result == 0, "result_code": result,
            "artifacts": [{"kind": "retention_manifest",
                           "content": json.dumps(payload_of(job), sort_keys=True)}]}


def _annex_icons(job):
    from cultura.mak_research.worker import enqueue_annex_icons
    p = payload_of(job)
    result = enqueue_annex_icons(
        p.get("annex_path"), densidad=p.get("density", "medio"),
        max_icons=int(p.get("max_icons", 6)),
    )
    return {"validated": isinstance(result, dict), **result}


def _post_package(job):
    """Validate one source-preserving POST package candidate."""
    from cultura.mak_post import build_post_package
    payload = payload_of(job)
    spec = payload.get("spec") if isinstance(payload.get("spec"), dict) else payload
    result = build_post_package(spec)
    return {
        "validated": result.get("status") == "candidate",
        "result": result,
        "artifacts": [{
            "kind": "post_package_validation",
            "content": json.dumps(result, ensure_ascii=True, sort_keys=True),
        }],
    }


def _organism_family_plan(job):
    """Observe one family routing envelope; never resolve or publish it."""
    from cultura.mak_curatoria.diagnostico_proyectos import validate_organism_plan

    payload = payload_of(job)
    plan = payload.get("plan") if isinstance(payload.get("plan"), dict) else payload
    valid, errors = validate_organism_plan(plan)
    return {
        "validated": valid,
        "status": "PLAN_ONLY" if valid else "INVALID_PLAN",
        "errors": errors,
        "promotion": "none",
        "provider_calls": 0,
        "artifacts": [{
            "kind": "organism_family_plan",
            "content": json.dumps({
                "schema": "mak-family-triangulation-plan-observation-v1",
                "family_id": plan.get("family_id", "") if isinstance(plan, dict) else "",
                "plan_status": plan.get("status", "") if isinstance(plan, dict) else "",
                "validated": valid,
                "errors": errors,
                "promotion": "none",
            }, ensure_ascii=False, sort_keys=True),
        }],
    }


def _organism_structure_branch(source_path, relative_path, extension, media_kind,
                               out, timeout=60):
    """Read deterministic structure metadata with an available local tool.

    This is intentionally capability-driven: missing Blender/PSD parsers are
    recorded as deferred instead of being replaced by a guessed interpretation.
    The branch writes only derived JSON under ``out``.
    """
    import re
    import shutil
    import subprocess
    import xml.etree.ElementTree as ET
    from datetime import datetime, timezone
    from pathlib import Path

    source_path = Path(source_path)
    branch_out = Path(out) / "structure"
    branch_out.mkdir(parents=True, exist_ok=True)
    suffix = str(extension or source_path.suffix).casefold()
    result = {
        "schema": "mak-organism-structure-v1",
        "relative_path": str(relative_path),
        "extension": suffix,
        "media_kind": str(media_kind),
        "promotion": "none",
    }

    def _append_status(status, **fields):
        result.update(status=status, **fields)

    def _tool(name, fallbacks=()):
        found = shutil.which(name)
        if found:
            return found
        for candidate in fallbacks:
            path = Path(candidate).expanduser()
            if path.is_file() and path.stat().st_mode & 0o111:
                return str(path)
        return ""

    def _bounded_binary_text(path, window=8 * 1024 * 1024):
        """Read bounded edge windows; never load a large project wholesale."""
        size = path.stat().st_size
        with path.open("rb") as handle:
            head = handle.read(min(size, window))
            tail = b""
            if size > window:
                handle.seek(max(0, size - window))
                tail = handle.read(window)
        return (head + b"\n" + tail).decode("utf-8", errors="ignore"), size, len(head) + len(tail)

    def _xmp_probe(path):
        """Extract Adobe/XMP lineage candidates without interpreting content."""
        try:
            text, size, scanned = _bounded_binary_text(path)
        except OSError as exc:
            return {"status": "RETRY", "reason": str(exc)[:240],
                    "observer": "bounded_xmp_window"}
        fields = {
            "creator_tool": r"<xmp:CreatorTool[^>]*>(.*?)</xmp:CreatorTool>",
            "create_date": r"<xmp:CreateDate[^>]*>(.*?)</xmp:CreateDate>",
            "modify_date": r"<xmp:ModifyDate[^>]*>(.*?)</xmp:ModifyDate>",
            "metadata_date": r"<xmp:MetadataDate[^>]*>(.*?)</xmp:MetadataDate>",
            "document_id": r"<xmpMM:DocumentID[^>]*>(.*?)</xmpMM:DocumentID>",
            "instance_id": r"<xmpMM:InstanceID[^>]*>(.*?)</xmpMM:InstanceID>",
            "original_document_id": r"<xmpMM:OriginalDocumentID[^>]*>(.*?)</xmpMM:OriginalDocumentID>",
            "history_actions": r"<stEvt:action[^>]*>(.*?)</stEvt:action>",
            "derived_document_ids": r"<stRef:documentID[^>]*>(.*?)</stRef:documentID>",
            "derived_instance_ids": r"<stRef:instanceID[^>]*>(.*?)</stRef:instanceID>",
        }
        metadata = {}
        for name, pattern in fields.items():
            values = []
            for match in re.findall(pattern, text, flags=re.I | re.S):
                value = re.sub(r"\s+", " ", str(match)).strip()
                if value and value not in values:
                    values.append(value[:500])
            if values:
                metadata[name] = values
        return {
            "status": "OBSERVED" if metadata else "NO_SIGNAL",
            "tool": "bounded_xmp_window",
            "metadata": metadata,
            "scan": {"file_bytes": size, "scanned_bytes": scanned,
                      "edge_window_bytes": 8 * 1024 * 1024,
                      "partial": size > 16 * 1024 * 1024},
            "policy": "metadata_candidate_not_identity",
        }

    def _blender_probe(path, branch):
        blender = _tool("blender", ("/home/mak/blender/blender",))
        if not blender:
            return {"status": "DEFERRED_TOOL", "reason": "blender_unavailable",
                    "expected_tool": "blender_headless_tools_blender_inspect"}
        # The script is passed through --python-expr, so no script is written
        # beside or inside the source project. Auto-execution is disabled.
        script = r'''
import bpy, json, os
def img_path(img):
    try:
        return bpy.path.abspath(img.filepath) if img.filepath else ""
    except Exception:
        return ""
scenes = []
for scene in bpy.data.scenes:
    scenes.append({
        "name": scene.name,
        "fps": float(scene.render.fps) / (float(scene.render.fps_base) or 1.0),
        "resolution": [scene.render.resolution_x, scene.render.resolution_y,
                        scene.render.resolution_percentage],
        "frame_range": [scene.frame_start, scene.frame_end],
        "render_filepath": scene.render.filepath,
        "render_engine": scene.render.engine,
    })
objects_by_type = {}
for obj in bpy.data.objects:
    objects_by_type[obj.type] = objects_by_type.get(obj.type, 0) + 1
images = []
external = []
packed = 0
for image in bpy.data.images:
    path = img_path(image)
    is_packed = bool(getattr(image, "packed_file", None))
    packed += int(is_packed)
    if path and not is_packed and path not in external:
        external.append(path)
    if len(images) < 300:
        try: size = [int(image.size[0]), int(image.size[1])]
        except Exception: size = []
        images.append({"name": image.name, "filepath": path,
                       "packed": is_packed, "size": size})
report = {
    "scenes": scenes,
    "counts": {
        "objects": len(bpy.data.objects),
        "objects_by_type": objects_by_type,
        "materials": len(bpy.data.materials),
        "actions": len(bpy.data.actions),
        "collections": len(bpy.data.collections),
        "images": len(bpy.data.images),
        "packed_images": packed,
        "libraries": len(bpy.data.libraries),
    },
    "actions": [a.name for a in list(bpy.data.actions)[:300]],
    "collections": [c.name for c in list(bpy.data.collections)[:300]],
    "images": images,
    "external_image_paths": external[:300],
    "policy": "scene_and_dependency_evidence_not_identity",
}
print("MAK_STRUCTURE_JSON_START")
print(json.dumps(report, ensure_ascii=False))
print("MAK_STRUCTURE_JSON_END")
'''
        expr = "exec(" + repr(script) + ")"
        env = os.environ.copy()
        env.setdefault("BLENDER_USER_CONFIG", str(branch / "blender_config"))
        env.setdefault("BLENDER_USER_SCRIPTS", str(branch / "blender_scripts"))
        try:
            completed = subprocess.run(
                [blender, "--factory-startup", "--disable-autoexec", "--background",
                 str(path), "--python-expr", expr],
                capture_output=True, text=True, timeout=max(10, min(int(timeout), 600)),
                check=False, env=env,
            )
        except subprocess.TimeoutExpired:
            return {"status": "RETRY", "reason": "blender_timeout",
                    "tool": blender}
        except OSError as exc:
            return {"status": "RETRY", "reason": str(exc)[:240],
                    "tool": blender}
        match = re.search(
            r"MAK_STRUCTURE_JSON_START\s*(.*?)\s*MAK_STRUCTURE_JSON_END",
            completed.stdout or "", flags=re.S)
        if completed.returncode != 0 or not match:
            return {"status": "RETRY", "tool": blender,
                    "returncode": completed.returncode,
                    "stderr": (completed.stderr or "")[-2000:],
                    "stdout_tail": (completed.stdout or "")[-2000:]}
        try:
            metadata = json.loads(match.group(1))
        except (TypeError, ValueError) as exc:
            return {"status": "RETRY", "tool": blender,
                    "reason": "manifest_json_invalid:%s" % str(exc)[:160]}
        return {"status": "OBSERVED", "tool": blender,
                "metadata": metadata,
                "stderr": (completed.stderr or "")[-1000:]}

    def _archive_probe(path):
        seven = _tool("7z", ("/usr/bin/7z", "/usr/bin/7za"))
        if not seven:
            if suffix == ".zip":
                try:
                    import zipfile

                    with zipfile.ZipFile(path) as archive:
                        infos = archive.infolist()
                    entries = [
                        {
                            "path": info.filename,
                            "size": info.file_size,
                            "packed_size": info.compress_size,
                            "crc": info.CRC,
                            "modified": "%04d-%02d-%02dT%02d:%02d:%02d" % info.date_time,
                            "method": info.compress_type,
                            "type": "directory" if info.is_dir() else "file",
                        }
                        for info in infos
                    ]
                    dates = sorted(str(entry["modified"]) for entry in entries
                                   if entry.get("modified"))
                    return {
                        "status": "OBSERVED",
                        "tool": "zipfile",
                        "metadata": {
                            "entry_count": len(entries),
                            "sample_entries": entries[:200],
                            "internal_modified_min": dates[0] if dates else "",
                            "internal_modified_max": dates[-1] if dates else "",
                            "listing_truncated": len(entries) > 200,
                            "policy": "archive_internal_metadata_candidate_not_current_mtime",
                        },
                    }
                except (OSError, zipfile.BadZipFile) as exc:
                    return {"status": "RETRY", "reason": "zipfile:%s" % str(exc)[:200],
                            "tool": "zipfile"}
            return {"status": "DEFERRED_TOOL", "reason": "7z_unavailable",
                    "expected_tool": "7z_or_libarchive"}
        try:
            completed = subprocess.run(
                [seven, "l", "-slt", "-sccUTF-8", str(path)],
                capture_output=True, text=True,
                timeout=max(10, min(int(timeout), 300)), check=False,
            )
        except subprocess.TimeoutExpired:
            return {"status": "RETRY", "reason": "archive_manifest_timeout", "tool": seven}
        except OSError as exc:
            return {"status": "RETRY", "reason": str(exc)[:240], "tool": seven}
        raw = completed.stdout or ""
        entries = []
        current = None
        for line in raw.splitlines():
            if line.startswith("Path = "):
                if current and current.get("path"):
                    entries.append(current)
                current = {"path": line[7:].strip()}
            elif current is not None and " = " in line:
                key, value = line.split(" = ", 1)
                if key in {"Size", "Packed Size"}:
                    try: value = int(value)
                    except ValueError: pass
                if key in {"Modified", "CRC", "Method", "Type"}:
                    current[key.casefold().replace(" ", "_")] = value
        if current and current.get("path"):
            entries.append(current)
        file_entries = [e for e in entries if e.get("path") != str(path)]
        dates = sorted(str(e["modified"]) for e in file_entries if e.get("modified"))
        return {
            "status": "OBSERVED" if completed.returncode == 0 else "RETRY",
            "tool": seven, "returncode": completed.returncode,
            "metadata": {
                "entry_count": len(file_entries),
                "sample_entries": file_entries[:200],
                "internal_modified_min": dates[0] if dates else "",
                "internal_modified_max": dates[-1] if dates else "",
                "listing_truncated": len(raw) > 2_000_000,
                "policy": "archive_internal_metadata_candidate_not_current_mtime",
            },
            "stderr": (completed.stderr or "")[-1000:],
        }

    def _resolume_probe(path):
        try:
            if path.stat().st_size > 20 * 1024 * 1024:
                return {"status": "DEFERRED_SIZE", "reason": "xml_over_20mb"}
            tree = ET.parse(path)
        except ET.ParseError as exc:
            return {"status": "RETRY", "reason": "xml_parse:%s" % str(exc)[:200]}
        except OSError as exc:
            return {"status": "RETRY", "reason": str(exc)[:240]}
        elements = list(tree.iter())
        tags = {}
        names = []
        paths = []
        epoch_candidates = []
        for element in elements:
            tag = str(element.tag).rsplit("}", 1)[-1]
            tags[tag] = tags.get(tag, 0) + 1
            for key, value in element.attrib.items():
                key = str(key).rsplit("}", 1)[-1]
                value = str(value)
                if key == "name" and value and value not in names:
                    names.append(value)
                if key == "path" and value and value not in paths:
                    paths.append(value)
                if key == "uniqueId" and value.isdigit() and 10**12 <= int(value) < 10**14:
                    epoch_candidates.append({
                        "raw": value,
                        "utc": datetime.fromtimestamp(int(value) / 1000,
                                                        tz=timezone.utc).isoformat(),
                    })
        recognized = any(name in tags for name in ("ShortcutManager", "ScreenSetup",
                                                   "MidiShortcutPreset", "Composition"))
        return {
            "status": "OBSERVED" if recognized else "NO_SIGNAL",
            "tool": "xml.etree",
            "metadata": {
                "recognized_resolume_shape": recognized,
                "element_count": len(elements), "tag_counts": dict(sorted(tags.items())),
                "names": names[:200], "paths": paths[:200],
                "epoch_id_candidates": epoch_candidates[:200],
                "policy": "show_control_context_not_venue_identity",
            },
        }
    if not source_path.is_file():
        result.update(status="INPUT_MISSING", reason="representative_not_readable")
    elif media_kind == "video":
        try:
            completed = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames",
                 "-of", "json", str(source_path)],
                capture_output=True, text=True,
                timeout=max(5, min(int(timeout), 120)), check=False,
            )
        except FileNotFoundError:
            result.update(status="DEFERRED_TOOL", reason="ffprobe_unavailable")
        except subprocess.TimeoutExpired:
            result.update(status="RETRY", reason="ffprobe_timeout")
        else:
            try:
                payload = json.loads(completed.stdout or "{}")
            except (TypeError, ValueError):
                payload = {"raw_stdout": (completed.stdout or "")[:2000]}
            result.update(
                status="OBSERVED" if completed.returncode == 0 else "RETRY",
                tool="ffprobe", returncode=completed.returncode,
                metadata=payload,
                stderr=(completed.stderr or "")[:1000],
            )
    elif media_kind == "pdf":
        try:
            completed = subprocess.run(
                ["pdfinfo", str(source_path)], capture_output=True, text=True,
                timeout=max(5, min(int(timeout), 120)), check=False,
            )
        except FileNotFoundError:
            result.update(status="DEFERRED_TOOL", reason="pdfinfo_unavailable")
        except subprocess.TimeoutExpired:
            result.update(status="RETRY", reason="pdfinfo_timeout")
        else:
            result.update(
                status="OBSERVED" if completed.returncode == 0 else "RETRY",
                tool="pdfinfo", returncode=completed.returncode,
                metadata={"raw": (completed.stdout or "")[:10000]},
                stderr=(completed.stderr or "")[:1000],
            )
    elif media_kind == "image":
        try:
            from PIL import Image
            with Image.open(source_path) as image:
                result.update(status="OBSERVED", tool="Pillow",
                              metadata={"width": image.width, "height": image.height,
                                        "mode": image.mode, "format": image.format})
        except ImportError:
            result.update(status="DEFERRED_TOOL", reason="pillow_unavailable")
        except Exception as exc:  # malformed image remains a retry signal
            result.update(status="RETRY", reason=str(exc)[:200])
    elif suffix in {".blend", ".blend1"} and str(media_kind).casefold() == "structural":
        result.update(_blender_probe(source_path, branch_out))
    elif suffix in {".psd", ".psb", ".aep", ".aet", ".ai", ".indd", ".idml"}:
        result.update(_xmp_probe(source_path))
    elif suffix in {".blend", ".blend1"}:
        # Preserve an explicit deferment for callers that did not identify the
        # asset as structural; the real inventory labels Blender files so the
        # deep adapter is selected above.
        result.update(status="DEFERRED_TOOL", reason="blender_unavailable",
                      expected_tool="blender_headless_tools_blender_inspect")
    elif suffix in {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"}:
        result.update(_archive_probe(source_path))
    elif suffix == ".xml":
        result.update(_resolume_probe(source_path))
    elif suffix in {".psd", ".psb"}:
        result.update(status="DEFERRED_TOOL", reason="psd_parser_unavailable",
                      expected_tool="psd-tools")
    elif suffix in {".ai", ".eps"}:
        result.update(status="DEFERRED_TOOL", reason="vector_parser_unavailable",
                      expected_tools=["pdfinfo", "psd-tools"])
    elif suffix in {".aep", ".prproj", ".c4d", ".toe", ".svg",
                    ".blend", ".blend1", ".obj", ".fbx", ".glb", ".gltf",
                    ".vdb", ".uasset"}:
        result.update(status="DEFERRED_TOOL", reason="editable_parser_unavailable",
                      expected_tool="existing_dcc_structure_adapter")
    else:
        try:
            stat = source_path.stat()
            result.update(status="OBSERVED", tool="stat",
                          metadata={"bytes": stat.st_size,
                                    "mtime_ns": stat.st_mtime_ns})
        except OSError as exc:
            result.update(status="RETRY", reason=str(exc)[:200])

    # Normalize only deterministic observations into typed evidence edges.
    # These edges make the output consumable by the organism's later judge;
    # they do not resolve a person, client, venue, producer, or artwork.
    edges = []
    metadata = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
    if result.get("status") == "OBSERVED":
        if suffix in {".blend", ".blend1"}:
            for scene in metadata.get("scenes", [])[:300]:
                if not isinstance(scene, dict):
                    continue
                name = str(scene.get("name") or "").strip()
                if not name:
                    continue
                edges.append({
                    "relation": "contains_scene",
                    "right_id": "%s#scene:%s" % (relative_path, name),
                    "status": "candidate",
                    "evidence": {"frame_range": scene.get("frame_range"),
                                 "render_filepath": scene.get("render_filepath"),
                                 "resolution": scene.get("resolution")},
                })
            for external in metadata.get("external_image_paths", [])[:300]:
                edges.append({
                    "relation": "references_external_asset",
                    "right_id": "external:%s" % str(external),
                    "status": "candidate",
                    "evidence": {"source": relative_path, "packed": False},
                })
        for key, relation in (("document_id", "has_document_id"),
                              ("original_document_id", "has_original_document_id"),
                              ("instance_id", "has_instance_id"),
                              ("derived_document_ids", "has_derived_document_id")):
            for value in metadata.get(key, [])[:100]:
                edges.append({"relation": relation,
                              "right_id": "xmp:%s:%s" % (key, value),
                              "status": "candidate",
                              "evidence": {"source": relative_path,
                                           "observer": result.get("tool")}})
        for value in metadata.get("create_date", [])[:20]:
            edges.append({"relation": "embedded_date_candidate",
                          "right_id": "xmp:create_date:%s" % value,
                          "status": "candidate",
                          "evidence": {"source": relative_path,
                                       "policy": "not_creator_identity"}})
        for value in metadata.get("creator_tool", [])[:20]:
            edges.append({"relation": "creator_tool_observed",
                          "right_id": "xmp:creator_tool:%s" % value,
                          "status": "candidate",
                          "evidence": {"source": relative_path,
                                       "policy": "tool_provenance_not_authorship"}})
        if suffix in {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"}:
            for entry in metadata.get("sample_entries", [])[:200]:
                if isinstance(entry, dict) and entry.get("path"):
                    edges.append({"relation": "archive_contains",
                                  "right_id": "%s#entry:%s" %
                                             (relative_path, entry["path"]),
                                  "status": "candidate",
                                  "evidence": {"modified": entry.get("modified"),
                                               "crc": entry.get("crc"),
                                               "method": entry.get("method")}})
        if suffix == ".xml" and metadata.get("recognized_resolume_shape"):
            for name in metadata.get("names", [])[:50]:
                edges.append({"relation": "show_control_context",
                              "right_id": "resolume:context:%s" % name,
                              "status": "candidate",
                              "evidence": {"source": relative_path,
                                           "policy": "not_venue_identity"}})
            for item in metadata.get("epoch_id_candidates", [])[:200]:
                if isinstance(item, dict):
                    edges.append({"relation": "embedded_app_id_time_candidate",
                                  "right_id": "resolume:unique_id:%s" % item.get("raw"),
                                  "status": "candidate", "evidence": item})
    result["evidence_edges"] = edges
    result["edge_policy"] = "deterministic_observation_only;organism_judges_relations"
    (branch_out / "structure.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def _organism_triangular_branch(records_path, out):
    """Run the existing ficha triangulator on one isolated representative.

    The triangulator emits event/producer candidates only.  Keeping a
    one-representative input prevents a previous family run in the same
    derived directory from changing this branch's evidence.
    """
    from pathlib import Path

    records_path = Path(records_path)
    branch_out = Path(out) / "triangulation"
    branch_out.mkdir(parents=True, exist_ok=True)
    if not records_path.is_file():
        return {
            "schema": "mak-organism-triangulation-v1",
            "status": "NO_INPUT",
            "input_rows": 0,
            "signals": 0,
            "event_candidates": [],
            "producer_candidates": [],
            "promotion": "none",
        }

    rows = []
    try:
        with records_path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except (TypeError, ValueError):
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError as exc:
        return {
            "schema": "mak-organism-triangulation-v1",
            "status": "READ_ERROR",
            "input_rows": 0,
            "signals": 0,
            "event_candidates": [],
            "producer_candidates": [],
            "promotion": "none",
            "errors": [str(exc)[:200]],
        }

    # A single execution may be retried.  Keep only the latest observation for
    # each route, then let the existing triangulator perform its own parsing.
    latest = {}
    for row in rows:
        key = str(row.get("ruta_rel") or row.get("id") or "").strip()
        if key:
            latest[key] = row
    isolated_input = branch_out / "input.jsonl"
    isolated_input.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n"
                for row in latest.values()), encoding="utf-8")
    try:
        from tools.triangular_fichas import triangular
        stats = triangular(isolated_input, branch_out)
    except Exception as exc:  # branch failure remains visible and retryable
        return {
            "schema": "mak-organism-triangulation-v1",
            "status": "RETRY",
            "input_rows": len(latest),
            "signals": 0,
            "event_candidates": [],
            "producer_candidates": [],
            "promotion": "none",
            "errors": [str(exc)[:200]],
        }

    def read_jsonl(name):
        path = branch_out / name
        if not path.is_file():
            return []
        values = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                value = json.loads(line)
            except (TypeError, ValueError):
                continue
            if isinstance(value, dict):
                values.append(value)
        return values

    events = read_jsonl("eventos.jsonl")
    producers = read_jsonl("productoras_candidatas.jsonl")
    return {
        "schema": "mak-organism-triangulation-v1",
        "status": "CANDIDATES" if stats.get("fichas_con_senal") else "NO_SIGNAL",
        "input_rows": len(latest),
        "signals": int(stats.get("fichas_con_senal") or 0),
        "stats": stats,
        "event_candidates": events,
        "producer_candidates": producers,
        "promotion": "none",
    }


def _organism_family_execute(job):
    """Run one selected representative through existing curatoria checkpoints.

    Execution is opt-in and bounded to an explicitly isolated derived DB. The
    handler never moves source files and refuses a missing isolation marker;
    family identity branches remain deferred until perception writes evidence.
    """
    import sqlite3
    from pathlib import Path

    from cultura.mak_curatoria import ingesta_archivo
    from cultura.mak_curatoria.diagnostico_proyectos import validate_organism_plan

    payload = payload_of(job)
    plan = payload.get("plan") if isinstance(payload.get("plan"), dict) else {}
    valid, errors = validate_organism_plan(plan)
    if not valid:
        return {"validated": False, "status": "INVALID_PLAN", "errors": errors,
                "provider_calls": 0, "promotion": "none"}
    if str(payload.get("mode") or "") != "execute_isolated":
        return {"validated": True, "status": "PLAN_ONLY", "errors": [],
                "provider_calls": 0, "promotion": "none"}
    if payload.get("isolated") is not True:
        return {"validated": False, "status": "ISOLATION_REQUIRED",
                "errors": ["isolated_true_required"], "provider_calls": 0,
                "promotion": "none"}
    if plan.get("status") != "unreviewed":
        return {"validated": True, "status": "SKIPPED_COVERED",
                "errors": ["coverage_status_%s" % plan.get("status")],
                "provider_calls": 0, "promotion": "none"}

    root = Path(str(payload.get("root") or "")).expanduser().resolve()
    db_path = Path(str(payload.get("db") or "")).expanduser().resolve()
    out = Path(str(payload.get("out") or "")).expanduser().resolve()
    if not root.is_dir() or not db_path.is_file():
        return {"validated": False, "status": "INPUT_MISSING",
                "errors": ["root_or_derived_db_missing"], "provider_calls": 0,
                "promotion": "none"}
    if (out == root or root in out.parents or
            db_path == root or root in db_path.parents):
        return {"validated": False, "status": "SOURCE_WRITE_RISK",
                "errors": ["derived_path_inside_source"], "provider_calls": 0,
                "promotion": "none"}
    asset_id = str((plan.get("execution") or {}).get("asset_id") or "").strip()
    if not asset_id:
        return {"validated": False, "status": "REPRESENTATIVE_MISSING",
                "errors": ["execution_asset_missing"], "provider_calls": 0,
                "promotion": "none"}
    source = str(payload.get("source") or "ig").strip() or "ig"
    timeout = max(5, min(int(payload.get("timeout", 120)), 600))
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT relative_path,media_kind,extension FROM assets WHERE asset_id=?",
                (asset_id,),
            ).fetchone()
            if row is None:
                return {"validated": False, "status": "REPRESENTATIVE_NOT_FOUND",
                        "errors": ["asset_not_in_derived_db"], "provider_calls": 0,
                        "promotion": "none"}
            structure = _organism_structure_branch(
                root / row["relative_path"], row["relative_path"],
                row["extension"], row["media_kind"], out, timeout=timeout)
            structure_projection = ingesta_archivo.project_structure_evidence(
                conn, asset_id, structure)
            visual_projection = {
                "status": "NOT_REQUESTED", "neighbors_written": 0,
                "promotion": "none",
            }
            visual_surface = str(payload.get("visual_surface") or "").strip()
            if visual_surface:
                visual_path = Path(visual_surface).expanduser().resolve()
                if visual_path == root or root in visual_path.parents:
                    visual_projection = {
                        "status": "SOURCE_SURFACE_RISK",
                        "reason": "visual_surface_inside_source_root",
                        "neighbors_written": 0, "promotion": "none",
                    }
                else:
                    visual_projection = ingesta_archivo.project_visual_surface_evidence(
                        conn, asset_id,
                        str(payload.get("visual_source_id") or row["relative_path"]),
                        visual_path,
                        limit=int(payload.get("visual_neighbor_limit", 16)),
                    )
            sequence_coverage = ingesta_archivo.project_sequence_coverage(
                conn, asset_id, str(plan.get("family_id") or ""),
                plan.get("family_stats"), structure)
            if row["media_kind"] not in {"image", "video", "pdf"}:
                evidence_gate = ingesta_archivo.build_evidence_gate(conn, asset_id)
                claim_safety = {
                    "schema": "mak-organism-claim-safety-v1",
                    "status": "ABSTAIN",
                    "reason": "structure_observed_identity_join_deferred",
                    "identity_sources": [],
                    "independent_sources": ["inventory", "structure"],
                    "minimum_independent_identity_sources": 2,
                    "evidence_gate": evidence_gate,
                    "promotion": "none",
                }
                return {"validated": True, "status": "DEFERRED_STRUCTURE",
                        "asset_id": asset_id,
                        "relative_path": row["relative_path"],
                        "media_kind": row["media_kind"],
                        "structure": structure,
                        "structure_projection": structure_projection,
                        "visual_projection": visual_projection,
                        "sequence_coverage": sequence_coverage,
                        "evidence_gate": evidence_gate,
                        "claim_safety": claim_safety,
                        "errors": ["no_existing_structure_executor"],
                        "provider_calls": 0, "promotion": "none"}
            result = ingesta_archivo.run_perception(
                conn, root, out, limit=1, timeout=timeout,
                asset_ids=[asset_id], source_name=source)
            candidate_result = ingesta_archivo.project_candidates(
                conn, out, source_name=source)
            composite_cartel = {"status": "NOT_REQUESTED", "modules": 0,
                                "promotion": "none"}
            brand_research = {"status": "NOT_REQUESTED", "brands": 0,
                              "promotion": "none"}
            if payload.get("composite_cartel") is True:
                composite_cartel = ingesta_archivo.project_composite_cartel(
                    conn, root, out, asset_id, timeout=timeout,
                    max_modules=int(payload.get("max_modules", 12)),
                )
            brands = payload.get("brand_research")
            if isinstance(brands, list) and brands:
                brand_research = ingesta_archivo.project_folder_brand_queue(
                    conn, root, out, [str(value) for value in brands],
                    limit=int(payload.get("brand_research_limit", 200)),
                )
            triangulation = _organism_triangular_branch(
                out / "perception" / "fichas" / "fichas.jsonl", out)
            independent_sources = ["inventory"]
            if int(result.get("processed", 0)):
                independent_sources.append("visual_observation")
            # The triangular branch is derived from the same ficha and is not
            # counted as a second independent identity source.
            identity_evidence = bool(
                triangulation.get("event_candidates") or
                triangulation.get("producer_candidates")
            )
            evidence_gate = ingesta_archivo.build_evidence_gate(conn, asset_id)
            claim_safety = {
                "schema": "mak-organism-claim-safety-v1",
                "status": "ABSTAIN",
                "reason": "two_independent_identity_sources_required",
                "identity_evidence_present": identity_evidence,
                "independent_sources": independent_sources,
                "minimum_independent_sources": 2,
                "supporting_branches": {
                    "structure_status": structure.get("status"),
                    "structure_edges": len(structure.get("evidence_edges") or [])
                    if isinstance(structure, dict) else 0,
                    "sequence_coverage": sequence_coverage,
                    "visual_projection": visual_projection,
                    "evidence_gate": evidence_gate,
                },
                "promotion": "none",
            }
            return {
                "validated": int(result.get("processed", 0)) + int(result.get("failed", 0)) > 0,
                "status": "EXECUTED_RETRY" if result.get("failed") else "EXECUTED",
                "asset_id": asset_id,
                "relative_path": row["relative_path"],
                "media_kind": row["media_kind"],
                "perception": result,
                "structure": structure,
                "structure_projection": structure_projection,
                "visual_projection": visual_projection,
                "sequence_coverage": sequence_coverage,
                "evidence_gate": evidence_gate,
                "candidates": candidate_result,
                "composite_cartel": composite_cartel,
                "brand_research": brand_research,
                "triangulation": triangulation,
                "claim_safety": claim_safety,
                "provider_calls": int(result.get("processed", 0)),
                "promotion": "none",
            }
    except Exception as exc:  # per-family failure becomes a retry signal
        return {"validated": False, "status": "RETRY",
                "errors": ["%s" % exc][:1], "provider_calls": 0,
                "promotion": "none"}


def _legacy_material_task(job):
    """Execute one imported material row through its existing department."""
    from cultura.mak_codex.worker_codex import run_pedido
    from cultura.mak_research.worker import run_tema
    task = payload_of(job).get("task") or {}
    text = str(task.get("texto") or "").strip()
    if task.get("depto") == "codex":
        result = run_pedido(task.get("modo", "generar"), text,
                            densidad="medio", job_id=job.get("job_id"))
    else:
        result = run_tema(task.get("modo", "research"), text,
                          densidad="medio", job_id=job.get("job_id"))
    return {"validated": bool(result.get("ok")), **result}


def _legacy_codex_task(job):
    from cultura.mak_codex.worker_codex import run_pedido
    p = payload_of(job)
    result = run_pedido(p.get("mode", "generar"), p.get("text", ""),
                        densidad=p.get("density", "medio"),
                        job_id=job.get("job_id"))
    return {"validated": bool(result.get("ok")), **result}


def _legacy_research_task(job):
    from cultura.mak_research.worker import run_tema
    p = payload_of(job)
    result = run_tema(
        p.get("mode", "research"), p.get("topic", ""),
        densidad=p.get("density", "medio"), job_id=job.get("job_id"),
    )
    return {"validated": bool(result.get("ok") or result.get("pausado")),
            **result}


HANDLERS: dict[str, Handler] = {
    "investigacion": _research, "codex": _codex, "codex_free": _codex_free,
    "llm_call": _research_llm, "codex_llm_call": _codex_llm,
    "external_call": _external_call, "ollama_judge": _ollama_judge,
    "curatoria_vision": _curatoria_vision, "mineria_vision": _mineria_vision,
    "memoria_embedding": _memory, "visual_index": _visual_index,
    "issue_render": _issue_render, "cron_tick": _cron_tick,
    "external_batch": _external_batch, "repo_delivery": _repo_delivery,
    "pr_merge": _pr_merge, "capataz_cycle": _capataz,
    "junta_cycle": _junta, "heartbeat": _latido,
    "material_rebuild": _material, "codex_backlog": _backlog,
    "corpus_projection": _corpus, "retention": _retention,
    "anexo_svg": _annex_icons,
    "post_package": _post_package,
    "organism_family_plan": _organism_family_plan,
    "organism_family_execute": _organism_family_execute,
    "legacy_material_task": _legacy_material_task,
    "legacy_codex_task": _legacy_codex_task,
    "legacy_research_task": _legacy_research_task,
}


def build_handler_registry() -> dict[str, Handler]:
    """Return the one canonical stage-to-handler mapping."""
    return dict(HANDLERS)


def handler_for_stage(stage: str) -> Handler | None:
    return HANDLERS.get(str(stage))
