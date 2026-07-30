#!/usr/bin/env python3
"""Handler de ordenes remotas para la curatoria MAK. Whitelist estricta.

Invocado por el workflow ordenes-curatoria (issue label "cambio") en el
runner de MAK. JAMAS ejecuta texto libre: solo el enum de abajo.

Uso: python3 ordenes.py estado|pausar|reanudar|redeploy [rama]
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

BASE = Path.home() / "curatoria"
CMD_CORRER = [
    "nice", "-n", "10", "python3", str(BASE / "percepcion.py"), "correr",
    "--raiz-rd", str(Path.home() / "RD"),
    "--raiz-ig", str(Path.home() / "portfolio_media" / "media"),
    "--out", str(BASE),
]
RAMA_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9/_.-]{0,80}$")


def _pid() -> str | None:
    r = subprocess.run(["pgrep", "-f", "percepcion.py correr"],
                       capture_output=True, text=True)
    pids = [p for p in r.stdout.split() if p.strip()]
    return pids[0] if pids else None


def estado() -> int:
    e = BASE / "estado.json"
    print("PID:", _pid() or "no corre")
    if e.exists():
        print(e.read_text()[:1500])
    rep = BASE / "reportes" / "REPORTE_CURATORIA.md"
    if rep.exists():
        print("\n".join(rep.read_text().splitlines()[:25]))
    return 0


def pausar() -> int:
    pid = _pid()
    if not pid:
        print("ya estaba detenida")
        return 0
    subprocess.run(["kill", pid], check=False)
    time.sleep(2)
    print("detenida" if not _pid() else "SIGTERM enviado, sigue viva (reintentar)")
    return 0


def reanudar() -> int:
    if _pid():
        print("ya corre, PID", _pid())
        return 0
    log = open(BASE / "percepcion.log", "ab")
    subprocess.Popen(CMD_CORRER, stdout=log, stderr=log,
                     stdin=subprocess.DEVNULL, start_new_session=True)
    time.sleep(3)
    pid = _pid()
    print("relanzada, PID", pid) if pid else print("FALLO relanzar (ver log)")
    return 0 if pid else 1


def redeploy(rama: str) -> int:
    if not RAMA_RE.match(rama):
        print("rama invalida")
        return 1
    repo = Path.home() / "flujo"
    r = subprocess.run(["git", "-C", str(repo), "fetch", "origin", rama],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print("fetch fallo:", r.stderr[-200:])
        return 1
    for f in ("percepcion.py", "reporter.py"):
        s = subprocess.run(
            ["git", "-C", str(repo), "show", f"FETCH_HEAD:cultura/mak_curatoria/{f}"],
            capture_output=True, text=True, timeout=60)
        if s.returncode != 0:
            print(f"{f}: no existe en {rama}")
            return 1
        (BASE / f).write_text(s.stdout)
        print(f"{f}: desplegado desde {rama}")
    print("redeploy OK (usar 'pausar' + 'reanudar' para aplicar)")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    orden = sys.argv[1]
    if orden == "estado":
        return estado()
    if orden == "pausar":
        return pausar()
    if orden == "reanudar":
        return reanudar()
    if orden == "redeploy" and len(sys.argv) >= 3:
        return redeploy(sys.argv[2])
    print("orden desconocida:", orden[:40])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
