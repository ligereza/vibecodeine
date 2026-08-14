#!/usr/bin/env python3
"""energia.py -- energia del organismo MAK: estado de WoL/WoWLAN, suspender.

El teléfono (xio) DESPIERTA a MAK con un magic packet a su MAC de wifi; MAK
puede DORMIR por comando (nunca por inactividad). El despertar es externo.

    python3 energia.py estado
    python3 energia.py dormir     # systemctl suspend (WoWLAN queda armado)
"""
import json
import subprocess
import sys

# La MAC de la interfaz Wi-Fi de esta caja se lee del entorno o del propio
# sistema; el repositorio no contiene una identidad de hardware.
#
# Se resuelven en este orden: MAK_MAC_ETH / MAK_MAC_WIFI del entorno, y si no,
# lo que diga /sys para esa interfaz. Si no hay ninguna, quedan vacias y el
# llamador se entera en vez de comparar contra una constante equivocada.
def _mac_de(iface: str, var: str) -> str:
    import os
    valor = os.environ.get(var, "").strip()
    if valor:
        return valor.lower()
    try:
        with open("/sys/class/net/%s/address" % iface) as fh:
            return fh.read().strip().lower()
    except OSError:
        return ""


MAC_WIFI = _mac_de("wlp0s20f3", "MAK_MAC_WIFI")  # red del telefono Xiaomi


def _run(cmd, timeout=6):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def estado():
    suspend = _run(["systemctl", "is-enabled", "suspend.target"]) or "?"
    wowlan = _run(["iw", "phy0", "wowlan", "show"]) or "(requiere root o no armado)"
    return {
        "mac_wifi": MAC_WIFI,
        "suspend_target": suspend,
        "wowlan": wowlan.replace("\n", " ")[:120],
        "despertar_desde_telefono": "magic packet UDP a %s (puerto 9)" % MAC_WIFI,
    }


def dormir():
    print("STATUS: suspendiendo MAK; despiértalo con un magic packet a %s"
          % MAC_WIFI, flush=True)
    r = subprocess.run(["systemctl", "suspend"], capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "estado":
        print(json.dumps(estado(), ensure_ascii=False, indent=2))
        return 0
    if sys.argv[1] == "dormir":
        ok, msg = dormir()
        print("suspend %s %s" % ("OK" if ok else "FALLÓ", msg))
        return 0 if ok else 1
    print("uso: energia.py [estado|dormir]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
