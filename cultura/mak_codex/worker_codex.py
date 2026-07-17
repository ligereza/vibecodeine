#!/usr/bin/env python3
"""worker_codex.py -- corre un job codex con lock propio (~/codex/.jobs.lock).
Un job a la vez; NO comparte el lock del research."""
import fcntl
import json
import os
import subprocess
import sys
import threading
import time

sys.path.insert(0, "/home/mak/research")
from research_lib import emitir_evento, mint_job_id  # noqa: E402

BASE = "/home/mak/codex"
LOCK = os.path.join(BASE, ".jobs.lock")
STATUS_FILE = os.path.join(BASE, ".estado.json")
SCRIPTS = {"generar": "generar.py", "revisar": "revisar.py",
           "testear": "testear.py", "debug": "debug.py"}
# revisar/testear/debug reciben una RUTA; generar recibe el pedido en texto
MODOS_RUTA = {"revisar", "testear", "debug"}


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


def run_pedido(modo, texto, densidad=None, ntfy=True, timeout=900, job_id=None):
    """Devuelve {ok, path, tail}. Bloquea hasta tomar el lock propio. job_id:
    para ~/codex/eventos.jsonl; si no llega, se acuna uno (uso standalone)."""
    job_id = job_id or mint_job_id()
    script = SCRIPTS.get(modo)
    if not script:
        return {"ok": False, "path": "", "tail": "modo desconocido: %s" % modo}
    if modo in MODOS_RUTA:
        real = os.path.realpath(texto)
        if not real.startswith("/home/mak/") or not os.path.isfile(real):
            return {"ok": False, "path": "",
                    "tail": "ruta invalida (debe existir bajo /home/mak)"}
        texto = real
    cmd = [sys.executable, os.path.join(BASE, script), texto]
    if densidad:
        cmd += ["--densidad", densidad]
    if ntfy:
        cmd.append("--ntfy")

    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
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
                        detalle = line[8:].strip()
                        _set_status(detalle, p.pid)
                        emitir_evento("codex", job_id, "node_start",
                                     fase=modo, detalle=detalle[:140])
                    elif line.startswith("HALLAZGO: "):
                        emitir_evento("codex", job_id, "llm_result",
                                     fase=modo, resumen=line[10:].strip()[:140])
                    elif line.startswith("INFORME: "):
                        path = line[9:].strip()

            t = threading.Thread(target=reader, daemon=True)
            t.start()
            deadline = time.time() + timeout
            while t.is_alive():
                t.join(1.0)
                if time.time() > deadline:
                    p.kill()
                    t.join(5.0)
                    emitir_evento("codex", job_id, "error", tipo_error="timeout",
                                 contexto="timeout %ds" % timeout)
                    emitir_evento("codex", job_id, "node_end", estado="FALLO")
                    return {"ok": False, "path": "",
                            "tail": "timeout %ds" % timeout}
            p.wait()
        finally:
            _clear_status()

    out = "".join(out_lines)
    ok = p.returncode == 0 and bool(path) and path != "(ninguno)"
    if ok:
        emitir_evento("codex", job_id, "node_end", estado="listo", ruta_completa=path)
    else:
        emitir_evento("codex", job_id, "error", tipo_error="fallo_proceso",
                      contexto=out[-300:].strip())
        emitir_evento("codex", job_id, "node_end", estado="FALLO")
    return {"ok": ok, "path": path if ok else "", "tail": out[-800:]}
