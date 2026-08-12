# -*- coding: utf-8 -*-
"""Un ensayo de MAK entra al archivo de iskvw por el mismo contrato.

El tramo que faltaba: `contrato_archivo.convertir()` ya traducia el micelio a
piezas+vinculos, pero un ENSAYO terminaba en una carpeta que ninguna piel
miraba. `desde_ensayo()` lo convierte, y vive en el contrato (no en el
generador) porque un ensayo existe en los dos lados: aca los curados de
`docs/cultura/ensayos/`, en la caja los que escribe `research.py --formato
ensayo`.

Lo que se fija es la regla del esquema, no la forma bonita: **ninguna pieza
afirma un dato que no tiene**. Un icono declarado y ausente del disco no
produce pieza; `declara_animacion` se LEE del archivo (tiene keyframes) en vez
de afirmarse; y los vinculos son `manual` y nunca `semantico`, porque nadie
midio una distancia aca -- los declara un manifiesto.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


contrato = _cargar("contrato_archivo_test",
                   REPO / "cultura" / "mak_plataforma" / "contrato_archivo.py")


UN_ENSAYO = {
    "slug": "demo",
    "titulo": "Synthetic essay fixture",
    "ruta": "docs/cultura/ensayos/demo/ensayo.md",
    "conceptos": [
        {"n": "07", "slug": "07-demo", "titulo": "Berlín: cae el muro",
         "descripcion": "1989: búnkeres y fábricas se vuelven catedrales.",
         "ancla": "### 2.5 Berlín", "estilo": "Brutalista concreto",
         "archivo": "07-berlin.svg", "archivo_src": "x/07-berlin.svg",
         "declara_animacion": True},
        {"n": "08", "slug": "08-sin-icono", "titulo": "Un concepto sin ícono",
         "descripcion": "Existe en el texto y no se ilustró.",
         "ancla": "### 4.1 Ácido"},
    ],
}


def test_un_ensayo_produce_ensayo_conceptos_e_iconos():
    d = contrato.desde_ensayo(UN_ENSAYO)
    clases = [p["clase"] for p in d["piezas"]]
    assert clases.count("informe") == 1
    assert clases.count("concepto") == 2
    # el segundo concepto no tiene icono en disco: NO produce pieza grafica
    assert clases.count("pieza_grafica") == 1


def test_un_icono_ausente_no_produce_pieza():
    """La regla 1 del esquema. Una pieza que afirma un archivo que no está es
    la mentira que el contrato existe para impedir."""
    sin_svg = json.loads(json.dumps(UN_ENSAYO))
    for c in sin_svg["conceptos"]:
        c.pop("archivo_src", None)
    d = contrato.desde_ensayo(sin_svg)
    assert not [p for p in d["piezas"] if p["clase"] == "pieza_grafica"]
    # y ningun medio queda apuntando a la nada
    assert all(not (p.get("medio") or {}).get("src") or p["clase"] == "informe"
               for p in d["piezas"])


def test_los_vinculos_son_manuales_y_no_semanticos():
    """`semantico` significa medido. Acá la relación la declara un manifiesto,
    y llamarla medida sería el mismo defecto que los vínculos por etiqueta
    fingiendo ser semánticos."""
    d = contrato.desde_ensayo(UN_ENSAYO)
    assert d["vinculos"]
    assert {v["clase"] for v in d["vinculos"]} == {"manual"}


def test_cada_concepto_cuelga_del_ensayo_y_cada_icono_de_su_concepto():
    d = contrato.desde_ensayo(UN_ENSAYO)
    ids = {p["id"] for p in d["piezas"]}
    ensayo = [p for p in d["piezas"] if p["clase"] == "informe"][0]["id"]
    conceptos = {p["id"] for p in d["piezas"] if p["clase"] == "concepto"}
    iconos = {p["id"] for p in d["piezas"] if p["clase"] == "pieza_grafica"}
    for v in d["vinculos"]:
        assert v["de"] in ids and v["a"] in ids       # ningun vinculo al vacio
    assert all(any(v["de"] == c and v["a"] == ensayo for v in d["vinculos"])
               for c in conceptos)
    assert all(any(v["de"] == i and v["a"] in conceptos for v in d["vinculos"])
               for i in iconos)


def test_un_concepto_sin_titulo_no_entra():
    """Un concepto NOMBRABLE se dice con una frase nominal. Sin nombre no hay
    concepto, y meterlo con el slug de relleno seria inventarle un nombre."""
    roto = json.loads(json.dumps(UN_ENSAYO))
    roto["conceptos"].append({"slug": "sin-nombre", "descripcion": "algo"})
    d = contrato.desde_ensayo(roto)
    assert len([p for p in d["piezas"] if p["clase"] == "concepto"]) == 2


def test_los_titulos_conservan_su_castellano():
    """Regla 2 del esquema: todo lo visible en castellano correcto. El id es
    clave de maquina y va sin tildes; el titulo es lo que lee un humano."""
    d = contrato.desde_ensayo(UN_ENSAYO)
    con = [p for p in d["piezas"] if p["clase"] == "concepto"][0]
    assert "Berlín" in con["titulo"]
    assert "búnkeres" in con["resumen"]
    assert "demo" in con["id"] and "í" not in con["id"]


def test_el_ancla_viaja_en_extra():
    """El pasaje que justifica el concepto. Es lo que hace que el ícono no
    reclame un significado que el ensayo no le dio."""
    d = contrato.desde_ensayo(UN_ENSAYO)
    con = [p for p in d["piezas"] if p["clase"] == "concepto"][0]
    assert con["extra"]["ancla"].startswith("###")


def test_declara_animacion_solo_si_el_llamador_lo_midio():
    """No se afirma: se lee del archivo.

    Que un SVG declare keyframes y que se mueva de forma perceptible son dos
    hechos distintos, y el contrato solo puede afirmar el que el archivo
    codifica. La medición perceptual pertenece al informe de integración y se
    ejecuta bajo demanda, no dentro de esta suite."""
    d = contrato.desde_ensayo(UN_ENSAYO)
    ico = [p for p in d["piezas"] if p["clase"] == "pieza_grafica"][0]
    assert ico["extra"] == {"declara_animacion": True}

    mudo = json.loads(json.dumps(UN_ENSAYO))
    mudo["conceptos"][0]["declara_animacion"] = False
    d2 = contrato.desde_ensayo(mudo)
    ico2 = [p for p in d2["piezas"] if p["clase"] == "pieza_grafica"][0]
    assert ico2["extra"] == {}
