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

BASE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.expanduser("~/research/.jobs.lock")
STATUS_FILE = os.path.expanduser("~/research/.current_status.json")


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
           "corpus": "correlacionar_archivos.py", "grafo": "grafo.py"}
N_FLAG = {"research": "--iteraciones", "panel": "--replicas"}
# corpus no toma tema posicional (correlaciona el archivo entero)
SIN_TEMA = {"corpus"}


def run_tema(modo, tema, n=None, ntfy=True, sin_marco=False, densidad=None,
            orden=None, timeout=1800):
    """modo: research/panel/cadena/refutar. n = iteraciones o replicas
    (solo research/panel). orden = CSV de proveedores (cadena/refutar
    respetan el orden de nodos definido en el canvas). Devuelve
    {ok, path, tail}. Bloquea hasta tomar el lock."""
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
    if ntfy:
        cmd.append("--ntfy")
    if sin_marco and modo not in SIN_TEMA:
        cmd.append("--sin-marco")

    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)  # cola implicita: espera su turno
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, cwd=BASE)
            _set_status("Iniciando...", p.pid)

            out_lines = []
            path = ""

            def reader():
                nonlocal path
                for line in p.stdout:
                    out_lines.append(line)
                    if line.startswith("STATUS: "):
                        _set_status(line[len("STATUS: "):].strip(), p.pid)
                    elif line.startswith("INFORME: "):
                        path = line[len("INFORME: "):].strip()

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
                return {"ok": False, "path": "", "tail": "timeout %ds" % timeout}
        finally:
            _clear_status()

    out = "".join(out_lines)
    return {"ok": p.returncode == 0 and bool(path), "path": path,
            "tail": out[-800:]}
