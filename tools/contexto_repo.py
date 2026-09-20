"""Digest mecanico del repo (0 tokens, sin ningun modelo).

Recorre el repo e imprime un mapa compacto: arbol de carpetas + archivos clave con
su primera linea util (titulo/docstring). Sirve como CONTEXTO barato para pasarle a
Claude/agentes en vez de que exploren (ahi se van ~500k tokens). Es os.walk + lectura
de encabezados: no llama a Gemini ni a Claude.

Uso:
    py tools/contexto_repo.py                         # mapa legible existente
    py tools/contexto_repo.py --json --root /ruta     # contexto vivo estructurado
    py tools/contexto_repo.py --json --query "hub RD"

El modo JSON no escribe archivos. Une el estado Git del root solicitado con el
indice AST existente de FLUJO: archivos Python, simbolos, imports, llamadas,
efectos, entrypoints y consumidores estaticos (``imported_by``). No interpreta
prosa ni convierte el resultado en una lista de tareas.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
              ".pytest_cache", "dist", "build", "agentes", "estado", "buzon",
              "checkpoints", "state", "actions-runner", "WIN", "curatoria_inbox",
              "RD", "OneDrive", "GoogleDrive", "Documents", "Documentos",
              "Desktop", "Escritorio", "Downloads", "Descargas", "Pictures",
              "Imágenes", "Videos", "Vídeos", "Music", "Música", "Público",
              "portfolio_media", "n8n-local", "searxng"}


def _skip(d: str) -> bool:
    # salta ocultos (.), internos/backups (_) y la lista negra
    return d in _SKIP_DIRS or d.startswith(".") or d.startswith("_")
# carpetas que son SALIDA generada (no tocar / no explorar a mano)
_GENERADAS = {"jobs", "projects", "datadrops", "context/*.html"}
_KEY_NAMES = {"SKILL.md", "pyproject.toml", "cli.py"}
_MAXDEPTH = 3


def _git(root: Path, *args: str) -> str:
    """Run one bounded read-only Git query and return stdout or empty."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (result.stdout or "").strip()


