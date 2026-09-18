#!/usr/bin/env python3
"""consultar_mak_search.py -- consumidor real del indice Azure AI Search de MAK.

Cierra la pieza que faltaba de las 5 que exige docs/AZURE_MAK_PLAN_2026_2027.md
(Entrada, Adaptador, Salida, Consumidor, Guardas): el indice mak-tools-v1 ya
tenia entrada/adaptador/salida desde 2026-09-18; este script es el primer
consumidor real. Generado por DeepSeek-V4-Pro (turno 8), verificado y
ejecutado por un agente antes de guardarse.

Uso:
    SEARCH_ENDPOINT=... SEARCH_KEY=... python3 tools/consultar_mak_search.py "texto" [--area X] [--departamento Y]
"""
import argparse
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


def main():
    parser = argparse.ArgumentParser(description="Consulta el indice mak-tools-v1 en Azure AI Search")
    parser.add_argument("consulta", type=str, help="Texto libre de busqueda")
    parser.add_argument("--area", type=str, default=None, help="Filtrar por area exacta")
    parser.add_argument("--departamento", type=str, default=None, help="Filtrar por departamento")
    args = parser.parse_args()

    endpoint = os.environ.get("SEARCH_ENDPOINT")
    key = os.environ.get("SEARCH_KEY")

    if not endpoint or not key:
        print("Error: Las variables de entorno SEARCH_ENDPOINT y SEARCH_KEY son requeridas")
        return

    credential = AzureKeyCredential(key)
    search_client = SearchClient(endpoint=endpoint, index_name="mak-tools-v1", credential=credential)

    filters = []
    if args.area:
        filters.append(f"area eq '{args.area}'")
    if args.departamento:
        filters.append(f"departamento eq '{args.departamento}'")

    filter_str = " and ".join(filters) if filters else None

    results = search_client.search(search_text=args.consulta, filter=filter_str,
                                    select=["id", "ruta", "area", "proposito", "departamento"])

    results_list = list(results)

    if not results_list:
        print(f"sin resultados para: {args.consulta}")
        return

    for result in results_list:
        ruta = result.get("ruta", "N/A")
        proposito = result.get("proposito", "N/A")
        area_val = result.get("area", "N/A")
        departamento_val = result.get("departamento", "N/A")
        score = round(result.get("@search.score", 0), 2)
        print(f"{ruta} -> {proposito} ({area_val}, {departamento_val}), {score}")


if __name__ == "__main__":
    main()
