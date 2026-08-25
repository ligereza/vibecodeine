#!/usr/bin/env python3
"""Run all synthetic native endpoint cases and print JSON evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from native_endpoint import compare_models, load_cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=Path(__file__).with_name("fixtures") / "cases.json",
    )
    args = parser.parse_args()
    results = [compare_models(case) for case in load_cases(args.fixtures)]
    print(json.dumps({"extractor_version": "native-endpoint-synthetic-v1", "cases": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
