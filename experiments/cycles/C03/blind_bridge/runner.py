"""Reproducible C03 runner: recover first, load truth second, then score."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bridge import load_observations, recover_direct, recover_mediated
from evaluator import evaluate, load_truth


ROOT = Path(__file__).resolve().parent


def run_pair(observations_path: Path, truth_path: Path) -> dict[str, Any]:
    observations = load_observations(observations_path)
    # The two recovery calls happen before truth is read.  Neither call gets a
    # path, object, or label from the evaluation fixture.
    direct = recover_direct(observations)
    mediated = recover_mediated(observations)
    truth = load_truth(truth_path)
    return {
        "observations": str(observations_path),
        "truth": str(truth_path),
        "catalog_status": observations["catalog_status"],
        "direct": {"recovery": direct, "evaluation": evaluate(direct, truth)},
        "mediated": {"recovery": mediated, "evaluation": evaluate(mediated, truth)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the isolated C03 blind bridge benchmark")
    parser.add_argument("--observations", type=Path, default=ROOT / "fixtures" / "observations.json")
    parser.add_argument("--truth", type=Path, default=ROOT / "fixtures" / "truth.json")
    parser.add_argument("--catalog-absent", action="store_true")
    args = parser.parse_args()
    if args.catalog_absent:
        args.observations = ROOT / "fixtures" / "observations_catalog_absent.json"
        args.truth = ROOT / "fixtures" / "truth_catalog_absent.json"
    payload = run_pair(args.observations, args.truth)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
