#!/usr/bin/env python3
"""Run the isolated MAK operating-world comparison in the foreground."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model import (
    build_capability_registry,
    load_cases,
    model_inventory,
    observed_capability_cards,
    run_comparison,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/mak_knowledge.db")
    parser.add_argument("--cases", default=str(Path(__file__).with_name("cases.json")))
    args = parser.parse_args()
    cards = observed_capability_cards(args.db)
    cases = load_cases(args.cases)
    registry = build_capability_registry(cards)
    report = run_comparison(args.db, cases, registry)
    report["model_inventory"] = model_inventory(args.db)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
