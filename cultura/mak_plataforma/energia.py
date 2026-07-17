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

MAC_ETH = "8c:47:be:20:02:67"    # enp3s0 (enlace al PC Windows)
MAC_WIFI = "a8:7e:ea:41:63:a1"   # wlp0s20f3 (red del teléfono Xiaomi)
CON_ETH = "lan-kvm"


def _run(cmd, timeout=6):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def estado():
    nm = _run(["nmcli", "-t", "-f", "802-3-ethernet.wake-on-lan",
               "con", "show", CON_ETH])
    suspend = _run(["systemctl", "is-enabled", "suspend.target"]) or "?"
    wowlan = _run(["iw", "phy0", "wowlan", "show"]) or "(requiere root o no armado)"
    return {
        "mac_eth": MAC_ETH,
        "mac_wifi": MAC_WIFI,
        "wol_eth_nm": nm or "(no configurado)",
        "suspend_target": suspend,
        "wowlan": wowlan.replace("\n", " ")[:120],
        "despertar_desde_telefono": "magic packet UDP a %s (puerto 9)" % MAC_WIFI,
        "despertar_desde_windows": "magic packet a %s (ethernet)" % MAC_ETH,
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
