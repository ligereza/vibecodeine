from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from public_normalizer import (
    NormalizationError,
    catalog_unavailable,
    normalize_file,
    normalize_payload,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
RUNNER = ROOT / "run_normalizer.py"


def _all_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from _all_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _all_keys(nested)


class PublicNormalizerTests(unittest.TestCase):
    def test_canonical_preserves_declared_observations_and_types(self):
        result = normalize_file(FIXTURES / "canonical_declared.json")

        self.assertEqual(result["archive_id"], "fixture-c03-canonical-001")
        self.assertEqual([item["type"] for item in result["records"]], ["post", "reel", "story"])
        self.assertEqual(result["posts"][0]["media"][0]["origin"]["ref"], "fixture-media-post-001")
        self.assertEqual(result["posts"][0]["media"][0]["hashes"]["sha256"], "b" * 64)
        self.assertEqual(result["reels"][0]["completeness"]["status"], "partial")
        self.assertEqual(result["completeness"]["status"], "complete")

    def test_declared_json_wrapper_adds_only_declared_array_type(self):
        result = normalize_file(FIXTURES / "declared_json_export.json")

        self.assertEqual(result["input_form"], "declared_json")
        self.assertEqual(result["posts"][0]["type"], "post")
        self.assertEqual(result["posts"][0]["published_at"], "declared-only")
        self.assertEqual(result["posts"][0]["media"][0]["evidence_refs"], ["fixture-evidence-media-001"])

    def test_html_json_incomplete_wrapper_is_interpretable(self):
        result = normalize_file(FIXTURES / "html_json_incomplete.html")

        self.assertEqual(result["source_format"], "html")
        self.assertEqual(result["catalog_status"], "unknown")
        self.assertEqual(result["completeness"]["status"], "partial")
        self.assertEqual(result["reels"][0]["media"][0]["origin"], "fixture-html-media-origin")

    def test_normalizer_does_not_emit_provenance_decisions_or_edges(self):
        payload = {
            "schema": "c03.public_input.canonical.v1",
            "archive_id": "explicit-001",
            "records": [
                {
                    "type": "post",
                    "id": "post-001",
                    "generated": "do-not-copy",
                    "RENDERS_TO": ["artifact-001"],
                    "media": [],
                }
            ],
        }

        result = normalize_payload(payload)
        keys = set(_all_keys(result))
        self.assertNotIn("generated", keys)
        self.assertNotIn("RENDERS_TO", keys)
        self.assertNotIn("author", keys)
        self.assertNotIn("relations", keys)
        self.assertNotIn("provenance_decision", keys)
        self.assertEqual(result["records"][0]["id"], "post-001")

    def test_catalog_unavailable_is_explicit_status_not_fixture_data(self):
        result = catalog_unavailable("archive-arica-001")

        self.assertEqual(result["catalog_status"], "unavailable")
        self.assertEqual(result["completeness"]["reason"], "no_real_public_export_local")
        self.assertEqual(result["records"], [])
        self.assertEqual(result["input_form"], "catalog_status")

    def test_fail_closed_for_required_invalid_inputs(self):
        invalid_files = (
            "invalid_missing_archive_id.json",
            "invalid_unknown_type.json",
            "invalid_media_without_origin.json",
            "invalid_uninterpretable.html",
        )
        for filename in invalid_files:
            with self.subTest(filename=filename):
                with self.assertRaises(NormalizationError):
                    normalize_file(FIXTURES / filename)

    def test_cli_success_and_closed_failure_exit_codes(self):
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        success = subprocess.run(
            [sys.executable, "-B", str(RUNNER), str(FIXTURES / "declared_json_export.json"), "--compact"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(json.loads(success.stdout)["archive_id"], "fixture-c03-json-001")

        unavailable = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--catalog-unavailable", "--archive-id", "archive-arica-001"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(unavailable.returncode, 0, unavailable.stderr)
        self.assertEqual(json.loads(unavailable.stdout)["catalog_status"], "unavailable")

        failure = subprocess.run(
            [sys.executable, "-B", str(RUNNER), str(FIXTURES / "invalid_media_without_origin.json")],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(failure.returncode, 2)
        self.assertIn("origin", failure.stderr)


if __name__ == "__main__":
    unittest.main()
