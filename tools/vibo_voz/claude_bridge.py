"""Puente CODE -> Claude Code (CLI headless), BAJO DEMANDA. Agentes por nombre.

No hay escucha ni polling: solo se ejecuta cuando CODE recibe una orden por voz,
asi que en reposo NO gasta tokens. Cada orden lanza 'claude -p ...' en la carpeta
del agente, en segundo plano y con su propio log, para no bloquear la voz.

Agentes:
  - "flujo"  : Claude Code en este repo (C:\\IA\\flujo). Alias: tu, aca, repo, code.
  - "unreal" : Claude en el proyecto de Unreal Engine (MYRA). Alias: ue, cowork,
               motor, myra. Carpeta configurable con VIBO_UNREAL_DIR.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

CLAUDE_CMD = os.environ.get("CLAUDE_CMD", "claude")
CLAUDE_PERM = os.environ.get("CLAUDE_PERMISSION_MODE", "acceptEdits")

_REPO = Path(__file__).resolve().parents[2]                 # C:\IA\flujo
_UNREAL = Path(os.environ.get("VIBO_UNREAL_DIR", r"C:\ARICA\MYRA"))
_LOGDIR = Path(__file__).resolve().parent / "agentes"

# carpeta de trabajo por agente
_DIRS = {"flujo": _REPO, "unreal": _UNREAL}
_ALIAS = {
    "flujo": "flujo", "tu": "flujo", "aca": "flujo", "repo": "flujo",
    "code": "flujo", "consola": "flujo", "1": "flujo",
    "unreal": "unreal", "ue": "unreal", "cowork": "unreal", "motor": "unreal",
    "myra": "unreal", "engine": "unreal", "3d": "unreal", "2": "unreal",
}
_procs: dict[str, subprocess.Popen] = {}


def _norm(agente) -> str | None:
    return _ALIAS.get(str(agente).strip().lower())


def _log_path(agente: str) -> Path:
    return _LOGDIR / f"agente_{agente}.log"


def encargar_a_claude(instruccion: str, agente: str = "flujo") -> dict:
    """Lanza a Claude (CLI headless) una tarea en la carpeta del agente, en segundo
    plano. agente: 'flujo' (este repo) o 'unreal' (proyecto UE). Solo corre cuando
    lo pides: en reposo no gasta tokens."""
    dest = _norm(agente)
    if not dest:
        return {"error": f"agente desconocido: {agente}", "validos": ["flujo", "unreal"]}
    cwd = _DIRS[dest]
    if not cwd.exists():
        return {"error": f"no existe la carpeta del agente {dest}: {cwd}"}
    prev = _procs.get(dest)
    if prev and prev.poll() is None:
        return {"ocupado": True, "agente": dest,
                "mensaje": f"el agente {dest} sigue trabajando; espera a que termine"}
    _LOGDIR.mkdir(exist_ok=True)
    log = _log_path(dest)
    try:
        fh = open(log, "w", encoding="utf-8")
        proc = subprocess.Popen(
            [CLAUDE_CMD, "-p", instruccion, "--permission-mode", CLAUDE_PERM],
            cwd=str(cwd), stdout=fh, stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        return {"error": f"no se encontro el CLI '{CLAUDE_CMD}'. Instala/loguea Claude Code o ajusta CLAUDE_CMD."}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    _procs[dest] = proc
    return {"lanzado": True, "agente": dest, "carpeta": str(cwd), "instruccion": instruccion.strip()}


def estado_agente(agente: str = "flujo") -> dict:
    """Dice si el agente sigue trabajando o termino, con las ultimas lineas del log."""
    dest = _norm(agente)
    if not dest:
        return {"error": f"agente desconocido: {agente}", "validos": ["flujo", "unreal"]}
    proc = _procs.get(dest)
    log = _log_path(dest)
    cola = ""
    if log.exists():
        lineas = log.read_text(encoding="utf-8", errors="replace").splitlines()
        cola = "\n".join(lineas[-8:])
    if proc is None:
        return {"agente": dest, "estado": "sin tareas todavia"}
    if proc.poll() is None:
        return {"agente": dest, "estado": "trabajando", "avance": cola}
    return {"agente": dest, "estado": "termino", "codigo": proc.returncode, "resultado": cola}


FUNCIONES = {
    "encargar_a_claude": encargar_a_claude,
    "estado_agente": estado_agente,
}

DECLARACIONES = [
    {
        "name": "encargar_a_claude",
        "description": "Lanza una tarea a una sesion de Claude Code local que trabaja en segundo plano. agente 'flujo' (este repo) o 'unreal' (proyecto de Unreal Engine, MYRA). Solo se ejecuta cuando lo pides. Usar cuando el usuario diga 'dile a Unreal/al de acá/a Claude que haga X'.",
        "parameters": {
            "type": "object",
            "properties": {
                "instruccion": {"type": "string", "description": "La tarea completa para Claude."},
                "agente": {"type": "string", "description": "flujo | unreal (acepta tu, aca, ue, cowork, myra)."},
            },
            "required": ["instruccion"],
        },
    },
    {
        "name": "estado_agente",
        "description": "Consulta como va un agente (flujo o unreal): si trabaja o termino, y su avance.",
        "parameters": {
            "type": "object",
            "properties": {"agente": {"type": "string", "description": "flujo | unreal."}},
        },
    },
]
