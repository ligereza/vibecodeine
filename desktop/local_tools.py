"""Herramientas locales READ-ONLY que Gemini puede invocar via function-calling.

Alcance de seguridad deliberado: SOLO lectura, SOLO dentro de PROJECT_ROOT, SIN
ejecucion de codigo/scripts. Gemini corre con la sola autorizacion de la API key
del usuario y sin confirmacion humana por-llamada -- exponerle ejecucion arbitraria
seria un riesgo real (prompt injection via contenido de un archivo leido podria
intentar hacerle pedir una accion destructiva). Si en el futuro se necesita
ejecutar algo, debe ser un tool nuevo, explicito, con confirmacion del usuario
antes de correr -- no agregar aqui sin ese guardrail.
"""
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Nunca leer estos, aunque esten dentro de PROJECT_ROOT
_BLOCKED_NAMES = {"config.json", ".env", ".env.local"}
_BLOCKED_EXTS = {".key", ".pem", ".db", ".sqlite", ".sqlite3"}
_BLOCKED_DIR_PARTS = {".git", "node_modules", "__pycache__"}

_MAX_FILE_BYTES = 200_000
_MAX_SEARCH_HITS = 40
_MAX_SEARCH_FILES = 2000


def _resolve_safe(path: str) -> str:
    """Resuelve path relativo a PROJECT_ROOT y valida que no escape ni toque
    archivos/carpetas bloqueadas. Lanza ValueError si no es seguro."""
    candidate = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    if os.path.commonpath([candidate, PROJECT_ROOT]) != PROJECT_ROOT:
        raise ValueError(f"Path fuera de PROJECT_ROOT, bloqueado: {path}")

    parts = candidate.replace(PROJECT_ROOT, "").split(os.sep)
    if any(p in _BLOCKED_DIR_PARTS for p in parts):
        raise ValueError(f"Path dentro de carpeta bloqueada: {path}")

    basename = os.path.basename(candidate)
    _, ext = os.path.splitext(basename)
    if basename in _BLOCKED_NAMES or ext.lower() in _BLOCKED_EXTS:
        raise ValueError(f"Archivo bloqueado (posible secreto/binario): {path}")

    return candidate


def read_file(path: str) -> str:
    """Lee un archivo de texto dentro del repo. Trunca si es muy grande."""
    try:
        full = _resolve_safe(path)
    except ValueError as e:
        return f"ERROR: {e}"
    if not os.path.isfile(full):
        return f"ERROR: no existe o no es archivo: {path}"
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(_MAX_FILE_BYTES + 1)
    except Exception as e:
        return f"ERROR: no se pudo leer {path}: {e}"
    if len(content) > _MAX_FILE_BYTES:
        content = content[:_MAX_FILE_BYTES] + f"\n...[truncado, archivo mayor a {_MAX_FILE_BYTES} bytes]"
    return content


def list_dir(path: str = ".") -> str:
    """Lista archivos y carpetas dentro de un directorio del repo."""
    try:
        full = _resolve_safe(path)
    except ValueError as e:
        return f"ERROR: {e}"
    if not os.path.isdir(full):
        return f"ERROR: no existe o no es directorio: {path}"
    try:
        entries = sorted(os.listdir(full))
    except Exception as e:
        return f"ERROR: no se pudo listar {path}: {e}"
    entries = [e for e in entries if e not in _BLOCKED_DIR_PARTS]
    lines = []
    for e in entries:
        full_e = os.path.join(full, e)
        tag = "/" if os.path.isdir(full_e) else ""
        lines.append(e + tag)
    return "\n".join(lines) if lines else "(vacio)"


def search_repo(query: str) -> str:
    """Busca un texto literal en archivos de texto del repo (case-insensitive).
    Devuelve hasta _MAX_SEARCH_HITS coincidencias como 'archivo:linea: contenido'."""
    if not query or not query.strip():
        return "ERROR: query vacia"
    query_lower = query.lower()
    hits = []
    files_scanned = 0
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        dirnames[:] = [d for d in dirnames if d not in _BLOCKED_DIR_PARTS]
        for fname in filenames:
            if files_scanned >= _MAX_SEARCH_FILES or len(hits) >= _MAX_SEARCH_HITS:
                break
            _, ext = os.path.splitext(fname)
            if fname in _BLOCKED_NAMES or ext.lower() in _BLOCKED_EXTS:
                continue
            full = os.path.join(dirpath, fname)
            files_scanned += 1
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        if query_lower in line.lower():
                            rel = os.path.relpath(full, PROJECT_ROOT)
                            hits.append(f"{rel}:{i}: {line.strip()[:200]}")
                            if len(hits) >= _MAX_SEARCH_HITS:
                                break
            except Exception:
                continue
        if files_scanned >= _MAX_SEARCH_FILES or len(hits) >= _MAX_SEARCH_HITS:
            break
    if not hits:
        return f"Sin resultados para '{query}' ({files_scanned} archivos escaneados)."
    return "\n".join(hits)


# Registro de tools: nombre -> (funcion, declaracion JSON Schema para Gemini)
FUNCTION_DECLARATIONS = [
    {
        "name": "read_file",
        "description": "Lee el contenido de un archivo de texto dentro del repo (solo lectura, path relativo a la raiz del repo).",
        "parameters": {
            "type": "OBJECT",
            "properties": {"path": {"type": "STRING", "description": "Path relativo del archivo, ej. 'desktop/gui.py'"}},
            "required": ["path"]
        }
    },
    {
        "name": "list_dir",
        "description": "Lista archivos y subcarpetas de un directorio dentro del repo (solo lectura).",
        "parameters": {
            "type": "OBJECT",
            "properties": {"path": {"type": "STRING", "description": "Path relativo del directorio, ej. 'desktop' o '.' para la raiz"}},
            "required": []
        }
    },
    {
        "name": "search_repo",
        "description": "Busca un texto literal (case-insensitive) en los archivos del repo, devuelve archivo:linea: contenido.",
        "parameters": {
            "type": "OBJECT",
            "properties": {"query": {"type": "STRING", "description": "Texto a buscar"}},
            "required": ["query"]
        }
    },
]

TOOL_DISPATCH = {
    "read_file": read_file,
    "list_dir": list_dir,
    "search_repo": search_repo,
}
