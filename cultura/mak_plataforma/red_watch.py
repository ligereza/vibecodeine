#!/usr/bin/env python3
"""red_watch.py -- memoria de cortes de INTERNET real (no solo del gateway).

Cron cada 2 min. El monitor de xio ve el TELEFONO por wifi; esto ve el
INTERNET (sonda a 1.1.1.1 / 8.8.8.8). Registra solo las TRANSICIONES en
~/plataforma/logs/red.jsonl:
  {"ts","epoch","estado":"caido"}                        -> se corto
  {"ts","epoch","estado":"volvio","duracion_s":312}      -> volvio, cuanto duro

Asi el organismo tiene memoria de cuando trabajo en local vs nube.
"""
import json
import os
import socket
import tempfile
import time

LOG = os.path.expanduser("~/plataforma/logs/red.jsonl")
STATE = os.path.expanduser("~/plataforma/.red_state.json")


def _atomic_write(path, text):
    temp_path = None
    try:
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=directory,
                prefix=".red-state-", suffix=".tmp", delete=False) as f:
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


def internet():
    for host, port in (("1.1.1.1", 443), ("8.8.8.8", 53)):
        try:
            s = socket.create_connection((host, port), timeout=3)
            s.close()
            return True
        except OSError:
            continue
    return False


def main():
    now = time.time()
    ts = time.strftime("%F %T")
    up = internet()
    try:
        with open(STATE) as f:
            st = json.load(f)
    except (OSError, ValueError):
        st = {"up": True, "since": now}
    if up == st.get("up", True):
        return  # sin cambio de estado, nada que registrar
    ev = {"ts": ts, "epoch": round(now)}
    if up:
        ev["estado"] = "volvio"
        ev["duracion_s"] = round(now - st.get("since", now))
    else:
        ev["estado"] = "caido"
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    except OSError:
        pass
    _atomic_write(STATE, json.dumps({"up": up, "since": now}))


if __name__ == "__main__":
    main()
