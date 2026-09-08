"""Stdlib tests for Project IR -> Research Job plan-only adaptation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sqlite3

from flujo.knowledge.episode_runner import probe_declared_consumer, record_probe
from flujo.knowledge.project_ir import LearningStore, build_project_ir
from flujo.knowledge.project_research import build_research_plan


class ProjectResearchTests(unittest.TestCase):
    def test_active_plant_project_gets_a_plan_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = build_project_ir(
                project_id="plant-demo", title="Plant cultivation study", source_root=Path(td),
                state="active", domains=["plants"], evidence=[{"source": "fixture", "status": "verified"}],
                artifacts=[{"relative_path": "manual.md", "format_family": "text"}],
            )
            plan = build_research_plan(project)
            self.assertEqual(plan["decision"], "select")
            self.assertEqual(plan["status"], "plan_only")
            self.assertEqual(plan["domain"], "plants")
            self.assertEqual(plan["external_calls"], 0)
            self.assertEqual(plan["writes"], 0)
            self.assertEqual(plan["route"]["format"], "informe")
            self.assertTrue(all(item["available"] for item in plan["dependencies"]))

    def test_review_required_project_abstains_before_research(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = build_project_ir(
                project_id="review-demo", title="Review", source_root=Path(td),
                state="review_required", domains=["plants"],
                artifacts=[{"relative_path": "notes.md", "format_family": "text"}],
            )
            plan = build_research_plan(project)
            self.assertEqual(plan["decision"], "abstain")
            self.assertEqual(plan["reason"], "project_state_requires_evidence")

    def test_unknown_format_abstains_instead_of_inventing_a_research_route(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = build_project_ir(
                project_id="opaque-demo", title="Opaque", source_root=Path(td),
                state="active", domains=["plants"], evidence=[{"source": "fixture", "status": "verified"}],
                artifacts=[{"relative_path": "opaque.xyz", "format_family": "unknown"}],
            )
            plan = build_research_plan(project)
            self.assertEqual(plan["decision"], "abstain")
            self.assertEqual(plan["reason"], "research_format_not_supported")

    def test_plan_only_probe_returns_needs_evidence_and_no_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = build_project_ir(
                project_id="plan-demo", title="Plan", source_root=Path(td),
                state="active", domains=["curatoria"], evidence=[{"source": "fixture", "status": "verified"}],
                artifacts=[{"relative_path": "notes.md", "format_family": "text"}],
            )
            decision = {
                "schema": "mak-project-router-v1",
                "decision": "select",
                "selected": {"tool_id": "research_job_router", "mode": "plan_only"},
            }
            probe = probe_declared_consumer(project, decision, repo_root=Path(td))
            self.assertEqual(probe["status"], "needs_evidence")
            self.assertEqual(probe["reason"], "research_plan_ready_no_job_created")
            self.assertEqual(probe["command"], [])
            self.assertEqual(probe["plan"]["writes"], 0)

    def test_plan_episode_is_idempotent_by_episode_id_and_plan_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = build_project_ir(
                project_id="idempotent-demo", title="Plan", source_root=root,
                state="active", domains=["curatoria"], evidence=[{"source": "fixture", "status": "verified"}],
                artifacts=[{"relative_path": "notes.md", "format_family": "text"}],
            )
            decision = {
                "schema": "mak-project-router-v1",
                "decision": "select",
                "selected": {"tool_id": "research_job_router", "mode": "plan_only"},
            }
            probe = probe_declared_consumer(project, decision, repo_root=root)
            store = LearningStore(root / "learning.sqlite")
            store.save_project(project)
            first = record_probe(store, project, decision, probe, episode_id="episode-plan-demo")
            second = record_probe(store, project, decision, probe, episode_id="episode-plan-demo")
            self.assertEqual(first, second)
            with sqlite3.connect(root / "learning.sqlite") as con:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM project_episodes").fetchone()[0], 1)
                observation = con.execute("SELECT observation_json FROM project_episodes").fetchone()[0]
                self.assertIn("plan_fingerprint", observation)


if __name__ == "__main__":
    unittest.main()
