"""CLI wrapper kept separate from the resolver so execution is auditable."""

from aep_endpoint import main


if __name__ == "__main__":
    raise SystemExit(main())
