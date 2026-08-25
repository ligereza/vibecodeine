from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aep_endpoint import build_observation, resolve_declared_path


class AepEndpointAdversarialTests(unittest.TestCase):
    def test_nonexistent_reference_is_unknown_with_missing_evidence(self) -> None:
        result = resolve_declared_path(
            {"declared_path": r"C:\ARICA\missing.mov", "target_is_folder": False},
            "/tmp/aep-endpoint-no-such-root",
        )
        self.assertEqual(result["local_resolution"]["status"], "unknown")
        self.assertEqual(result["local_resolution"]["cause"], "MISSING_EVIDENCE")
        self.assertEqual(result["local_resolution"]["candidate_count"], 0)

    def test_ambiguous_basename_is_registered_and_not_unique(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = root / "one" / "same.png"
            second = root / "two" / "same.png"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_bytes(b"one")
            second.write_bytes(b"two")
            result = resolve_declared_path(
                {"declared_path": r"C:\ARICA\same.png", "target_is_folder": False},
                root,
                explicit_candidates=[first, second],
            )
        self.assertEqual(result["local_resolution"]["status"], "ambiguous")
        self.assertEqual(result["local_resolution"]["candidate_count"], 2)
        self.assertEqual(
            result["local_resolution"]["evidence"]["probes"][0]["basename"],
            "same.png",
        )

    def test_existing_reference_does_not_prove_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "BANNER.png"
            source.write_bytes(b"declared source")
            result = resolve_declared_path(
                {"declared_path": r"C:\ARICA\BANNER.png", "target_is_folder": False},
                root,
            )
        self.assertEqual(result["local_resolution"]["status"], "candidate")
        self.assertTrue(result["local_resolution"]["evidence"]["probes"][0]["exists"])
        self.assertEqual(result["output_claim"]["status"], "unknown")

    def test_declared_folder_is_observed_but_not_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "ARICA"
            root.mkdir()
            result = resolve_declared_path(
                {"declared_path": r"C:\ARICA", "target_is_folder": True},
                root,
            )
        self.assertEqual(result["declared_target_is_folder"], True)
        self.assertEqual(result["local_resolution"]["local_kind"], "folder")
        self.assertEqual(result["output_claim"]["status"], "unknown")

    def test_absent_public_bridge_returns_unknown(self) -> None:
        fake_reader = type(
            "FakeReaderResult",
            (),
            {
                "declared": [],
                "completeness": "exhaustive",
                "error": "",
                "truncated": False,
                "chunks_seen": 0,
                "header": None,
            },
        )()
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "ARICA.aep"
            input_path.write_bytes(b"test input")
            with patch("aep_endpoint._load_flujo_api", return_value=lambda _: fake_reader):
                result = build_observation(input_path, Path(temp))
        self.assertEqual(result["public_catalog"]["status"], "unavailable")
        self.assertEqual(result["public_catalog"]["join"]["status"], "unknown")
        self.assertFalse(result["public_catalog"]["join"]["verifiable"])

    def test_payload_has_no_forbidden_output_relation(self) -> None:
        fake_reader = type(
            "FakeReaderResult",
            (),
            {
                "declared": [],
                "completeness": "exhaustive",
                "error": "",
                "truncated": False,
                "chunks_seen": 0,
                "header": None,
            },
        )()
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "ARICA.aep"
            input_path.write_bytes(b"test input")
            with patch("aep_endpoint._load_flujo_api", return_value=lambda _: fake_reader):
                payload = json.dumps(build_observation(input_path, temp), sort_keys=True)
        self.assertNotIn("RENDERS_TO", payload)
        self.assertNotIn('"generated"', payload)


if __name__ == "__main__":
    unittest.main()
