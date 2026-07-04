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
import time
from pathlib import Path

CLAUDE_CMD = os.environ.get("CLAUDE_CMD", "claude")
CLAUDE_PERM = os.environ.get("CLAUDE_PERMISSION_MODE", "acceptEdits")
# Ahorro: modelo mas barato para el secretario (ej. haiku) y reutilizar contexto.
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "").strip()          # vacio = default de la cuenta
CLAUDE_CONTINUE = os.environ.get("CLAUDE_CONTINUE", "").strip() in ("1", "true", "si", "yes")

# Anti-bucle: no mas de N ordenes por ventana de segundos, y un solo secretario a la vez.
_MAX_ORDENES = 5
_VENTANA_SEG = 60
_lanzamientos: list[float] = []

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

# Se antepone a cada orden. Ahorro + anti-bucle + no preguntar.
_PREAMBULO = (
    "Eres el 'secretario': un Claude headless que ejecuta UNA orden y termina. Reglas:\n"
    "- NO puedes preguntar de vuelta (nadie te lee). Si algo es ambiguo, elige lo mas "
    "razonable y NO destructivo, hazlo, y reporta en 2-3 lineas que hiciste y que asumiste.\n"
    "- AHORRO: si un operador te da CONTEXTO ya preparado, CONFIA en el y NO re-explores el "
    "repo. Si la tarea es simple, no hagas el onboarding completo (no leas handoffs, airdrop, "
    "repo_map). Lee solo lo minimo indispensable.\n"
    "- ANTI-BUCLE: haz la tarea UNA sola vez y termina. No lances otros procesos, no invoques "
    "otros agentes, no te repitas."
)


def _armar_prompt(instruccion: str, contexto: str) -> str:
    partes = [_PREAMBULO]
    if contexto and contexto.strip():
        partes.append("CONTEXTO ya preparado por el operador (usalo, NO re-explores el repo "
                      "salvo que falte algo critico):\n" + contexto.strip())
    partes.append("Tarea: " + instruccion.strip())
    return "\n\n".join(partes)


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


def _pid_path(nombre: str) -> Path:
    return _LOGDIR / f"agente_{nombre}.pid"


def _es_proceso_agente(pid: int) -> bool:
    """Confirma que el PID sigue vivo y es un proceso de Claude/node (evita matar
    otra cosa si el PID se reciclo)."""
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                             capture_output=True, text=True, timeout=10).stdout.lower()
    except Exception:  # noqa: BLE001
        return False
    return "claude.exe" in out or "node.exe" in out or "cmd.exe" in out


def supervisar_procesos() -> dict:
    """Capataz: da la foto de TODOS los procesos claude de la maquina, distingue
    sesiones (y sus ayudantes) de los agentes que lanzo la voz, y avisa si hay
    agentes colgados. Es solo lectura; para limpiar usa limpiar_procesos."""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='claude.exe'\" | "
             "Select-Object ProcessId,ParentProcessId,@{n='MB';e={[int]($_.WorkingSetSize/1MB)}} | "
             "ConvertTo-Json -Compress"],
            capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    if not out:
        return {"total": 0, "resumen": "No hay procesos de Claude corriendo."}
    try:
        data = json.loads(out)
    except Exception:  # noqa: BLE001
        return {"error": "no pude leer la lista de procesos"}
    if isinstance(data, dict):
        data = [data]
    pids = {int(d["ProcessId"]) for d in data}
    agentes_pids = set()
    for pf in _LOGDIR.glob("agente_*.pid"):
        try:
            agentes_pids.add(int(pf.read_text(encoding="utf-8").strip()))
        except Exception:  # noqa: BLE001
            pass
    raices = [d for d in data if int(d["ParentProcessId"]) not in pids]
    agentes_vivos = [int(d["ProcessId"]) for d in data if int(d["ProcessId"]) in agentes_pids]
    total = len(data)
    resumen = (f"{total} procesos claude: ~{len(raices)} sesion(es) con sus ayudantes, "
               + (f"{len(agentes_vivos)} agente(s) de voz activo(s)." if agentes_vivos
                  else "ningun agente de voz colgado."))
    return {"total": total, "sesiones_aprox": len(raices),
            "agentes_voz_activos": agentes_vivos, "resumen": resumen}


