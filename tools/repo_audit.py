#!/usr/bin/env python3
"""Compact read-only audit for the web surface and local database contracts."""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
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
        "ok": not web["dead_modules"] and not stale and not db_errors and not missing_consumers,
        "policy": {
            "read_only": True,
            "historical_win_excluded": True,
            "missing_databases_allowed": True,
            "automatic_delete": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    result = audit()
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=True, indent=2))
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
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
