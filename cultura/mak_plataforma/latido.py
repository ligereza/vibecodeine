#!/usr/bin/env python3
"""latido.py -- el latido del organismo: cada tanto, un concepto nuevo.

El cron lo gatilla (cada 3h). Con topes para no desbordar las APIs gratis:
  - MAX_DIA latidos por dia
  - MIN_GAP entre latidos
  - se salta si la carga esta alta (el cuerpo ocupado)
Lanza UN research DESCRIPTIVO (pasa la guardia) desde las semillas culturales.
Editable: ~/plataforma/semillas_latido.txt (una idea por linea).
Apagar: quitar la linea MAK-LATIDO del crontab.
"""
import json
import os
import time
import urllib.parse
import urllib.request

HOME = os.path.expanduser("~")
SEMILLAS = os.path.join(HOME, "plataforma/semillas_latido.txt")
IDX = os.path.join(HOME, "plataforma/.latido_idx")
STATE = os.path.join(HOME, "plataforma/.latido_state.json")
LOG = os.path.join(HOME, "plataforma/logs/latido.log")
RESEARCH = "http://127.0.0.1:8890/run"

MAX_DIA = 5           # latidos por dia como maximo
MIN_GAP_S = 2 * 3600  # al menos 2h entre latidos
LOAD_MAX = 3.0        # si load1 > esto, el cuerpo esta ocupado: saltar

SEED_DEFAULT = [
    "genealogia cultural de la tilde y los signos diacriticos del castellano",
    "el paradigma indiciario de Ginzburg como lente para leer registros culturales",
    "drogas de diseno en la cultura electronica: historia, estetica y reduccion de dano",
    "la gramatica del telar como sistema generativo de patrones (field, border, medallion)",
    "esteganografia cultural: senales de baja entropia escondidas en el lenguaje cotidiano",
    "entropia de archivos borrados: el git log como sustrato de una poetica del descarte",
    "branding de cepas y diagramas de Markush: el mito del linaje como retorica visual",
    "herramientas espejo (dual-use) en el arte digital: cuando el filo esta en la aplicacion",
]


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


def semillas():
    try:
        with open(SEMILLAS, encoding="utf-8") as f:
            s = [x.strip() for x in f if x.strip() and not x.startswith("#")]
        return s or SEED_DEFAULT
    except OSError:
        try:
            with open(SEMILLAS, "w", encoding="utf-8") as f:
                f.write("# semillas del latido -- una idea por linea, edita libremente.\n")
                f.write("\n".join(SEED_DEFAULT) + "\n")
        except OSError:
            pass
        return SEED_DEFAULT


def prox_idx(n):
    i = 0
    try:
        with open(IDX) as f:
            i = int(f.read().strip() or "0")
    except (OSError, ValueError):
        i = 0
    try:
        with open(IDX, "w") as f:
            f.write(str((i + 1) % max(n, 1)))
    except OSError:
        pass
    return i % max(n, 1)


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


def main():
    ts = time.strftime("%F %T")
    now = time.time()
    hoy = time.strftime("%Y-%m-%d")
    st = _state()
    if st.get("date") != hoy:
        st = {"date": hoy, "count": 0, "last": 0}
    if st["count"] >= MAX_DIA:
        log("%s skip: tope diario (%d)" % (ts, MAX_DIA))
        return
    if now - st.get("last", 0) < MIN_GAP_S:
        log("%s skip: gap < %dh" % (ts, MIN_GAP_S // 3600))
        return
    if load1() > LOAD_MAX:
        log("%s skip: load %.2f > %s" % (ts, load1(), LOAD_MAX))
        return
    sem = semillas()
    tema = "latido: " + sem[prox_idx(len(sem))]
    data = urllib.parse.urlencode(
        {"modo": "research", "tema": tema, "densidad": "corto"}).encode()
    req = urllib.request.Request(
        RESEARCH, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            resp = r.read(2000).decode("utf-8", "replace")
        st["count"] += 1
        st["last"] = now
        _save(st)
        log("%s latido #%d/%d: %s -> %s"
            % (ts, st["count"], MAX_DIA, tema[:70], resp[:80]))
    except Exception as e:  # noqa: BLE001 - el latido no debe tumbar nada
        log("%s latido FALLO: %s" % (ts, str(e)[:140]))


if __name__ == "__main__":
    main()
