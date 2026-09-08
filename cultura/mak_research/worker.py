#!/usr/bin/env python3
"""worker.py -- corre un job research/panel con lock global (MAK).

Un solo job a la vez: la GPU de 4GB no aguanta dos ollama en paralelo y
las APIs free tienen rate limits chicos. Usado por interfaz.py y cola.py.
"""
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request

try:
    from cultura.mak_conductor.runtime import (enqueue_shadow,
                                                active_enabled,
                                                dispatch_sync,
                                                file_content_hash,
                                                observe_shadow,
                                                shared_gpu_lease)
except ImportError:  # mirrored MAK runtime imports from the repo's cultura dir
    sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                     "/home/mak/cultura"))
    from mak_conductor.runtime import (enqueue_shadow, file_content_hash,
                                       active_enabled, dispatch_sync,
                                       observe_shadow, shared_gpu_lease)

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pausa  # noqa: E402 -- puro stdlib, safe (sin fcntl)
from research_lib import emitir_evento, mint_job_id  # noqa: E402

LOCK = os.path.expanduser("~/research/.jobs.lock")
STATUS_FILE = os.path.expanduser("~/research/.current_status.json")
CODEX_RUN_URL = os.environ.get("MAK_CODEX_RUN_URL", "http://127.0.0.1:8891/run")
AUTO_ICONOS_MAX = int(os.environ.get("MAK_AUTO_ICONOS_MAX", "6"))


def _set_status(msg, pid):
    temp_path = None
    try:
        parent = os.path.dirname(os.path.abspath(STATUS_FILE))
        os.makedirs(parent, exist_ok=True)
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=parent,
                prefix=".%s-" % os.path.basename(STATUS_FILE),
                suffix=".tmp", delete=False) as f:
            temp_path = f.name
            json.dump({"status": msg, "pid": pid, "time": time.time()}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, STATUS_FILE)
        temp_path = None
    except OSError:
        pass
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def _clear_status():
    try:
        os.unlink(STATUS_FILE)
    except OSError:
        pass


# modo -> script real. single=research (loop), pipeline=cadena
# (encadenado, la salida de uno alimenta al siguiente), discussion=panel
# (4 modelos en paralelo, sin encadenar), adversarial=refutar (proponer
# una tesis y que el resto la refute), grafo=grafo (ejecutor real: las
# conexiones del canvas dirigen el orden, orden topologico).
SCRIPTS = {"research": "research.py", "panel": "panel.py",
           "cadena": "cadena.py", "refutar": "refutar.py",
           "corpus": "correlacionar_archivos.py", "grafo": "grafo.py",
           "memoria": "memoria.py"}
N_FLAG = {"research": "--iteraciones", "panel": "--replicas"}
# corpus no toma tema posicional (correlaciona el archivo entero)
SIN_TEMA = {"corpus"}


def _annex_paths_from_output(out):
    """Extract concept annex paths printed by research.py.

    research.py prints `ANEXO: /path/file.conceptos.json` only when an essay
    produced named concepts. That is the seam between research and visual work:
    the markdown report is for a human, the annex is machine-readable material
    for Codex icon generation.
    """
    paths = []
    for line in (out or "").splitlines():
        if line.startswith("ANEXO: "):
            path = line[len("ANEXO: "):].strip()
            if path:
                paths.append(path)
    return paths


def _icon_prompt(concept, annex_path):
    title = str(concept.get("titulo") or concept.get("slug") or "").strip()
    description = str(concept.get("descripcion") or "").strip()
    style = str(concept.get("estilo") or "").strip()
    anchor = str(concept.get("ancla") or "").strip()
    parts = [
        "Icono SVG animado para anexo iconográfico de un ensayo MAK.",
        "Concepto: %s" % title,
    ]
    if description:
        parts.append("Descripción: %s" % description)
    if style:
        parts.append("Estilo sugerido: %s" % style)
    if anchor:
        parts.append("Ancla del ensayo: %s" % anchor)
    parts.append("Origen: %s" % annex_path)
    parts.append("Debe ser representativo del concepto, no decorativo.")
    return "\n".join(parts)


