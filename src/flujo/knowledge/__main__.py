"""Entrada re-ejecutable del knowledge store para tareas de indexado.

Uso:
    py -m flujo.knowledge ingest-dossiers   # indexa projects/cultura/dossiers/*.md
    py -m flujo.knowledge list dossiers     # lista entidades de una categoria

La ingesta es idempotente: correrla dos veces no cambia nada si los .md
fuente no cambiaron. El indice vive en knowledge/dossiers/*.yaml (metadata +
referencia por ruta, sin copiar el cuerpo del dossier).
"""

from __future__ import annotations

import sys

from .store import ingest_dossiers, list_entities


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else ""
    if cmd == "ingest-dossiers":
        paths = ingest_dossiers()
        for p in paths:
            print(p)
        print(f"OK: {len(paths)} dossiers indexados")
        return 0
    if cmd == "list":
        entity = argv[1] if len(argv) > 1 else "dossiers"
        items = list_entities(entity)
        for item in items:
            print(item)
        if not items:
            print(f"sin entidades para {entity}")
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
