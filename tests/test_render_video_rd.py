# -*- coding: utf-8 -*-
"""build_expr de tools/render_video_rd.py (rama video, opcion B 2026-07-22)."""
import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location(
    "render_video_rd",
    pathlib.Path(__file__).resolve().parents[1] / "tools" / "render_video_rd.py",
)
rvr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rvr)


def test_expr_frames_automaticos_y_swap_movie():
    expr = rvr.build_expr("/tmp/reel.mp4", "/tmp/out.mp4", "CUDA", None)
    assert "clip.frame_duration" in expr          # frames del clip, no hardcode
    assert "n.image.source == 'MOVIE'" in expr    # solo re-apunta texturas MOVIE
    assert "use_auto_refresh = True" in expr
    assert "compute_device_type = 'CUDA'" in expr
    assert "'FFMPEG'" in expr and "'H264'" in expr


def test_expr_cpu_sin_bloque_gpu():
    expr = rvr.build_expr("v.mp4", "o.mp4", "CPU", None)
    assert "compute_device_type" not in expr


def test_expr_max_frames_cap():
    expr = rvr.build_expr("v.mp4", "o.mp4", "OPTIX", 24)
    assert "min(sc.frame_end, 24)" in expr
    assert "compute_device_type = 'OPTIX'" in expr


def _string_literals(expr: str) -> str:
    """The string literals the expression carries, as Python reads them."""
    import ast

    tree = ast.parse(expr)
    return "".join(
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )


def test_expr_rutas_escapadas():
    # `compile("")` succeeds, so compiling on its own would keep passing if
    # `build_expr` ever returned nothing: the check has to say the paths
    # arrived and survived escaping, not only that the result parses.
    expr = rvr.build_expr(r"C:\rd\reel.mp4", r"C:\rd\out.mp4", "CPU", None)
    compile(expr, "<expr>", "exec")  # el expr debe ser python valido con rutas win
    assert expr.strip(), "build_expr devolvio un expr vacio"
    assert "reel.mp4" in expr and "out.mp4" in expr
    # An unescaped backslash before `rd` turns into a carriage return, and the
    # expression still compiles -- it just renders to the wrong directory.
    assert "\r" not in _string_literals(expr), (
        "la ruta se escapo mal: quedo un retorno de carro en vez de `\\rd`"
    )
