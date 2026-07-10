"""Tests de los helpers puros de blender_nodes (sin Blender/bpy).

La geometria de referencia es la medida del FRAME2.png real (9898x9899,
ventana pixel (6488,378)-(9350,4272)) -- ver docstring del modulo.
"""
import pytest

from flujo.eventos.blender_nodes import WINDOW_UV, cover_mapping, hue_de_rgb, _parse_args

FRAME_REAL = (9898, 9899)
INPUT_CUADRADO = (1179, 1179)


def _aplicar(uv, scale, loc):
    return (uv[0] * scale[0] + loc[0], uv[1] * scale[1] + loc[1])


def test_window_uv_sano():
    assert 0 < WINDOW_UV["x0"] < WINDOW_UV["x1"] < 1
    assert 0 < WINDOW_UV["y0"] < WINDOW_UV["y1"] < 1


def test_cover_input_cuadrado_recorta_ancho():
    # ventana portrait (w/h ~0.735) + input cuadrado: llena el alto,
    # recorta los costados centrado.
    scale, loc = cover_mapping(WINDOW_UV, FRAME_REAL, INPUT_CUADRADO)
    # esquinas de la ventana -> recorte central del input
    u0 = _aplicar((WINDOW_UV["x0"], WINDOW_UV["y0"]), scale, loc)
    u1 = _aplicar((WINDOW_UV["x1"], WINDOW_UV["y1"]), scale, loc)
    assert u0[1] == pytest.approx(0.0, abs=1e-6)
    assert u1[1] == pytest.approx(1.0, abs=1e-6)
    # horizontal: banda centrada de ancho ~0.735
    ancho = u1[0] - u0[0]
    assert ancho == pytest.approx(0.735, abs=0.01)
    assert u0[0] == pytest.approx((1 - ancho) / 2, abs=1e-6)


def test_cover_input_igual_a_ventana_es_identidad():
    # input con exactamente el aspect de la ventana: sin recorte
    win_w = (WINDOW_UV["x1"] - WINDOW_UV["x0"]) * FRAME_REAL[0]
    win_h = (WINDOW_UV["y1"] - WINDOW_UV["y0"]) * FRAME_REAL[1]
    scale, loc = cover_mapping(WINDOW_UV, FRAME_REAL, (round(win_w), round(win_h)))
    u0 = _aplicar((WINDOW_UV["x0"], WINDOW_UV["y0"]), scale, loc)
    u1 = _aplicar((WINDOW_UV["x1"], WINDOW_UV["y1"]), scale, loc)
    assert u0[0] == pytest.approx(0.0, abs=1e-3)
    assert u0[1] == pytest.approx(0.0, abs=1e-3)
    assert u1[0] == pytest.approx(1.0, abs=1e-3)
    assert u1[1] == pytest.approx(1.0, abs=1e-3)


def test_cover_input_mas_portrait_recorta_alto():
    # input mas vertical que la ventana: llena el ancho, recorta el alto
    scale, loc = cover_mapping(WINDOW_UV, FRAME_REAL, (500, 2000))
    u0 = _aplicar((WINDOW_UV["x0"], WINDOW_UV["y0"]), scale, loc)
    u1 = _aplicar((WINDOW_UV["x1"], WINDOW_UV["y1"]), scale, loc)
    assert u0[0] == pytest.approx(0.0, abs=1e-6)
    assert u1[0] == pytest.approx(1.0, abs=1e-6)
    assert 0.0 < u0[1] < u1[1] < 1.0
    # recorte centrado
    assert u0[1] == pytest.approx(1.0 - u1[1], abs=1e-6)


def test_cover_dimensiones_invalidas():
    with pytest.raises(ValueError):
        cover_mapping(WINDOW_UV, FRAME_REAL, (0, 100))
    with pytest.raises(ValueError):
        cover_mapping({"x0": 0.5, "x1": 0.5, "y0": 0.1, "y1": 0.9},
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
        _parse_args(["blender", "--", "--frame", "f.png"])
    with pytest.raises(SystemExit):
        _parse_args(["blender", "--", "--desconocido", "x"])
