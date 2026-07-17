#!/usr/bin/env python3
"""guardia.py -- gate de recursos: nada pesado arranca si el cuerpo esta al limite."""
import os
import shutil
import time

LOAD_MAX = 6.0        # 8 nucleos: sobre 6 el box sufre
MEM_MIN_MB = 2048
DISCO_MIN_GB = 5.0


def recursos_ok():
    """(bool, motivo). True si hay cuerpo para un trabajo pesado."""
    load1 = os.getloadavg()[0]
    if load1 > LOAD_MAX:
        return False, "load %.1f > %.1f" % (load1, LOAD_MAX)
    mem = -1
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    mem = int(line.split()[1]) // 1024
                    break
    except OSError:
        pass
    if 0 <= mem < MEM_MIN_MB:
        return False, "memoria %dMB < %dMB" % (mem, MEM_MIN_MB)
    libre_gb = shutil.disk_usage("/").free / 1e9
    if libre_gb < DISCO_MIN_GB:
        return False, "disco %.1fGB < %.1fGB" % (libre_gb, DISCO_MIN_GB)
    return True, "ok"


def esperar_recursos(max_espera=300, paso=10):
    """Espera hasta que haya recursos o venza el plazo. True = adelante."""
    inicio = time.time()
    while True:
        ok, motivo = recursos_ok()
        if ok:
            return True
        if time.time() - inicio > max_espera:
            print("STATUS: guardia vencio la espera (%s)" % motivo, flush=True)
            return False
        print("STATUS: esperando recursos (%s)" % motivo, flush=True)
        time.sleep(paso)


if __name__ == "__main__":
    ok, motivo = recursos_ok()
    print("recursos_ok=%s (%s)" % (ok, motivo))
    raise SystemExit(0 if ok else 1)
