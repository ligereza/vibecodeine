#!/usr/bin/env python3
"""Genera un resumen de uso acumulado a partir de los metadatos de los informes y paneles."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
INFORMES_DIR = ROOT / "informes"
PANELES_DIR = ROOT / "paneles"
OUTPUT = ROOT / "USO.md"


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"warning: saltando {path.name}: {exc}", file=sys.stderr)
        return {}
    return data if isinstance(data, dict) else {}


def collect() -> tuple[Counter, Counter, int, int, int]:
    provider_calls: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()
    tavily_basic = 0
    tavily_advanced = 0
    total_duration = 0
    count = 0

    for directory in (INFORMES_DIR, PANELES_DIR):
        for path in sorted(directory.glob("*.json")):
            data = load_json(path)
            meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
            calls = meta.get("llmCalls") if isinstance(meta.get("llmCalls"), dict) else {}
            for provider, value in calls.items():
                if isinstance(value, int):
                    provider_calls[provider] += value
            errors = meta.get("errors") if isinstance(meta.get("errors"), list) else []
            for error in errors:
                if isinstance(error, str) and error.strip():
                    error_counts[error] += 1
            findings = data.get("findings") if isinstance(data.get("findings"), list) else []
            for finding in findings:
                if not isinstance(finding, dict):
                    continue
                ftype = str(finding.get("type", ""))
                if ftype == "tavily_answer":
                    depth = str(finding.get("depth", "basic")).lower()
                    if depth == "advanced":
                        tavily_advanced += 1
                    else:
                        tavily_basic += 1
            queries = meta.get("queries") if isinstance(meta.get("queries"), list) else []
            for query in queries:
                if isinstance(query, str) and query.strip():
                    tavily_basic += 1
            duration = meta.get("ms")
            if isinstance(duration, (int, float)):
                total_duration += int(duration)
                count += 1
    return provider_calls, error_counts, tavily_basic, tavily_advanced, total_duration // max(count, 1)


def build_markdown(provider_calls: Counter, error_counts: Counter, tavily_basic: int, tavily_advanced: int, avg_ms: int) -> str:
    lines = ["# Uso acumulado de la cadena de investigación", ""]
    lines.extend(["## Llamadas acumuladas por proveedor", "", "| proveedor | llamadas |", "|---|---:|"])
    if provider_calls:
        for provider, value in sorted(provider_calls.items()):
            lines.append(f"| {provider} | {value} |")
    else:
        lines.append("| — | 0 |")

    lines.extend(["", "## Errores más frecuentes", "", "| error | veces |", "|---|---:|"])
    if error_counts:
        for error, value in error_counts.most_common(10):
            lines.append(f"| {error} | {value} |")
    else:
        lines.append("| — | 0 |")

    credits = tavily_basic + (2 * tavily_advanced)
    lines.extend(["", "## Búsquedas Tavily", "", f"- básicas: {tavily_basic}", f"- avanzadas: {tavily_advanced}", f"- créditos estimados: {credits}"])
    lines.extend(["", "## Duración promedio", "", f"- promedio por meta de json: {avg_ms} ms ({avg_ms / 1000:.2f} s)"])
    return "\n".join(lines) + "\n"


def main() -> int:
    provider_calls, error_counts, tavily_basic, tavily_advanced, avg_ms = collect()
    OUTPUT.write_text(build_markdown(provider_calls, error_counts, tavily_basic, tavily_advanced, avg_ms), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
