#!/usr/bin/env python3
"""metricas_capataz.py -- instrumentacion del director autonomo (FASE 0).

Lee bitacora_capataz.jsonl y genera metricas de:
- tasa de decisiones exitosas vs fallback
- tasa de parse OK vs fallos
- distribucion por proveedor y accion
- tendencia de fiabilidad

Salida: METRICAS_CAPATAZ.md (tablas ASCII).
"""
from __future__ import annotations

import datetime
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def cargar_bitacora(ruta: str, dias: int = 7) -> list[dict]:
    """Carga bitacora_capataz.jsonl, filtra por timestamp.

    Tolerante: lineas corruptas se saltan, se cuenta como "corruptas".
    Retorna lista de entradas validas + dict con stats de corrupcion.
    """
    ruta_p = Path(ruta)
    if not ruta_p.exists():
        return []

    entradas = []
    ahora = datetime.datetime.now()
    cutoff = ahora - datetime.timedelta(days=dias)

    try:
        with ruta_p.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if not isinstance(entry, dict):
                        continue
                    # Parsear timestamp
                    ts_str = entry.get("ts", "")
                    try:
                        ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                        if ts >= cutoff:
                            entradas.append(entry)
                    except ValueError:
                        # Timestamp invalido, saltamos
                        continue
                except (json.JSONDecodeError, ValueError):
                    continue
    except OSError:
        pass

    return entradas


def tasas(entradas: list[dict]) -> dict:
    """Calcula metricas agregadas a partir de entradas de bitacora.

    Retorna dict con:
    - total: cantidad de entradas
    - fallback_rate: % de entradas con fallback_usado=true
    - por_proveedor: {proveedor: {n, fallback_n, fallback_pct}}
    - por_accion: {accion: {n, fallback_n, fallback_pct}}
    - parse_ok_rate: % de entradas con resultado_resumen no vacio
    - decisiones_con_decisor_nivel: cuantas entradas traen el campo F1a
      decisor_nivel (bitacora vieja, pre-F1a, no lo trae -- se excluye de
      local_rate/escalado_rate en vez de contarse como 0, para no mezclar
      periodos distintos del capataz en la misma tasa)
    - local_rate: % de esas entradas con decisor_nivel == "local"
    - escalado_rate: % de esas entradas con escalado == true
    """
    if not entradas:
        return {
            "total": 0,
            "fallback_rate": 0.0,
            "parse_ok_rate": 0.0,
            "por_proveedor": {},
            "por_accion": {},
            "decisiones_con_decisor_nivel": 0,
            "local_rate": None,
            "escalado_rate": None,
        }

    total = len(entradas)
    fallback_count = sum(1 for e in entradas if e.get("fallback_usado", False))
    parse_ok_count = sum(1 for e in entradas if e.get("resultado_resumen"))

    # F1a: solo entradas que YA traen decisor_nivel (bitacora post-F1a).
    con_decisor_nivel = [e for e in entradas if e.get("decisor_nivel") is not None]
    n_decisor_nivel = len(con_decisor_nivel)
    local_rate = (
        round(100.0 * sum(1 for e in con_decisor_nivel if e.get("decisor_nivel") == "local")
              / n_decisor_nivel, 1)
        if n_decisor_nivel > 0 else None
    )
    escalado_rate = (
        round(100.0 * sum(1 for e in con_decisor_nivel if e.get("escalado")) / n_decisor_nivel, 1)
        if n_decisor_nivel > 0 else None
    )

    por_prov: dict[str, dict[str, Any]] = {}
    por_accion: dict[str, dict[str, Any]] = {}

    for entry in entradas:
        prov = entry.get("proveedor_decisor", "ninguno")
        accion = entry.get("accion", "desconocida")
        fallback = entry.get("fallback_usado", False)

        if prov not in por_prov:
            por_prov[prov] = {"n": 0, "fallback_n": 0}
        por_prov[prov]["n"] += 1
        if fallback:
            por_prov[prov]["fallback_n"] += 1

        if accion not in por_accion:
            por_accion[accion] = {"n": 0, "fallback_n": 0}
        por_accion[accion]["n"] += 1
        if fallback:
            por_accion[accion]["fallback_n"] += 1

    # Calcular porcentajes
    for prov_dict in por_prov.values():
        prov_dict["fallback_pct"] = (
            round(100.0 * prov_dict["fallback_n"] / prov_dict["n"], 1)
            if prov_dict["n"] > 0 else 0.0
        )

    for accion_dict in por_accion.values():
        accion_dict["fallback_pct"] = (
            round(100.0 * accion_dict["fallback_n"] / accion_dict["n"], 1)
            if accion_dict["n"] > 0 else 0.0
        )

    return {
        "total": total,
        "fallback_rate": round(100.0 * fallback_count / total, 1) if total > 0 else 0.0,
        "parse_ok_rate": round(100.0 * parse_ok_count / total, 1) if total > 0 else 0.0,
        "por_proveedor": por_prov,
        "por_accion": por_accion,
        "decisiones_con_decisor_nivel": n_decisor_nivel,
        "local_rate": local_rate,
        "escalado_rate": escalado_rate,
    }


