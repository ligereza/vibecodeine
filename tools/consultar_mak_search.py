#!/usr/bin/env python3
"""Diagnostic CLI for the shared MAK Azure AI Search adapter.

The canonical consumer is the MAK Hub route ``/api/azure/search/tools``.
This command is intentionally only a terminal view for operators and uses the
same adapter as the Hub, so authentication, filters, and response contracts
cannot drift into two independent implementations.

Usage:
    python3 tools/consultar_mak_search.py "text" [--area X] [--departamento Y]

Authentication:
    The shared adapter reuses the existing MAK ``az login`` session. An
    explicit SEARCH_KEY remains a fallback for an isolated service account,
    but is never printed or required by default.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cultura.mak_plataforma.azure_search import search_tools  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Consulta el indice mak-tools-v1 en Azure AI Search")
    parser.add_argument("consulta", type=str, help="Texto libre de busqueda")
    parser.add_argument("--area", type=str, default=None, help="Filtrar por area exacta")
    parser.add_argument("--departamento", type=str, default=None, help="Filtrar por departamento")
    args = parser.parse_args()

    payload = search_tools(args.consulta, area=args.area,
                           departamento=args.departamento)
    if not payload.get("available"):
        print("consulta no disponible: %s" % payload.get("error", "unknown"),
              file=sys.stderr)
        return 2

    results_list = payload.get("results", [])
    if not results_list:
        print(f"sin resultados para: {args.consulta}")
        return 0

    for result in results_list:
        ruta = result.get("ruta", "N/A")
        proposito = result.get("proposito", "N/A")
        area_val = result.get("area", "N/A")
        departamento_val = result.get("departamento", "N/A")
        score = round(result.get("score", 0), 2)
        print(f"{ruta} -> {proposito} ({area_val}, {departamento_val}), {score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
