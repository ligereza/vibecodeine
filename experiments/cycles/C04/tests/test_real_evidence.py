from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RealEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / "real_evidence.json").read_text(encoding="utf-8"))

    def test_real_aep_and_media_hashes_are_preserved(self):
        self.assertEqual(
            self.payload["source_documents"]["aep_sha256"],
            "99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460",
        )
        self.assertEqual(
            self.payload["artifact"]["sha256"],
            "b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776",
        )

    def test_nonconventional_dimensions_are_not_normalized(self):
        self.assertEqual(self.payload["artifact"]["dimensions"], {"width": 256, "height": 1536})
        self.assertEqual(self.payload["evaluation"]["claims"]["dimensions"]["status"], "observed")

    def test_native_reference_is_supported_but_output_role_unknown(self):
        claims = self.payload["evaluation"]["claims"]
        self.assertEqual(claims["uses"]["status"], "supported")
        self.assertEqual(claims["output_role"]["status"], "unknown")
        self.assertFalse(self.payload["limits"]["export_event_observed"])

    def test_no_export_relations_are_materialized_without_event(self):
        self.assertEqual(self.payload["evaluation"]["relations"], [])
        self.assertEqual(self.payload["limits"]["generated_or_renders_to_relations"], [])
        self.assertIn("does not prove export causality", self.payload["limits"]["claim_limit"])


if __name__ == "__main__":
    unittest.main()