def render_md(t: dict) -> str:
    """Genera markdown con tablas de metricas."""
    lines = [
        "# Metricas del Capataz (FASE 0)",
        "",
        "## Resumen General",
        "",
    ]

    total = t.get("total", 0)
    fb_rate = t.get("fallback_rate", 0.0)
    parse_ok = t.get("parse_ok_rate", 0.0)

    lines.extend([
        f"- **Total de decisiones**: {total}",
        f"- **Tasa de fallback**: {fb_rate}%",
        f"- **Tasa parse OK**: {parse_ok}%",
        "",
    ])

    # Tabla por proveedor
    lines.extend([
        "## Decisiones por Proveedor",
        "",
        "| proveedor | decisiones | fallback_n | fallback_pct |",
        "|---|---:|---:|---:|",
    ])

    por_prov = t.get("por_proveedor", {})
    if por_prov:
        for prov in sorted(por_prov.keys()):
            stats = por_prov[prov]
            n = stats.get("n", 0)
            fb_n = stats.get("fallback_n", 0)
            fb_pct = stats.get("fallback_pct", 0.0)
            lines.append(f"| {prov} | {n} | {fb_n} | {fb_pct}% |")
    else:
        lines.append("| — | 0 | 0 | 0% |")

    lines.append("")

    # Tabla por accion
    lines.extend([
        "## Decisiones por Accion",
        "",
        "| accion | total | fallback_n | fallback_pct |",
        "|---|---:|---:|---:|",
    ])

    por_accion = t.get("por_accion", {})
    if por_accion:
        for accion in sorted(por_accion.keys()):
            stats = por_accion[accion]
            n = stats.get("n", 0)
            fb_n = stats.get("fallback_n", 0)
            fb_pct = stats.get("fallback_pct", 0.0)
            lines.append(f"| {accion} | {n} | {fb_n} | {fb_pct}% |")
    else:
        lines.append("| — | 0 | 0 | 0% |")

    lines.append("")

    # F1a: local (ollama) vs nube -- solo si hay bitacora post-F1a
    n_decisor_nivel = t.get("decisiones_con_decisor_nivel", 0)
    lines.extend([
        "## F1a -- Local vs Nube",
        "",
    ])
    if n_decisor_nivel:
        local_rate = t.get("local_rate")
        escalado_rate = t.get("escalado_rate")
        lines.extend([
            f"- **Decisiones con decisor_nivel (post-F1a)**: {n_decisor_nivel}",
            f"- **Tasa LOCAL (ollama)**: {local_rate}%",
            f"- **Tasa de escalada a nube**: {escalado_rate}%",
            "",
        ])
    else:
        lines.append("- (sin decisiones con campo decisor_nivel todavia -- bitacora pre-F1a)")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    """CLI: carga bitacora, calcula metricas, escribe METRICAS_CAPATAZ.md."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera metricas del capataz a partir de bitacora_capataz.jsonl"
    )
    parser.add_argument(
        "ruta",
        nargs="?",
        default="bitacora_capataz.jsonl",
        help="Ruta a bitacora_capataz.jsonl (default: bitacora_capataz.jsonl en cwd)",
    )
    parser.add_argument(
        "--dias",
        type=int,
        default=7,
        help="Filtrar por ultimos N dias (default: 7)",
    )

    args = parser.parse_args()

    # Cargar bitacora
    entradas = cargar_bitacora(args.ruta, dias=args.dias)

    # Calcular tasas
    t = tasas(entradas)

    # Renderizar markdown
    md = render_md(t)

    # Escribir al lado de la bitacora
    ruta_p = Path(args.ruta)
    salida = ruta_p.parent / "METRICAS_CAPATAZ.md"

    try:
        salida.write_text(md, encoding="utf-8")
        print(f"wrote {salida.name}")
        return 0
    except OSError as e:
        print(f"error escribiendo {salida}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
