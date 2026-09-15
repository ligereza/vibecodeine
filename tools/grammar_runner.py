"""CLI for the MAK-local bounded grammar experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cultura.mak_research.grammar import (
    GrammarRunError,
    resume_experiment,
    run_experiment,
    status_experiment,
    stop_experiment,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="grammar_runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run")
    run.add_argument("--corpus", required=True, type=Path)
    run.add_argument("--generations", type=int, default=3, choices=range(1, 4))
    run.add_argument("--seed", type=int, default=42)
    run.add_argument("--max-candidates", type=int, default=24)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--run-id")
    run.add_argument("--stop-after-generation", type=int)

    for command in ("resume", "status", "stop"):
        action = subparsers.add_parser(command)
        action.add_argument("--checkpoint", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "run":
            result = run_experiment(
                corpus=args.corpus,
                generations=args.generations,
                seed=args.seed,
                max_candidates=args.max_candidates,
                output=args.output,
                run_id=args.run_id,
                stop_after_generation=args.stop_after_generation,
            )
        elif args.command == "resume":
            result = resume_experiment(args.checkpoint)
        elif args.command == "status":
            result = status_experiment(args.checkpoint)
        else:
            result = stop_experiment(args.checkpoint)
    except GrammarRunError as exc:
        _parser().error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