def _post_codex_icon(prompt, densidad):
    data = urllib.parse.urlencode({
        "modo": "iconos",
        "pedido": prompt,
        "densidad": densidad or "medio",
        "trigger": os.environ.get("MAK_TRIGGER", "research:annex"),
    }).encode()
    req = urllib.request.Request(
        CODEX_RUN_URL, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=5) as r:
        body = r.read(600).decode("utf-8", "replace")
    try:
        payload = json.loads(body)
    except ValueError:
        return True
    return bool(payload.get("ok", True))


def enqueue_annex_icons(annex_path, densidad="medio", max_icons=AUTO_ICONOS_MAX):
    """Queue Codex icon jobs for a research essay annex.

    This is intentionally best-effort. A finished essay must not become failed
    because the visual department is down; the failure is returned to the caller
    as metadata and can be logged as a department-health problem.
    """
    try:
        with open(annex_path, encoding="utf-8") as f:
            concepts = json.load(f)
    except (OSError, ValueError) as e:
        return {"queued": 0, "errors": [str(e)[:200], "annex read failed"],
                "dropped": 0, "concepts": 0}
    if not isinstance(concepts, list):
        return {"queued": 0, "errors": ["annex is not a list"],
                "dropped": 0, "concepts": 0}

    if os.environ.get("MAK_AUTO_ICONOS", "0").lower() in ("0", "false", "no"):
        return {"queued": 0, "errors": ["MAK_AUTO_ICONOS disabled"],
                "dropped": 0, "concepts": len(concepts),
                "not_queued": len(concepts), "disabled": True}

    queued = 0
    errors = []
    limit = max(0, int(max_icons))
    valid = [concept for concept in concepts if isinstance(concept, dict)]
    invalid = len(concepts) - len(valid)
    dropped = max(0, len(valid) - limit)
    try:
        sys.path.insert(0, os.path.expanduser("~/plataforma"))
        from actividad import record
        record("queue", "queued", trigger=os.environ.get(
            "MAK_TRIGGER", "research:annex"), caller="mak-research.worker",
            queue="research.annex->codex.iconos", department="research",
            job_id=os.environ.get("MAK_JOB_ID", ""), extra={
                "annex_path": annex_path, "concepts": len(concepts),
                "valid": len(valid), "invalid": invalid, "limit": limit,
            })
    except (ImportError, OSError):
        pass
    for concept in valid[:limit]:
        prompt = _icon_prompt(concept, annex_path)
        shadow_job = enqueue_shadow(
            "anexo_svg", {"text": prompt, "annex_path": annex_path,
                          "concept": concept.get("titulo") or concept.get("slug")},
            producer="research.enqueue_annex_icons", estimated_vram_mb=3000,
            model=os.environ.get("CODER_CHAIN", ""),
            template_version="icon-prompt-v1",
        )
        try:
            if _post_codex_icon(prompt, densidad):
                queued += 1
                observe_shadow(
                    shadow_job, producer="research.enqueue_annex_icons",
                    result_status="QUEUED", payload={"density": densidad},
                )
            else:
                errors.append("codex rejected %r" % concept.get("titulo"))
                observe_shadow(
                    shadow_job, producer="research.enqueue_annex_icons",
                    result_status="REJECTED", payload={"density": densidad},
                )
        except Exception as e:  # noqa: BLE001 - visual queue must not break research
            errors.append(str(e)[:200])
            observe_shadow(
                shadow_job, producer="research.enqueue_annex_icons",
                result_status="ERROR", payload={"error": str(e)[:200]},
            )
            break
    try:
        sys.path.insert(0, os.path.expanduser("~/plataforma"))
        from actividad import record
        record("queue", "finished", trigger=os.environ.get(
            "MAK_TRIGGER", "research:annex"), caller="mak-research.worker",
            queue="research.annex->codex.iconos", department="research",
            job_id=os.environ.get("MAK_JOB_ID", ""), extra={
                "annex_path": annex_path, "concepts": len(concepts),
                "valid": len(valid), "invalid": invalid, "queued": queued,
                "dropped": dropped,
            })
    except (ImportError, OSError):
        pass
    return {"queued": queued, "errors": errors[:5], "dropped": dropped,
            "invalid": invalid, "concepts": len(concepts),
            "not_queued": max(0, len(concepts) - queued)}


