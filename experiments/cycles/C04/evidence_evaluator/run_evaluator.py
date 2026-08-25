#!/usr/bin/env python3
"""Run the C04 adversarial benchmark and report conservative metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evidence_evaluator import evaluate


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def run(adversarial_dir: Path, expected_dir: Path) -> dict[str, Any]:
    cases = sorted(adversarial_dir.glob("*.json"))
    if not cases:
        raise ValueError(f"no adversarial fixtures in {adversarial_dir}")
    case_results = []
    false_positives = 0
    abstentions = 0
    positive_count = 0
    assessed_count = 0
    for fixture_path in cases:
        fixture = _load(fixture_path)
        case_id = fixture.get("case_id")
        expected = _load(expected_dir / f"{case_id}.json")
        result = evaluate(fixture)
        for item in expected.get("claims", []):
            claim = item["claim"]
            expected_positive = bool(item.get("expected_positive"))
            predicted = result["claims"][claim]["status"]
            assessed_count += 1
            positive_count += int(expected_positive)
            false_positives += int(not expected_positive and predicted == "supported")
            abstentions += int(expected_positive and predicted in {"unknown", "candidate", "observed"})
        case_results.append({
            "case_id": case_id,
            "fixture": fixture_path.name,
            "expected": expected,
            "result": result,
        })
    return {
        "schema": "mak-cycle-c04-evidence-benchmark-v1",
        "case_count": len(case_results),
        "claim_count": assessed_count,
        "positive_claim_count": positive_count,
        "false_positives": false_positives,
        "false_positive_rate": false_positives / assessed_count if assessed_count else 0.0,
        "abstentions": abstentions,
        "abstention_rate_among_positive_claims": abstentions / positive_count if positive_count else 0.0,
        "cases": case_results,
    }


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adversarial-dir", type=Path, default=root / "fixtures" / "adversarial")
    parser.add_argument("--expected-dir", type=Path, default=root / "fixtures" / "expected")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    report = run(args.adversarial_dir, args.expected_dir)
    if args.compact:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
