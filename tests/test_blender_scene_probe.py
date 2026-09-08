from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools.blender_scene_probe import (
    MARKER,
    PROBE_EXPRESSION,
    _probe_payload,
    probe_file,
)


def test_expression_only_reads_scene_paths():
    assert "bpy.data.scenes" in PROBE_EXPRESSION
    assert "bpy.ops.render" not in PROBE_EXPRESSION
    assert "bpy.ops.wm.save" not in PROBE_EXPRESSION


def test_probe_extracts_scene_paths_without_writing(tmp_path: Path, monkeypatch):
    blend = tmp_path / "scene.blend"
    blend.write_bytes(b"fixture")
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        payload = {
            "filepath": str(blend),
            "scenes": [{"name": "Scene", "render_filepath": "C:/renders/"}],
        }
        return subprocess.CompletedProcess(
            command, 0, f"{MARKER}{json.dumps(payload)}\n", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    row = probe_file(blend, blender=tmp_path / "blender", timeout=5)

    assert row["status"] == "ok"
    assert row["scenes"][0]["render_filepath"] == "C:/renders/"
    assert "--background" in calls[0]
    assert "--disable-autoexec" in calls[0]


def test_missing_probe_payload_is_a_decoder_limit(tmp_path: Path, monkeypatch):
    blend = tmp_path / "scene.blend"
    blend.write_bytes(b"fixture")

    monkeypatch.setattr(
        subprocess, "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 1, "", "bad"))
    row = probe_file(blend, blender=tmp_path / "blender", timeout=5)

    assert row["status"] == "decoder_limit"
    assert row["returncode"] == 1


def test_payload_parser_rejects_non_scene_shape():
    assert _probe_payload(f"{MARKER}[]") is None


def test_payload_parser_ignores_malformed_marker():
    assert _probe_payload(f"{MARKER}{{not-json}}") is None
