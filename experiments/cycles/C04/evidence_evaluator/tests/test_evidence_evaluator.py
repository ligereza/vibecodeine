from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evidence_evaluator import FORBIDDEN_RELATIONS, InputError, evaluate
from run_evaluator import run


FIXTURES = ROOT / "fixtures" / "adversarial"
EXPECTED = ROOT / "fixtures" / "expected"


def load_fixture(case_id: str) -> dict:
    fixture_path = next(FIXTURES.glob(f"*_{case_id}.json"))
    with fixture_path.open(encoding="utf-8") as handle:
        return json.load(handle)


class C04EvidenceEvaluatorTests(unittest.TestCase):
    def test_adversarial_expected_statuses_are_separate_and_match(self) -> None:
        statuses = set()
        for fixture_path in sorted(FIXTURES.glob("*.json")):
            with fixture_path.open(encoding="utf-8") as handle:
                fixture = json.load(handle)
            self.assertNotIn("expected_status", json.dumps(fixture))
            result = evaluate(fixture)
            expected_path = EXPECTED / f"{fixture['case_id']}.json"
            with expected_path.open(encoding="utf-8") as handle:
                expected = json.load(handle)
            for item in expected["claims"]:
                claim = item["claim"]
                self.assertEqual(result["claims"][claim]["status"], item["expected_status"], fixture_path.name)
                statuses.add(result["claims"][claim]["status"])
            self.assertEqual(
                [relation["relation"] for relation in result["relations"]],
                expected["expected_relations"],
            )
        self.assertEqual(statuses, {"observed", "supported", "candidate", "unknown", "contradicted"})

    def test_declared_exists_supports_uses_but_not_output_role(self) -> None:
        result = evaluate(load_fixture("declared_exists"))
        self.assertEqual(result["claims"]["uses"]["status"], "supported")
        self.assertEqual(result["claims"]["output_role"]["status"], "unknown")
        self.assertEqual(result["relations"], [])

    def test_exists_without_declaration_is_unknown_not_supported(self) -> None:
        result = evaluate(load_fixture("exists_not_declared"))
        self.assertEqual(result["claims"]["local_media"]["status"], "observed")
        self.assertEqual(result["claims"]["uses"]["status"], "unknown")

    def test_ambiguous_basename_is_candidate(self) -> None:
        result = evaluate(load_fixture("ambiguous_basename"))
        self.assertEqual(result["claims"]["uses"]["status"], "candidate")
        self.assertIsNone(result["selected_observation_id"])

    def test_same_technical_id_with_different_hash_is_contradicted(self) -> None:
        result = evaluate(load_fixture("technical_hash_conflict"))
        self.assertEqual(result["claims"]["uses"]["status"], "contradicted")
        self.assertIn("hash", result["claims"]["uses"]["reason"])

    def test_explicit_event_is_required_for_output_relations(self) -> None:
        result = evaluate(load_fixture("explicit_export_event"))
        self.assertEqual(result["claims"]["output_role"]["status"], "supported")
        self.assertEqual(
            {relation["relation"] for relation in result["relations"]},
            FORBIDDEN_RELATIONS,
        )
        for relation in result["relations"]:
            self.assertTrue(relation["evidence_refs"])

    def test_event_without_refs_cannot_promote_output_role(self) -> None:
        fixture = copy.deepcopy(load_fixture("explicit_export_event"))
        fixture["export_event"]["evidence_refs"] = []
        result = evaluate(fixture)
        self.assertEqual(result["claims"]["output_role"]["status"], "unknown")
        self.assertEqual(result["relations"], [])

    def test_nonconventional_dimensions_are_observed_verbatim(self) -> None:
        result = evaluate(load_fixture("nonconventional_dimensions"))
        dimensions = result["claims"]["dimensions"]
        self.assertEqual(dimensions["status"], "observed")
        self.assertEqual(dimensions["details"]["dimensions"], {"width": 256, "height": 1536})
        self.assertEqual(result["claims"]["output_role"]["status"], "unknown")

    def test_malformed_input_fails_closed(self) -> None:
        fixture = load_fixture("declared_exists")
        fixture["native_aep"]["declarations"][0]["evidence_refs"] = "not-a-list"
        with self.assertRaises(InputError):
            evaluate(fixture)

    def test_runner_reports_zero_false_positives_and_abstentions(self) -> None:
        report = run(FIXTURES, EXPECTED)
        self.assertEqual(report["case_count"], 6)
        self.assertEqual(report["false_positives"], 0)
        self.assertEqual(report["abstentions"], 0)
        self.assertEqual(report["positive_claim_count"], 3)


if __name__ == "__main__":
    unittest.main()
