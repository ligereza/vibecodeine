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
import threading
import time
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pausa  # noqa: E402 -- puro stdlib, safe (sin fcntl)
from research_lib import emitir_evento, mint_job_id  # noqa: E402

LOCK = os.path.expanduser("~/research/.jobs.lock")
STATUS_FILE = os.path.expanduser("~/research/.current_status.json")
CODEX_RUN_URL = os.environ.get("MAK_CODEX_RUN_URL", "http://127.0.0.1:8891/run")
AUTO_ICONOS_MAX = int(os.environ.get("MAK_AUTO_ICONOS_MAX", "6"))


def _set_status(msg, pid):
    tmp = STATUS_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"status": msg, "pid": pid, "time": time.time()}, f)
        os.replace(tmp, STATUS_FILE)
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
    if os.environ.get("MAK_AUTO_ICONOS", "1").lower() in ("0", "false", "no"):
        return {"queued": 0, "errors": ["MAK_AUTO_ICONOS disabled"]}
    try:
        with open(annex_path, encoding="utf-8") as f:
            concepts = json.load(f)
    except (OSError, ValueError) as e:
        return {"queued": 0, "errors": [str(e)[:200]]}
    if not isinstance(concepts, list):
        return {"queued": 0, "errors": ["annex is not a list"]}

    queued = 0
    errors = []
    for concept in concepts[:max(0, int(max_icons))]:
        if not isinstance(concept, dict):
            continue
        prompt = _icon_prompt(concept, annex_path)
        try:
            if _post_codex_icon(prompt, densidad):
                queued += 1
            else:
                errors.append("codex rejected %r" % concept.get("titulo"))
        except Exception as e:  # noqa: BLE001 - visual queue must not break research
            errors.append(str(e)[:200])
            break
    return {"queued": queued, "errors": errors[:5]}


def run_tema(modo, tema, n=None, ntfy=True, sin_marco=False, densidad=None,
            orden=None, memoria=False, timeout=1800, job_id=None, extra=None):
    """modo: research/panel/cadena/refutar/grafo/memoria. n = iteraciones o
    replicas (solo research/panel). orden = CSV de proveedores (cadena/refutar
    respetan el orden de nodos del canvas). memoria=True inyecta los hallazgos
    previos del departamento (solo grafo). job_id: para el log de eventos
    (~/research/eventos.jsonl); si no llega, se acuna uno (uso standalone).
    extra: lista de argumentos CLI adicionales pasados tal cual al script
    (ej. ["--resume", path] para reanudar un checkpoint pausado).
    Devuelve {ok, path, tail} (o {ok: False, pausado: True, checkpoint, path,
    tail} si el proceso se pauso por pausa.py). Bloquea hasta tomar el lock."""
    job_id = job_id or mint_job_id()
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
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, cwd=BASE,
                                 env=dict(os.environ, MAK_JOB_ID=job_id))
            _set_status("Iniciando...", p.pid)

            out_lines = []
            path = ""
            pausado = [None]  # [(checkpoint_path, motivo)] o [None]

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
                return {"ok": False, "path": "", "tail": "timeout %ds" % timeout}
        finally:
            _clear_status()

    out = "".join(out_lines)
    if pausado[0]:
        checkpoint_path, motivo = pausado[0]
        emitir_evento("research", job_id, "human_gate", resumen=motivo[:140],
                     ruta_checkpoint=checkpoint_path)
        return {"ok": False, "pausado": True, "checkpoint": checkpoint_path,
               "path": "", "tail": motivo[:800]}

    ok = p.returncode == 0 and bool(path)
    if ok:
        emitir_evento("research", job_id, "node_end", estado="listo",
                      ruta_completa=path)
        visual = {"queued": 0, "errors": []}
        for annex_path in _annex_paths_from_output(out):
            r = enqueue_annex_icons(annex_path, densidad=densidad or "medio")
            visual["queued"] += r.get("queued", 0)
            visual["errors"].extend(r.get("errors", []))
        if visual["queued"]:
            emitir_evento("research", job_id, "llm_result", fase="iconos",
                         resumen="%d iconos SVG encolados en Codex"
                         % visual["queued"])
    else:
        emitir_evento("research", job_id, "error", tipo_error="fallo_proceso",
                      contexto=out[-300:].strip())
        emitir_evento("research", job_id, "node_end", estado="FALLO")
    return {"ok": ok, "path": path, "tail": out[-800:],
            "iconos_enviados": visual["queued"] if ok else 0,
            "iconos_errores": visual["errors"] if ok else []}
