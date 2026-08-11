#!/usr/bin/env python3
"""backlog_codex.py -- auto-refill de backlog_codex.txt (verbo 'desarrollar').
Espejo minimal de plataforma/backlog.py, para texto plano en vez de jsonl.
Fuentes: (a) roles.MODULOS con TODO/FIXME o sin test_<modulo>.py hermano;
(b) codex/eventos.jsonl tipo~'hallazgo'; (c) proveedor con api_errors>successes
(>=5 intentos) en salud_proveedores.json. Dedup normalizado, tope 40, idempotente.
"""
import json
import os
import re
import sys
import threading
import time
import unicodedata
from contextlib import contextmanager

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

HOME = os.path.expanduser("~")
sys.path.insert(0, os.path.join(HOME, "plataforma"))

BACKLOG_TXT = os.path.join(HOME, "plataforma", "backlog_codex.txt")
EVENTOS_CODEX = os.path.join(HOME, "codex", "eventos.jsonl")
SALUD_PROVEEDORES = os.path.join(HOME, "research", "salud_proveedores.json")
MAX_PENDIENTES = 40
# Separate cap for auto-generated items (2026-07-26). Measured cause:
# trabajo.py walks the backlog in ROTATION, so every line takes a turn. With 15
# tasks -- 10 of them auto-generated filler like "agregar test / resolver TODO
# en X" -- the curated priorities got 1 turn out of 15. The filler was not
# blocking anything: it was diluting. Capping ONLY the auto items (they carry a
# "# auto DATE" marker) leaves curated tasks undiluted and keeps the mechanism.
# Retirement: when the backlog gains an explicit per-line priority.
MAX_AUTO = 3
MAX_HALLAZGOS = 3
_BACKLOG_LOCK = threading.RLock()


@contextmanager
def _exclusive_backlog_lock(path):
    """Serialize the complete read-candidate-deduplicate-append cycle."""
    with _BACKLOG_LOCK:
        lock_path = os.path.abspath(path) + ".lock"
        parent = os.path.dirname(lock_path)
        os.makedirs(parent, exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

_MARCADOR_RE = re.compile(r"\s*#\s*auto\s+\d{8}\s*$")
_TODO_RE = re.compile(r"#\s*(TODO|FIXME)\b")


def _norm(texto):
    """Dedup key: sin marcador, sin accents, lowercase, ws colapsado."""
    texto = _MARCADOR_RE.sub("", texto)
    nfd = unicodedata.normalize("NFD", texto)
    sin_accents = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", sin_accents.lower().strip())


def _cargar_lineas(path):
    lineas = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for cruda in f:
                s = cruda.strip()
                if s and not s.startswith("#"):
                    lineas.append(s)
    except OSError:
        pass
    return lineas


def _fuente_modulos():
    """Modulo con TODO/FIXME en comentario, o sin test_<modulo>.py hermano."""
    tareas = []
    try:
        import roles
        modulos = list(roles.MODULOS)
    except Exception:
        return tareas

    for modulo in modulos:
        try:
            with open(modulo, "r", encoding="utf-8") as f:
                contenido = f.read()
        except OSError:
            continue
        tiene_todo = bool(_TODO_RE.search(contenido))
        test_hermano = os.path.join(os.path.dirname(modulo), "test_" + os.path.basename(modulo))
        if tiene_todo or not os.path.exists(test_hermano):
            tareas.append("agregar test / resolver TODO en %s" % modulo)
    return tareas


def _texto_hallazgo(d):
    for clave in ("detalle", "resumen", "mensaje", "texto", "contexto"):
        v = d.get(clave)
        if isinstance(v, str) and v.strip():
            return v.strip()[:200]
    return json.dumps(d, ensure_ascii=False)[:200]


def _fuente_hallazgos():
    """codex/eventos.jsonl: lineas con tipo que contiene 'hallazgo'."""
    tareas = []
    try:
        with open(EVENTOS_CODEX, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    d = json.loads(linea)
                except (ValueError, json.JSONDecodeError):
                    continue
                if isinstance(d, dict) and "hallazgo" in str(d.get("tipo", "")).lower():
                    tareas.append("resolver hallazgo codex: %s" % _texto_hallazgo(d))
                    if len(tareas) >= MAX_HALLAZGOS:
                        break
    except OSError:
        pass
    return tareas


def _fuente_salud():
    """Proveedor con api_errors > successes y >=5 intentos -> tarea de retry."""
    tareas = []
    try:
        with open(SALUD_PROVEEDORES, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError, json.JSONDecodeError):
        return tareas

    proveedores = data.get("proveedores", {})
    if not isinstance(proveedores, dict):
        return tareas

    for nombre, stats in proveedores.items():
        if not isinstance(stats, dict):
            continue
        successes = stats.get("successes", 0)
        api_errors = stats.get("api_errors", 0)
        intentos = successes + api_errors + stats.get("timeouts", 0) + stats.get("errors", 0)
        if intentos >= 5 and api_errors > successes:
            tareas.append("envolver proveedor %s con retry/circuit-breaker en la cadena" % nombre)
    return tareas


def _main_unlocked():
    existentes = _cargar_lineas(BACKLOG_TXT)
    existing_normalized = {_norm(line_text) for line_text in existentes}
    total_actual = len(existentes)

    candidatos = _fuente_modulos() + _fuente_hallazgos() + _fuente_salud()
    fecha = time.strftime("%Y%m%d")
    agregadas = []
    vistos = set()

    current_auto_count = sum(1 for line_text in existentes
                             if _MARCADOR_RE.search(line_text))

    for texto in candidatos:
        if total_actual + len(agregadas) >= MAX_PENDIENTES:
            break
        if current_auto_count + len(agregadas) >= MAX_AUTO:
            break
        n = _norm(texto)
        if n in existing_normalized or n in vistos:
            continue
        vistos.add(n)
        agregadas.append(texto + " # auto " + fecha)

    if agregadas:
        try:
            with open(BACKLOG_TXT, "a", encoding="utf-8") as f:
                for linea in agregadas:
                    f.write(linea + "\n")
        except OSError as e:
            print("ERROR escribiendo backlog: %s" % e)
            return

    print("agregadas: %d" % len(agregadas))
    for linea in agregadas:
        print(linea)
    print("total pendientes ahora: %d" % (total_actual + len(agregadas)))


def main():
    with _exclusive_backlog_lock(BACKLOG_TXT):
        return _main_unlocked()


if __name__ == "__main__":
    main()
