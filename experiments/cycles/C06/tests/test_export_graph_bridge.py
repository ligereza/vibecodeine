from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from export_graph_bridge import materialize


def valid_witness() -> dict:
    checks = {
        name: {"status": "pass", "reason": "fixture"}
        for name in (
            "source_hash_matches_native_snapshot",
            "script_and_marker_agree",
            "marker_target_matches_output",
            "source_contains_exported_objects",
            "output_contains_exported_objects",
            "output_is_blender_glb",
            "output_after_script_and_marker",
        )
    }
    return {
        "schema": "mak-cycle-c05-export-witness-v1",
        "witness": {
            "status": "supported",
            "event_type": "export",
            "source_ref": "authoring:blend:ARICA/RAYU.blend",
            "target_ref": "artifact:glb:rayu_resources.glb",
            "evidence_refs": ["C05/marker/sha256=marker", "C05/output/sha256=output"],
            "checks": checks,
        },
    }


class ExportGraphBridgeTests(unittest.TestCase):
    def test_complete_witness_materializes_one_export_edge(self):
        graph = materialize(valid_witness())
        self.assertEqual(graph["claim"]["status"], "supported")
        self.assertEqual(len(graph["edges"]), 1)
        self.assertEqual(graph["edges"][0]["relation"], "EXPORTS_TO")

    def test_missing_refs_abstains_and_emits_no_edge(self):
        witness = valid_witness()
        witness["witness"]["evidence_refs"] = []
        graph = materialize(witness)
        self.assertEqual(graph["claim"]["status"], "unknown")
        self.assertEqual(graph["claim"]["reason"], "witness_evidence_refs_missing")
        self.assertEqual(graph["edges"], [])

    def test_failed_check_abstains_and_emits_no_edge(self):
        witness = valid_witness()
        witness["witness"]["checks"]["output_contains_exported_objects"]["status"] = "fail"
        graph = materialize(witness)
        self.assertEqual(graph["claim"]["status"], "unknown")
        self.assertIn("output_contains_exported_objects", graph["claim"]["reason"])
        self.assertEqual(graph["edges"], [])

    def test_unknown_status_abstains_even_with_refs(self):
        witness = valid_witness()
        witness["witness"]["status"] = "unknown"
        graph = materialize(witness)
        self.assertEqual(graph["claim"]["status"], "unknown")
        self.assertEqual(graph["edges"], [])


if __name__ == "__main__":
    unittest.main()
