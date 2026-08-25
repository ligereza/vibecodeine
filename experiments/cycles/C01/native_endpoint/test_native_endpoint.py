from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from native_endpoint import (
    EDGE_RELATIONS,
    EDGE_STATUSES,
    SCHEMA,
    compare_models,
    direct_authoring_deliverable_join,
    extract_graph,
    load_cases,
)


ROOT = Path(__file__).parent
CASES = load_cases(ROOT / "fixtures" / "cases.json")
BY_ID = {case["case_id"]: case for case in CASES}


class NativeEndpointTests(unittest.TestCase):
    def test_all_edges_match_shared_contract(self) -> None:
        for case in CASES:
            result = compare_models(case)
            self.assertEqual(result["archive_id"], "artist-001")
            for edge in result["edges"] + result["direct_join"]["edges"]:
                self.assertEqual(edge["schema"], SCHEMA)
                self.assertIn(edge["relation"], EDGE_RELATIONS)
                self.assertIn(edge["status"], EDGE_STATUSES)
                if edge["status"] != "unknown":
                    self.assertTrue(edge["evidence_refs"])
                self.assertIsNone(edge["score"])

    def test_case_6_one_document_generates_multiple_versions(self) -> None:
        result = compare_models(BY_ID["case-6-multiple-versions"])
        deliverables = {node["id"] for node in result["nodes"] if node["kind"] == "deliverable"}
        self.assertEqual(deliverables, {"deliverable-6:v1", "deliverable-6:v2"})
        self.assertEqual(len(result["direct_join"]["edges"]), 2)
        self.assertEqual(
            {link["deliverable_id"] for link in result["mediated_links"]},
            deliverables,
        )
        v2_edges = [edge for edge in result["edges"] if edge["source"]["id"] == "deliverable-6:v2"]
        self.assertEqual([edge["relation"] for edge in v2_edges], ["derived_from", "specializes"])
        self.assertIn("specializes", next(link for link in result["mediated_links"] if link["deliverable_id"] == "deliverable-6:v2")["lineage_relations"])
        self.assertEqual(set(result["activity_states"].values()), {"completed"})

    def test_case_7_shared_source_is_visible_only_in_mediated_context(self) -> None:
        result = compare_models(BY_ID["case-7-shared-source"])
        links = result["mediated_links"]
        self.assertEqual({link["deliverable_id"] for link in links}, {"deliverable-7:a", "deliverable-7:b"})
        self.assertTrue(all("source-7-shared" in link["technical_inputs"] for link in links))
        self.assertEqual(len(result["direct_join"]["edges"]), 2)
        self.assertFalse(any(edge["relation"] == "uses" for edge in result["direct_join"]["edges"]))

    def test_case_8_native_graph_without_identifiable_output_stays_unanchored(self) -> None:
        result = compare_models(BY_ID["case-8-no-identifiable-output"])
        self.assertEqual(result["direct_join"]["edges"], [])
        self.assertEqual(result["mediated_links"], [])
        self.assertIn("unidentified-output-8", result["direct_join"]["unanchored_deliverable_ids"])
        unknown_generated = [
            edge for edge in result["edges"]
            if edge["relation"] == "generated" and edge["target"]["id"] == "unidentified-output-8"
        ]
        self.assertEqual(len(unknown_generated), 1)
        self.assertEqual(unknown_generated[0]["status"], "contradicted")
        self.assertEqual(result["activity_states"]["activity-export-8"], "failed")

    def test_direct_join_does_not_infer_from_filename_or_extension(self) -> None:
        fixture = json.loads(json.dumps(BY_ID["case-6-multiple-versions"]))
        fixture["nodes"].append({
            "kind": "deliverable",
            "id": "deliverable-name-only",
            "filename": "authoring-6.blend",
            "extension": ".blend",
            "identifiable": True,
        })
        graph = extract_graph(fixture)
        direct = direct_authoring_deliverable_join(graph)
        self.assertIn("deliverable-name-only", direct.unanchored_deliverable_ids)
        self.assertNotIn("deliverable-name-only", {edge.target_id for edge in direct.edges})

    def test_fixture_can_run_from_clean_temporary_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c01-native-") as temp_dir:
            copied = Path(temp_dir) / "cases.json"
            shutil.copy2(ROOT / "fixtures" / "cases.json", copied)
            clean_cases = load_cases(copied)
            self.assertEqual([case["case_id"] for case in clean_cases], list(BY_ID))
            self.assertEqual(len(compare_models(clean_cases[0])["edges"]), 15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
