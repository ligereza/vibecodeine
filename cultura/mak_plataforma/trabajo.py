#!/usr/bin/env python3
"""trabajo.py -- el orquestador del trabajo autonomo del organismo MAK.

El cron lo dispara cada CADA_MIN. En cada tick hace UNA unidad de trabajo,
ciclando los verbos de roles.py (multiplicar/definir/limpiar/desarrollar) por
round-robin, con topes de carga/cupo/gap. El ritmo se adapta a la red: offline
(local serial y lento) se espacia mas. El fallback nube<->local lo maneja
red_ok() dentro de las libs de cada departamento; aca solo se decide QUE y
CUANDO, y se despacha por HTTP a research :8890 / codex :8891.

Apagar: quitar la linea MAK-TRABAJO del crontab.
Ajustar ritmo/verbos/modulos/semillas: editar roles.py.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

HOME = os.path.expanduser("~")
import sys
sys.path.insert(0, os.path.join(HOME, "plataforma"))
sys.path.insert(0, os.path.join(HOME, "research"))
import roles  # noqa: E402
try:
    from research_lib import red_ok  # comparte la deteccion de red
except Exception:  # noqa: BLE001 - si falla, asumimos online
    def red_ok():
        return True

STATE = os.path.join(HOME, "plataforma/.trabajo_state.json")
LOG = os.path.join(HOME, "plataforma/logs/trabajo.log")
BACKLOG = os.path.join(HOME, "plataforma/backlog_codex.txt")
SEMILLAS_F = os.path.join(HOME, "plataforma/semillas_latido.txt")
RESEARCH = "http://127.0.0.1:8890/run"
CODEX = "http://127.0.0.1:8891/run"


def log(m):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(m + "\n")
    except OSError:
        pass


def load1():
    try:
        return os.getloadavg()[0]
    except (OSError, AttributeError):
        return 0.0


def _state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save(s):
    try:
        with open(STATE, "w") as f:
            json.dump(s, f)
    except OSError:
        pass


def _lineas(path, fallback):
    try:
        with open(path, encoding="utf-8") as f:
            xs = [x.strip() for x in f if x.strip() and not x.startswith("#")]
        return xs or fallback
    except OSError:
        return fallback


def _post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return r.read(2000).decode("utf-8", "replace")


def _tarea(verbo, st):
    """Arma (depto, payload_dict) para un verbo, o None si no hay trabajo."""
    v = next((x for x in roles.VERBOS if x["verbo"] == verbo), None)
    if not v:
        return None
    fuente = v["fuente"]
    sems = _lineas(SEMILLAS_F, roles.SEMILLAS)
    if fuente == "concepto":
        i = st.get("sem_idx", 0) % len(sems)
        st["sem_idx"] = i + 1
        return ("research", {"modo": v["modo"], "tema": sems[i], "densidad": "corto"})
    if fuente == "definir":
        i = st.get("def_idx", 0) % len(sems)
        st["def_idx"] = i + 1
        tema = "definicion cultural precisa y genealogia de: " + sems[i]
        return ("research", {"modo": v["modo"], "tema": tema, "densidad": "corto"})
    if fuente == "modulo":
        mods = roles.MODULOS
        i = st.get("mod_idx", 0) % len(mods)
        st["mod_idx"] = i + 1
        return ("codex", {"modo": v["modo"], "pedido": mods[i], "densidad": "medio"})
    if fuente == "backlog":
        bl = _lineas(BACKLOG, [])
        if not bl:
            return None  # sin backlog: desarrollar no tiene trabajo este tick
        i = st.get("bl_idx", 0) % len(bl)
        st["bl_idx"] = i + 1
        return ("codex", {"modo": v["modo"], "pedido": bl[i], "densidad": "medio"})
    return None


def main():
    ts = time.strftime("%F %T")
    now = time.time()
    hoy = time.strftime("%Y-%m-%d")
    st = _state()
    if st.get("date") != hoy:
        st = {"date": hoy, "count": 0, "last": 0, "verbo_idx": 0}
    if load1() > roles.LOAD_MAX:
        log("%s skip: load %.2f > %s" % (ts, load1(), roles.LOAD_MAX))
        return
    online = red_ok()
    gap = (roles.GAP_MIN if online else roles.GAP_MIN_OFFLINE) * 60
    if now - st.get("last", 0) < gap:
        return  # aun en el gap; el proximo tick del cron reintenta
    if st.get("count", 0) >= roles.MAX_DIA:
        log("%s skip: tope diario (%d)" % (ts, roles.MAX_DIA))
        return

    # round-robin: probar verbos hasta encontrar uno con trabajo
    n = len(roles.VERBOS)
    idx = st.get("verbo_idx", 0) % n
    tarea = None
    verbo = None
    for k in range(n):
        verbo = roles.VERBOS[(idx + k) % n]["verbo"]
        tarea = _tarea(verbo, st)
        if tarea:
            st["verbo_idx"] = (idx + k + 1) % n
            break
    if not tarea:
        log("%s skip: ningun verbo con trabajo" % ts)
        _save(st)
        return

    depto, payload = tarea
    url = RESEARCH
    if depto == "codex":
        url = CODEX
    try:
        resp = _post(url, payload)
        st["count"] = st.get("count", 0) + 1
        st["last"] = now
        _save(st)
        etiqueta = payload.get("tema") or payload.get("pedido") or ""
        log("%s [%s] %s #%d/%d (%s) -> %s"
            % (ts, "on" if online else "OFF", verbo, st["count"], roles.MAX_DIA,
               etiqueta[:60], resp[:50]))
    except Exception as e:  # noqa: BLE001 - el orquestador no debe morir
        _save(st)
        log("%s [%s] %s FALLO: %s" % (ts, "on" if online else "OFF", verbo, str(e)[:120]))


if __name__ == "__main__":
    main()
