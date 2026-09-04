"""Measure what each hub GET route sends per item, against a declared budget.

The repository ratchets its tool registry, its language and its consumer
inventory. Nothing watched response size, which is how
`/api/portfolio/copilot/map` came to answer 4,367,883 bytes so that its only
consumer could read three fields per row -- about 4% of what it received.

Total bytes are the wrong ratchet: they depend on how big the operator's
archive is that day, so a pin would fail on this machine and pass vacuously on
a fresh clone. **Bytes per item** is a property of the route's shape. A route
spending 620 bytes to place a dot on a map is spending them whether the archive
holds 3 rows or 7044.

The tool drives the dispatcher in-process with a request double -- it starts no
server, opens no socket, and only issues GETs, which the hub answers read-only.

    python -m tools.hub_payload_budget                  # routes over budget
    python -m tools.hub_payload_budget --all            # every measured route
    python -m tools.hub_payload_budget --json
    python -m tools.hub_payload_budget --capture        # print a fresh budget

A measured zero is an error, not a clean bill: with too few items in the
archive the per-item figure means nothing, and the tool says so instead of
reporting that everything is fine.
"""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HUB_DIR = ROOT / "cultura" / "mak_plataforma"
if str(HUB_DIR) not in sys.path:
    sys.path.insert(0, str(HUB_DIR))

BUDGET_FILE = ROOT / "data" / "hub_payload_budget.json"
SCHEMA = "mak-hub-payload-budget-v1"

# Below this the per-item figure is noise, not a measurement.
MIN_ITEMS_TO_JUDGE = 20

# A route whose biggest value is a list of this many entries is a collection
# route: the per-item cost is the thing worth watching.
MIN_ITEMS_TO_REPORT = 5


