#!/usr/bin/env python3
"""raton.py -- explorador mecanico de referencias rotas en MAK. Sin agente.

No llama a ningun modelo, no ejecuta codigo ajeno, no escribe nada. Por cada
archivo .py rastreado en git, extrae los literales de string que declaran una
ruta de archivo (AST, no regex sobre texto), y comprueba si esa ruta existe
de verdad, resuelta contra las raices fisicas conocidas de MAK (este repo,
el checkout de FLUJO, y $HOME).

El area de movimiento del raton es el directorio de primer nivel del archivo
que declara la referencia (tools/, cultura/, src/, tests/, docs/...). El
raton reporta a que area pertenece cada hallazgo; no decide por si solo si
puede cruzar de un area a otra -- esa es una decision aparte, humana o de
otra capa, no de este script.

Uso:
    python3 tools/raton.py                 # reporte de texto
    python3 tools/raton.py --json out.json # ademas, JSON completo

Nota sobre ejecucion real (no solo esta lectura estatica): probado el
2026-09-17 dentro de Docker con la copia del repo montada de solo lectura
(-v repo:ro) y --network none. Un script adversarial de prueba confirmo que
escribir o borrar dentro del repo montado y alcanzar la red quedan
bloqueados por el sistema, no por costumbre. Un montaje de solo lectura sin
carpeta de salida aparte rompe scripts legitimos que escriben su propio
reporte (ej. scripts/flyer_duplicates_report.py); montar ademas un
directorio de salida separado, en escritura, es la forma correcta.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

KNOWN_EXTENSIONS = (
    ".py", ".md", ".json", ".js", ".jsx", ".mjs", ".sh", ".yml", ".yaml",
    ".service", ".timer", ".ps1", ".txt", ".jsonl", ".sqlite", ".db",
)

ROOTS = [
    REPO_ROOT,
    REPO_ROOT / "flujo",
    Path(os.path.expanduser("~")),
    Path(os.path.expanduser("~")) / "plataforma",
]

# Prefijos que no son referencias de archivo local (URLs, plantillas, MIME).
SKIP_PREFIXES = ("http://", "https://", "ftp://", "data:", "{", "%",
                  "vnd.", "application/", "text/", "image/")


def _tracked_py_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "*.py"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True,
    )
    return [line for line in out.stdout.splitlines() if line]


def _looks_like_path(value: str) -> bool:
    if not value or len(value) > 200 or "\n" in value:
        return False
    if value.startswith(SKIP_PREFIXES):
        return False
    if not value.lower().endswith(KNOWN_EXTENSIONS):
        return False
    # A bare extension or filename with no directory ("jobs.jsonl", ".md")
    # is not a checkable path: it is either an endswith() comparison target
    # or a name resolved elsewhere at runtime (cwd, a job dir, an argument).
    # Requiring a separator keeps only literals that declare where to look.
    if "/" not in value:
        return False
    if any(ch in value for ch in ("<", ">", "*", "?", "|", "%s", "%d", "{")):
        return False
    return True


def _resolve(path_str: str) -> str | None:
    expanded = os.path.expanduser(os.path.expandvars(path_str))
    p = Path(expanded)
    if p.is_absolute():
        return str(p) if p.exists() else None
    for root in ROOTS:
        candidate = root / p
        if candidate.exists():
            return str(candidate)
    return None


def _area_of(file_path: str) -> str:
    parts = Path(file_path).parts
    return parts[0] if parts else "(raiz)"


def _string_literals(source: str, file_path: str) -> list[tuple[str, int]]:
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.append((node.value, node.lineno))
    return found


def scan() -> dict:
    files = _tracked_py_files()
    findings = []
    scanned = 0
    candidates_checked = 0
    for rel_path in files:
        full_path = REPO_ROOT / rel_path
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        for value, lineno in _string_literals(source, rel_path):
            if not _looks_like_path(value):
                continue
            candidates_checked += 1
            if _resolve(value) is None:
                findings.append({
                    "declared_in": rel_path,
                    "area": _area_of(rel_path),
                    "line": lineno,
                    "referenced_path": value,
                })
    return {
        "schema": "raton-scan-v1",
        "files_scanned": scanned,
        "path_like_literals_checked": candidates_checked,
        "unresolved_count": len(findings),
        "findings": findings,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", help="ademas, escribir el reporte completo aca")
    args = ap.parse_args(argv)

    result = scan()
    print(f"archivos .py escaneados       : {result['files_scanned']}")
    print(f"literales tipo-ruta revisados : {result['path_like_literals_checked']}")
    print(f"referencias sin resolver      : {result['unresolved_count']}")
    print()

    by_area: dict[str, list[dict]] = {}
    for f in result["findings"]:
        by_area.setdefault(f["area"], []).append(f)

    for area in sorted(by_area):
        items = by_area[area]
        print(f"== area: {area}  ({len(items)} hallazgos) ==")
        for it in items:
            print(f"  {it['declared_in']}:{it['line']}  ->  {it['referenced_path']}")
        print()

    if args.json:
        Path(args.json).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"reporte completo: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
