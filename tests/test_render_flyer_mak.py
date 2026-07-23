"""Tests de tools/render_flyer_mak.py -- SIN Blender real (mock subprocess).

Cubre: composicion del comando Blender (blend correcto, --python-expr con
los settings anti-OOM y el material 'flyer_final'), parseo RENDER_OK/FALLO
y paleta de color con una imagen sintetica chica (PIL, ya es dependencia
del repo).
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "render_flyer_mak.py"
_spec = importlib.util.spec_from_file_location("render_flyer_mak", MODULE_PATH)
render_flyer_mak = importlib.util.module_from_spec(_spec)
sys.modules["render_flyer_mak"] = render_flyer_mak
_spec.loader.exec_module(render_flyer_mak)


def _synthetic_image(path: Path) -> None:
    from PIL import Image

    img = Image.new("RGB", (64, 64), (10, 200, 30))
    img.save(path)


def test_build_blender_command_uses_cartelera_blend_and_python_expr():
    cmd = render_flyer_mak.build_blender_command(
        Path("/home/mak/blender/blender"),
        Path("/home/mak/RD/AUTOMATIZACION/cartelera.blend"),
        Path("/tmp/input_ig.jpg"),
        Path("/tmp/out/render_output.png"),
    )
    assert cmd[0] == str(Path("/home/mak/blender/blender"))
    assert "-b" in cmd
    assert str(Path("/home/mak/RD/AUTOMATIZACION/cartelera.blend")) in cmd
    assert "--python-expr" in cmd
    expr = cmd[cmd.index("--python-expr") + 1]
    assert isinstance(expr, str) and expr


def test_python_expr_contains_anti_oom_settings():
    expr = render_flyer_mak.build_blender_python_expr(
        Path("/tmp/input_ig.jpg"), Path("/tmp/render_output.png"),
    )
    assert "scene.render.use_simplify = True" in expr
    assert "texture_limit_render = '2048'" in expr
    assert "scene.cycles.use_auto_tile = True" in expr
    assert "scene.cycles.tile_size = 512" in expr
    assert "scene.render.use_persistent_data = False" in expr
    assert "scene.cycles.samples = 512" in expr
    assert "'CUDA'" in expr
    assert "CPU" not in expr.split("compute_device_type")[0]  # no fallback silencioso a CPU antes de forzar GPU


def test_python_expr_contains_flyer_final_material_search_and_no_material_guard():
    expr = render_flyer_mak.build_blender_python_expr(
        Path("/tmp/input_ig.jpg"), Path("/tmp/render_output.png"),
    )
    assert "flyer_final" in expr
    assert "TEX_IMAGE" in expr
    assert "NO_MATERIAL_FLYER_FINAL" in expr  # falla claro si no encuentra el material, no silencioso
    # las rutas se embeben via repr() (fuente Python valida, backslashes escapados en Windows)
    assert repr(str(Path("/tmp/input_ig.jpg"))) in expr
    assert repr(str(Path("/tmp/render_output.png"))) in expr


def test_extract_palette_returns_hex_colors(tmp_path):
    imagen = tmp_path / "input_ig.jpg"
    _synthetic_image(imagen)
    palette_png = tmp_path / "palette_ig.png"
    palette_json = tmp_path / "palette_ig.json"

    colores = render_flyer_mak.extract_palette(imagen, palette_png, palette_json)

    assert colores, "debe devolver al menos un color"
    assert all(c.startswith("#") and len(c) == 7 for c in colores)
    assert palette_png.exists()
    assert palette_json.exists()
    import json
    data = json.loads(palette_json.read_text(encoding="utf-8"))
    assert data["colors"] == colores


def test_parse_render_marker_ok():
    texto = "algo de log\notra linea\nRENDER_OK: /tmp/out/render_output.png\n"
    resultado = render_flyer_mak.parse_render_marker(texto)
    assert resultado == (True, "/tmp/out/render_output.png")


def test_parse_render_marker_fallo():
    texto = "GPU: {...}\nRENDER_FALLO: no encontre el material flyer_final\n"
    resultado = render_flyer_mak.parse_render_marker(texto)
    assert resultado == (False, "no encontre el material flyer_final")


def test_parse_render_marker_none_when_missing():
    assert render_flyer_mak.parse_render_marker("sin marcador aca\n") is None


def test_run_render_fails_clear_when_blend_missing(tmp_path):
    ok, motivo = render_flyer_mak.run_render(
        Path("/usr/bin/true"), tmp_path, tmp_path / "no_existe.jpg", tmp_path / "out.png",
    )
    assert ok is False
    assert "cartelera.blend" in motivo


def test_run_render_ok_when_blender_succeeds_and_writes_output(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / render_flyer_mak.BLEND_FILE).write_text("fake blend", encoding="utf-8")
    imagen = tmp_path / "input_ig.jpg"
    imagen.write_bytes(b"fake")
    output = tmp_path / "out" / "render_output.png"

    def fake_run(cmd, capture_output, text, timeout):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"fake png")
        return subprocess.CompletedProcess(cmd, 0, stdout="GPU: ok", stderr="")

    monkeypatch.setattr(render_flyer_mak.subprocess, "run", fake_run)

    ok, detalle = render_flyer_mak.run_render(
        Path("/home/mak/blender/blender"), base, imagen, output,
    )
    assert ok is True
    assert detalle == str(output)


def test_run_render_fallo_when_blender_exits_nonzero(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / render_flyer_mak.BLEND_FILE).write_text("fake blend", encoding="utf-8")
    imagen = tmp_path / "input_ig.jpg"
    imagen.write_bytes(b"fake")
    output = tmp_path / "out" / "render_output.png"

    def fake_run(cmd, capture_output, text, timeout):
        return subprocess.CompletedProcess(
            cmd, 1, stdout="", stderr="Error: CUDA out of memory\n",
        )

    monkeypatch.setattr(render_flyer_mak.subprocess, "run", fake_run)

    ok, detalle = render_flyer_mak.run_render(
        Path("/home/mak/blender/blender"), base, imagen, output,
    )
    assert ok is False
    assert "CUDA out of memory" in detalle


def test_run_render_fallo_when_output_missing_despite_success_exit(tmp_path, monkeypatch):
    base = tmp_path / "base"
    base.mkdir()
    (base / render_flyer_mak.BLEND_FILE).write_text("fake blend", encoding="utf-8")
    imagen = tmp_path / "input_ig.jpg"
    imagen.write_bytes(b"fake")
    output = tmp_path / "out" / "render_output.png"

    def fake_run(cmd, capture_output, text, timeout):
        return subprocess.CompletedProcess(cmd, 0, stdout="GPU: ok", stderr="")

    monkeypatch.setattr(render_flyer_mak.subprocess, "run", fake_run)

    ok, detalle = render_flyer_mak.run_render(
        Path("/home/mak/blender/blender"), base, imagen, output,
    )
    assert ok is False
    assert "no genero el archivo" in detalle


def test_main_prints_render_ok_and_exits_0(tmp_path, monkeypatch, capsys):
    base = tmp_path / "base"
    base.mkdir()
    (base / render_flyer_mak.BLEND_FILE).write_text("fake blend", encoding="utf-8")
    imagen = tmp_path / "input_ig.jpg"
    _synthetic_image(imagen)
    out_dir = tmp_path / "out"

    def fake_run_render(blender_exe, base_dir, imagen_path, output_path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake png")
        return True, str(output_path)

    monkeypatch.setattr(render_flyer_mak, "run_render", fake_run_render)

    code = render_flyer_mak.main([
        "--imagen", str(imagen), "--out", str(out_dir), "--base", str(base),
        "--blender", "/home/mak/blender/blender",
    ])
    captured = capsys.readouterr()
    assert code == 0
    assert "RENDER_OK:" in captured.out


def test_main_prints_render_fallo_and_exits_1_when_image_missing(tmp_path, capsys):
    code = render_flyer_mak.main([
        "--imagen", str(tmp_path / "no_existe.jpg"), "--out", str(tmp_path / "out"),
    ])
    captured = capsys.readouterr()
    assert code == 1
    assert "RENDER_FALLO:" in captured.out


def test_main_prints_render_fallo_when_render_step_fails(tmp_path, monkeypatch, capsys):
    imagen = tmp_path / "input_ig.jpg"
    _synthetic_image(imagen)
    out_dir = tmp_path / "out"

    def fake_run_render(blender_exe, base_dir, imagen_path, output_path):
        return False, "no existe /home/mak/RD/AUTOMATIZACION/cartelera.blend"

    monkeypatch.setattr(render_flyer_mak, "run_render", fake_run_render)

    code = render_flyer_mak.main(["--imagen", str(imagen), "--out", str(out_dir)])
    captured = capsys.readouterr()
    assert code == 1
    assert "RENDER_FALLO:" in captured.out
    assert "cartelera.blend" in captured.out
