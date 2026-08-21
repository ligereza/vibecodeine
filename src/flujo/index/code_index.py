"""Static Python structure index for bounded agent context.

The index stores AST-derived metadata, not source text. It is read-only with
respect to the scanned tree and is intended to answer: which modules,
symbols, imports, consumers and side effects are relevant to an incident?
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "mak-code-structure-v1"
BRIEF_SCHEMA = "mak-code-brief-v1"
DEFAULT_OUTPUT = "context/code_structure_index.json"
SKIP_DIRS = frozenset({
    ".git", ".venv", ".agents", ".codex", ".claude", "__pycache__",
    ".pytest_cache", "node_modules", "dist", "build", ".mypy_cache",
    ".ruff_cache", "WIN",
})

_EFFECT_IMPORTS = {
    "sqlite3": "database",
    "subprocess": "process",
    "socket": "network",
    "urllib": "network",
    "requests": "network",
    "httpx": "network",
    "flask": "http_server",
    "fastapi": "http_server",
    "typer": "cli",
}
_EFFECT_CALLS = {
    "open": "filesystem_read_or_write",
    "subprocess.run": "process",
    "subprocess.Popen": "process",
    "os.system": "process",
    "os.remove": "filesystem_write",
    "os.unlink": "filesystem_write",
    "Path.write_text": "filesystem_write",
    "Path.write_bytes": "filesystem_write",
    "Path.unlink": "filesystem_write",
    "Path.rename": "filesystem_write",
    "Path.replace": "filesystem_write",
    "write_text": "filesystem_write",
    "write_bytes": "filesystem_write",
    "unlink": "filesystem_write",
    "rename": "filesystem_write",
    "replace": "filesystem_write",
    "sqlite3.connect": "database",
    "urllib.request.urlopen": "network",
    "requests.get": "network",
    "requests.post": "network",
}


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return "%s.%s" % (parent, node.attr) if parent else node.attr
    return ""


def _decorator_name(node: ast.AST) -> str:
    if isinstance(node, ast.Call):
        return _call_name(node.func)
    return _call_name(node)


def _module_name(root: Path, path: Path) -> str:
    relative = path.relative_to(root)
    parts = list(relative.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_main_guard(node: ast.If) -> bool:
    test = node.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1:
        return False
    if not isinstance(test.ops[0], ast.Eq) or len(test.comparators) != 1:
        return False
    left, right = test.left, test.comparators[0]
    return (
        isinstance(left, ast.Name) and left.id == "__name__"
        and isinstance(right, ast.Constant) and right.value == "__main__"
    ) or (
        isinstance(right, ast.Name) and right.id == "__name__"
        and isinstance(left, ast.Constant) and left.value == "__main__"
    )


class _StructureVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: set[str] = set()
        self.from_imports: set[str] = set()
        self.symbols: list[dict[str, Any]] = []
        self.calls: set[str] = set()
        self.effects: set[str] = set()
        self.entrypoints: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)
            effect = _EFFECT_IMPORTS.get(alias.name.split(".")[0])
            if effect:
                self.effects.add(effect)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        prefix = "." * node.level + (node.module or "")
        for alias in node.names:
            imported = "%s.%s" % (prefix, alias.name) if prefix else alias.name
            self.from_imports.add(imported)
            effect = _EFFECT_IMPORTS.get((node.module or "").split(".")[0])
            if effect:
                self.effects.add(effect)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_symbol(node, "function")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_symbol(node, "async_function")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record_symbol(node, "class")
        self.generic_visit(node)

    def _record_symbol(self, node: ast.AST, kind: str) -> None:
        decorators = [
            value for value in (_decorator_name(item) for item in getattr(node, "decorator_list", []))
            if value
        ]
        name = str(getattr(node, "name", ""))
        self.symbols.append({
            "name": name,
            "kind": kind,
            "line": int(getattr(node, "lineno", 0) or 0),
            "end_line": int(getattr(node, "end_lineno", 0) or 0),
            "decorators": sorted(set(decorators)),
        })
        if name == "main" or any("command" in item or "route" in item for item in decorators):
            self.entrypoints.add(name)

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func)
        if name:
            self.calls.add(name)
            for call, effect in _EFFECT_CALLS.items():
                if name == call or name.endswith("." + call):
                    self.effects.add(effect)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        if _is_main_guard(node):
            self.entrypoints.add("__main__")
        self.generic_visit(node)


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.py")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def inspect_file(root: Path, path: Path) -> dict[str, Any]:
    relative = path.relative_to(root).as_posix()
    result: dict[str, Any] = {
        "path": relative,
        "module": _module_name(root, path),
        "sha256": _sha256(path),
        "lines": 0,
        "imports": [],
        "from_imports": [],
        "symbols": [],
        "calls": [],
        "effects": [],
        "entrypoints": [],
        "syntax_error": None,
        "imported_by": [],
    }
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        result["lines"] = source.count("\n") + (1 if source else 0)
        tree = ast.parse(source, filename=relative)
    except SyntaxError as exc:
        result["syntax_error"] = {
            "message": str(exc.msg),
            "line": int(exc.lineno or 0),
            "offset": int(exc.offset or 0),
        }
        return result
    except OSError as exc:
        result["syntax_error"] = {"message": type(exc).__name__, "line": 0, "offset": 0}
        return result
    visitor = _StructureVisitor()
    visitor.visit(tree)
    result.update({
        "imports": sorted(visitor.imports),
        "from_imports": sorted(visitor.from_imports),
        "symbols": sorted(visitor.symbols, key=lambda item: (item["line"], item["name"])),
        "calls": sorted(visitor.calls)[:200],
        "effects": sorted(visitor.effects),
        "entrypoints": sorted(visitor.entrypoints),
    })
    return result


def _import_candidates(owner: str, imported: str, *, is_package: bool = False) -> list[str]:
    """Resolve absolute and relative imports to possible local modules."""
    if imported.startswith("."):
        level = len(imported) - len(imported.lstrip("."))
        target = imported[level:]
        package = owner.split(".") if is_package else owner.split(".")[:-1]
        if level > 1:
            package = package[: max(0, len(package) - level + 1)]
        absolute = ".".join(package + ([target] if target else []))
    else:
        absolute = imported
    candidates = []
    while absolute:
        candidates.append(absolute)
        absolute = absolute.rsplit(".", 1)[0] if "." in absolute else ""
    return candidates


def _attach_consumers(files: list[dict[str, Any]]) -> None:
    modules = {item["module"] for item in files if item.get("module")}
    reverse: dict[str, set[str]] = {module: set() for module in modules}
    for item in files:
        owner = item.get("module", "")
        imports = list(item.get("imports", [])) + list(item.get("from_imports", []))
        for imported in imports:
            for candidate in _import_candidates(
                owner,
                imported,
                is_package=item.get("path", "").endswith("/__init__.py"),
            ):
                if candidate in reverse and candidate != owner:
                    reverse[candidate].add(owner)
                    break
    for item in files:
        item["imported_by"] = sorted(reverse.get(item.get("module", ""), set()))


def build_index(root: str | Path, *, query: str = "") -> dict[str, Any]:
    """Build a bounded AST index without storing source text."""
    base = Path(root).expanduser().resolve()
    files = [inspect_file(base, path) for path in _iter_python_files(base)]
    _attach_consumers(files)
    syntax_errors = sum(1 for item in files if item.get("syntax_error"))
    symbols = sum(len(item.get("symbols", [])) for item in files)
    effects: dict[str, int] = {}
    for item in files:
        for effect in item.get("effects", []):
            effects[effect] = effects.get(effect, 0) + 1
    result = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(base),
        "skip_dirs": sorted(SKIP_DIRS),
        "summary": {
            "python_files": len(files),
            "total_lines": sum(item.get("lines", 0) for item in files),
            "symbols": symbols,
            "syntax_errors": syntax_errors,
            "effect_modules": effects,
        },
        "files": files,
    }
    if query:
        result["brief"] = make_brief(result, query)
    return result


def save_index(index: dict[str, Any], output: str | Path) -> Path:
    path = Path(output).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def load_index(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))


def make_brief(index: dict[str, Any], query: str, *, limit: int = 20) -> dict[str, Any]:
    tokens = [token for token in re.findall(r"[a-zA-Z0-9_.-]+", query.lower()) if token]
    matches: list[tuple[int, dict[str, Any]]] = []
    for item in index.get("files", []):
        hay = " ".join([
            item.get("path", ""), item.get("module", ""),
            " ".join(symbol.get("name", "") for symbol in item.get("symbols", [])),
            " ".join(item.get("imports", [])), " ".join(item.get("calls", [])),
            " ".join(item.get("effects", [])),
        ]).lower()
        score = sum(1 for token in tokens if token in hay)
        if score:
            matches.append((score, item))
    matches.sort(key=lambda pair: (-pair[0], pair[1].get("path", "")))
    selected = []
    for score, item in matches[:limit]:
        selected.append({
            "score": score,
            "path": item.get("path"),
            "module": item.get("module"),
            "symbols": item.get("symbols", [])[:30],
            "effects": item.get("effects", []),
            "imported_by": item.get("imported_by", []),
            "syntax_error": item.get("syntax_error"),
        })
    return {
        "schema": BRIEF_SCHEMA,
        "query": query,
        "matches": selected,
        "candidate_paths": [item["path"] for item in selected],
        "summary": index.get("summary", {}),
        "source_text_included": False,
    }


def render_brief(brief: dict[str, Any]) -> str:
    lines = [
        "# MAK code structure brief",
        "",
        "- schema: `%s`" % brief.get("schema", BRIEF_SCHEMA),
        "- query: `%s`" % brief.get("query", ""),
        "- source_text_included: `false`",
        "",
        "## Candidate modules",
        "",
    ]
    for item in brief.get("matches", []):
        symbols = ", ".join(symbol.get("name", "") for symbol in item.get("symbols", []))
        effects = ", ".join(item.get("effects", [])) or "none"
        lines.append("- `%s` (score %s; effects: %s; symbols: %s)" % (
            item.get("path", ""), item.get("score", 0), effects, symbols or "none"))
    if not brief.get("matches"):
        lines.append("- no structural match")
    return "\n".join(lines) + "\n"
