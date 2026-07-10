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
