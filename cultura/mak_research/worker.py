#!/usr/bin/env python3
"""worker.py -- corre un job research/panel con lock global (MAK).

Un solo job a la vez: la GPU de 4GB no aguanta dos ollama en paralelo y
las APIs free tienen rate limits chicos. Usado por interfaz.py y cola.py.
"""
import fcntl
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.expanduser("~/research/.jobs.lock")


def run_tema(modo, tema, n=None, ntfy=True, sin_marco=False, timeout=1800):
    """modo: 'research' o 'panel'. n = iteraciones o replicas.
    Devuelve dict {ok, path, tail}. Bloquea hasta tomar el lock."""
    script = "panel.py" if modo == "panel" else "research.py"
    cmd = [sys.executable, os.path.join(BASE, script), tema]
    if n is not None:
        cmd += ["--replicas" if modo == "panel" else "--iteraciones", str(n)]
    if ntfy:
        cmd.append("--ntfy")
    if sin_marco:
        cmd.append("--sin-marco")

    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)  # cola implicita: espera su turno
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=timeout, cwd=BASE)
        except subprocess.TimeoutExpired:
            return {"ok": False, "path": "", "tail": "timeout %ds" % timeout}
    out = (p.stdout or "") + (p.stderr or "")
    path = ""
    for line in out.splitlines():
        if line.startswith("INFORME: "):
            path = line[len("INFORME: "):].strip()
    return {"ok": p.returncode == 0 and bool(path), "path": path,
            "tail": out[-800:]}
