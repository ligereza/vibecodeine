#!/usr/bin/env python3
"""Genera índices de informes y paneles a partir de los archivos markdown y json reales."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
INFORMES_DIR = ROOT / "informes"
PANELES_DIR = ROOT / "paneles"


def parse_timestamp(path: Path) -> str:
    m = re.match(r"^(\d{8})-(\d{6})", path.stem)
    if not m:
        return "sin-fecha"
    try:
        dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    except ValueError:
        return "sin-fecha"
    return dt.strftime("%Y-%m-%d %H:%M")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"warning: saltando {path.name}: {exc}", file=sys.stderr)
        return {}
    return data if isinstance(data, dict) else {}


def get_topic(data: dict[str, Any]) -> str:
    return str(
        data.get("topic")
        or data.get("tema")
        or data.get("title")
        or data.get("titulo")
        or "sin tema"
    ).strip()


def get_sources(data: dict[str, Any]) -> list[str]:
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    for key in ("sources", "fuentes"):
        values = meta.get(key) if isinstance(meta.get(key), list) else None
        if values:
            return [str(v) for v in values if str(v).strip()]
    return []


def build_rows(directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for md_path in sorted(directory.glob("*.md")):
        json_path = directory / f"{md_path.stem}.json"
        data = load_json(json_path)
        rows.append(
            {
                "fecha": parse_timestamp(md_path),
                "tema": get_topic(data),
                "fuentes": get_sources(data),
                "link": md_path.name,
            }
        )
    return rows


def write_index(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [f"# Índice de {path.parent.name}", "", "| fecha | tema | fuentes | link |", "|---|---|---|---|"]
    for row in rows:
        fuentes = "; ".join(row["fuentes"][:5]) if row["fuentes"] else "—"
        lines.append(f"| {row['fecha']} | {row['tema']} | {fuentes} | [{row['link']}]({row['link']}) |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    for directory, target in ((INFORMES_DIR, INFORMES_DIR / "INDEX.md"), (PANELES_DIR, PANELES_DIR / "INDEX.md")):
        rows = build_rows(directory)
        write_index(target, rows)
        print(f"wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
