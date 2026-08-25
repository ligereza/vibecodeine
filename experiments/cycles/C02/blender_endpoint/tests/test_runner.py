from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ENDPOINT = Path(__file__).resolve().parents[1]
if str(ENDPOINT) not in sys.path:
    sys.path.insert(0, str(ENDPOINT))
import run_c02_blender_endpoint as runner  # noqa: E402


class RunnerTests(unittest.TestCase):
    def test_sanitise_removes_absolute_locators_but_keeps_observed_dependency_flags(self):
        source = {
            "provenance": {"source_path": "/private/source/RAYU.blend"},
            "native": {"dependencies": [{
                "absolute_path": "/private/texture.jpg",
                "path": "//textures/texture.jpg",
                "exists": False,
                "packed": True,
            }]},
        }
        result = runner._sanitise_native_snapshot(source)
        self.assertNotIn("source_path", result["provenance"])
        self.assertNotIn("absolute_path", result["native"]["dependencies"][0])
        self.assertEqual(result["native"]["dependencies"][0]["packed"], True)
        self.assertEqual(result["native"]["dependencies"][0]["exists"], False)
        self.assertEqual(source["provenance"]["source_path"], "/private/source/RAYU.blend")

    def test_report_separates_observed_candidate_and_unknown_without_mp4_claim(self):
        evidence = {
            "status": "observed",
            "source": {"path": str(runner.SOURCE)},
            "integrity": {
                "sha256_before": runner.EXPECTED_SHA256,
                "sha256_after": runner.EXPECTED_SHA256,
                "unchanged": True,
            },
            "extractor": {"blender_version": "Blender 4.5.4 LTS"},
            "probe": {"exit_code": 0, "wrapper_command": "probe"},
            "observation": {"native": {
                "dirty": True,
                "scenes": [{
                    "name": "Scene", "frame_start": 1, "frame_end": 2,
                    "frame_current": 1, "collections": [], "view_layers": [],
                    "camera": {"name": "Camera", "present": True, "type": "CAMERA"},
                    "render": {"engine": "CYCLES", "resolution_x": 1,
                               "resolution_y": 1, "resolution_percentage": 100,
                               "file_format": "PNG", "film_transparent": False,
                               "filepath": "C:/renders/"},
                    "objects": [],
                }],
                "dependencies": [],
            }},
        }
        report = runner.render_report(evidence)
        self.assertIn("## Hechos observados", report)
        self.assertIn("## Candidatos (no confirmados)", report)
        self.assertIn("## Unknown", report)
        self.assertIn("No se puede determinar desde este snapshot si existe un MP4", report)
        self.assertNotIn("MP4 generado por este `.blend`", report)

    def test_digest_mismatch_fails_closed_without_calling_probe(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "RAYU.blend"
            source.write_bytes(b"not-the-frozen-source")
            with patch.object(runner, "SOURCE", source), patch.object(
                runner, "sha256", return_value="different"
            ) as digest, patch.object(runner.subprocess, "run") as probe:
                result = runner.observe()
        self.assertEqual(result["status"], "blocked_source_digest_mismatch")
        probe.assert_not_called()
        self.assertEqual(digest.call_count, 2)

    def test_outputs_are_json_and_report_are_written_inside_endpoint(self):
        evidence = {
            "status": "blocked_blender_unavailable",
            "source": {"path": str(runner.SOURCE)},
            "integrity": {"sha256_before": runner.EXPECTED_SHA256},
            "extractor": {}, "probe": {"exit_code": None}, "observation": None,
        }
        with tempfile.TemporaryDirectory(dir=ENDPOINT) as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot.json"
            report = root / "REPORT.md"
            runner.write_outputs(evidence, snapshot, report)
            payload = json.loads(snapshot.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "blocked_blender_unavailable")
            self.assertNotIn("path", payload["source"])
            self.assertIn("Unknown", report.read_text(encoding="utf-8"))

    def test_sanitised_command_removes_absolute_host_locators(self):
        command = "/home/mak/blender/blender /home/mak/flujo/tools/blender_scene_probe.py /home/mak/curatoria_inbox/ARICA/RAYU.blend"
        sanitised = runner._sanitised_command(command)
        self.assertEqual(sanitised, "blender tools/blender_scene_probe.py ARICA/RAYU.blend")

    def test_sanitised_command_removes_temporary_endpoint_path(self):
        command = f"python3 --output {runner.ENDPOINT_DIR}/tmpabcd.json"
        self.assertNotIn("/home/mak/", runner._sanitised_command(command))


if __name__ == "__main__":
    unittest.main()
