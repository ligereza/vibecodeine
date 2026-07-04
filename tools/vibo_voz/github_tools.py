"""Herramientas de GitHub SOLO LECTURA para Vibo Voz.

Cada funcion hace una consulta superficial (rapida, sin clonar nada) a la API
REST de GitHub y devuelve un dict simple que Gemini pueda leer en voz alta.
El token se lee de la variable de entorno GITHUB_TOKEN y solo necesita permisos
de lectura (Contents / Issues / Metadata).
"""
from __future__ import annotations

import os
import datetime as _dt

import requests

_API = "https://api.github.com"
_TIMEOUT = 15


def _cfg():
    owner = os.environ.get("GITHUB_OWNER", "ligereza")
    repo = os.environ.get("GITHUB_REPO", "vibecodeine")
    token = os.environ.get("GITHUB_TOKEN", "")
    return owner, repo, token


def _headers():
    _, _, token = _cfg()
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get(path: str, params: dict | None = None):
    r = requests.get(f"{_API}{path}", headers=_headers(), params=params, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


# --- Herramientas que Vibo puede invocar por voz -------------------------------

def pedidos_abiertos() -> dict:
    """Lista los issues abiertos del repo (los 'pedidos'). Excluye pull requests."""
    owner, repo, _ = _cfg()
    try:
        data = _get(f"/repos/{owner}/{repo}/issues", {"state": "open", "per_page": 30})
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    pedidos = [
        {"numero": it["number"], "titulo": it["title"], "abierto": it["created_at"][:10]}
        for it in data
        if "pull_request" not in it
    ]
    return {"total": len(pedidos), "pedidos": pedidos}


def existe(consulta: str) -> dict:
    """Busca de forma superficial si algo ya existe en el repo: primero por
    nombre de archivo/ruta y luego por contenido (code search). 'consulta' es
    lo que el usuario describe: un tema, un producto, un nombre de pieza."""
    owner, repo, _ = _cfg()
    resultados: list[dict] = []
    # 1) por nombre de archivo
    try:
        f = _get("/search/code", {"q": f"{consulta} in:path repo:{owner}/{repo}", "per_page": 5})
        for it in f.get("items", []):
            resultados.append({"tipo": "archivo", "ruta": it["path"]})
    except Exception:  # noqa: BLE001
        pass
    # 2) por contenido
    if len(resultados) < 5:
        try:
            c = _get("/search/code", {"q": f"{consulta} repo:{owner}/{repo}", "per_page": 5})
            for it in c.get("items", []):
                if not any(r["ruta"] == it["path"] for r in resultados):
                    resultados.append({"tipo": "contenido", "ruta": it["path"]})
        except Exception:  # noqa: BLE001
            pass
    return {"consulta": consulta, "encontrado": bool(resultados), "coincidencias": resultados[:8]}


def cambios_recientes(cantidad: int = 5) -> dict:
    """Devuelve los ultimos commits (que cambio ultimamente en el repo)."""
    owner, repo, _ = _cfg()
    try:
        data = _get(f"/repos/{owner}/{repo}/commits", {"per_page": max(1, min(int(cantidad), 15))})
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    cambios = [
        {
            "fecha": c["commit"]["author"]["date"][:10],
            "mensaje": c["commit"]["message"].splitlines()[0],
        }
        for c in data
    ]
    return {"total": len(cambios), "cambios": cambios}


def guardar_idea(texto: str) -> dict:
    """Guarda una idea del usuario en un archivo local (no toca GitHub).
    La relacion con el rubro la hace Vibo en su respuesta hablada."""
    ruta = os.path.join(os.path.dirname(__file__), "ideas_capturadas.md")
    sello = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ruta, "a", encoding="utf-8") as fh:
        fh.write(f"- [{sello}] {texto.strip()}\n")
    return {"guardado": True, "archivo": "ideas_capturadas.md"}


# Mapa nombre -> funcion, para el despacho de tool-calls de la Live API.
FUNCIONES = {
    "pedidos_abiertos": pedidos_abiertos,
    "existe": existe,
    "cambios_recientes": cambios_recientes,
    "guardar_idea": guardar_idea,
}

# Declaraciones para Gemini (que herramientas existen y sus parametros).
DECLARACIONES = [
    {
        "name": "pedidos_abiertos",
        "description": "Lista los issues abiertos del repo, es decir los pedidos pendientes.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "existe",
        "description": "Revisa de forma superficial si un tema, pieza o producto ya existe en el repo.",
        "parameters": {
            "type": "object",
            "properties": {
                "consulta": {"type": "string", "description": "Lo que el usuario quiere verificar."}
            },
            "required": ["consulta"],
        },
    },
    {
        "name": "cambios_recientes",
        "description": "Muestra los ultimos commits: que cambio ultimamente.",
        "parameters": {
            "type": "object",
            "properties": {
                "cantidad": {"type": "integer", "description": "Cuantos commits traer (por defecto 5)."}
            },
        },
    },
    {
        "name": "guardar_idea",
        "description": "Guarda una idea dictada por el usuario para no perderla.",
        "parameters": {
            "type": "object",
            "properties": {
                "texto": {"type": "string", "description": "La idea, tal cual la dicto el usuario."}
            },
            "required": ["texto"],
        },
    },
]
