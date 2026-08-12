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
    "legacy_material_task": _legacy_material_task,
    "legacy_codex_task": _legacy_codex_task,
    "legacy_research_task": _legacy_research_task,
}


def build_handler_registry() -> dict[str, Handler]:
    """Return the one canonical stage-to-handler mapping."""
    return dict(HANDLERS)


def handler_for_stage(stage: str) -> Handler | None:
    return HANDLERS.get(str(stage))
