#!/usr/bin/env python3
"""salud.py -- snapshot de salud del organismo MAK (lib + CLI)."""
import json
import os
import shutil
import subprocess
import time

CARPETAS_PRODUCTOS = {
    "research": ["informes", "paneles", "cadenas", "refutaciones",
                 "correlaciones", "grafos", "memoria"],
    "codex": ["piezas", "revisiones"],
    "lenguaje": ["lexico"],
}
SERVICIOS = {
    "research": "research/interfaz.py",
    "cola": "research/cola.py",
    "codex": "codex/interfaz_codex.py",
    "hub": "plataforma/hub.py",
    "xio_monitor": "xio_puente/monitor.py",
}


def _mem_disponible_mb():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except OSError:
        pass
    return -1


def _gpu():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5)
        if out.returncode == 0 and out.stdout.strip():
            t, u, util = [x.strip() for x in out.stdout.strip().split(",")[:3]]
            return {"vram_total_mb": int(t), "vram_usada_mb": int(u),
                    "uso_pct": int(util)}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        pass
    return {"error": "nvidia-smi no disponible"}


def _proceso_vivo(patron):
    try:
        r = subprocess.run(["pgrep", "-f", patron], capture_output=True,
                           text=True, timeout=5)
        pids = [p for p in r.stdout.split() if p.isdigit()]
        return pids[0] if pids else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _contar_md(base, sub):
    try:
        d = os.path.join(base, sub)
        return sum(1 for f in os.listdir(d) if f.endswith(".md"))
    except OSError:
        return 0


def snapshot():
    load1, load5, load15 = os.getloadavg()
    disco = shutil.disk_usage("/")
    home = os.path.expanduser("~")
    productos = {}
    for dept, subs in CARPETAS_PRODUCTOS.items():
        base = os.path.join(home, dept if dept != "research" else "research")
        productos[dept] = {s: _contar_md(base, s) for s in subs}
    servicios = {}
    for nombre, patron in SERVICIOS.items():
        pid = _proceso_vivo(patron)
        servicios[nombre] = {"vivo": pid is not None, "pid": pid}
    try:
        with open("/proc/uptime") as f:
            uptime_s = int(float(f.read().split()[0]))
    except OSError:
        uptime_s = -1
    return {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "load": [round(load1, 2), round(load5, 2), round(load15, 2)],
        "mem_disponible_mb": _mem_disponible_mb(),
        "disco_libre_gb": round(disco.free / 1e9, 1),
        "gpu": _gpu(),
        "servicios": servicios,
        "productos": productos,
        "uptime_s": uptime_s,
    }


if __name__ == "__main__":
    print(json.dumps(snapshot(), ensure_ascii=False, indent=2))
