"""Tests de projects/tapiz/vibecode (reconciliado 2026-07-10).

El paquete vive fuera de src/flujo, asi que se agrega su carpeta al path.
Cubre: primitivas compartidas (ansi), render estatico (spaces), render de
linea (void), proxy vivo (life) y medidor de potencia (power).
"""

import io
import sys
from pathlib import Path

TAPIZ_DIR = Path(__file__).resolve().parents[1] / "projects" / "tapiz"
sys.path.insert(0, str(TAPIZ_DIR))

import vibecode  # noqa: E402
from vibecode.ansi import RESET, bg_gray, fg_gray, tokenize  # noqa: E402
from vibecode.render import style_text  # noqa: E402
from vibecode.power import PowerMeter  # noqa: E402
from vibecode.spaces import PALETTES, render_spaces, render_static  # noqa: E402
from vibecode.void import render_line_blocks, render_line_negative  # noqa: E402


def _strip_ansi(text: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;?]*[a-zA-Z]", "", text)


def test_tokenize_preserva_todo():
    line = "def foo(a, b):  return a"
    tokens = tokenize(line)
    assert "".join(part for _, part in tokens) == line
    kinds = {kind for kind, _ in tokens}
    assert kinds == {"word", "space"}


def test_gray_clamp():
    assert bg_gray(-5) == bg_gray(0)
    assert fg_gray(99) == fg_gray(23)


def test_render_static_conserva_texto_ghost():
    code = "if x:\n    y = 1"
    out = render_static(code, mode="void", palette_name="flujo")
    # El texto original debe seguir presente (ghost), los espacios rellenados con el fill char
    plain = _strip_ansi(out)
    assert "if" in plain and "y = 1".replace(" ", "·") in plain.replace("·", "·")
    assert "·" in plain  # espacios -> fill char


def test_render_static_paleta_desconocida_cae_a_flujo():
    out_bad = render_static("a  b", palette_name="no-existe")
    out_flujo = render_static("a  b", palette_name="flujo")
    assert out_bad == out_flujo


def test_paleta_default_es_flujo():
    assert list(PALETTES.keys())[0] == "flujo"


def test_render_spaces_estatico_escribe_a_file():
    buf = io.StringIO()
    render_spaces("x = 1", mode="void", animate=False, file=buf)
    out = buf.getvalue()
    assert "Tapiz Spaces" in _strip_ansi(out)
    assert "x" in _strip_ansi(out)


def test_void_render_line_ancho_exacto():
    line = "    return data"
    for fn in (render_line_negative, render_line_blocks):
        out = fn(line, width=40, ghost=True)
        assert len(_strip_ansi(out)) == 40


def test_void_render_line_recorta():
    out = render_line_negative("x" * 100, width=10, ghost=False)
    assert len(_strip_ansi(out)) == 10


def test_style_text_reposo_vs_actividad():
    text = "a  b"
    quiet = style_text(text, power=0.0)
    busy = style_text(text, power=1.0)
    assert _strip_ansi(quiet) == text
    assert _strip_ansi(busy) == text
    assert quiet != busy  # la potencia cambia el estilo


def test_power_meter_sube_y_decae():
    meter = PowerMeter(window=1.0, threshold=10)
    assert meter.power() == 0.0
    meter.pulse(100)
    assert meter.power() > 0.5


def test_life_proxy_restaura_stdout():
    original = sys.stdout
    with vibecode.watch():
        print("hola vibecode")
        assert sys.stdout is not original
    assert sys.stdout is original


def test_api_publica():
    for name in ("init", "deinit", "watch", "life", "pulse", "render_spaces"):
        assert hasattr(vibecode, name)


def test_svg_export_xml_valido_y_paleta_flujo(tmp_path):
    import xml.etree.ElementTree as ET
    from vibecode.svg_export import FLUJO_HEX, export_svg

    out = tmp_path / "pieza.svg"
    export_svg("def f(x):\n    return x\n     y", str(out), mode="void")
    svg = out.read_text(encoding="utf-8")
    ET.fromstring(svg)  # XML valido
    assert FLUJO_HEX["ink"] in svg       # fondo
    assert FLUJO_HEX["support"] in svg   # bloques de 1 y 4 espacios (idx len%5)
    assert FLUJO_HEX["accent"] in svg    # bloque de 5 espacios (idx 0)
    assert "<animate" not in svg         # sin -a no hay animacion


def test_svg_export_animado_y_sin_ghost(tmp_path):
    from vibecode.svg_export import GHOST_COLOR, export_svg

    out = tmp_path / "pieza.svg"
    export_svg("a b\n  c", str(out), animate=True, ghost=False)
    svg = out.read_text(encoding="utf-8")
    assert "<animate" in svg and 'dur="90s"' in svg
    assert GHOST_COLOR not in svg  # sin ghost el texto no lleva gris fantasma


def test_svg_export_escapa_html(tmp_path):
    from vibecode.svg_export import export_svg

    out = tmp_path / "pieza.svg"
    export_svg("if a < b: c = '<&>'", str(out))
    svg = out.read_text(encoding="utf-8")
    assert "&lt;" in svg and "&amp;" in svg
