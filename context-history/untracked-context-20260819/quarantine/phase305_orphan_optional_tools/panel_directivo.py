#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""panel_directivo.py - directiva view of MAK: quality, portfolio, control.

A read dashboard + orchestration buttons for the human operator. Written by
the director (not by codex) so it compiles and serves on the first try.

    python3 panel_directivo.py            # http://0.0.0.0:8901

Routes:
    GET  /            HTML panel (inline CSS/JS, dark)
    GET  /api/datos   JSON metrics read from disk
    POST /api/accion  {"accion": "vetear"|"entregar"|"junta"|"capataz"|...}
                      -> runs the organ script, returns last output lines

Every read is try/except: a missing file shows "sin datos", never crashes.
Stdlib only. Nothing here spends tokens.
"""

import html
import json
import os
import re
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOME = Path.home()
PANEL_PORT = int(os.environ.get("PANEL_PORT", "8901"))

DEPARTAMENTOS = (("research", 8890), ("codex", 8891), ("hub", 8900), ("ollama", 11434))
LLAVES = ("WATSONX_API_KEY", "WATSONX_PROJECT_ID", "TAVILY_API_KEY")
ENV_LLAVES = HOME / "n8n-local" / "research.env"

MARCAS_SIN_RELLENAR = ("[su nombre]", "[tu nombre", "[insertar", "[completar",
                       "[pendiente]", "lorem ipsum")

RUTAS = {
    "informes": HOME / "research" / "informes",
    "piezas": HOME / "codex" / "piezas",
    "campo": HOME / "flujo" / "iskvw" / "datos" / "campo.json",
    "obras": HOME / "flujo" / "iskvw" / "datos" / "obras.json",
    "animadas": HOME / "flujo" / "iskvw" / "datos" / "animadas.json",
    "fichas": HOME / "curatoria" / "fichas" / "fichas.jsonl",
    "material": HOME / "plataforma" / "material.jsonl",
    "bitacora": HOME / "plataforma" / "bitacora_capataz.jsonl",
}

ACCIONES = {
    "vetear": ["python3", str(HOME / "plataforma" / "revisor.py"), "--enforce"],
    "entregar": ["python3", str(HOME / "plataforma" / "entregar.py"), "--limit", "1"],
    "junta": ["python3", str(HOME / "plataforma" / "junta.py")],
    "capataz": ["python3", str(HOME / "plataforma" / "capataz.py")],
}


# ---------------------------------------------------------------- lecturas
def _leer_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def _ultimas_lineas(path, n=200000):
    try:
        return Path(path).read_text(encoding="utf-8").splitlines()[-n:]
    except Exception:
        return []


def _probar(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.5):
            return True, 0
    except OSError as e:
        return False, str(e)[:80]


def _llaves_presentes():
    env = {}
    try:
        for linea in ENV_LLAVES.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            k, v = linea.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return {k: bool(env.get(k)) for k in LLAVES}


def _calidad_informes(n=20):
    """Ultimos n informes: marcadores sin rellenar, errores, refutados, fuentes."""
    try:
        archivos = sorted(RUTAS["informes"].glob("*.json"))[-n:]
    except Exception:
        return {"contados": 0}
    con_marca = con_error = refutados = con_fuentes = 0
    ejemplos = []
    for p in archivos:
        d = _leer_json(p)
        if not isinstance(d, dict):
            continue
        report = (d.get("report") or "").lower()
        if any(m in report for m in MARCAS_SIN_RELLENAR):
            con_marca += 1
            if len(ejemplos) < 3:
                ejemplos.append(p.name[:60])
        if d.get("meta", {}).get("errors"):
            con_error += 1
        v = d.get("verificacion") or {}
        if v.get("refutado") is not None:
            refutados += 1
        if v.get("fuentes_primarias"):
            con_fuentes += 1
    return {"contados": len(archivos), "con_marca": con_marca,
            "con_error": con_error, "refutados": refutados,
            "con_fuentes": con_fuentes, "ejemplos": ejemplos}


def _calidad_piezas(n=20):
    meta_re = re.compile(r"^meta:\s*(\{.*\})\s*$", re.M)
    try:
        archivos = sorted(RUTAS["piezas"].glob("*.md"))[-n:]
    except Exception:
        return {"contados": 0}
    con_meta = con_error = 0
    for p in archivos:
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        m = meta_re.search(t)
        if not m:
            continue
        con_meta += 1
        try:
            if json.loads(m.group(1)).get("errors"):
                con_error += 1
        