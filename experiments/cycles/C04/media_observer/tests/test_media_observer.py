from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import media_observer


REAL_MEDIA = Path("/home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4")


class MediaObserverTests(unittest.TestCase):
    def test_ffprobe_command_is_metadata_only(self) -> None:
        command = media_observer.build_ffprobe_command(REAL_MEDIA)
        self.assertIn("-show_format", command)
        self.assertIn("-show_streams", command)
        self.assertIn("-show_entries", command)
        self.assertIn("-count_frames", command)
        self.assertEqual(command[-1], str(REAL_MEDIA))
        self.assertNotIn("-y", command)
        self.assertNotIn("-vf", command)
        self.assertNotIn("-c:v", command)

    def test_sanitizer_preserves_unconventional_dimensions_and_drops_metadata(self) -> None:
        raw = {
            "streams": [
                {
                    "index": 0,
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": "256",
                    "height": "1536",
                    "duration": "44.627917",
                    "nb_frames": "1070",
                    "nb_read_frames": "1070",
                    "tags": {"creation_time": "secret"},
                    "disposition": {"default": 1},
                }
            ],
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "format_long_name": "QuickTime / MOV",
                "duration": "44.627917",
                "nb_streams": "1",
                "tags": {"encoder": "secret"},
            },
        }
        result = media_observer.sanitize_ffprobe_payload(raw)
        self.assertEqual(result["dimensions"], {"width": 256, "height": 1536})
        self.assertEqual(result["frames"]["video"], 1070)
        self.assertNotIn("tags", json.dumps(result))
        self.assertNotIn("disposition", json.dumps(result))

    def test_real_observation_has_expected_technical_facts(self) -> None:
        result = media_observer.observe_media(REAL_MEDIA)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["artifact"]["sha256"], media_observer.EXPECTED_SHA256)
        self.assertEqual(result["artifact"]["bytes"], 12092541)
        self.assertEqual(result["media"]["container"]["format"], "mov,mp4,m4a,3gp,3g2,mj2")
        self.assertEqual(result["media"]["dimensions"], {"width": 256, "height": 1536})
        self.assertEqual(result["media"]["frames"]["video"], 1070)
        self.assertEqual(result["media"]["streams"][0]["codec"], "h264")
        self.assertEqual(result["media"]["streams"][1]["codec"], "aac")
        self.assertEqual(result["probe"]["exit_code"], 0)
        self.assertTrue(result["integrity"]["unchanged_during_probe"])

    def test_json_has_no_forbidden_relation_or_role_terms(self) -> None:
        result = media_observer.observe_media(REAL_MEDIA)
        serialized = json.dumps(result, sort_keys=True).lower()
        for forbidden in ("generated", "renders_to", "output"):
            self.assertNotIn(forbidden, serialized)

    def test_missing_ffprobe_is_an_explicit_block(self) -> None:
        result = media_observer.observe_media(REAL_MEDIA, ffprobe_bin="definitely-missing-ffprobe")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["block_reason"], "ffprobe_unavailable_or_timed_out")
        self.assertIsNone(result["probe"]["exit_code"])
        self.assertTrue(result["integrity"]["after_matches"])

    def test_nonzero_ffprobe_is_an_explicit_block_and_hash_is_rechecked(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["fake"], returncode=9, stdout="", stderr="probe failed"
        )
        with patch("media_observer.subprocess.run", return_value=completed):
            result = media_observer.observe_media(REAL_MEDIA)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["block_reason"], "ffprobe_failed")
        self.assertEqual(result["probe"]["exit_code"], 9)
        self.assertTrue(result["integrity"]["before_matches"])
        self.assertTrue(result["integrity"]["after_matches"])


if __name__ == "__main__":
    unittest.main()
