#!/usr/bin/env python3
"""vigilar_red.py -- vigilancia de egreso de MAK (mitigacion del dossier).

Muestrea las conexiones establecidas y alerta por ntfy si MAK se comporta
como un escaner: muchas IPs distintas de la LAN/hotspot contactadas en poco
tiempo (firma del vector (e) del dossier). Solo lectura, sin sudo. Cron */5.
"""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, "/home/mak/research")
from research_lib import load_env, ntfy_publish  # noqa: E402

ESTADO = "/home/mak/plataforma/logs/vigilar_red.json"
GATEWAY = "192.168.95.203"
# destinos "normales": el gateway (routing) y el PC Windows. Un barrido a
# MUCHAS IPs distintas de estos rangos es la senal de alarma.
RANGOS_LAN = ("192.168.50.", "192.168.95.")
UMBRAL_HOSTS = 8          # >8 hosts LAN distintos = posible escaneo
ANTISPAM_S = 1800
IP_RE = re.compile(r"(\d+\.\d+\.\d+\.\d+):(\d+)")


def _conexiones():
    """Destinos remotos de conexiones TCP establecidas (ss, sin sudo)."""
    try:
        out = subprocess.run(["ss", "-tn", "state", "established"],
                             capture_output=True, text=True, timeout=8).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    dests = []
    for line in out.splitlines()[1:]:
        cols = line.split()
        if len(cols) >= 4:
            m = IP_RE.search(cols[-1])  # peer address:port
            if m:
                dests.append(m.group(1))
    return dests


def revisar():
    dests = _conexiones()
    lan_hosts = sorted({ip for ip in dests
                        if any(ip.startswith(r) for r in RANGOS_LAN)
                        and ip != GATEWAY})
    snapshot = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                "conexiones": len(dests),
                "hosts_lan_distintos": len(lan_hosts),
                "muestra": lan_hosts[:15]}
    os.makedirs(os.path.dirname(ESTADO), exist_ok=True)
    tmp = ESTADO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False)
    os.replace(tmp, ESTADO)

    if len(lan_hosts) > UMBRAL_HOSTS:
        _alerta("MAK contacto %d hosts distintos de la LAN/hotspot en un "
                "instante (posible escaneo). Muestra: %s"
                % (len(lan_hosts), ", ".join(lan_hosts[:8])))
    return snapshot


def _alerta(mensaje):
    marca = "/home/mak/plataforma/logs/.vigilar_alerta"
    try:
        if os.path.exists(marca) and time.time() - os.path.getmtime(marca) < ANTISPAM_S:
            return
    except OSError:
        pass
    load_env()
    ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""), mensaje,
                 title="MAK vigilancia de red", priority="high")
    try:
        open(marca, "w").close()
    except OSError:
        pass


if __name__ == "__main__":
    print(json.dumps(revisar(), ensure_ascii=False, indent=1))
