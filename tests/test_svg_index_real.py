# -*- coding: utf-8 -*-
"""El índice de respaldo de SVG Studio no puede listar archivos que no existen.

`web/src/data/svgIndex.ts` es lo que la galería dibuja mientras llega la
respuesta de `/api/list-svg-works`, y lo único que tiene cuando no hay backend.

Medido en vivo el 2026-07-26: 16 entradas apuntaban a `02_editables_svg/` y
`03_final_vectorizado_svg/`, dos carpetas borradas ESE MISMO DÍA al quedarse
sólo con las contraportadas aprobadas. Se borraron los archivos y no se
regeneró el índice, así que abrir SVG Studio disparaba 16 errores 404 y mostraba
piezas rotas. El defecto lo introduje yo al limpiar; este test evita repetirlo.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDICE = REPO_ROOT / "web" / "src" / "data" / "svgIndex.ts"


def _rutas() -> list[str]:
    texto = INDICE.read_text(encoding="utf-8")
    return re.findall(r'"svgUrl":\s*"([^"]+)"', texto)


def test_toda_pieza_del_indice_existe_en_disco():
    rutas = _rutas()
    assert rutas, "el índice quedó vacío"
    faltan = [r for r in rutas if not (REPO_ROOT / r.lstrip("/")).is_file()]
    assert not faltan, (
        "svgIndex.ts lista piezas que no están en disco. Si borraste o moviste "
        "SVGs, actualizá el índice en el mismo commit: es lo que la galería "
        "muestra cuando no hay backend.\n  " + "\n  ".join(faltan)
    )


def test_no_quedan_carpetas_retiradas():
    """Las dos que se retiraron el 2026-07-26 por no ser el diseño aprobado."""
    texto = INDICE.read_text(encoding="utf-8")
    for carpeta in ("02_editables_svg", "03_final_vectorizado_svg",
                    "05_dark_neon", "06_dark_vectorizado_svg"):
        assert carpeta not in texto, (
            f"{carpeta} volvió al índice; esa carpeta no existe y su diseño no "
            "es el aprobado (la referencia es 09_contraportadas_dark)"
        )


def test_estan_las_piezas_que_si_existen():
    """Lo contrario del test anterior: el índice tampoco puede quedarse corto.

    Las dos piezas de eventos existían en disco y NO estaban en el respaldo, así
    que sin backend la galería mostraba suplementos y nada de eventos.
    """
    rutas = set(_rutas())
    for carpeta in ("svg/eventos_rd", "svg/suplementos_rd/09_contraportadas_dark"):
        for svg in sorted((REPO_ROOT / carpeta).glob("*.svg")):
            rel = "/" + svg.relative_to(REPO_ROOT).as_posix()
            assert rel in rutas, f"{rel} está en disco pero no en el índice"
