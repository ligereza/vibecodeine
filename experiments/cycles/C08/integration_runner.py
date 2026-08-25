"""Run C07, then evaluate its graph on the same fixture cases."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from c07_integration import C07_GRAPH, evaluate_c07_graph


ROOT = Path(__file__).resolve().parent


def main() -> int:
    c07_runner = subprocess.run([sys.executable, str(ROOT.parent / "C07" / "runner.py")], cwd=ROOT.parent.parent.parent, check=False)
    if c07_runner.returncode != 0:
        return c07_runner.returncode
    report = evaluate_c07_graph(C07_GRAPH)
    output = ROOT / "c07_integration_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    candidate = report["candidate"]
    baseline = report["baseline"]
    print(json.dumps({
        "candidate_recall": candidate["recall"],
        "candidate_coverage": candidate["coverage"],
        "baseline_recall": baseline["recall"],
        "candidate_count": report["predicted_relation_count"],
        "gold_count": report["gold_relation_count"],
        "status_counts": report["status_counts"],
        "output": str(output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
