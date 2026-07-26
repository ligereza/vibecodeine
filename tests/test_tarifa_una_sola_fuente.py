# -*- coding: utf-8 -*-
"""The RD tariff has ONE source: data/rd_packs.json.

Measured defect (2026-07-26): the price lived hardcoded in two places,
src/flujo/plano/packs.py and web/src/rdBrand.ts. Python was moved to read the
JSON, but the web kept its own copy and the hub never applied any override, so
editing the tariff changed the rider PDF and left the app showing the old
figures. The hub now serves /api/rd-packs and main.tsx applies it before React
mounts; the numbers still written in rdBrand.ts are the fallback for a static
build with no hub to ask.

A fallback that disagrees with the real tariff is worse than no fallback, so
this test pins them together.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARIFA = REPO_ROOT / "data" / "rd_packs.json"
RD_BRAND = REPO_ROOT / "web" / "src" / "rdBrand.ts"


def _precios_del_json() -> dict[str, int]:
    datos = json.loads(TARIFA.read_text(encoding="utf-8"))
    return {pid: int(p["precio"]) for pid, p in datos["packs"].items()}


def _precios_del_typescript() -> dict[str, int]:
    """Precios del objeto PACKS de rdBrand.ts, por bloque `id: 'X'` .. `precio`."""
    texto = RD_BRAND.read_text(encoding="utf-8")
    bloques = re.findall(
        r"id:\s*'([A-Z]+)'.*?precio:\s*([\d_]+)", texto, re.S)
    return {pid: int(precio.replace("_", "")) for pid, precio in bloques}


def test_python_lee_la_tarifa_del_archivo():
    from flujo.plano import packs

    esperado = _precios_del_json()
    real = {pid: int(p["precio"]) for pid, p in packs.PACKS.items()}
    assert real == esperado, (
        "packs.py no esta leyendo data/rd_packs.json (probablemente cayo al "
        "respaldo interno; revisa el aviso en stderr)"
    )


def test_el_respaldo_del_typescript_coincide_con_la_tarifa():
    json_precios = _precios_del_json()
    ts_precios = _precios_del_typescript()
    assert ts_precios, "no se pudieron leer los precios de rdBrand.ts"
    comunes = {k: ts_precios[k] for k in json_precios if k in ts_precios}
    assert comunes == json_precios, (
        "el respaldo de precios en web/src/rdBrand.ts quedo desfasado de "
        "data/rd_packs.json. La tarifa se edita en el JSON; si cambia, el "
        "respaldo del bundle estatico se actualiza en el mismo commit.\n"
        f"  json: {json_precios}\n  rdBrand.ts: {comunes}"
    )


def test_el_hub_sirve_la_misma_tarifa():
    """/api/rd-packs sale del modulo packs, no de una copia aparte."""
    from flujo.plano import packs

    fuente = (REPO_ROOT / "src" / "flujo" / "web" / "hub.py").read_text(encoding="utf-8")
    assert '"/api/rd-packs"' in fuente, "el endpoint desaparecio"
    assert "_packs.PACKS" in fuente, (
        "el endpoint dejo de servir flujo.plano.packs; una tercera copia de la "
        "tarifa es exactamente el defecto que esto evita"
    )
    assert packs.ALL_PACKS and packs.DEFAULT_PACK in packs.PACKS
