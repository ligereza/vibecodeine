#!/usr/bin/env python3
"""pausa.py -- pausa-en-error para el research MAK (checkpoints humanos).

Cuando el LLM se queda sin proveedores (o Tavily falla duro) en medio de
una investigacion, en vez de morir o degradar el informe a un placeholder,
research.py guarda un checkpoint recuperable y sale con codigo 3. Un
humano (o proceso de guardia) puede leer el checkpoint, decidir una accion
(reintentar/editar/saltar) y reanudar con --resume.

Puro stdlib, importable en Windows (sin fcntl): lo usa tambien worker.py
(Linux) para reconocer la marca en el stdout del subproceso.
"""
import json
import os
import tempfile
import threading
from contextlib import contextmanager

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

DIR_CHECKPOINTS = os.path.join(os.path.expanduser("~"), "research", "checkpoints")

MARCA = "PAUSADO: "
_CHECKPOINT_LOCK = threading.RLock()


@contextmanager
def _exclusive_checkpoint_lock(path):
    """Serialize human actions across MAK processes."""
    with _CHECKPOINT_LOCK:
        lock_path = os.path.abspath(path) + ".lock"
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


def _write_json_atomic(path, data):
    parent = os.path.dirname(os.path.abspath(path))
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=parent,
                prefix=".%s-" % os.path.basename(path), suffix=".tmp",
                delete=False) as f:
            temp_path = f.name
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def guardar_checkpoint(datos, base_dir=None):
    """Escribe <base_dir or DIR_CHECKPOINTS>/<job_id>.json (mkdir -p).
    Devuelve la ruta absoluta escrita."""
    job_id = datos["job_id"]
    destino = base_dir or DIR_CHECKPOINTS
    os.makedirs(destino, exist_ok=True)
    path = os.path.abspath(os.path.join(destino, "%s.json" % job_id))
    with _exclusive_checkpoint_lock(path):
        _write_json_atomic(path, datos)
    return path


def cargar_checkpoint(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def aplicar_accion(path, accion, texto=""):
    """Carga el checkpoint en `path`, aplica `accion`, lo guarda de vuelta
    y devuelve el dict resultante.

    accion:
        "reintentar" -- no-op (se reintenta tal cual quedo)
        "editar"     -- datos["current"] = texto
        "saltar"     -- datos["saltar"] = True
    """
    with _exclusive_checkpoint_lock(path):
        datos = cargar_checkpoint(path)
        if accion == "reintentar":
            pass
        elif accion == "editar":
            datos["current"] = texto
        elif accion == "saltar":
            datos["saltar"] = True
        else:
            raise ValueError("accion desconocida: %s" % accion)
        _write_json_atomic(path, datos)
    return datos


def formatear_marca(path, motivo):
    """Linea de stdout que anuncia la pausa: 'PAUSADO: <path> | <motivo>'.
    motivo se recorta a 200 caracteres y se limpia de saltos de linea."""
    motivo_limpio = " ".join(str(motivo).split())[:200]
    return "%s%s | %s" % (MARCA, path, motivo_limpio)


def parsear_marca(line):
    """Inverso de formatear_marca. Devuelve (path, motivo) o None si la
    linea no arranca con la marca."""
    if not line.startswith(MARCA):
        return None
    resto = line[len(MARCA):].rstrip("\n").rstrip("\r")
    partes = resto.split(" | ", 1)
    if len(partes) != 2:
        return None
    return partes[0], partes[1]
