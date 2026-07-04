"""Digest mecanico del repo (0 tokens, sin ningun modelo).

Recorre el repo e imprime un mapa compacto: arbol de carpetas + archivos clave con
su primera linea util (titulo/docstring). Sirve como CONTEXTO barato para pasarle a
Claude/agentes en vez de que exploren (ahi se van ~500k tokens). Es os.walk + lectura
de encabezados: no llama a Gemini ni a Claude.

Uso:
    py contexto_repo.py                 # imprime el mapa
    py contexto_repo.py > contexto.txt  # lo guardas para pasarlo como contexto
"""
from __future__ import annotations

import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
              ".pytest_cache", "dist", "build", "agentes", "estado", "buzon",
              "checkpoints"}


def _skip(d: str) -> bool:
    # salta ocultos (.), internos/backups (_) y la lista negra
    return d in _SKIP_DIRS or d.startswith(".") or d.startswith("_")
# carpetas que son SALIDA generada (no tocar / no explorar a mano)
_GENERADAS = {"jobs", "projects", "datadrops", "context/*.html"}
_KEY_NAMES = {"README.md", "SKILL.md", "pyproject.toml", "cli.py", "CLAUDE.md",
              "AGENTS.md", "REPO_MAP.md"}
_MAXDEPTH = 3


def _primera_linea_util(p: Path) -> str:
    try:
        for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = ln.strip().lstrip("#").lstrip('"').strip()
            if s and not s.startswith(("---", "import", "from", "#!/")):
                return s[:90]
    except Exception:  # noqa: BLE001
        return ""
    return ""


def _arbol():
    print("== ARBOL (carpetas, prof " + str(_MAXDEPTH) + ") ==")
    for root, dirs, _files in os.walk(_REPO):
        rel = Path(root).relative_to(_REPO)
        depth = len(rel.parts)
        dirs[:] = sorted(d for d in dirs if not _skip(d))
        if depth >= _MAXDEPTH:
            dirs[:] = []
        if str(rel) == ".":
            continue
        print("  " * (depth - 1) + "- " + rel.parts[-1] + "/")


def _clave():
    print("\n== ARCHIVOS CLAVE (con su titulo) ==")
    vistos = 0
    for root, dirs, files in os.walk(_REPO):
        dirs[:] = [d for d in dirs if not _skip(d)]
        for f in sorted(files):
            if f in _KEY_NAMES:
                p = Path(root) / f
                rel = p.relative_to(_REPO)
                print(f"  {rel}  ->  {_primera_linea_util(p)}")
                vistos += 1
    if not vistos:
        print("  (ninguno)")


def main():
    print(f"# CONTEXTO DEL REPO: {_REPO}\n# (digest mecanico, 0 tokens)\n")
    _arbol()
    _clave()
    print("\n== ZONAS GENERADAS / NO TOCAR A MANO ==")
    for z in sorted(_GENERADAS):
        print(f"  {z}  (salida generada; leer solo si el pipeline lo requiere)")
    print("\n== COMO USAR ESTE MAPA ==")
    print("  Pasaselo a un agente como 'contexto' o leelo en vez de explorar.")
    print("  Para el detalle de un archivo puntual: leelo directo (barato).")


if __name__ == "__main__":
    main()
