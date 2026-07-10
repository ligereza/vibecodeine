"""Tests de los helpers puros de blender_nodes (sin Blender/bpy).

La geometria de referencia es la medida del FRAME2.png real (9898x9899,
ventana pixel (6488,378)-(9350,4272)) -- ver docstring del modulo.
Modelo validado en vivo 2026-07-10: el contenido ajusta al ANCHO de la
ventana siempre; el alto sobrante lo maneja el fade (no el mapping).
"""
import pytest

from flujo.eventos.blender_nodes import (
    WINDOW_UV, fitwidth_mapping, hue_de_rgb, _parse_args, _resolver_ruta,
)

FRAME_REAL = (9898, 9899)
INPUT_CUADRADO = (1179, 1179)


def _aplicar(uv, scale, loc):
    return (uv[0] * scale[0] + loc[0], uv[1] * scale[1] + loc[1])


def test_window_uv_sano():
    assert 0 < WINDOW_UV["x0"] < WINDOW_UV["x1"] < 1
    assert 0 < WINDOW_UV["y0"] < WINDOW_UV["y1"] < 1


def test_fitwidth_cuadrado_llena_ancho_centrado_en_alto():
    # input cuadrado en ventana portrait (w/h ~0.735): llena el ancho
    # exacto; en vertical el contenido ocupa ~73% centrado y el resto
    # queda fuera de [0,1] (lo apaga el fade, no el mapping).
    scale, loc = fitwidth_mapping(WINDOW_UV, FRAME_REAL, INPUT_CUADRADO)
    u0 = _aplicar((WINDOW_UV["x0"], WINDOW_UV["y0"]), scale, loc)
    u1 = _aplicar((WINDOW_UV["x1"], WINDOW_UV["y1"]), scale, loc)
    assert u0[0] == pytest.approx(0.0, abs=1e-6)   # ancho: borde a borde
    assert u1[0] == pytest.approx(1.0, abs=1e-6)
    assert u0[1] < 0.0 < 1.0 < u1[1]               # alto: sobra ventana
    assert u0[1] == pytest.approx(1.0 - u1[1], abs=1e-6)  # centrado
    # fraccion visible del alto de la ventana que ocupa el contenido
    assert 1.0 / (u1[1] - u0[1]) == pytest.approx(0.735, abs=0.01)


def test_fitwidth_input_aspecto_ventana_es_identidad():
    win_w = (WINDOW_UV["x1"] - WINDOW_UV["x0"]) * FRAME_REAL[0]
    win_h = (WINDOW_UV["y1"] - WINDOW_UV["y0"]) * FRAME_REAL[1]
    scale, loc = fitwidth_mapping(WINDOW_UV, FRAME_REAL, (round(win_w), round(win_h)))
    u0 = _aplicar((WINDOW_UV["x0"], WINDOW_UV["y0"]), scale, loc)
    u1 = _aplicar((WINDOW_UV["x1"], WINDOW_UV["y1"]), scale, loc)
    assert u0[0] == pytest.approx(0.0, abs=1e-3)
    assert u0[1] == pytest.approx(0.0, abs=1e-3)
    assert u1[0] == pytest.approx(1.0, abs=1e-3)
    assert u1[1] == pytest.approx(1.0, abs=1e-3)


def test_fitwidth_input_muy_vertical_recorta_alto():
    # input mas vertical que la ventana: igual llena el ancho; el alto
    # visible es una banda central del input (v' dentro de [0,1] en toda
    # la ventana -> el excedente del input queda fuera de la ventana).
    scale, loc = fitwidth_mapping(WINDOW_UV, FRAME_REAL, (500, 2000))
    u0 = _aplicar((WINDOW_UV["x0"], WINDOW_UV["y0"]), scale, loc)
    u1 = _aplicar((WINDOW_UV["x1"], WINDOW_UV["y1"]), scale, loc)
    assert u0[0] == pytest.approx(0.0, abs=1e-6)
    assert u1[0] == pytest.approx(1.0, abs=1e-6)
    assert 0.0 < u0[1] < u1[1] < 1.0
    assert u0[1] == pytest.approx(1.0 - u1[1], abs=1e-6)  # banda centrada


def test_fitwidth_dimensiones_invalidas():
    with pytest.raises(ValueError):
        fitwidth_mapping(WINDOW_UV, FRAME_REAL, (0, 100))
    with pytest.raises(ValueError):
        fitwidth_mapping({"x0": 0.5, "x1": 0.5, "y0": 0.1, "y1": 0.9},
                         FRAME_REAL, INPUT_CUADRADO)


def test_hue_de_rgb():
    assert hue_de_rgb((0, 254, 254)) == pytest.approx(0.5, abs=1e-3)   # cyan
    assert hue_de_rgb((255, 0, 0)) == pytest.approx(0.0, abs=1e-3)     # rojo
    assert hue_de_rgb((0, 255, 0)) == pytest.approx(1 / 3, abs=1e-3)   # verde
    # neutros: hue 0 pero irrelevante (S=0); no debe reventar
    assert hue_de_rgb((30, 30, 30)) == 0.0
    # fuera de rango se clampa
    assert hue_de_rgb((300, -5, 0)) == pytest.approx(0.0, abs=1e-3)


def test_parse_args():
    argv = ["blender", "-b", "x.blend", "--python", "s.py", "--",
            "--frame", "f.png", "--input", "i.jpg", "--salida", "o.png"]
    parsed = _parse_args(argv)
    assert parsed["frame"] == "f.png"
    assert parsed["input"] == "i.jpg"
    assert parsed["salida"] == "o.png"
    assert parsed["color_png"] is None


def test_parse_args_faltan_obligatorios():
    with pytest.raises(SystemExit):
        _parse_args(["blender", "--", "--frame", "f.png"])  # falta --input
    with pytest.raises(SystemExit):
        _parse_args(["blender", "--", "--desconocido", "x"])


def test_parse_args_solo_input_es_valido():
    parsed = _parse_args(["blender", "--", "--input", "i.jpg"])
    assert parsed["input"] == "i.jpg"
    assert parsed["frame"] is None  # default se deriva del .blend en main()


def test_resolver_ruta(tmp_path):
    real = tmp_path / "FRAME2.png"
    real.write_bytes(b"x")
    # relativa inexistente desde CWD -> cae a la carpeta del .blend
    assert _resolver_ruta("FRAME2.png", str(tmp_path)) == str(real)
    # absoluta o existente: intacta
    assert _resolver_ruta(str(real), str(tmp_path)) == str(real)
    # None pasa de largo (arg opcional ausente)
    assert _resolver_ruta(None, str(tmp_path)) is None
