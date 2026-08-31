#!/usr/bin/env python3
"""Compact read-only audit for web, database and tool-consumer contracts.

The tool inventory deliberately reports evidence instead of deciding whether a
zero-reference CLI is dead: operator-run commands have no in-tree caller by
design.  Historical ``WIN`` and external mounts are outside the scan.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import sqlite3
import tokenize
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WEB_SRC = ROOT / "web" / "src"
MODULE_SUFFIXES = {".ts", ".tsx"}
STALE_TOKENS = (
    "bridge_" + "issue_render",
    "enviar_" + "a_mak",
    "instalar_" + "enviar_a_mak",
    "claude.yml",
)
DB_PATHS = (
    ROOT / "data" / "rd.db",
    ROOT / "data" / "rd_datos.db",
    ROOT / "data" / "mak_knowledge.db",
    ROOT / "data" / "flujo.db",
)
DB_CONSUMERS = {
    "data/rd.db": (
        "src/flujo/rd/database.py",
        "src/flujo/departments.py",
        "src/flujo/knowledge/operational_bridge.py",
        "tools/gen_propuesta_directiva.py",
        "cultura/mak_plataforma/hub.py",
    ),
    "data/rd_datos.db": (
        "src/flujo/rd/datos.py",
        "src/flujo/rd/informe.py",
        "src/flujo/departments.py",
        "src/flujo/web/hub.py",
    ),
    "data/mak_knowledge.db": (
        "src/flujo/knowledge/project_api.py",
        "src/flujo/knowledge/system_status.py",
        "src/flujo/knowledge/operational_bridge.py",
        "src/flujo/web/hub.py",
        "cultura/mak_plataforma/hub.py",
        "tools/build_application_intake.py",
        "tools/mak_status.py",
    ),
    "data/flujo.db": ("src/flujo/index/db.py", "src/flujo/cli.py"),
}

TOOL_SEARCH_ROOTS = (
    "src", "tools", "cultura", "scripts", ".github", "iskvw", "xio",
)
TOOL_TEXT_SUFFIXES = {
    ".css", ".html", ".js", ".json", ".mjs", ".md", ".py", ".sh",
    ".toml", ".ts", ".tsx", ".txt", ".yml", ".yaml",
}
# Consumer evidence is about executable/configuration references.  Markup,
# exported JSON and vendor text can be enormous on the full MAK box and are
# not production callers of a Python tool.
PRODUCTION_SEARCH_SUFFIXES = {
    ".py", ".js", ".mjs", ".ts", ".tsx", ".sh", ".toml", ".yml", ".yaml",
}
TOOL_SKIP_DIRS = {
    ".git", ".venv", "__pycache__", "_archive", "build", "cache", "dist",
    "fixtures", "logs", "node_modules", "state", "venv",
}


def _text_files(root: Path, relative_roots: tuple[str, ...]) -> list[Path]:
    """Return bounded text surfaces, excluding caches and history."""
    files: list[Path] = []
    for relative in relative_roots:
        base = root / relative
        if not base.is_dir():
            continue
        for directory, dirnames, filenames in os.walk(base):
            kept: list[str] = []
            for name in sorted(dirnames):
                if name in TOOL_SKIP_DIRS:
                    continue
                # /home/mak is the machine root, so it can contain unrelated
                # nested checkouts (for example src/ml-mobileclip).  A nested
                # .git marks such a checkout as an external boundary; walking
                # it would turn this bounded inventory into a home-directory
                # scan.
                candidate = Path(directory) / name
                if (candidate / ".git").exists():
                    continue
                kept.append(name)
            dirnames[:] = kept
            for filename in sorted(filenames):
                path = Path(directory) / filename
                if path.suffix.lower() in TOOL_TEXT_SUFFIXES:
                    files.append(path)
    return sorted(set(files))


def _searchable_text(path: Path, text: str) -> str:
    """Remove Python comments/docstrings before looking for consumers.

    A mention in a comment or module documentation explains a tool but does
    not invoke it.  Keeping executable string literals preserves subprocess
    command lists and dynamic imports while avoiding those false positives.
    """
    if path.suffix.lower() != ".py":
        return text
    lines = text.splitlines(keepends=True)
    try:
        tree = ast.parse(text)
        docstring_lines: set[int] = set()
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if not body or not isinstance(body, list):
                continue
            first = body[0]
            value = getattr(first, "value", None)
            if (isinstance(first, ast.Expr) and isinstance(value, ast.Constant)
                    and isinstance(value.value, str)):
                docstring_lines.update(range(first.lineno - 1, first.end_lineno))
        for index in docstring_lines:
            lines[index] = "\n" if lines[index].endswith("\n") else ""
        masked = "".join(lines)
        chars = list(masked)
        for token in tokenize.generate_tokens(io.StringIO(masked).readline):
            if token.type != tokenize.COMMENT:
                continue
            start_line, start_col = token.start
            end_line, end_col = token.end
            if start_line == end_line:
                offset = sum(len(line) for line in lines[:start_line - 1])
                for index in range(offset + start_col, offset + end_col):
                    chars[index] = " "
        return "".join(chars)
    except (SyntaxError, tokenize.TokenError, IndentationError):
        # An unparsable source file is still searchable, but this function must
        # never turn an audit into a crash or silently discard evidence.
        return text


def _tool_inventory(root: Path = ROOT) -> dict[str, Any]:
    """Measure top-level ``tools/*.py`` references without mutating files.

    A production/test reference is returned as a path list so a count can be
    audited.  The target file itself is excluded: its own name in a docstring
    is not a consumer.  Workflow hits are limited to ``.github/workflows``.
    """
    tools_dir = root / "tools"
    tool_paths = sorted(path for path in tools_dir.glob("*.py") if path.is_file())
    production_files = [
        path for path in _text_files(root, TOOL_SEARCH_ROOTS)
        if path.suffix.lower() in PRODUCTION_SEARCH_SUFFIXES
    ]
    test_files = [
        path for path in _text_files(root, ("tests",))
        if path.suffix.lower() == ".py"
    ]
    workflow_files = [
        path for path in _text_files(root, (".github/workflows",))
        if path.suffix.lower() in {".yml", ".yaml"}
    ]

    def load(paths: list[Path]) -> dict[Path, str]:
        loaded: dict[Path, str] = {}
        for path in paths:
            try:
                loaded[path] = _searchable_text(
                    path, path.read_text(encoding="utf-8", errors="replace")
                )
            except OSError:
                continue
        return loaded

    production_text = load(production_files)
    test_text = load(test_files)
    workflow_text = load(workflow_files)
    rows: list[dict[str, Any]] = []
    for tool_path in tool_paths:
        name = tool_path.name
        stem = tool_path.stem
        import_pattern = re.compile(
            rf"\b(?:from\s+|import\s+){re.escape(stem)}\b"
        )

        def hits(texts: dict[Path, str]) -> list[str]:
            found: list[str] = []
            for path, text in texts.items():
                # All paths in the bounded inventories are absolute paths
                # rooted at ROOT.  Comparing them directly avoids resolving
                # hundreds of symlinks once per tool (important now that MAK
                # itself is the user's home directory).
                if path == tool_path:
                    continue
                if (name in text or f"tools.{stem}" in text
                        or import_pattern.search(text)):
                    found.append(path.relative_to(root).as_posix())
            return found

        production = hits(production_text)
        tests = hits(test_text)
        workflows = hits(workflow_text)
        rows.append({
            "path": f"tools/{name}",
            "exists": True,
            "refs_production": production,
            "refs_test": tests,
            "workflows": workflows,
            "consumer_evidence": bool(production or tests or workflows),
        })

    with_production = sum(bool(row["refs_production"]) for row in rows)
    with_tests_only = sum(
        bool(row["refs_test"]) and not row["refs_production"] for row in rows
    )
    without_refs = sum(not row["consumer_evidence"] for row in rows)
    with_workflow = sum(bool(row["workflows"]) for row in rows)
    return {
        "schema": "mak-tool-consumer-inventory-v1",
        "scope": list(TOOL_SEARCH_ROOTS),
        "historical_win_excluded": True,
        "count": len(rows),
        "files": rows,
        "summary": {
            "with_production_reference": with_production,
            "tests_only": with_tests_only,
            "without_any_reference": without_refs,
            "with_workflow_trigger": with_workflow,
        },
    }


def _module_id(path: Path) -> str:
    return path.relative_to(WEB_SRC).with_suffix("").as_posix()


def _web_graph() -> dict[str, Any]:
    files = {path.resolve() for path in WEB_SRC.rglob("*") if path.suffix in MODULE_SUFFIXES}
    modules = {_module_id(path): path for path in files}
    edges: dict[str, set[str]] = {name: set() for name in modules}
    pattern = re.compile(r"(?:from\s+|import\s*)['\"](\.[^'\"]+)['\"]")
    for owner, path in modules.items():
        for raw in pattern.findall(path.read_text(encoding="utf-8", errors="replace")):
            target = (path.parent / raw).resolve()
            candidates = (
                target,
                target.with_suffix(".ts"),
                target.with_suffix(".tsx"),
                target / "index.ts",
                target / "index.tsx",
            )
            hit = next((candidate for candidate in candidates if candidate in files), None)
            if hit is not None:
                edges[owner].add(_module_id(hit))

    roots = [name for name in ("main", "mainPlano", "mainRd") if name in modules]
    reachable: set[str] = set()
    pending = list(roots)
    while pending:
        current = pending.pop()
        if current in reachable:
            continue
        reachable.add(current)
        pending.extend(edges.get(current, ()))
    dead = sorted(name for name in set(modules) - reachable if name != "vite-env.d")
    return {
        "modules": len(modules),
        "roots": roots,
        "reachable": len(reachable),
        "dead_modules": dead,
        "declaration_only": ["vite-env.d"] if "vite-env.d" in modules else [],
    }


def _active_files() -> list[Path]:
    paths = [ROOT / "web", ROOT / ".github" / "workflows"]
    files: list[Path] = []
    for base in paths:
        if base.is_dir():
            files.extend(path for path in base.rglob("*") if path.is_file() and "node_modules" not in path.parts)
    return files


def _stale_refs() -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in _active_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for token in STALE_TOKENS:
            if token in text:
                findings.append({
                    "path": path.relative_to(ROOT).as_posix(),
                    "token": token,
                })
    return findings


def _db_inventory() -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for path in DB_PATHS:
        relative = path.relative_to(ROOT).as_posix()
        item: dict[str, Any] = {
            "path": relative,
            "exists": path.is_file(),
            "consumers": list(DB_CONSUMERS.get(relative, ())),
        }
        item["missing_consumers"] = [
            consumer for consumer in item["consumers"]
            if not (ROOT / consumer).is_file()
        ]
        if not path.is_file():
            inventory.append(item)
            continue
        item["bytes"] = path.stat().st_size
        try:
            with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as connection:
                tables = [row[0] for row in connection.execute(
                    "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"
                )]
                item["tables"] = len(tables)
                item["rows"] = sum(
                    connection.execute('select count(*) from "' + table.replace('"', '""') + '"').fetchone()[0]
                    for table in tables
                )
                item["integrity"] = connection.execute("pragma integrity_check").fetchone()[0]
        except (OSError, sqlite3.Error) as exc:
            item["error"] = type(exc).__name__
        inventory.append(item)
    return inventory


def audit() -> dict[str, Any]:
    web = _web_graph()
    stale = _stale_refs()
    databases = _db_inventory()
    db_errors = [item for item in databases if item.get("error")]
    missing_consumers = [item for item in databases if item.get("missing_consumers")]
    return {
        "schema": "mak-repo-audit-v1",
        "web": web,
        "stale_active_references": stale,
        "databases": databases,
        "tools": _tool_inventory(),
        "ok": not web["dead_modules"] and not stale and not db_errors and not missing_consumers,
        "policy": {
            "read_only": True,
            "historical_win_excluded": True,
            "missing_databases_allowed": True,
            "automatic_delete": False,
        },
    }


def _tools_markdown(tools: dict[str, Any]) -> str:
    """Render the generated tool inventory without adding a second data source."""
    summary = tools["summary"]
    lines = [
        "# MAK tool consumer inventory",
        "",
        "Generated by `tools/repo_audit.py --format markdown`; this is a",
        "read-only projection of `mak-tool-consumer-inventory-v1`, not a hand-",
        "maintained registry. Historical `WIN` and `curatoria_inbox` are out of",
        "scope. A missing reference is evidence for classification, not proof of",
        "death.",
        "",
        f"- schema: `{tools['schema']}`",
        f"- count: **{tools['count']}**",
        f"- production references: **{summary['with_production_reference']}**",
        f"- tests only: **{summary['tests_only']}**",
        f"- no direct reference: **{summary['without_any_reference']}**",
        f"- workflow triggers: **{summary['with_workflow_trigger']}**",
        "",
        "| tool | production refs | test refs | workflow refs | evidence |",
        "|---|---|---|---|---|",
    ]
    def fmt(values: list[str]) -> str:
        return "<br>".join(f"`{value}`" for value in values) or "—"

    for row in tools["files"]:
        lines.append("| %s | %s | %s | %s | %s |" % (
            f"`{row['path']}`",
            fmt(row["refs_production"]),
            fmt(row["refs_test"]),
            fmt(row["workflows"]),
            "yes" if row["consumer_evidence"] else "no",
        ))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format", choices=("json", "text", "markdown"), default="text"
    )
    args = parser.parse_args()
    result = audit()
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=True, indent=2))
    elif args.format == "markdown":
        print(_tools_markdown(result["tools"]), end="")
    else:
        web = result["web"]
        print("repo-audit: %s" % ("OK" if result["ok"] else "ATTENTION"))
        print("web_modules=%d reachable=%d dead=%d" % (
            web["modules"], web["reachable"], len(web["dead_modules"])))
        print("stale_active_references=%d" % len(result["stale_active_references"]))
        for item in result["databases"]:
            print("db=%s exists=%s tables=%s rows=%s integrity=%s" % (
                item["path"], item["exists"], item.get("tables", 0),
                item.get("rows", 0), item.get("integrity", "missing")))
            if item.get("missing_consumers"):
                print("db_missing_consumers=%s:%s" % (
                    item["path"], ",".join(item["missing_consumers"])))
        tools = result["tools"]
        summary = tools["summary"]
        print("tools=%d production_refs=%d tests_only=%d no_refs=%d workflows=%d" % (
            tools["count"], summary["with_production_reference"],
            summary["tests_only"], summary["without_any_reference"],
            summary["with_workflow_trigger"]))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