def limpiar_procesos() -> dict:
    """Artefacto de limpieza: mata SOLO los agentes que el sistema de voz lanzo y
    quedaron abandonados (via sus archivos .pid). NUNCA toca tus sesiones abiertas."""
    _LOGDIR.mkdir(exist_ok=True)
    matados, ya_muertos = [], []
    for pf in _LOGDIR.glob("agente_*.pid"):
        try:
            pid = int(pf.read_text(encoding="utf-8").strip())
        except Exception:  # noqa: BLE001
            pf.unlink(missing_ok=True)
            continue
        if _es_proceso_agente(pid):
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                               capture_output=True, timeout=10)
                matados.append(pid)
            except Exception:  # noqa: BLE001
                pass
        else:
            ya_muertos.append(pid)
        pf.unlink(missing_ok=True)
    # limpiar referencias en memoria de procesos ya terminados
    for n in list(_procs):
        if _procs[n].poll() is not None:
            del _procs[n]
    return {"matados": matados, "ya_estaban_muertos": ya_muertos, "total_matados": len(matados)}


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
    if CLAUDE_MODEL:            # modelo barato para ahorrar
        base += ["--model", CLAUDE_MODEL]
    if CLAUDE_CONTINUE:        # reutiliza contexto de la sesion anterior
        base += ["--continue"]
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


