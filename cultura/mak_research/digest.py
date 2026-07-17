#!/usr/bin/env python3
"""Genera un digest resumido de los informes de los últimos 7 días."""
from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
INFORMES_DIR = ROOT / "informes"
OUTPUT = ROOT / "DIGEST.md"


def parse_date_from_name(path: Path) -> datetime | None:
    m = re.match(r"^(\d{8})-(\d{6})", path.stem)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    except ValueError:
        return None


def extract_summary(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if re.search(r"resumen", line, re.I):
            collected: list[str] = []
            for candidate in lines[index + 1 :]:
                if re.match(r"^#{1,6}\s+", candidate):
                    break
                stripped = candidate.strip()
                if stripped:
                    collected.append(stripped)
            if collected:
                return " ".join(collected).strip()
            break
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        if paragraph.strip():
            return re.sub(r"\s+", " ", paragraph).strip()
    return "Sin resumen disponible."


def iter_recent_reports(directory: Path) -> Iterable[tuple[Path, str]]:
    cutoff = datetime.now().date() - timedelta(days=7)
    for path in sorted(directory.glob("*.md")):
        stamp = parse_date_from_name(path)
        if stamp is None:
            continue
        if stamp.date() >= cutoff:
            yield path, extract_summary(path.read_text(encoding="utf-8"))


def write_digest(items: list[tuple[Path, str]]) -> None:
    lines = ["# Digest de informes (últimos 7 días)", ""]
    for path, summary in items:
        lines.append(f"- [{path.name}]({path.relative_to(ROOT).as_posix()}): {summary}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    items = list(iter_recent_reports(INFORMES_DIR))
    if not items:
        OUTPUT.write_text("# Digest de informes (últimos 7 días)\n\nNo hay informes recientes.\n", encoding="utf-8")
        print("No hay informes recientes.")
        return 0
    write_digest(items)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    for path, _summary in items:
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
