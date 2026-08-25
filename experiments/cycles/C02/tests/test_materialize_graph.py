from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


CYCLE = Path(__file__).resolve().parents[1]
if str(CYCLE) not in sys.path:
    sys.path.insert(0, str(CYCLE))

from materialize_graph import FORBIDDEN_RELATIONS, materialize  # noqa: E402


class MaterializeGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blender = json.loads(
            (CYCLE / "blender_endpoint/snapshot.json").read_text(encoding="utf-8")
        )
        cls.aep = json.loads(
            (CYCLE / "aep_endpoint/observation.json").read_text(encoding="utf-8")
        )
        cls.graph = materialize(cls.blender, cls.aep)

    def test_both_native_documents_share_fixed_archive_root(self):
        self.assertEqual(self.graph["archive_id"], "archive-arica-001")
        authoring = [node for node in self.graph["nodes"] if node["kind"] == "authoring"]
        self.assertEqual({node["format"] for node in authoring}, {"blend", "aep"})
        self.assertTrue(all(node["archive_id"] == self.graph["archive_id"] for node in self.graph["nodes"]))

    def test_aep_reference_becomes_uses_candidate_not_generated(self):
        mp4_edges = [
            edge for edge in self.graph["edges"]
            if any(node.get("locator", "").endswith("tottem_ojo.mp4") for node in self.graph["nodes"]
                   if node["id"] == edge["target"]["id"])
        ]
        self.assertEqual(len(mp4_edges), 1)
        self.assertEqual(mp4_edges[0]["relation"], "uses")
        self.assertEqual(mp4_edges[0]["status"], "candidate")
        self.assertIn("output role unknown", mp4_edges[0]["claim_limit"])

    def test_blender_render_configuration_is_capability_not_output(self):
        capabilities = [item for item in self.graph["capabilities"] if item["capability"] == "render"]
        self.assertEqual(len(capabilities), 1)
        self.assertEqual(capabilities[0]["status"], "observed")
        self.assertIn("configured capability", capabilities[0]["claim_limit"])
        self.assertEqual(capabilities[0]["settings"]["engine"], "CYCLES")

    def test_public_join_is_explicit_unknown(self):
        public = [item for item in self.graph["unknowns"] if item["type"] == "public_join"]
        self.assertEqual(len(public), 1)
        self.assertEqual(public[0]["status"], "unknown")
        self.assertEqual(self.graph["safety"]["public_catalog_available"], False)

    def test_every_aep_output_role_remains_unknown(self):
        self.assertEqual(len(self.graph["output_role_unknowns"]), 5)
        self.assertTrue(all(item["reason"] for item in self.graph["output_role_unknowns"]))

    def test_forbidden_provenance_relations_cannot_enter_graph(self):
        self.assertTrue(self.graph["safety"]["forbidden_relations_absent"])
        self.assertFalse(any(edge["relation"] in FORBIDDEN_RELATIONS for edge in self.graph["edges"]))
        self.assertFalse(self.graph["safety"]["learning_or_inference_performed"])


if __name__ == "__main__":
    unittest.main()
