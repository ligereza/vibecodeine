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


def test_el_estado_de_una_pieza_se_declara_no_se_adivina():
    """La galería marcaba TODO como "borrador", incluidas las contraportadas ya
    impresas y aprobadas: el trabajo terminado se veía a medio hacer.

    El estado no se puede deducir del archivo -- que un SVG exista no dice si se
    aprobó. Se declara en data/svg_estados.json, editable a mano, y gana la
    última regla que coincide para poder escribir una general y su excepción.
    """
    import json

    from flujo.web.hub import HubRequestHandler

    handler = HubRequestHandler.__new__(HubRequestHandler)

    aprobada = "svg/suplementos_rd/09_contraportadas_dark/02_impulso.svg"
    assert handler._estado_svg(aprobada) == "aprobado"

    # La plantilla vive DENTRO de suplementos pero no es una pieza que se
    # entregue: es la excepción que la última regla tiene que poder ganar.
    plantilla = "svg/suplementos_rd/_plantilla/contraportada_cambios.svg"
    assert handler._estado_svg(plantilla) == "borrador"

    # Algo no declarado cae al valor por defecto, nunca a "aprobado".
    assert handler._estado_svg("svg/lo_que_sea/pieza_nueva.svg") == "borrador"

    datos = json.loads((REPO_ROOT / "data" / "svg_estados.json").read_text(encoding="utf-8"))
    for regla in datos["reglas"]:
        assert regla["estado"] in ("aprobado", "en-revision", "borrador")
        assert regla.get("nota"), "cada regla dice POR QUE ese estado"
