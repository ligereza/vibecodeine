from __future__ import annotations

import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path

from bridge import (
    OBSERVATION_SCHEMA,
    ObservationError,
    load_observations,
    normalize_observations,
    recover,
    recover_direct,
    recover_mediated,
)
from evaluator import evaluate, load_truth


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class BlindBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.observations = load_observations(FIXTURES / "observations.json")
        cls.truth = load_truth(FIXTURES / "truth.json")

    def test_recovery_api_has_one_observation_argument(self) -> None:
        self.assertEqual(list(inspect.signature(recover).parameters), ["observations"])
        self.assertEqual(list(inspect.signature(recover_direct).parameters), ["observations"])
        self.assertEqual(list(inspect.signature(recover_mediated).parameters), ["observations"])

    def test_normalizer_rejects_evaluation_fields(self) -> None:
        payload = json.loads((FIXTURES / "observations.json").read_text(encoding="utf-8"))
        payload["truth"] = {"pub-exact": "local-exact"}
        with self.assertRaises(ObservationError):
            normalize_observations(payload)

    def test_exact_hash_is_confirmed_by_both_strategies(self) -> None:
        direct = recover_direct(self.observations)
        mediated = recover_mediated(self.observations)
        for result in (direct, mediated):
            item = next(row for row in result["results"] if row["query_id"] == "pub-exact")
            self.assertEqual(item["status"], "confirmed")
            self.assertEqual(item["local_id"], "local-exact")
            self.assertTrue(item["evidence_refs"])

    def test_reencode_is_technical_baseline_candidate_and_mediated_confirmation(self) -> None:
        direct = recover_direct(self.observations)
        mediated = recover_mediated(self.observations)
        direct_item = next(row for row in direct["results"] if row["query_id"] == "pub-reencode")
        mediated_item = next(row for row in mediated["results"] if row["query_id"] == "pub-reencode")
        self.assertEqual((direct_item["status"], direct_item["local_id"]), ("candidate", "local-reencode"))
        self.assertEqual((mediated_item["status"], mediated_item["local_id"]), ("confirmed", "local-reencode"))
        self.assertEqual(mediated_item["method"], "mediated_native_observation")

    def test_same_dimensions_decoy_is_false_direct_candidate_but_mediated_is_anchored(self) -> None:
        direct = recover_direct(self.observations)
        mediated = recover_mediated(self.observations)
        direct_item = next(row for row in direct["results"] if row["query_id"] == "pub-decoy")
        mediated_item = next(row for row in mediated["results"] if row["query_id"] == "pub-decoy")
        self.assertEqual(direct_item["status"], "candidate")
        self.assertEqual(direct_item["local_id"], "local-decoy-a")
        self.assertEqual(set(direct_item["candidate_local_ids"]), {"local-decoy-a", "local-decoy-z"})
        self.assertEqual((mediated_item["status"], mediated_item["local_id"]), ("confirmed", "local-decoy-z"))

    def test_missing_public_local_ambiguity_and_explicit_conflict_are_preserved(self) -> None:
        direct = recover_direct(self.observations)
        mediated = recover_mediated(self.observations)
        direct_by_id = {row["query_id"]: row for row in direct["results"]}
        mediated_by_id = {row["query_id"]: row for row in mediated["results"]}
        self.assertEqual(direct_by_id["pub-no-local"]["status"], "unknown")
        self.assertEqual(direct_by_id["pub-ambiguous"]["status"], "ambiguous")
        self.assertEqual(direct_by_id["pub-conflict"]["status"], "confirmed")
        self.assertEqual(mediated_by_id["pub-conflict"]["status"], "contradicted")
        self.assertEqual(mediated_by_id["pub-conflict"]["method"], "explicit_native_conflict")
        self.assertIn("local-only", direct["orphan_local_ids"])
        self.assertIn("local-only", mediated["orphan_local_ids"])

    def test_evaluation_is_separate_and_reports_tp_fp_abstentions_and_coverage(self) -> None:
        direct = evaluate(recover_direct(self.observations), self.truth)
        mediated = evaluate(recover_mediated(self.observations), self.truth)
        self.assertEqual(direct["metrics"], {
            "abstentions": 2,
            "contradicted": 0,
            "coverage": 2 / 3,
            "decision_coverage": 4 / 6,
            "fp": 2,
            "linkable_cases": 3,
            "total_cases": 6,
            "tp": 2,
        })
        self.assertEqual(mediated["metrics"], {
            "abstentions": 3,
            "contradicted": 1,
            "coverage": 1.0,
            "decision_coverage": 3 / 6,
            "fp": 0,
            "linkable_cases": 3,
            "total_cases": 6,
            "tp": 3,
        })

    def test_catalog_absent_returns_unknown_without_local_candidates(self) -> None:
        observations = load_observations(FIXTURES / "observations_catalog_absent.json")
        truth = load_truth(FIXTURES / "truth_catalog_absent.json")
        result = recover(observations)
        self.assertEqual(result["catalog_status"], "unavailable")
        self.assertEqual(result["results"][0]["status"], "unknown")
        self.assertEqual(result["results"][0]["reason"], "public_catalog_unavailable")
        self.assertEqual(result["results"][0]["candidate_local_ids"], [])
        self.assertEqual(evaluate(result, truth)["metrics"]["coverage"], 0.0)

    def test_runner_emits_json_and_never_requires_truth_for_recovery(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "runner.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["direct"]["evaluation"]["metrics"]["fp"], 2)
        self.assertEqual(payload["mediated"]["evaluation"]["metrics"]["fp"], 0)
        self.assertNotIn("generated", completed.stdout.lower())
        self.assertNotIn("renders_to", completed.stdout.lower())


if __name__ == "__main__":
    unittest.main()
