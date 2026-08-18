import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "render_video_sequence_mak.py"
SPEC = importlib.util.spec_from_file_location("render_video_sequence_mak", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_build_command_uses_sequence_script_and_manifest(tmp_path):
    command = module.build_blender_command(
        Path("/home/mak/blender/blender"),
        Path("/home/mak/RD/AUTOMATIZACION/RD.paravideo.blend"),
        tmp_path / "input.mp4",
        tmp_path / "frames",
        tmp_path / "render_manifest.json",
        frame_end=24,
    )
    assert "--python" in command
    assert str(module.BLENDER_SCRIPT) in command
    assert "--out-dir" in command
    assert "--manifest" in command
    assert "--frame-end" in command
    assert "--no-persistent-data" not in command


def test_build_command_can_disable_persistent_data(tmp_path):
    command = module.build_blender_command(
        Path("/home/mak/blender/blender"),
        Path("/home/mak/RD/AUTOMATIZACION/RD.paravideo.blend"),
        tmp_path / "input.mp4",
        tmp_path / "frames",
        tmp_path / "render_manifest.json",
        persistent_data=False,
    )
    assert command[-1] == "--no-persistent-data"


def test_manifest_requires_cycles_128_gpu_and_png_count(tmp_path):
    (tmp_path / "frame_0001.png").write_bytes(b"png")
    manifest = tmp_path / "render_manifest.json"
    manifest.write_text(json.dumps({
        "engine": "CYCLES",
        "samples": 128,
        "gpu": {"device": "GPU"},
        "png_count": 1,
    }), encoding="utf-8")
    assert module._manifest_is_valid(manifest, tmp_path) == (True, str(manifest))


def test_manifest_rejects_cpu_or_wrong_samples(tmp_path):
    (tmp_path / "frame_0001.png").write_bytes(b"png")
    manifest = tmp_path / "render_manifest.json"
    manifest.write_text(json.dumps({
        "engine": "CYCLES",
        "samples": 512,
        "gpu": {"device": "CPU"},
        "png_count": 1,
    }), encoding="utf-8")
    ok, detail = module._manifest_is_valid(manifest, tmp_path)
    assert ok is False
    assert "samples" in detail
