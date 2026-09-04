"""Inventory the routes the MAK plataforma hub serves, and say which are untested.

`cultura/mak_plataforma/hub.py` dispatches from two long if-chains inside
`do_GET` (458 lines) and `do_POST` (191 lines). A route is one more `if p ==`
branch, so adding one is easy and forgetting to cover it is easier: nothing in
the repository lists what the hub answers, and eleven test modules touch it
without anybody knowing which branches they reach.

This tool reads the dispatchers with `ast` -- it never imports or starts the
hub -- and reports every literal path they match, cross-referenced against the
paths that appear in `tests/`. Read-only: it writes nothing.

    python -m tools.hub_route_inventory              # untested routes
    python -m tools.hub_route_inventory --all        # every route
    python -m tools.hub_route_inventory --json       # machine-readable
    python -m tools.hub_route_inventory --fail-on-untested   # exit 1 if any

A route counted as tested only means its literal path appears somewhere under
`tests/`. That is evidence of contact, not of a contract being checked, so the
covered list is an upper bound and the untested list is the reliable half.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HUB = ROOT / "cultura" / "mak_plataforma" / "hub.py"
TESTS = ROOT / "tests"
DISPATCHERS = ("do_GET", "do_POST", "do_PUT", "do_DELETE", "do_PATCH")


def _string_literals(node: ast.AST) -> list[str]:
    """Every str constant directly under a comparison operand."""
    found: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            found.append(child.value)
    return found


def _routes_in(function: ast.FunctionDef) -> list[dict[str, object]]:
    """Literal paths compared against the request path inside one dispatcher.

    Three shapes carry every branch the hub uses: `p == "/x"`, `p in ("/x",
    "/x/")` and `p.startswith("/x/")`. Comparisons against anything but a path
    variable are ignored, which is why the operand name is checked rather than
    collecting every string in the body.
    """
    routes: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()

    def record(path: str, match: str, line: int) -> None:
        if not path.startswith("/"):
            return
        key = (path, match)
        if key in seen:
            return
        seen.add(key)
        routes.append({"path": path, "match": match, "line": line})

    for node in ast.walk(function):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, ast.Eq):
                    for value in _string_literals(comparator):
                        record(value, "exact", node.lineno)
                elif isinstance(op, ast.In):
                    for value in _string_literals(comparator):
                        record(value, "exact", node.lineno)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"startswith", "endswith"}:
                for argument in node.args:
                    for value in _string_literals(argument):
                        record(value, node.func.attr, node.lineno)

    routes.sort(key=lambda row: (str(row["path"]), str(row["match"])))
    return routes


def inventory(hub_path: Path = HUB) -> dict[str, object]:
    tree = ast.parse(hub_path.read_text(encoding="utf-8"), filename=str(hub_path))
    by_method: dict[str, list[dict[str, object]]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in DISPATCHERS:
            method = node.name.removeprefix("do_")
            by_method.setdefault(method, []).extend(_routes_in(node))
    return {
        "schema": "mak-hub-route-inventory-v1",
        "hub": str(hub_path.relative_to(ROOT)),
        "methods": {method: rows for method, rows in sorted(by_method.items())},
    }


def _test_corpus(tests_dir: Path = TESTS) -> str:
    parts = []
    for path in sorted(tests_dir.rglob("*.py")):
        try:
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return "\n".join(parts)


def annotate(data: dict[str, object], corpus: str) -> dict[str, object]:
    for rows in data["methods"].values():  # type: ignore[union-attr]
        for row in rows:
            row["tested"] = str(row["path"]) in corpus
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.hub_route_inventory",
        description="List the MAK hub's routes and which ones no test mentions.",
    )
    parser.add_argument("--all", action="store_true", help="list every route, not only untested")
    parser.add_argument("--json", action="store_true", help="emit the inventory as JSON")
    parser.add_argument(
        "--fail-on-untested",
        action="store_true",
        help="exit 1 when at least one route is untested",
    )
    args = parser.parse_args(argv)

    if not HUB.is_file():
        print(f"hub not found: {HUB}", file=sys.stderr)
        return 3

    data = annotate(inventory(), _test_corpus())
    methods: dict[str, list[dict[str, object]]] = data["methods"]  # type: ignore[assignment]

    total = sum(len(rows) for rows in methods.values())
    untested = [
        (method, row)
        for method, rows in methods.items()
        for row in rows
        if not row["tested"]
    ]

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))
        return 1 if (args.fail_on_untested and untested) else 0

    print(f"{data['hub']}: {total} rutas literales en {len(methods)} despachadores")
    for method, rows in methods.items():
        shown = rows if args.all else [row for row in rows if not row["tested"]]
        if not shown:
            continue
        print(f"\n{method} ({len(rows)} rutas, {sum(1 for r in rows if not r['tested'])} sin test)")
        for row in shown:
            mark = " " if row["tested"] else "!"
            print(f"  {mark} {row['path']:<48} {row['match']:<10} hub.py:{row['line']}")

    print(f"\nsin mencion en tests/: {len(untested)} de {total}")
    return 1 if (args.fail_on_untested and untested) else 0


if __name__ == "__main__":
    raise SystemExit(main())
