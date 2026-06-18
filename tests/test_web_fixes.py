"""Tests de los fixes del editor (v0.30.1):
- IG detecta URLs sin esquema
- preview SVG responsive (no se sale de pantalla)
- formatos verticales cargan con orientación correcta
"""

import pytest

from flujo.intake.email_parser import extract_instagram_links
from flujo.web.svg_preview import render_svg
from flujo.web.editor import load_format_state, analizar_instagram


# --- IG: detección robusta ------------------------------------------------

def test_ig_sin_esquema():
    assert extract_instagram_links("instagram.com/p/ABC/") == ["https://instagram.com/p/ABC/"]


def test_ig_sin_www_ni_https():
    out = extract_instagram_links("mira instagram.com/reel/XYZ/ gracias")
    assert out == ["https://instagram.com/reel/XYZ/"]


def test_ig_normaliza_http_a_https():
    out = extract_instagram_links("http://instagram.com/p/ABC123")
    assert out == ["https://instagram.com/p/ABC123"]


def test_ig_ignora_querystring():
    out = extract_instagram_links("https://www.instagram.com/p/ABC/?igsh=zz")
    assert out == ["https://www.instagram.com/p/ABC/"]


def test_ig_varios_links_dedup():
    out = extract_instagram_links("instagram.com/p/A1/ y instagram.com/p/A1/ y instagram.com/p/B2/")
    assert out == ["https://instagram.com/p/A1/", "https://instagram.com/p/B2/"]


def test_analizar_ig_url_directa_detecta():
    out = analizar_instagram("instagram.com/p/ABC123/")
    assert "Links de Instagram detectados: 1" in out
    assert "SIN LINKS" not in out.upper()


# --- preview responsive ----------------------------------------------------

def test_render_svg_responsive():
    cfg = {"canvas": {"width": 3300, "height": 1300}, "palette": {},
           "documents": [{"id": "d", "elements": []}]}
    svg = render_svg(cfg, responsive=True)
    head = svg.splitlines()[0]
    assert 'width="100%"' in head
    assert "3300px" not in head
    assert 'viewBox="0 0 3300 1300"' in head


def test_render_svg_export_mantiene_px():
    cfg = {"canvas": {"width": 3300, "height": 1300}, "palette": {},
           "documents": [{"id": "d", "elements": []}]}
    svg = render_svg(cfg, responsive=False)
    assert "3300px" in svg


# --- orientación de formatos ----------------------------------------------

def test_flyer_fisico_carga_vertical():
    cfg, _, _ = load_format_state("evt_flyer_fisico_10x14")
    w, h = cfg["canvas"]["width"], cfg["canvas"]["height"]
    assert h > w, "el flyer físico 10x14 debe ser vertical"
    assert "_aviso_orientacion" in cfg


def test_etiqueta_sigue_horizontal():
    cfg, _, _ = load_format_state("sup_etiqueta_165x65")
    w, h = cfg["canvas"]["width"], cfg["canvas"]["height"]
    assert w > h, "la etiqueta 16.5x6.5 es horizontal"


def test_cartelera_vertical_sin_aviso():
    cfg, _, _ = load_format_state("evt_cartelera_individual_1080x1920")
    w, h = cfg["canvas"]["width"], cfg["canvas"]["height"]
    assert h > w
    # no necesita reconciliación (no tiene plantilla horizontal)
    assert "_aviso_orientacion" not in cfg