class _Probe:
    """Enough of a request handler for the dispatcher to answer into."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.rfile = io.BytesIO(b"")
        self.headers: dict[str, str] = {}
        self.command = "GET"
        self.calls: list[tuple] = []
        self.redirect: dict | None = None

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        self.calls.append(("send", body, code))

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.calls.append(("bytes", data, code))

    def send_response(self, code):
        self.redirect = {"code": code}

    def send_header(self, key, value):
        if self.redirect is not None:
            self.redirect.setdefault("headers", {})[key] = value

    def end_headers(self):
        pass


def _routes(hub) -> list[str]:
    from tools.hub_route_inventory import inventory

    prefixes = tuple("/" + prefix for prefix in getattr(hub, "SERVICE_PROXY_PREFIXES", ()))
    return sorted(
        {
            str(row["path"])
            for row in inventory()["methods"].get("GET", [])
            if row["match"] == "exact"
            and not any(str(row["path"]).startswith(prefix) for prefix in prefixes)
        }
    )


def _largest_collection(payload: dict) -> tuple[str | None, int, int]:
    """(key, entries, bytes) of the biggest list the payload carries."""
    best: tuple[str | None, int, int] = (None, 0, 0)
    for key, value in payload.items():
        if not isinstance(value, list) or not value:
            continue
        size = len(json.dumps(value, ensure_ascii=False))
        if size > best[2]:
            best = (key, len(value), size)
    return best


def measure(paths: list[str] | None = None) -> dict:
    """Drive each route once and record what it sends."""
    import hub

    routes = paths if paths is not None else _routes(hub)
    rows = []
    for path in routes:
        probe = _Probe(path)
        try:
            hub.H.do_GET(probe)
        except Exception as error:  # noqa: BLE001 - a crash is not this tool's job
            rows.append({"route": path, "error": f"{type(error).__name__}: {error}"[:120]})
            continue
        if not probe.calls:
            continue
        kind, payload, code = probe.calls[-1]
        if kind != "json" or not isinstance(payload, dict):
            continue
        total = len(json.dumps(payload, ensure_ascii=False))
        key, entries, collection_bytes = _largest_collection(payload)
        row = {
            "route": path,
            "status": code,
            "bytes": total,
            "collection": key,
            "items": entries,
        }
        if entries >= MIN_ITEMS_TO_REPORT:
            row["bytes_per_item"] = round(collection_bytes / entries, 1)
        rows.append(row)
    rows.sort(key=lambda row: -row.get("bytes", 0))
    return {"schema": SCHEMA, "routes": rows}


def load_budget(path: Path = BUDGET_FILE) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": SCHEMA, "routes": {}}
    if data.get("schema") != SCHEMA:
        return {"schema": SCHEMA, "routes": {}}
    return data


def findings(measured: dict, budget: dict) -> list[dict]:
    """Routes over their declared per-item budget, or not declared at all."""
    declared = budget.get("routes", {})
    out: list[dict] = []
    for row in measured["routes"]:
        if "bytes_per_item" not in row:
            continue
        route = row["route"]
        rule = declared.get(route)
        if rule is None:
            out.append({
                "route": route,
                "kind": "sin_declarar",
                "detail": (
                    f"{row['bytes_per_item']} bytes por item en `{row['collection']}` "
                    "y ninguna entrada en el presupuesto"
                ),
            })
            continue
        cap = rule.get("max_bytes_per_item")
        if cap is not None and row["bytes_per_item"] > cap:
            out.append({
                "route": route,
                "kind": "sobre_presupuesto",
                "detail": (
                    f"{row['bytes_per_item']} bytes por item, el techo declarado "
                    f"es {cap}"
                ),
            })
    return out


def _too_small_to_judge(measured: dict) -> bool:
    return not any(
        row.get("items", 0) >= MIN_ITEMS_TO_JUDGE for row in measured["routes"]
    )


def capture(measured: dict, budget: dict) -> dict:
    """A budget declaring each route's current cost, rounded up with headroom."""
    declared = dict(budget.get("routes", {}))
    for row in measured["routes"]:
        if "bytes_per_item" not in row:
            continue
        previous = declared.get(row["route"], {})
        declared[row["route"]] = {
            "max_bytes_per_item": int(row["bytes_per_item"] * 1.25) + 1,
            "collection": row["collection"],
            # How many entries the collection held when this was measured. An
            # expensive row on twelve rows costs nothing; the same row on seven
            # thousand is the defect this file exists to catch. Recorded so the
            # rule can tell those apart without re-measuring.
            "items_at_capture": row["items"],
            "note": previous.get("note", ""),
        }
    return {
        "schema": SCHEMA,
        "note": (
            "Techo de bytes por item de cada ruta de coleccion del hub. La medida "
            "es por item y no en total, porque el total depende de cuantas piezas "
            "tenga el archivo ese dia: pinchar el total fallaria en la maquina del "
            "operador y pasaria en vacio en un clon recien hecho. Regenerar con "
            "`python -m tools.hub_payload_budget --capture`."
        ),
        "routes": dict(sorted(declared.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.hub_payload_budget",
        description="Measure hub GET payload cost per item against a declared budget.",
    )
    parser.add_argument("--all", action="store_true", help="list every measured route")
    parser.add_argument("--json", action="store_true", help="emit the measurement as JSON")
    parser.add_argument("--capture", action="store_true", help="print a fresh budget file")
    parser.add_argument(
        "--fail-on-findings", action="store_true", help="exit 1 when something is over"
    )
    args = parser.parse_args(argv)

    measured = measure()
    budget = load_budget()

    if args.capture:
        print(json.dumps(capture(measured, budget), indent=2, ensure_ascii=False))
        return 0

    if args.json:
        print(json.dumps(
            {"measured": measured, "findings": findings(measured, budget)},
            indent=2, ensure_ascii=False,
        ))
        return 0

    collection_routes = [row for row in measured["routes"] if "bytes_per_item" in row]
    if _too_small_to_judge(measured):
        print(
            "el archivo de este checkout no tiene items suficientes para que "
            f"bytes-por-item signifique algo (minimo {MIN_ITEMS_TO_JUDGE}). "
            "No es un visto bueno: es que no se midio nada.",
            file=sys.stderr,
        )
        return 2

    if args.all:
        print(f"{'bytes':>12} {'items':>7} {'b/item':>8}  ruta")
        for row in measured["routes"]:
            if "bytes" not in row:
                continue
            per_item = row.get("bytes_per_item", "")
            print(f"{row['bytes']:>12,} {row.get('items', 0):>7} {per_item:>8}  {row['route']}")
        print()

    found = findings(measured, budget)
    print(f"rutas de coleccion medidas: {len(collection_routes)}")
    print(f"hallazgos: {len(found)}")
    for finding in found:
        print(f"  ! {finding['route']}: {finding['detail']}")

    return 1 if (args.fail_on_findings and found) else 0


if __name__ == "__main__":
    raise SystemExit(main())
