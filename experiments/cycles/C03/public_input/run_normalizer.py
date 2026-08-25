#!/usr/bin/env python3
"""CLI for the C03 public-input normalizer."""

from __future__ import annotations

import argparse
import json
import sys

from public_normalizer import NormalizationError, catalog_unavailable, normalize_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize a declared C03 public export")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("input", nargs="?", help="local .json/.html/.htm export")
    group.add_argument(
        "--catalog-unavailable",
        action="store_true",
        help="emit the explicit no-real-export-local status",
    )
    parser.add_argument(
        "--archive-id",
        help="explicit archive id required with --catalog-unavailable",
    )
    parser.add_argument("--compact", action="store_true", help="emit one-line JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.catalog_unavailable:
            if not args.archive_id:
                raise NormalizationError("--archive-id is required with --catalog-unavailable")
            result = catalog_unavailable(args.archive_id)
        else:
            if args.archive_id:
                raise NormalizationError("--archive-id is only valid with --catalog-unavailable")
            result = normalize_file(args.input)
    except (NormalizationError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.compact:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
