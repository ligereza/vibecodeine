#!/usr/bin/env python3
"""latido.py -- the organism heartbeat: an occasional new concept.

Cron triggers it every three hours. Limits prevent free APIs from being
overloaded:
  - MAX_DIA heartbeats per day
  - MIN_GAP between heartbeats
  - skip when system load is high
It launches one descriptive research request through the guard from cultural
seeds.
Editable: ~/plataforma/semillas_latido.txt (one idea per line).
Disable: remove the MAK-LATIDO line from crontab.
"""
import json
import os
import tempfile
import time
import urllib.parse
import urllib.request

try:
    from cultura.mak_conductor.runtime import active_enabled, dispatch_sync
except ImportError:  # pragma: no cover - direct MAK deployment
    import sys
    sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH", "/home/mak/flujo/cultura"))
    try:
        from mak_conductor.runtime import active_enabled, dispatch_sync
    except ImportError:
        active_enabled = lambda: False
        dispatch_sync = None

HOME = os.path.expanduser("~")
SEMILLAS = os.path.join(HOME, "plataforma/semillas_latido.txt")
IDX = os.path.join(HOME, "plataforma/.latido_idx")
STATE = os.path.join(HOME, "plataforma/.latido_state.json")
LOG = os.path.join(HOME, "plataforma/logs/latido.log")
RESEARCH = "http://127.0.0.1:8890/run"

MAX_DIA = 5           # maximum heartbeats per day
MIN_GAP_S = 2 * 3600  # at least two hours between heartbeats
LOAD_MAX = 3.0        # skip when load1 exceeds this threshold

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


def _atomic_write(path, text):
    temp_path = None
    try:
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=directory,
                prefix=".latido-", suffix=".tmp", delete=False) as f:
            temp_path = f.name
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
        temp_path = None
    except OSError:
        pass
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
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
        _atomic_write(
            SEMILLAS,
            "# semillas del latido -- una idea por linea, edita libremente.\n"
            + "\n".join(SEED_DEFAULT) + "\n")
        return SEED_DEFAULT


def prox_idx(n):
    i = 0
    try:
        with open(IDX) as f:
            i = int(f.read().strip() or "0")
    except (OSError, ValueError):
        i = 0
    _atomic_write(IDX, str((i + 1) % max(n, 1)))
    return i % max(n, 1)


def _state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save(s):
    _atomic_write(STATE, json.dumps(s, ensure_ascii=False))


def main():
    if active_enabled() and dispatch_sync is not None:
        payload = {"bucket": int(time.time() // 7200)}

        def handle(_job):
            result = _main_unlocked()
            return {"validated": True, "result": result,
                    "artifacts": [{
                        "kind": "heartbeat_manifest",
                        "content": json.dumps(payload, sort_keys=True),
                        "staging_path": LOG,
                    }]}

        return dispatch_sync(
            "heartbeat", payload, producer="platform.latido.main",
            handler=handle, template_version="heartbeat-v1",
        )
    return _main_unlocked()


def _main_unlocked():
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
    return 0


if __name__ == "__main__":
    main()
