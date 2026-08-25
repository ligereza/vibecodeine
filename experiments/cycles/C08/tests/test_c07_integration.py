from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from c07_integration import C07_GRAPH, evaluate_c07_graph  # noqa: E402


class C07IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = evaluate_c07_graph(C07_GRAPH)

    def test_candidate_and_baseline_use_the_same_five_cases(self) -> None:
        self.assertEqual(
            self.report["same_cases"],
            [
                "export_without_project",
                "frames_plus_export",
                "project_without_export",
                "same_name_different_work",
                "same_work_different_proportions",
            ],
        )
        self.assertEqual(self.report["baseline"]["recall"], 0.0)

    def test_graph_improves_recall_without_promoting_edges(self) -> None:
        self.assertGreater(self.report["candidate"]["recall"], self.report["baseline"]["recall"])
        self.assertEqual(self.report["status_counts"].get("supported", 0), 0)
        self.assertGreater(self.report["status_counts"].get("pending_relation", 0), 0)

    def test_missing_counterparts_remain_actionable(self) -> None:
        self.assertGreater(self.report["pending_or_unresolved_by_case"]["export_without_project"], 0)
        self.assertGreater(self.report["pending_or_unresolved_by_case"]["project_without_export"], 0)


if __name__ == "__main__":
    unittest.main()