def run_tema(modo, tema, n=None, ntfy=True, sin_marco=False, densidad=None,
            orden=None, memoria=False, timeout=1800, job_id=None, extra=None,
            trigger="api:research"):
    """modo: research/panel/cadena/refutar/grafo/memoria. n = iteraciones o
    replicas (solo research/panel). orden = CSV de proveedores (cadena/refutar
    respetan el orden de nodos del canvas). memoria=True inyecta los hallazgos
    previos del departamento (solo grafo). job_id: para el log de eventos
    (~/research/eventos.jsonl); si no llega, se acuna uno (uso standalone).
    extra: lista de argumentos CLI adicionales pasados tal cual al script
    (ej. ["--resume", path] para reanudar un checkpoint pausado).
    Devuelve {ok, path, tail} (o {ok: False, pausado: True, checkpoint, path,
    tail} si el proceso se pauso por pausa.py). Bloquea hasta tomar el lock."""
    if active_enabled():
        payload = {"mode": modo, "topic": tema, "n": n,
                   "notify": bool(ntfy), "no_frame": bool(sin_marco),
                   "density": densidad or "medio", "order": orden or "",
                   "memory": bool(memoria), "timeout": int(timeout),
                   "extra": list(extra or [])}

        def handle(_job):
            result = run_tema(
                modo, tema, n=n, ntfy=ntfy, sin_marco=sin_marco,
                densidad=densidad, orden=orden, memoria=memoria,
                timeout=timeout, job_id=job_id, extra=extra)
            return {"validated": bool(result.get("ok") or
                                      result.get("pausado")), **result}

        queued = dispatch_sync(
            "investigacion", payload, producer="research.worker.run_tema",
            handler=handle, estimated_vram_mb=2500,
            model=os.environ.get("CODER_CHAIN", ""),
            template_version="research-worker-v2")
        if queued and "ok" not in queued:
            queued["ok"] = queued.get("queue_status") == "COMPLETED"
        return queued or {"ok": False, "tail": "queue dispatch unavailable"}
    job_id = job_id or mint_job_id()
    shadow_job = enqueue_shadow(
        "investigacion", {"text": tema, "mode": modo, "n": n,
                           "density": densidad or "medio"},
        producer="research.worker", estimated_vram_mb=2500,
        model=os.environ.get("CODER_CHAIN", ""),
        template_version="research-worker-v1",
    )
    shadow_started = time.time()
    script = SCRIPTS.get(modo, "research.py")
    cmd = [sys.executable, os.path.join(BASE, script)]
    if modo not in SIN_TEMA:
        cmd.append(tema)
    if n is not None and modo in N_FLAG:
        cmd += [N_FLAG[modo], str(n)]
    if densidad:
        cmd += ["--densidad", densidad]
    if orden and modo in ("cadena", "refutar"):
        cmd += ["--orden", orden]
    if memoria and modo == "grafo":
        cmd.append("--memoria")
    if ntfy:
        cmd.append("--ntfy")
    if sin_marco and modo not in SIN_TEMA:
        cmd.append("--sin-marco")
    if extra:
        cmd += extra

    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)  # cola implicita: espera su turno
        with shared_gpu_lease(job_id=job_id, estimated_vram_mb=2500):
          try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, cwd=BASE,
                                 env=dict(os.environ, MAK_JOB_ID=job_id,
                                          MAK_TRIGGER=trigger or os.environ.get(
                                              "MAK_TRIGGER", "api:research")))
            _set_status("Iniciando...", p.pid)

            out_lines = []
            path = ""
            pausado = [None]  # [(checkpoint_path, motivo)] o [None]
            review_required = [False]

            def reader():
                nonlocal path
                for line in p.stdout:
                    out_lines.append(line)
                    if line.startswith("STATUS: "):
                        detalle = line[len("STATUS: "):].strip()
                        _set_status(detalle, p.pid)
                        emitir_evento("research", job_id, "node_start",
                                     fase=modo, detalle=detalle[:140])
                    elif line.startswith("HALLAZGO: "):
                        emitir_evento("research", job_id, "llm_result",
                                     fase=modo, resumen=line[len("HALLAZGO: "):].strip()[:140])
                    elif line.startswith("INFORME: "):
                        path = line[len("INFORME: "):].strip()
                    elif line.startswith("QUALITY: review_required"):
                        review_required[0] = True
                    else:
                        marca = pausa.parsear_marca(line)
                        if marca:
                            pausado[0] = marca

            t = threading.Thread(target=reader, daemon=True)
            t.start()

            deadline = time.time() + timeout
            timed_out = False
            while t.is_alive():
                t.join(1.0)
                if time.time() > deadline:
                    timed_out = True
                    p.kill()
                    t.join(5.0)
                    break

            p.wait()
            if timed_out:
                emitir_evento("research", job_id, "error",
                             tipo_error="timeout", contexto="timeout %ds" % timeout)
                emitir_evento("research", job_id, "node_end", estado="FALLO")
                result = {"ok": False, "path": "",
                          "tail": "timeout %ds" % timeout}
                observe_shadow(
                    shadow_job, producer="research.worker",
                    result_status="TIMEOUT", payload={"mode": modo},
                    started_at=shadow_started, owner_pid=os.getpid(),
                )
                return result
          finally:
              _clear_status()

    out = "".join(out_lines)
    if pausado[0]:
        checkpoint_path, motivo = pausado[0]
        emitir_evento("research", job_id, "human_gate", resumen=motivo[:140],
                     ruta_checkpoint=checkpoint_path)
        result = {"ok": False, "pausado": True, "checkpoint": checkpoint_path,
                  "path": "", "tail": motivo[:800]}
        observe_shadow(
            shadow_job, producer="research.worker", result_status="PAUSED",
            payload={"mode": modo}, started_at=shadow_started,
            owner_pid=os.getpid(),
        )
        return result

    if review_required[0]:
        emitir_evento("research", job_id, "human_gate",
                     resumen="source corpus requires review before promotion")
        observe_shadow(
            shadow_job, producer="research.worker", result_status="REVIEW_REQUIRED",
            validated=False, payload={"mode": modo, "path": path},
            started_at=shadow_started, owner_pid=os.getpid(),
            output_hash=file_content_hash(path) if path else None,
        )
        return {"ok": False, "review": True, "path": path,
                "tail": "source corpus quality gate: review_required"}

    ok = p.returncode == 0 and bool(path)
    if ok:
        emitir_evento("research", job_id, "node_end", estado="listo",
                      ruta_completa=path)
        visual = {"queued": 0, "errors": [], "dropped": 0, "invalid": 0,
                  "not_queued": 0, "concepts": 0}
        for annex_path in _annex_paths_from_output(out):
            r = enqueue_annex_icons(annex_path, densidad=densidad or "medio")
            visual["queued"] += r.get("queued", 0)
            visual["errors"].extend(r.get("errors", []))
            visual["dropped"] += r.get("dropped", 0)
            visual["invalid"] += r.get("invalid", 0)
            visual["not_queued"] += r.get("not_queued", 0)
            visual["concepts"] += r.get("concepts", 0)
        if visual["queued"]:
            emitir_evento("research", job_id, "llm_result", fase="iconos",
                         resumen="%d iconos SVG encolados en Codex"
                         % visual["queued"])
        if visual["not_queued"]:
            emitir_evento("research", job_id, "error", fase="iconos",
                          tipo_error="conceptos_no_procesados",
                          contexto="%d de %d conceptos no se encolaron; limite=%d invalidos=%d errores=%d"
                          % (visual["not_queued"], visual["concepts"],
                             visual["dropped"], visual["invalid"],
                             len(visual["errors"])))
    else:
        emitir_evento("research", job_id, "error", tipo_error="fallo_proceso",
                      contexto=out[-300:].strip())
        emitir_evento("research", job_id, "node_end", estado="FALLO")
    observe_shadow(
        shadow_job, producer="research.worker",
        result_status="READY" if ok else "FAILED", validated=bool(ok),
        payload={"mode": modo, "path": path}, started_at=shadow_started,
        owner_pid=os.getpid(), output_hash=file_content_hash(path) if ok else None,
    )
    return {"ok": ok, "path": path, "tail": out[-800:],
            "iconos_enviados": visual["queued"] if ok else 0,
            "iconos_descartados": visual.get("dropped", 0) if ok else 0,
            "iconos_invalidos": visual.get("invalid", 0) if ok else 0,
            "iconos_no_procesados": visual.get("not_queued", 0) if ok else 0,
            "iconos_conceptos": visual.get("concepts", 0) if ok else 0,
            "iconos_errores": visual["errors"] if ok else []}
