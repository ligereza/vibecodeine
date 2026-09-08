"""Stdlib tests for the read-only Project IR API summary."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from flujo.knowledge.project_api import learning_summary
from flujo.knowledge.contract_registry import ContractRegistry, audit_contracts, contract_snapshot
from flujo.knowledge.project_ir import LearningStore, build_project_ir


class ProjectApiTests(unittest.TestCase):
    def test_summary_exposes_latest_abstain_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db = root / "learning.sqlite"
            project = build_project_ir(
                project_id="api-demo", title="API demo", source_root=root,
                state="review_required", unknowns=["evidence"],
            )
            store = LearningStore(db)
            store.save_project(project)
            store.record_episode(
                project_id="api-demo", objective="safe route", phase="gate",
                action={"tool": "project_router"}, observation={}, outcome={
                    "decision": "abstain",
                }, validation={"status": "needs_evidence"}, status="abstained",
                episode_id="episode-api-demo",
            )
            registry = ContractRegistry(db)
            registry.materialize(contract_snapshot())
            registry.record_audit(audit_contracts(contract_snapshot(), root), run_id="run-api")
            before = db.stat().st_size
            summary = learning_summary(db)
            after = db.stat().st_size

            self.assertEqual(before, after)
            self.assertEqual(summary["episodes"], {"abstained": 1})
            self.assertEqual(summary["latest_abstain"]["episode_id"], "episode-api-demo")
            self.assertEqual(summary["latest_abstain"]["phase"], "gate")
            expected_consumers = sum(1 for row in contract_snapshot() if row["kind"] == "consumer")
            self.assertEqual(summary["contracts"]["counts"]["consumer"], expected_consumers)
            self.assertEqual(summary["audits"]["latest_run"], "run-api")
            self.assertTrue(summary["audits"]["attention"])


if __name__ == "__main__":
    unittest.main()
