"""Gate the isolated C05 export-witness graph bridge."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from export_graph_bridge import materialize


ROOT = Path(__file__).resolve().parent
INPUT = ROOT.parent / "C05" / "real_export_witness.json"
OUTPUT = ROOT / "real_export_graph.json"


def main() -> int:
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_export_graph_bridge.py"],
        cwd=ROOT.parent.parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    witness = json.loads(INPUT.read_text(encoding="utf-8"))
    graph = materialize(witness)
    OUTPUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "tests_exit_code": tests.returncode,
        "witness_input": str(INPUT),
        "claim_status": graph["claim"]["status"],
        "edge_count": len(graph["edges"]),
        "adversarial_cases": 3,
        "output": str(OUTPUT),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if tests.returncode == 0 and graph["claim"]["status"] == "supported" and len(graph["edges"]) == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
