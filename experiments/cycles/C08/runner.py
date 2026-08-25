"""Run C08 and write a JSON report inside C08."""

from __future__ import annotations

import json
from pathlib import Path

from evaluator import evaluate_fixture
from fixtures import build_fixture


ROOT = Path(__file__).resolve().parent


def main() -> int:
    report = evaluate_fixture(build_fixture())
    output = ROOT / "report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name, section in report["sections"].items():
        if name == "portfolio":
            print(f"{name}: baseline_score={section['baseline']['portfolio_score']:.3f} candidate_score={section['candidate']['portfolio_score']:.3f} redundancy={section['candidate']['redundancy']['rate']:.3f}")
        else:
            candidate = section["candidate"]
            print(f"{name}: p@1={candidate['precision_at_1']:.3f} recall={candidate['recall']:.3f} coverage={candidate['coverage']:.3f}")
    print(f"report={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
