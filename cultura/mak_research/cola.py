#!/usr/bin/env python3
"""cola.py -- interfaz ntfy: manda un tema desde el iPhone, MAK investiga.

Suscribe https://ntfy.sh/$NTFY_TOPIC_IN (stream JSON). Mensajes:
    <tema>                 -> research.py (3 iteraciones)
    panel: <tema>          -> panel.py (2 replicas)
    research: <tema>       -> research.py
Respuestas (ack, informe, errores) salen por $NTFY_TOPIC_OUT.
El informe lo publica el propio research/panel via --ntfy; aca solo
ack de inicio y fallos. Un job a la vez (lock de worker.py).

Correr como servicio: cron @reboot (ver instalacion en MAK_RESEARCH.md).
"""
import json
import os
import time
import urllib.request

from research_lib import load_env, ntfy_publish
from worker import run_tema

PIDFILE = os.path.expanduser("~/research/.cola.pid")


def _ya_corre():
    try:
        pid = int(open(PIDFILE).read().strip())
        os.kill(pid, 0)
        return pid != os.getpid()
    except (OSError, ValueError):
        return False


def procesar(texto):
    texto = texto.strip()
    if not texto:
        return
    modo, tema, n = "research", texto, 2
    low = texto.lower()
    if low.startswith("panel:") or low.startswith("panel "):
        modo, tema, n = "panel", texto[6:].strip(), 1
    elif low.startswith("research:"):
        tema = texto[9:].strip()
    if not tema:
        return
    out = os.environ.get("NTFY_TOPIC_OUT", "")
    ntfy_publish(out, "%s: \"%s\" en cola (un job a la vez)" % (modo, tema),
                 title="MAK recibio")
    r = run_tema(modo, tema, n=n, ntfy=True)
    if not r["ok"]:
        ntfy_publish(out, "fallo %s \"%s\":\n%s" % (modo, tema, r["tail"]),
                     title="MAK fallo", priority="high")


def escuchar():
    load_env()
    topic = os.environ.get("NTFY_TOPIC_IN", "")
    if not topic:
        raise SystemExit("Falta NTFY_TOPIC_IN en research.env")
    if _ya_corre():
        raise SystemExit("cola.py ya corre (pid en %s)" % PIDFILE)
    os.makedirs(os.path.dirname(PIDFILE), exist_ok=True)
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))

    url = "https://ntfy.sh/%s/json" % topic
    while True:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=None) as stream:
                for raw in stream:
                    try:
                        msg = json.loads(raw.decode("utf-8", "replace"))
                    except ValueError:
                        continue
                    if msg.get("event") == "message":
                        procesar(msg.get("message", ""))
        except Exception as e:  # noqa: BLE001 - red caida: reintentar siempre
            print("stream caido: %s; reintento en 10s" % str(e)[:120],
                  flush=True)
            time.sleep(10)


if __name__ == "__main__":
    escuchar()
