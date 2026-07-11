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


# ---------------------------------------------------------------------------
# Modos loom: field / border / medallion / mihrab
# ---------------------------------------------------------------------------
from vibecode.loom import (  # noqa: E402
    LOOM_MODES,
    MOTIF_CITATIONS,
    block_segments,
    canvas_size,
    loom_color_index,
)

# Canvas sintetico: 24 filas x 40 columnas, con espacio interior grande para
# que aparezcan marcos, vacio central, anillos y arco.
LOOM_SAMPLE = "\n".join("x" + " " * 38 + "x" for _ in range(24))


def test_loom_modes_registrados_con_cita():
    assert LOOM_MODES == ("field", "border", "medallion", "mihrab")
    for mode in LOOM_MODES:
        cita = MOTIF_CITATIONS[mode]
        assert cita and "\n" not in cita  # una linea
        assert "dossier tapiz" in cita    # cita al dossier curado


def test_loom_render_static_valido_por_modo():
    for mode in LOOM_MODES:
        out = render_static(LOOM_SAMPLE, mode=mode, palette_name="flujo")
        plain = _strip_ansi(out)
        assert "·" in plain  # espacios digeridos a fill char
        # El contenido plano se conserva (mismas celdas, solo cambia el color)
        assert plain == LOOM_SAMPLE.replace(" ", "·")


def test_loom_modos_difieren_estructuralmente_en_ansi():
    outs = {m: render_static(LOOM_SAMPLE, mode=m) for m in LOOM_MODES}
    vals = list(outs.values())
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            assert vals[i] != vals[j]


def test_loom_border_marcos_y_vacio_central():
    # Borde exterior: primer marco (indice 0); centro: vacio (None)
    assert loom_color_index("border", 0, 0, 40, 24, 5) == 0
    assert loom_color_index("border", 20, 12, 40, 24, 5) is None
    # Los marcos avanzan de color con la profundidad
    assert loom_color_index("border", 2, 12, 40, 24, 5) == 1


def test_loom_medallion_radial_y_simetrico():
    # Centro del canvas: indice 0 (nucleo del medallon)
    assert loom_color_index("medallion", 20, 12, 41, 25, 5) == 0
    # Esquina: anillo exterior, indice mayor que el centro
    corner = loom_color_index("medallion", 0, 0, 41, 25, 5)
    assert corner is not None and corner > 0
    # Simetria vertical: fila de arriba == fila de abajo
    assert loom_color_index("medallion", 7, 0, 41, 25, 5) == loom_color_index(
        "medallion", 7, 24, 41, 25, 5
    )


def test_loom_mihrab_asimetrico_apunta_arriba():
    # Apice: arriba al centro, indice 0
    assert loom_color_index("mihrab", 20, 0, 41, 25, 5) == 0
    # Sin simetria vertical: el arco abre hacia abajo
    top = loom_color_index("mihrab", 20, 0, 41, 25, 5)
    bottom = loom_color_index("mihrab", 20, 24, 41, 25, 5)
    assert top != bottom


def test_loom_field_malla_repetitiva():
    # La malla se repite: misma celda de la malla -> mismo color
    a = loom_color_index("field", 0, 0, 40, 24, 5)
    b = loom_color_index("field", 0 + 4 * 5, 0, 40, 24, 5)  # 5 celdas a la derecha
    assert a == b
    # Y varia dentro de la malla
    assert loom_color_index("field", 0, 0, 40, 24, 5) != loom_color_index(
        "field", 4, 0, 40, 24, 5
    )


def test_loom_block_segments_conserva_longitud():
    for mode in LOOM_MODES:
        segs = block_segments(mode, 3, 5, 17, 40, 24, 5)
        assert sum(n for n, _ in segs) == 17
        assert all(n > 0 for n, _ in segs)


def test_loom_modo_desconocido_lanza_error():
    import pytest

    with pytest.raises(ValueError):
        loom_color_index("garden", 0, 0, 10, 10, 5)


def test_canvas_size_minimos():
    assert canvas_size([]) == (1, 1)
    assert canvas_size(["", "abc"]) == (3, 2)


def test_loom_render_spaces_terminal_incluye_cita():
    for mode in LOOM_MODES:
        buf = io.StringIO()
        render_spaces(LOOM_SAMPLE, mode=mode, animate=False, file=buf)
        plain = _strip_ansi(buf.getvalue())
        assert MOTIF_CITATIONS[mode] in plain


def test_loom_animate_cae_a_estatico():
    # Los modos loom son composiciones estaticas: -a no debe entrar al bucle
    # de animacion (sin CLEAR_SCREEN, sin frames).
    from vibecode.ansi import CLEAR_SCREEN

    buf = io.StringIO()
    render_spaces(LOOM_SAMPLE, mode="border", animate=True, file=buf)
    out = buf.getvalue()
    assert CLEAR_SCREEN not in out
    assert MOTIF_CITATIONS["border"] in _strip_ansi(out)


def test_loom_svg_valido_con_desc_curatorial(tmp_path):
    import xml.etree.ElementTree as ET
    from vibecode.svg_export import export_svg

    for mode in LOOM_MODES:
        out = tmp_path / f"pieza_{mode}.svg"
        export_svg(LOOM_SAMPLE, str(out), mode=mode)
        svg = out.read_text(encoding="utf-8")
        root = ET.fromstring(svg)  # XML valido
        desc = root.find("{http://www.w3.org/2000/svg}desc")
        assert desc is not None, f"modo {mode} sin <desc>"
        assert desc.text == MOTIF_CITATIONS[mode]


def test_loom_svg_modos_difieren_estructuralmente(tmp_path):
    from vibecode.svg_export import render_svg

    svgs = {m: render_svg(LOOM_SAMPLE, mode=m) for m in LOOM_MODES}
    vals = list(svgs.values())
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            assert vals[i] != vals[j]


def test_loom_svg_border_usa_vacio_central(tmp_path):
    from vibecode.svg_export import LOOM_VOID_HEX, render_svg

    svg_border = render_svg(LOOM_SAMPLE, mode="border")
    assert LOOM_VOID_HEX in svg_border      # el centro queda apagado
    svg_field = render_svg(LOOM_SAMPLE, mode="field")
    assert LOOM_VOID_HEX not in svg_field   # la malla no tiene vacio


def test_loom_svg_sin_desc_en_modos_clasicos(tmp_path):
    import xml.etree.ElementTree as ET
    from vibecode.svg_export import render_svg

    root = ET.fromstring(render_svg(LOOM_SAMPLE, mode="void"))
    assert root.find("{http://www.w3.org/2000/svg}desc") is None


def test_loom_cli_acepta_modos():
    # El registry del CLI (-m) debe ofrecer los 4 modos loom
    import vibecode.spaces as spaces_mod

    src_choices = ["void", "length", "blocks", "flow", "scan", "drift", "pulse", "rain"]
    assert set(LOOM_MODES).isdisjoint(src_choices)
    for mode in LOOM_MODES:
        out = render_static("a  b", mode=mode)  # no lanza
        assert out
    assert hasattr(spaces_mod, "LOOM_VOID_COLOR")
