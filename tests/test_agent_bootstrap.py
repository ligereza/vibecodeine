from __future__ import annotations

import unittest
from pathlib import Path

from tools.agent_bootstrap import SCHEMA, build_packet, current_packet


ROOT = Path(__file__).resolve().parents[1]


class AgentBootstrapTests(unittest.TestCase):
    def test_packet_is_compact_current_state_and_pins_context(self):
        packet = build_packet(
            ROOT,
            "test bounded delegated task",
            ["experiments/cycles/C04/media_observer/"],
        )
        self.assertIn(f"schema={SCHEMA}", packet)
        self.assertIn("agents.md=", packet)
        self.assertIn("docs/MAK_CURRENT_STATE.md=", packet)
        self.assertIn("context/LAST_HANDOFF.md=", packet)
        self.assertIn("write_set=experiments/cycles/C04/media_observer/", packet)
        self.assertIn("## Agent bootstrap — CURRENT", packet)
        self.assertIn("historical sections are excluded", packet)

    def test_current_packet_stops_before_historical_heading(self):
        handoff = (ROOT / "context/LAST_HANDOFF.md").read_text(encoding="utf-8")
        packet = current_packet(handoff)
        self.assertIn("Stage 2D accepted", packet)
        self.assertIn("171 focused tests", packet)
        self.assertIn("docs/MAK_SYSTEM_DIRECTIVE.md", packet)
        self.assertIn("mak-archive-observation-batch-v1", packet)
        self.assertNotIn("## C02 — observación nativa real", packet)


if __name__ == "__main__":
    unittest.main()
