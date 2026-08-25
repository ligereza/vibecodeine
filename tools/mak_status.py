#!/usr/bin/env python3
"""Print the unified read-only MAK operational status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from flujo.knowledge.system_status import system_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show the unified read-only status of the MAK knowledge loop."
    )
    parser.add_argument(
        "--db",
        default="data/mak_knowledge.db",
        help="Path to the MAK knowledge SQLite database.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root recorded as status provenance.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the complete machine-readable status.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    result = system_status(
        Path(args.db).expanduser(), repo_root=root, physical_root=root.parent
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    print(f"status={result['status']}")
    print(f"schema={result['schema']}")
    print(f"read_only={result['read_only']}")
    print(f"attention={result['counts']['attention']}")
    print(f"blocked={result['counts']['blocked']}")
    policy = result.get("learning", {}).get("policy", {})
    if policy:
        print(f"policy_schema={policy.get('schema', 'unknown')}")
        print(f"policy_status={policy.get('status', 'unknown')}")
        print(f"policy_reason={policy.get('reason', 'unknown')}")
        projects = result.get("learning", {}).get("projects", {})
        print(f"projects_review_required={projects.get('review_required', 0)}")
    if result["next_actions"]:
        print("next_actions:")
        for action in result["next_actions"]:
            print(f"- {action}")
    else:
        print("next_actions=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