def _git_state(root: Path) -> dict[str, object]:
    """Return current checkout facts without treating prose as authority."""
    requested = root.expanduser().resolve()
    git_root_raw = _git(requested, "rev-parse", "--show-toplevel")
    if not git_root_raw:
        return {
            "available": False,
            "requested_root": str(requested),
            "reason": "not_a_git_checkout_or_git_unavailable",
        }
    git_root = Path(git_root_raw).resolve()
    status = _git(git_root, "status", "--short")
    remotes = {}
    for line in _git(git_root, "remote", "-v").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] not in remotes:
            remotes[fields[0]] = fields[1]
    upstream = _git(git_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    ahead = behind = None
    if upstream:
        counts = _git(git_root, "rev-list", "--left-right", "--count", "HEAD...@{upstream}").split()
        if len(counts) == 2 and all(value.isdigit() for value in counts):
            ahead, behind = (int(counts[0]), int(counts[1]))
    changed = []
    for line in status.splitlines():
        if len(line) >= 4:
            changed.append({"xy": line[:2], "path": line[3:]})
    return {
        "available": True,
        "requested_root": str(requested),
        "git_root": str(git_root),
        "remote": remotes,
        "branch": _git(git_root, "branch", "--show-current"),
        "head": _git(git_root, "rev-parse", "HEAD"),
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "clean": not changed,
        "changed": changed,
    }


def _load_code_index_module() -> object | None:
    """Load the existing AST indexer without installing or importing a repo."""
    candidates = [
        _REPO / "flujo" / "src" / "flujo" / "index" / "code_index.py",
        _REPO / "src" / "flujo" / "index" / "code_index.py",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("mak_code_index", path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except (OSError, ImportError, SyntaxError, AttributeError):
            continue
    return None


def _first_doc_line(value: str | None) -> str:
    """Keep only a short source-owned purpose label in the live index."""
    if not value:
        return ""
    for raw_line in value.splitlines():
        line = raw_line.strip()
        if line:
            return line[:240]
    return ""


def _attach_purposes(root: Path, files: list[dict[str, object]]) -> None:
    """Add first-line purposes without copying source bodies to the index."""
    for item in files:
        path = root / str(item.get("path", ""))
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
        except (OSError, SyntaxError):
            continue
        item["purpose"] = _first_doc_line(ast.get_docstring(tree))
        nodes = {
            (getattr(node, "name", ""), getattr(node, "lineno", 0)): node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        for symbol in item.get("symbols", []):
            if not isinstance(symbol, dict):
                continue
            node = nodes.get((symbol.get("name", ""), symbol.get("line", 0)))
            if node is not None:
                symbol["purpose"] = _first_doc_line(ast.get_docstring(node))


def _live_context(root: Path, query: str = "") -> dict[str, object]:
    """Build one machine-readable, read-only context package for an agent."""
    payload: dict[str, object] = {
        "schema": "mak-repo-context-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "requested_git_checkout",
        "git": _git_state(root),
    }
    indexer = _load_code_index_module()
    if indexer is None:
        payload["python"] = {"available": False, "reason": "code_indexer_not_found"}
        return payload
    try:
        structure = indexer.build_index(root, query=query)  # type: ignore[attr-defined]
    except (OSError, ValueError, RuntimeError) as exc:
        payload["python"] = {"available": False, "reason": type(exc).__name__}
        return payload
    files = structure.get("files", [])
    if isinstance(files, list):
        _attach_purposes(root, files)
    payload["python"] = {
        "available": True,
        "schema": structure.get("schema"),
        "root": structure.get("root"),
        "summary": structure.get("summary", {}),
        "files": structure.get("files", []),
    }
    if query:
        payload["query"] = indexer.make_brief(structure, query)  # type: ignore[attr-defined]
    return payload


def _primera_linea_util(p: Path) -> str:
    try:
        for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = ln.strip().lstrip("#").lstrip('"').strip()
            if s and not s.startswith(("---", "import", "from", "#!/")):
                return s[:90]
    except Exception:  # noqa: BLE001
        return ""
    return ""


def _arbol(repo: Path = _REPO):
    print("== ARBOL (carpetas, prof " + str(_MAXDEPTH) + ") ==")
    for root, dirs, _files in os.walk(repo):
        rel = Path(root).relative_to(repo)
        depth = len(rel.parts)
        dirs[:] = sorted(d for d in dirs if not _skip(d))
        if depth >= _MAXDEPTH:
            dirs[:] = []
        if str(rel) == ".":
            continue
        print("  " * (depth - 1) + "- " + rel.parts[-1] + "/")


def _clave(repo: Path = _REPO):
    print("\n== ARCHIVOS CLAVE (con su titulo) ==")
    vistos = 0
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if not _skip(d)]
        for f in sorted(files):
            if f in _KEY_NAMES:
                p = Path(root) / f
                rel = p.relative_to(repo)
                print(f"  {rel}  ->  {_primera_linea_util(p)}")
                vistos += 1
    if not vistos:
        print("  (ninguno)")


def _map(repo: Path = _REPO):
    print(f"# CONTEXTO DEL REPO: {repo}\n# (digest mecanico, 0 tokens)\n")
    _arbol(repo)
    _clave(repo)
    print("\n== ZONAS GENERADAS / NO TOCAR A MANO ==")
    for z in sorted(_GENERADAS):
        print(f"  {z}  (salida generada; leer solo si el pipeline lo requiere)")
    print("\n== COMO USAR ESTE MAPA ==")
    print("  Pasaselo a un agente como 'contexto' o leelo en vez de explorar.")
    print("  Para el detalle de un archivo puntual: leelo directo (barato).")


# tarea -> rutas recomendadas (fuentes de verdad a leer + rutas gordas a derivar)
_TASK_ROUTES = [
    (("web", "hub", "react", "vite", "visualizer", "studio", "svg studio"),
     ["web/src/components/", "web/src/App.tsx", "context/flujo_hub.html (generado)"]),
    (("cli", "comando", "command", "typer"),
     ["src/flujo/cli.py", "docs/CLI.md"]),
    (("flyer", "suplemento", "dark", "vectoriz", "logo", "pieza", "brief", "packs", "svg"),
     [".claude/skills/entregas-rd/", ".claude/skills/taller-svg-rd/SKILL.md",
      "assets/logo/", "svg/suplementos_rd/ (derivar: muchos SVG)"]),
    (("voz", "gemini", "agente", "handoff", "contexto"),
     ["tools/contexto_repo.py --json", "tools/mak_status.py --json"]),
    (("resolume", "chataigne", "noisette"),
     ["src/flujo/resolume/automator.py",
      "BLOQUEADOR: sin .noisette real; no adivinar el schema"]),
    (("test", "pytest"),
     ["tests/", "context/test_lane_map.json"]),
]


def _task(keywords: str):
    kw = keywords.lower()
    print(f"# CONTEXTO PARA LA TAREA: {keywords}\n")
    print("== LEER PRIMERO (fuente de verdad, barato) ==")
    for r in ("tools/contexto_repo.py --json", "tools/mak_status.py --json"):
        print(f"  {r}")
    hits = [routes for keys, routes in _TASK_ROUTES if any(k in kw for k in keys)]
    print("\n== RUTAS RELEVANTES A LA TAREA ==")
    if hits:
        for routes in hits:
            for r in routes:
                print(f"  {r}")
    else:
        print("  (sin match; corre 'map' y elige a mano)")
    print("\n== COMO USARLO (bajo consumo) ==")
    print("  1. Lee tu las fuentes de verdad de arriba (poco volumen, critico).")
    print("  2. Rutas gordas -> derivar a un subagente Sonnet (Agent tool, model sonnet).")
    print("  3. Da a Aider SOLO los archivos de la tarea. Ver docs/AIDER_API_SETUP.md.")


def main():
    args = sys.argv[1:]
    repo = Path.cwd()
    if "--root" in args:
        index = args.index("--root")
        if index + 1 >= len(args):
            raise SystemExit("--root requiere una ruta")
        repo = Path(args[index + 1])
        del args[index:index + 2]
    else:
        detected_root = _git(repo, "rev-parse", "--show-toplevel")
        if detected_root:
            repo = Path(detected_root)
    if "--json" in args:
        args.remove("--json")
        query = ""
        if "--query" in args:
            index = args.index("--query")
            if index + 1 >= len(args):
                raise SystemExit("--query requiere texto")
            query = args[index + 1]
            del args[index:index + 2]
        print(json.dumps(_live_context(repo, query), ensure_ascii=False, indent=2, sort_keys=True))
        return
    cmd = args[0] if args else "map"
    if cmd == "task":
        _task(" ".join(args[1:]) or "(sin keywords)")
    else:  # 'map' o sin args (retrocompatible)
        _map(repo)


if __name__ == "__main__":
    main()
