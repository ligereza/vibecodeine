from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluator import evaluate_fixture, evaluate_portfolio, evaluate_ranked, select_portfolio  # noqa: E402
from fixtures import build_fixture  # noqa: E402


class C08EvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = build_fixture()
        cls.report = evaluate_fixture(cls.fixture)

    def test_adversarial_frame_fixture_is_large(self) -> None:
        frames = [item for item in self.fixture["items"] if item["case_id"] == "frames_one_work"]
        self.assertEqual(len(frames), 2048)
        self.assertEqual({item["work_id"] for item in frames}, {"work-lumen"})

    def test_unknown_baseline_is_zero_and_candidate_is_measurable(self) -> None:
        relations = self.report["sections"]["relations"]
        self.assertEqual(relations["baseline"]["recall"], 0.0)
        self.assertGreater(relations["candidate"]["precision_at_1"], 0.0)
        self.assertGreater(relations["candidate"]["recall"], 0.0)

    def test_phase_series_and_portfolio(self) -> None:
        self.assertGreater(self.report["sections"]["phases"]["candidate"]["recall"], 0.0)
        self.assertGreater(self.report["sections"]["series"]["candidate"]["precision_at_1"], 0.0)
        portfolio = self.report["sections"]["portfolio"]
        self.assertEqual(portfolio["baseline"]["coverage"]["score"], 0.0)
        self.assertEqual(portfolio["candidate"]["coverage"]["score"], 1.0)
        self.assertLessEqual(portfolio["candidate"]["redundancy"]["rate"], 0.25)
        self.assertEqual(portfolio["selection_method"], "greedy_phase_coverage")

    def test_planner_is_derived_and_avoids_frame_flood(self) -> None:
        selected = select_portfolio(self.fixture["portfolio"]["intent"], self.fixture["items"])
        self.assertTrue(selected)
        self.assertLessEqual(sum(item.startswith("frame-lumen-") for item in selected), 1)

    def test_report_is_json_serializable_and_per_case(self) -> None:
        encoded = json.dumps(self.report, sort_keys=True)
        self.assertIn("frames_one_work", encoded)
        self.assertEqual(set(self.report["sections"]["relations"]["candidate"]["by_case"]), {case["id"] for case in self.fixture["cases"]})

    def test_empty_portfolio_is_safe(self) -> None:
        result = evaluate_portfolio(self.fixture["portfolio"]["intent"], [], self.fixture["items"], self.fixture["phases"]["gold"])
        self.assertEqual(result["selected_count"], 0)
        self.assertEqual(result["redundancy"]["rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
