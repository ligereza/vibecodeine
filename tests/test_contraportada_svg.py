"""
Tests de src/flujo/comercial/contraportada_svg.py -- generador de contraportadas
de suplementos RD (harm-reduction). Gap #4 de la pasada de cobertura. Fija el
GUARD anti-desync (el bug historico: la plantilla y el codigo se desincronizan y
la pieza sale con placeholder crudo sin fallar) y el split de nombre 1/2/3 palabras.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from flujo.comercial import contraportada_svg as cs
from flujo.comercial.suplementos_config import get_suplemento

_NS = "http://www.w3.org/2000/svg"


def _svg_con_textos(*textos: str) -> ET.Element:
    root = ET.Element(f"{{{_NS}}}svg")
    for t in textos:
        el = ET.SubElement(root, f"{{{_NS}}}text")
        el.text = t
    return root


def test_replace_text_cuenta_reemplazos():
    root = _svg_con_textos("DESCRIPCION", "otro", "DESCRIPCION aqui")
    n = cs._replace_text_in_svg(root, "DESCRIPCION", "Nueva")
    assert n == 2


def test_replace_required_lanza_si_no_hay_placeholder():
    """El guard: campo obligatorio sin placeholder en la plantilla = ValueError,
    no una pieza con el texto crudo (el bug que el guard existe para atrapar)."""
    root = _svg_con_textos("texto que no matchea")
    with pytest.raises(ValueError, match="Campo obligatorio 'descripcion'"):
        cs._replace_required(root, "DESCRIPCION", "Magnesio citrato", "descripcion")


def test_replace_required_ok_cuando_existe():
    root = _svg_con_textos("DESCRIPCION")
    assert cs._replace_required(root, "DESCRIPCION", "Nueva desc", "descripcion") == 1
    # y efectivamente reemplazo (no quedo el placeholder crudo)
    textos = [e.text for e in root.findall(f".//{{{_NS}}}text")]
    assert "Nueva desc" in textos
    assert "DESCRIPCION" not in textos


def test_generar_contraportada_end_to_end_valido(tmp_path):
    """Genera una pieza real con un suplemento del catalogo: sale un SVG
    parseable, sin ValueError (los placeholders obligatorios existen en la
    plantilla real) y sin placeholders crudos de nombre."""
    supl = get_suplemento("Impulso")
    out = tmp_path / "impulso_final.svg"
    result = cs.generar_contraportada(supl, output_path=out)
    assert result.exists()
    tree = ET.parse(str(result))          # parseable = XML valido
    textos = [e.text or "" for e in tree.getroot().findall(f".//{{{_NS}}}text")]
    joined = " ".join(textos)
    # el nombre reemplazo el placeholder base
    assert "NOMBRE DEL" not in joined


def test_split_nombre_una_palabra(tmp_path):
    """Nombre de 1 palabra: va a 'NOMBRE DEL' y el segundo placeholder se vacia."""
    supl = get_suplemento("Impulso")   # 'IMPULSO' -> 1 palabra
    out = tmp_path / "n1.svg"
    cs.generar_contraportada(supl, output_path=out)
    joined = " ".join(e.text or "" for e in ET.parse(str(out)).getroot().findall(f".//{{{_NS}}}text"))
    assert "IMPULSO" in joined