def encargar_a_claude(instruccion: str, agente: str = "flujo", contexto: str = "") -> dict:
    """Lanza a Claude (CLI headless) una tarea en la carpeta del proyecto, en
    segundo plano. 'agente' es un nombre de proyectos.json (flujo, unreal, ...).
    'contexto' es info ya preparada por el operador (Gemini) para que Claude NO
    tenga que re-explorar el repo (ahorro grande). Solo corre cuando lo pides."""
    dest = _norm(agente)
    if not dest:
        validos = list(_cargar_proyectos().keys())
        return {"error": f"proyecto desconocido: {agente}", "validos": validos}
    carpeta = _cargar_proyectos()[dest]
    if not carpeta.exists():
        return {"error": f"no existe la carpeta de {dest}: {carpeta}"}
    # Un solo secretario a la vez (revisa TODOS los procesos, no solo este destino).
    for nombre, p in _procs.items():
        if p.poll() is None:
            return {"ocupado": True, "agente": nombre,
                    "mensaje": f"el secretario esta ocupado con {nombre}; espera a que termine"}
    # Anti-bucle: no mas de _MAX_ORDENES en _VENTANA_SEG segundos.
    ahora = time.time()
    _lanzamientos[:] = [t for t in _lanzamientos if ahora - t < _VENTANA_SEG]
    if len(_lanzamientos) >= _MAX_ORDENES:
        return {"error": "muchas ordenes seguidas (freno anti-bucle); espera un momento antes de otra."}
    exe = _resolver_claude()
    if not exe:
        return {"error": "no encuentro el CLI de Claude. Pon la ruta completa en "
                         "CLAUDE_CMD del .env (ej: C:\\Users\\<tu>\\AppData\\Roaming\\npm\\claude.cmd)."}
    _LOGDIR.mkdir(exist_ok=True)
    try:
        fh = open(_log_path(dest), "w", encoding="utf-8")
        proc = subprocess.Popen(
            _comando(exe, _armar_prompt(instruccion, contexto)),
            cwd=str(carpeta), stdout=fh, stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        return {"error": f"no se pudo ejecutar '{exe}'. Ajusta CLAUDE_CMD en el .env."}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    _procs[dest] = proc
    _lanzamientos.append(ahora)
    try:
        _pid_path(dest).write_text(str(proc.pid), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    marcar_estado(dest, "empezo", instruccion)

    def _vigilar_fin(nombre: str, p: subprocess.Popen):
        p.wait()
        _pid_path(nombre).unlink(missing_ok=True)  # ya termino: quitar su .pid
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


_SENSIBLES = ("id_rsa", "id_ed25519", ".pem", ".key", ".p12", ".pfx",
              "credential", "secret", "token", ".env")


def leer_archivo(ruta: str, lineas: int = 120) -> dict:
    """Lee un archivo de texto del repo o de un proyecto configurado, SIN llamar a
    Claude. Por seguridad: solo dentro de esas carpetas y nunca archivos de
    credenciales (asi Gemini no puede leer .env, llaves, etc. a la nube)."""
    p = (Path(ruta) if Path(ruta).is_absolute() else _REPO / ruta).resolve()
    # 1) solo dentro del repo o de los proyectos configurados
    permitidas = [_REPO.resolve()] + [d.resolve() for d in _cargar_proyectos().values()]
    if not any(p == base or base in p.parents for base in permitidas):
        return {"error": "por seguridad solo leo archivos dentro del repo o de los proyectos configurados."}
    # 2) nunca archivos de credenciales
    low = p.name.lower()
    if low == ".env" or any(s in low for s in _SENSIBLES):
        return {"error": "por seguridad no leo archivos de credenciales (.env, llaves, secrets)."}
    if not p.exists() or not p.is_file():
        return {"error": f"no existe el archivo: {p}"}
    try:
        txt = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    n = max(1, min(int(lineas), 300))
    return {"archivo": str(p), "total_lineas": len(txt), "contenido": "\n".join(txt[:n])}


def escribir_archivo(ruta: str, texto: str, modo: str = "agregar") -> dict:
    """Crea o agrega texto a un archivo SIN llamar a Claude (barato, para guardar
    notas/prompts/textos). modo: 'agregar' (default) o 'nuevo'. Restringido al
    repo/proyectos y bloquea credenciales; en 'nuevo' no pisa archivos existentes."""
    p = (Path(ruta) if Path(ruta).is_absolute() else _REPO / ruta).resolve()
    permitidas = [_REPO.resolve()] + [d.resolve() for d in _cargar_proyectos().values()]
    if not any(p == base or base in p.parents for base in permitidas):
        return {"error": "por seguridad solo escribo dentro del repo o de los proyectos configurados."}
    low = p.name.lower()
    if low == ".env" or any(s in low for s in _SENSIBLES):
        return {"error": "por seguridad no escribo sobre archivos de credenciales."}
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        if modo == "nuevo":
            if p.exists() and p.stat().st_size > 0:
                return {"error": f"{p.name} ya existe; usa modo 'agregar' para no pisarlo."}
            p.write_text(texto, encoding="utf-8")
        else:
            with open(p, "a", encoding="utf-8") as fh:
                fh.write(texto if texto.endswith("\n") else texto + "\n")
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    return {"escrito": True, "archivo": str(p), "modo": modo}


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
    "leer_archivo": leer_archivo,
    "escribir_archivo": escribir_archivo,
    "supervisar_procesos": supervisar_procesos,
    "limpiar_procesos": limpiar_procesos,
}

DECLARACIONES = [
    {
        "name": "listar_proyectos",
        "description": "Dice a que proyectos/sesiones puede mandar ordenes CODE y cual esta trabajando ahora. Usar cuando el usuario pregunte 'a quienes le puedo mandar', 'quien esta trabajando'.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "encargar_a_claude",
        "description": "Lanza una tarea a una sesion de Claude Code local (secretario) que trabaja en segundo plano, en la carpeta del proyecto. Antes de llamar, actua como OPERADOR: junta el contexto necesario con tus herramientas (leer_archivo, existe...), reducelo a lo esencial, y pasalo en 'contexto' para que Claude NO re-explore el repo (gran ahorro).",
        "parameters": {
            "type": "object",
            "properties": {
                "instruccion": {"type": "string", "description": "La tarea completa para Claude."},
                "agente": {"type": "string", "description": "nombre del proyecto: flujo | unreal | ..."},
                "contexto": {"type": "string", "description": "Contexto YA reducido (rutas, snippets, datos) para que Claude no re-explore. Mientras mas preciso, mas barato."},
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
    {
        "name": "leer_archivo",
        "description": "Lee un archivo de texto del repo SIN llamar a Claude (barato). Usalo para REVISAR contenido tu mismo antes de decidir si de verdad necesitas al secretario Claude.",
        "parameters": {
            "type": "object",
            "properties": {
                "ruta": {"type": "string", "description": "ruta del archivo (relativa al repo o absoluta)."},
                "lineas": {"type": "integer", "description": "cuantas lineas leer (por defecto 120)."},
            },
            "required": ["ruta"],
        },
    },
    {
        "name": "escribir_archivo",
        "description": "Guarda/agrega texto en un archivo SIN llamar a Claude (barato). Usalo para guardar notas, prompts o textos que dicte el usuario. NO uses el secretario Claude solo para escribir texto.",
        "parameters": {
            "type": "object",
            "properties": {
                "ruta": {"type": "string", "description": "ruta del archivo (relativa al repo o absoluta)."},
                "texto": {"type": "string", "description": "el contenido a guardar."},
                "modo": {"type": "string", "description": "'agregar' (default) o 'nuevo'."},
            },
            "required": ["ruta", "texto"],
        },
    },
    {
        "name": "supervisar_procesos",
        "description": "Da la foto de todos los procesos de Claude: cuantas sesiones, cuantos agentes de voz, si hay colgados. Solo lectura. Usar cuando pregunte 'que hay corriendo', 'cuantos claude tengo', 'como esta la maquina'.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "limpiar_procesos",
        "description": "Limpia (mata) los agentes que el sistema de voz lanzo y quedaron abandonados. Seguro: NO toca las sesiones de Claude que el usuario abrio. Usar cuando pida 'limpia procesos', 'mata lo colgado', 'limpieza'.",
        "parameters": {"type": "object", "properties": {}},
    },
]
