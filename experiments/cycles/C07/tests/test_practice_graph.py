from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fixtures.build_fixtures import create_case
from practice_graph import PENDING, UNRESOLVED, build_graph, inspect_artifact


class PracticeGraphTests(unittest.TestCase):
    def test_artifact_extracts_required_media_fields_and_xmp(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = create_case("frames_plus_export", temp)
            image = inspect_artifact(paths[0], root=temp)
            xmp_path = next(path for path in paths if path.suffix == ".xmp")
            xmp = inspect_artifact(xmp_path, root=temp)
            self.assertEqual(image.extension, "png")
            self.assertEqual(image.bytes > 0, True)
            self.assertEqual(image.dimensions, {"width": 80, "height": 40})
            self.assertEqual(image.aspect_ratio, 2.0)
            self.assertIsNotNone(image.sha256)
            self.assertEqual(image.sequence_family, "aurora")
            self.assertEqual(image.sequence_index, 1)
            self.assertTrue(xmp.xml_xmp["readable"])

    def test_frames_plus_export_emits_explainable_component_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            graph = build_graph(create_case("frames_plus_export", temp), root=temp)
            candidates = graph["relation_candidates"]
            components = [item for item in candidates if item["relation"] == "component_of"]
            self.assertTrue(components)
            self.assertTrue(all(item["score_breakdown"]["signals"] for item in components))
            self.assertTrue(all(item["evidence_refs"] and item["next_probe"] for item in components))
            self.assertFalse(any("export.xmp" in (item["target_id"] or "") for item in components))
            self.assertFalse(any("frame_0002" in (item["target_id"] or "") for item in components))
            published = [item for item in candidates if item["relation"] == "published_as"]
            self.assertTrue(published)
            self.assertTrue(all(item["status"] != "supported" for item in published))

    def test_missing_counterparts_are_actionable_not_terminal_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            export_graph = build_graph(create_case("export_without_project", temp), root=temp)
            project_graph = build_graph(create_case("project_without_export", temp), root=temp)
            self.assertTrue(any(item["target_id"] is None and item["status"] in {PENDING, UNRESOLVED} for item in export_graph["relation_candidates"]))
            self.assertTrue(any(item["target_id"] is None and item["status"] in {PENDING, UNRESOLVED} for item in project_graph["relation_candidates"]))
            for graph in (export_graph, project_graph):
                for item in graph["relation_candidates"]:
                    self.assertNotEqual(item["status"], "unknown")
                    self.assertTrue(item["missing_evidence"])

    def test_adversarial_same_name_is_not_supported_and_ratio_is_pending(self):
        with tempfile.TemporaryDirectory() as temp:
            different = build_graph(create_case("same_name_different_work", temp), root=temp)
            same_work = build_graph(create_case("same_work_different_proportions", temp), root=temp)
            same_name = [item for item in different["relation_candidates"] if item["relation"] == "manifestation_of"]
            ratio = [item for item in same_work["relation_candidates"] if item["relation"] == "manifestation_of"]
            self.assertTrue(same_name)
            self.assertNotEqual(same_name[0]["status"], "supported")
            self.assertTrue(any(item["status"] == PENDING for item in ratio))
            self.assertTrue(any(signal["name"] == "different_aspect_ratio" for signal in ratio[0]["score_breakdown"]["signals"]))

    def test_graph_is_json_serializable_and_candidate_contract_is_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            graph = build_graph(create_case("frames_plus_export", temp), root=temp)
            json.dumps(graph)
            required = {"score", "score_breakdown", "evidence_refs", "alternatives", "missing_evidence", "next_probe"}
            for candidate in graph["relation_candidates"]:
                self.assertTrue(required.issubset(candidate))


if __name__ == "__main__":
    unittest.main()
