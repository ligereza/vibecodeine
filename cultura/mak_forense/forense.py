#!/usr/bin/env python3
"""Analisis forense de procedencia sobre un registro de MAK.

    python3 cultura/mak_forense/forense.py testeos
    python3 cultura/mak_forense/forense.py muestras
    python3 cultura/mak_forense/forense.py jsonl ~/curatoria/fichas/fichas.jsonl \
        --grupo fuente --contenido categoria,datos_evento --instante indexado_en

Responde una pregunta: de las anotaciones que hay aca, cuales son un hecho
nuevo y cuales son el rastro de otra anotacion. Nunca escribe en la fuente y
nunca borra: deja hallazgos con su certeza, y la exclusion la decide una
persona. Mismo contrato que `triangular.py` con `revision_humana: pendiente`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

try:
    from . import fuentes
    from .patrones import MINIMO_TRAMO, analizar
except ImportError:  # direct execution: python cultura/mak_forense/forense.py
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fuentes  # noqa: E402
    from patrones import MINIMO_TRAMO, analizar  # noqa: E402

# Orden de lectura del informe: lo que el analisis probo primero, lo que
# necesita una persona al final.
_ORDEN_CERTEZA = {"confirmado": 0, "probable": 1, "pendiente": 2}


def _imprimir(analisis, detalle: int) -> None:
    c = analisis.cobertura
    print()
    print("  registros analizados    :", c.registros)
    print("  grupos                  :", c.grupos)
    print("  pares comparados        :", c.pares_comparados)
    print()

    por_patron = analisis.por_patron()
    if not por_patron:
        print("  sin hallazgos.")
    else:
        print("  HALLAZGOS (anotaciones alcanzadas por cada patron)")
        for patron, n in por_patron.items():
            print("    %-26s: %d" % (patron, n))
        print()
        print("  por certeza:", ", ".join(
            "%s=%d" % (k, v) for k, v in analisis.por_certeza().items() if v))

    grandes = sorted(analisis.hallazgos,
                     key=lambda h: (_ORDEN_CERTEZA[h.certeza], -h.n))[:detalle]
    if grandes:
        print()
        print("  LOS %d MAS GRANDES" % len(grandes))
        for h in grandes:
            origen = " <- %s" % h.origen if h.origen else ""
            print("    [%s] %s · %s%s" % (h.certeza, h.patron, h.grupo, origen))
            print("        %s" % h.explicacion)

    print()
    print("  LO QUE ESTE ANALISIS NO PUEDE VER")
    for limite in c.limites:
        print("    - %s" % limite)
    print()
    print("  nada se borro: cada hallazgo marca registros que siguen en la fuente.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fuente", choices=("testeos", "muestras", "jsonl"))
    ap.add_argument("archivo", nargs="?", help="ruta del JSONL (solo fuente=jsonl)")
    ap.add_argument("--db", default=fuentes.DB_RD,
                    help="base RD en solo lectura (default %(default)s)")
    ap.add_argument("--grupo", help="campo que agrupa (jsonl)")
    ap.add_argument("--contenido", help="campos separados por coma que definen "
                                        "«la misma anotacion» (jsonl)")
    ap.add_argument("--orden", help="campo de posicion dentro del grupo (jsonl)")
    ap.add_argument("--identificador", help="campo id (jsonl)")
    ap.add_argument("--fecha", help="campo con la fecha declarada (jsonl)")
    ap.add_argument("--instante", help="campo con el instante real de carga (jsonl)")
    ap.add_argument("--minimo-tramo", type=int, default=MINIMO_TRAMO,
                    help="largo minimo de un tramo compartido para contar "
                         "(default %(default)s; con 4 aparecen falsos positivos "
                         "de coincidencia generica)")
    ap.add_argument("--detalle", type=int, default=8,
                    help="cuantos hallazgos mostrar en detalle")
    ap.add_argument("--json", dest="salida_json",
                    help="ademas, escribir el informe completo aca")
    args = ap.parse_args(argv)

    if args.fuente == "testeos":
        registros, limites = fuentes.desde_testeos_rd(args.db)
    elif args.fuente == "muestras":
        registros, limites = fuentes.desde_muestras_rd(args.db)
    else:
        if not (args.archivo and args.grupo and args.contenido):
            ap.error("jsonl necesita ARCHIVO, --grupo y --contenido")
        registros, limites = fuentes.desde_jsonl(
            args.archivo,
            campo_grupo=args.grupo,
            campos_contenido=[c.strip() for c in args.contenido.split(",") if c.strip()],
            campo_orden=args.orden,
            campo_id=args.identificador,
            campo_fecha=args.fecha,
            campo_instante=args.instante,
        )

    if not registros:
        print("  la fuente no tiene registros: nada que analizar.")
        return 0

    analisis = analizar(registros, minimo_tramo=args.minimo_tramo,
                        limites_extra=limites)
    _imprimir(analisis, args.detalle)

    if args.salida_json:
        with open(args.salida_json, "w", encoding="utf-8") as fh:
            fh.write(analisis.como_json(indent=1))
        print("  informe                 :", args.salida_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
