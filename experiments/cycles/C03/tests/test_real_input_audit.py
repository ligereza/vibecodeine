from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


CYCLE = Path(__file__).resolve().parents[1]
if str(CYCLE) not in sys.path:
    sys.path.insert(0, str(CYCLE))

from real_input_audit import KNOWN_ZIP, audit  # noqa: E402


class RealInputAuditTests(unittest.TestCase):
    def test_known_zip_is_a_catalog_absence_not_a_public_catalog(self):
        payload = audit(KNOWN_ZIP)
        self.assertTrue(payload["input"]["exists"])
        self.assertFalse(payload["input"]["extracted"])
        self.assertEqual(payload["catalog_status"], "unavailable")
        self.assertEqual(payload["public_join"], "unknown")
        self.assertEqual(payload["archive"]["member_count"], 9)
        self.assertEqual(payload["archive"]["media_members_excluding_brand_logo"], [])

    def test_missing_candidate_fails_closed(self):
        payload = audit(CYCLE / "does-not-exist.zip")
        self.assertEqual(payload["catalog_status"], "unavailable")
        self.assertFalse(payload["input"]["exists"])
        self.assertEqual(payload["public_join"], "unknown")


if __name__ == "__main__":
    unittest.main()
