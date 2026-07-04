"""Puente CODE -> Claude Code (CLI headless), BAJO DEMANDA. Proyectos configurables.

No se engancha a un chat abierto: cada orden lanza un 'claude -p ...' NUEVO en la
CARPETA del proyecto elegido, en segundo plano y con su log. En reposo no gasta
tokens (solo corre cuando das una orden).

Los proyectos NO estan fijos en el codigo: se leen de proyectos.json (local,
ignorado por git). Asi puedes agregar/cambiar proyectos sin reprogramar. Ver
proyectos.example.json.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

CLAUDE_CMD = os.environ.get("CLAUDE_CMD", "claude")
CLAUDE_PERM = os.environ.get("CLAUDE_PERMISSION_MODE", "acceptEdits")

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]                                    # C:\IA\flujo
_LOGDIR = _HERE / "agentes"
# ESTADO compartido: bitacora que dejan agentes y sesiones (empezo/termino una
# labor). Lo escriben procesos/hooks gratis; CODE solo lo LEE cuando preguntas.
_ESTADO = _HERE / "estado" / "ESTADO.md"


def marcar_estado(proyecto: str, evento: str, detalle: str = "") -> None:
    """Deja una linea en la bitacora ESTADO (empezo / termino / lo que sea)."""
    _ESTADO.parent.mkdir(parents=True, exist_ok=True)
    sello = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    corto = (detalle or "").strip().splitlines()[0][:120] if detalle else ""
    with open(_ESTADO, "a", encoding="utf-8") as fh:
        fh.write(f"- [{sello}] {proyecto}: {evento}" + (f" - {corto}" if corto else "") + "\n")

# Alias de voz -> nombre canonico del proyecto (para hablar natural).
_ALIAS = {
    "tu": "flujo", "aca": "flujo", "repo": "flujo", "code": "flujo", "consola": "flujo",
    "ue": "unreal", "cowork": "unreal", "motor": "unreal", "engine": "unreal",
    "3d": "unreal", "myra": "unreal",
}

_procs: dict[str, subprocess.Popen] = {}


def _cargar_proyectos() -> dict[str, Path]:
    """Lee proyectos.json; si no existe, usa un default razonable."""
    cfg = _HERE / "proyectos.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            return {k.lower(): Path(v) for k, v in data.items()}
        except Exception:  # noqa: BLE001
            pass
    return {
        "flujo": _REPO,
        "unreal": Path(os.environ.get("VIBO_UNREAL_DIR", r"C:\ARICA\MYRA")),
    }


def _norm(nombre) -> str | None:
    proyectos = _cargar_proyectos()
    n = str(nombre).strip().lower()
    if n in proyectos:
        return n
    alias = _ALIAS.get(n)
    return alias if alias in proyectos else None


def _log_path(nombre: str) -> Path:
    return _LOGDIR / f"agente_{nombre}.log"


def _resolver_claude() -> str | None:
    """Ubica el CLI de Claude. En Windows suele ser claude.cmd (npm global), que
    no se puede ejecutar directo: hay que resolver la ruta y correrlo con cmd /c."""
    c = CLAUDE_CMD
    if os.path.sep in c or os.path.isabs(c):
        return c if Path(c).exists() else None
    hallado = shutil.which(c)  # respeta PATHEXT: encuentra claude.cmd / .exe
    if hallado:
        return hallado
    # fallback conocido: instalacion npm global
    npm = Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd"
    return str(npm) if npm.exists() else None


def _comando(exe: str, instruccion: str) -> list[str]:
    base = [exe, "-p", instruccion, "--permission-mode", CLAUDE_PERM]
    # .cmd/.bat en Windows: CreateProcess no los corre directo -> envolver en cmd /c
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", *base]
    return base


def listar_proyectos() -> dict:
    """Dice a que proyectos puede mandar CODE y quien esta trabajando ahora."""
    proyectos = _cargar_proyectos()
    salida = []
    for nombre, carpeta in proyectos.items():
        proc = _procs.get(nombre)
        estado = "trabajando" if (proc and proc.poll() is None) else "libre"
        salida.append({"nombre": nombre, "carpeta": str(carpeta),
                       "existe": carpeta.exists(), "estado": estado})
    return {"proyectos": salida}


def encargar_a_claude(instruccion: str, agente: str = "flujo") -> dict:
    """Lanza a Claude (CLI headless) una tarea en la carpeta del proyecto, en
    segundo plano. 'agente' es un nombre de proyectos.json (flujo, unreal, ...).
    Solo corre cuando lo pides: en reposo no gasta tokens."""
    dest = _norm(agente)
    if not dest:
        validos = list(_cargar_proyectos().keys())
        return {"error": f"proyecto desconocido: {agente}", "validos": validos}
    carpeta = _cargar_proyectos()[dest]
    if not carpeta.exists():
        return {"error": f"no existe la carpeta de {dest}: {carpeta}"}
    prev = _procs.get(dest)
    if prev and prev.poll() is None:
        return {"ocupado": True, "agente": dest,
                "mensaje": f"{dest} sigue trabajando; espera a que termine"}
    exe = _resolver_claude()
    if not exe:
        return {"error": "no encuentro el CLI de Claude. Pon la ruta completa en "
                         "CLAUDE_CMD del .env (ej: C:\\Users\\<tu>\\AppData\\Roaming\\npm\\claude.cmd)."}
    _LOGDIR.mkdir(exist_ok=True)
    try:
        fh = open(_log_path(dest), "w", encoding="utf-8")
        proc = subprocess.Popen(
            _comando(exe, instruccion),
            cwd=str(carpeta), stdout=fh, stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        return {"error": f"no se pudo ejecutar '{exe}'. Ajusta CLAUDE_CMD en el .env."}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    _procs[dest] = proc
    marcar_estado(dest, "empezo", instruccion)

    def _vigilar_fin(nombre: str, p: subprocess.Popen):
        p.wait()
        marcar_estado(nombre, "termino", _leer_log(nombre, 5))

    threading.Thread(target=_vigilar_fin, args=(dest, proc), daemon=True).start()
    return {"lanzado": True, "agente": dest, "carpeta": str(carpeta), "instruccion": instruccion.strip()}


def estado_agente(agente: str = "flujo") -> dict:
    """Dice si un proyecto sigue trabajando o termino (resumen del avance)."""
    dest = _norm(agente)
    if not dest:
        return {"error": f"proyecto desconocido: {agente}", "validos": list(_cargar_proyectos().keys())}
    proc = _procs.get(dest)
    if proc is None:
        return {"agente": dest, "estado": "sin tareas todavia"}
    cola = _leer_log(dest, 8)
    if proc.poll() is None:
        return {"agente": dest, "estado": "trabajando", "avance": cola}
    return {"agente": dest, "estado": "termino", "codigo": proc.returncode, "resultado": cola}


def detener_agente(agente: str = "flujo") -> dict:
    """Detiene un agente que CODE lanzo (mata SU proceso y sus hijos). Solo puede
    parar lo que CODE mismo arranco, no procesos externos."""
    dest = _norm(agente)
    if not dest:
        return {"error": f"proyecto desconocido: {agente}", "validos": list(_cargar_proyectos().keys())}
    proc = _procs.get(dest)
    if proc is None or proc.poll() is not None:
        return {"agente": dest, "detenido": False, "mensaje": f"{dest} no tiene un proceso activo"}
    try:
        if os.name == "nt":
            # /T mata el arbol (el claude headless puede tener hijos)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True, timeout=10)
        else:
            proc.terminate()
    except Exception as e:  # noqa: BLE001
        return {"agente": dest, "detenido": False, "error": str(e)}
    return {"agente": dest, "detenido": True}


def leer_respuesta(agente: str = "flujo") -> dict:
    """Devuelve la respuesta/salida final de un proyecto para leerla en voz alta."""
    dest = _norm(agente)
    if not dest:
        return {"error": f"proyecto desconocido: {agente}", "validos": list(_cargar_proyectos().keys())}
    texto = _leer_log(dest, 40)
    return {"agente": dest, "respuesta": texto or "(todavia no hay respuesta)"}


def leer_estado(lineas: int = 15) -> dict:
    """Lee la bitacora ESTADO: que empezaron o terminaron los agentes y sesiones.
    Usar cuando el usuario pregunte 'que ha pasado', 'novedades', 'que hicieron'."""
    if not _ESTADO.exists():
        return {"estado": "(sin novedades todavia)"}
    todas = _ESTADO.read_text(encoding="utf-8", errors="replace").splitlines()
    n = max(1, min(int(lineas), 50))
    return {"estado": "\n".join(todas[-n:])}


def _leer_log(nombre: str, n: int) -> str:
    log = _log_path(nombre)
    if not log.exists():
        return ""
    lineas = log.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lineas[-n:])


FUNCIONES = {
    "listar_proyectos": listar_proyectos,
    "encargar_a_claude": encargar_a_claude,
    "estado_agente": estado_agente,
    "detener_agente": detener_agente,
    "leer_respuesta": leer_respuesta,
    "leer_estado": leer_estado,
}

DECLARACIONES = [
    {
        "name": "listar_proyectos",
        "description": "Dice a que proyectos/sesiones puede mandar ordenes CODE y cual esta trabajando ahora. Usar cuando el usuario pregunte 'a quienes le puedo mandar', 'quien esta trabajando'.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "encargar_a_claude",
        "description": "Lanza una tarea a una sesion de Claude Code local que trabaja en segundo plano, en la carpeta del proyecto. 'agente' es un nombre de proyecto (flujo, unreal, o el que sea de proyectos.json). Solo corre cuando lo pides.",
        "parameters": {
            "type": "object",
            "properties": {
                "instruccion": {"type": "string", "description": "La tarea completa para Claude."},
                "agente": {"type": "string", "description": "nombre del proyecto: flujo | unreal | ..."},
            },
            "required": ["instruccion"],
        },
    },
    {
        "name": "estado_agente",
        "description": "Consulta como va un proyecto: si trabaja o termino, y su avance.",
        "parameters": {
            "type": "object",
            "properties": {"agente": {"type": "string", "description": "nombre del proyecto."}},
        },
    },
    {
        "name": "detener_agente",
        "description": "Detiene un agente que CODE lanzo (mata su proceso). Solo sirve para lo que CODE mismo arranco, no procesos externos. Usar cuando el usuario diga 'para el agente X', 'detene Unreal', 'cancela eso'.",
        "parameters": {
            "type": "object",
            "properties": {"agente": {"type": "string", "description": "nombre del proyecto."}},
        },
    },
    {
        "name": "leer_respuesta",
        "description": "Trae la respuesta/salida final de un proyecto para leersela en voz alta al usuario.",
        "parameters": {
            "type": "object",
            "properties": {"agente": {"type": "string", "description": "nombre del proyecto."}},
        },
    },
    {
        "name": "leer_estado",
        "description": "Lee la bitacora ESTADO (que empezaron o terminaron los agentes y sesiones). Usar cuando el usuario pregunte 'que ha pasado', 'novedades', 'que hicieron'.",
        "parameters": {
            "type": "object",
            "properties": {"lineas": {"type": "integer", "description": "cuantas lineas recientes (por defecto 15)."}},
        },
    },
]
