"""Stdlib tests for conservative Project IR routing."""

from __future__ import annotations

import unittest

from flujo.knowledge.project_ir import build_project_ir
from flujo.knowledge.project_router import evaluate_route, route_project


class ProjectRouterTests(unittest.TestCase):
    def _project(self, *, state="candidate", domains=("rd",), family="3d"):
        return build_project_ir(
            project_id="router-demo", title="Router demo", source_root="/tmp/router-demo",
            domains=domains, state=state,
            artifacts=[{"relative_path": "scene.blend", "format_family": family}],
        )

    def test_selects_read_only_blend_audit(self) -> None:
        decision = route_project(self._project())
        self.assertEqual(decision["decision"], "select")
        self.assertEqual(decision["selected"]["tool_id"], "blend_scene_audit")
        self.assertEqual(decision["next_action"], "execute_read_only")

    def test_unknown_state_abstains_even_with_a_matching_format(self) -> None:
        decision = route_project(self._project(state="unknown"))
        self.assertTrue(decision["abstention"])
        self.assertEqual(decision["reason"], "project_state_requires_evidence")

    def test_review_required_state_abstains_before_consumer_selection(self) -> None:
        decision = route_project(self._project(state="review_required"))
        self.assertEqual(decision["reason"], "project_state_requires_evidence")

    def test_unrecognized_format_abstains(self) -> None:
        decision = route_project(self._project(domains=("cultura",), family="opaque"))
        self.assertEqual(decision["decision"], "abstain")
        self.assertEqual(decision["reason"], "no_declared_consumer")

    def test_route_evaluation_does_not_call_or_execute_tools(self) -> None:
        decision = route_project(self._project())
        self.assertEqual(evaluate_route(decision, {"status": "ok", "validation": "passed"})["status"], "succeeded")
        self.assertEqual(evaluate_route(decision, {"status": "ok"})["status"], "needs_evidence")


if __name__ == "__main__":
    unittest.main()
