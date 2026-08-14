#!/usr/bin/env python3
"""Read-only egress guard for the active MAK Linux runtime.

The guard samples established TCP connections and alerts when MAK contacts
many peers on a locally detected network in a short interval. Network ranges
come from the local Linux interface table or an explicit environment override;
there is no fixed gateway, peer, or remote runtime address here.
"""
import ipaddress
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/home/mak/research")
from research_lib import load_env, ntfy_publish  # noqa: E402

ESTADO = "/home/mak/plataforma/logs/vigilar_red.json"
UMBRAL_HOSTS = 8          # >8 hosts LAN distintos = posible escaneo
ANTISPAM_S = 1800


def _local_networks():
    """Return local IPv4 networks and addresses without a fixed IP policy."""
    override = os.environ.get("MAK_NETWORK_CIDRS", "").strip()
    if override:
        networks = []
        for value in override.split(","):
            try:
                networks.append(ipaddress.ip_network(value.strip(), strict=False))
            except ValueError:
                continue
        return networks, set()

    try:
        out = subprocess.run(
            ["ip", "-o", "-4", "addr", "show", "scope", "global"],
            capture_output=True, text=True, timeout=8,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return [], set()

    networks = []
    addresses = set()
    for line in out.splitlines():
        for column in line.split():
            if "/" not in column:
                continue
            try:
                interface = ipaddress.ip_interface(column)
            except ValueError:
                continue
            networks.append(interface.network)
            addresses.add(str(interface.ip))
            break
    return networks, addresses


def _conexiones():
    """Destinos remotos de conexiones TCP establecidas (ss, sin sudo)."""
    try:
        out = subprocess.run(["ss", "-tn", "state", "established"],
                             capture_output=True, text=True, timeout=8).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    dests = []
    for line in out.splitlines():
        cols = line.split()
        if len(cols) >= 4:
            peer = cols[-1].rsplit(":", 1)[0].strip("[]")
            try:
                ipaddress.ip_address(peer)
            except ValueError:
                continue
            dests.append(peer)
    return dests


def revisar():
    dests = _conexiones()
    networks, local_addresses = _local_networks()
    lan_hosts = sorted({ip for ip in dests if ip not in local_addresses and any(
        ipaddress.ip_address(ip) in network for network in networks)})
    snapshot = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                "conexiones": len(dests),
                "hosts_lan_distintos": len(lan_hosts),
                "muestra": lan_hosts[:15],
                "redes_locales": [str(network) for network in networks]}
    os.makedirs(os.path.dirname(ESTADO), exist_ok=True)
    tmp = ESTADO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False)
    os.replace(tmp, ESTADO)

    if len(lan_hosts) > UMBRAL_HOSTS:
        _alerta("MAK contacted %d distinct local-network peers in one "
                "sample (possible scan). Sample: %s"
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
                 title="MAK network guard", priority="high")
    try:
        open(marca, "w").close()
    except OSError:
        pass


if __name__ == "__main__":
    print(json.dumps(revisar(), ensure_ascii=False, indent=1))
