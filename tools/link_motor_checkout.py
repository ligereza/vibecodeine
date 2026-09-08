"""Compose the MAK box with the FLUJO motor by linking the expected path.

Several contracts are written against the *composed* layout: the motor sits at
``<mak_root>/flujo``. ``flujo.departments.catalog`` probes ``src/flujo/rd``
through that path, and ``context/learning/replay_suite_v1.json`` names sources
like ``flujo/tests/test_title_resolution.py`` relative to the MAK root. That
holds in the operator's home checkout and nowhere else, so a git worktree or a
CI clone fails those tests on a missing directory rather than on a real defect.

This tool creates that one symlink and nothing else. It never deletes, never
overwrites, and never follows through on an existing path: if
``<mak_root>/flujo`` is already a directory, a file, or a link pointing
somewhere else, the tool reports it and exits non-zero, leaving the operator to
decide.

    python -m tools.link_motor_checkout --check     # report, change nothing
    python -m tools.link_motor_checkout --dry-run   # say what it would create
    python -m tools.link_motor_checkout             # create the link

``MAK_FLUJO_ROOT`` overrides motor discovery; see ``tools.motor_checkout``.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

# Run as a script (`python tools/link_motor_checkout.py`) as well as a module:
# the repo hygiene contract asks every VIVO tool what it does with a bare
# `--help`, and that invocation does not put the repository on sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.motor_checkout import MAK_ROOT, is_motor_checkout, motor_root  # noqa: E402

OK = 0
NOTHING_TO_DO = 0
CONFLICT = 2
NO_MOTOR = 3


def _describe(path: Path) -> str:
    if path.is_symlink():
        return f"symlink -> {os.readlink(path)}"
    if path.is_dir():
        return "directory"
    if path.exists():
        return "file"
    return "absent"


def plan(mak_root: Path) -> tuple[Path, Path | None, str]:
    """Return the link path, the motor it should point at, and the situation."""
    link = mak_root / "flujo"

    if link.is_symlink():
        target = Path(os.readlink(link))
        resolved = target if target.is_absolute() else (mak_root / target)
        if is_motor_checkout(resolved):
            return link, resolved, "already_linked"
        return link, None, "conflict"
    if link.exists():
        if is_motor_checkout(link):
            return link, link, "already_present"
        return link, None, "conflict"

    motor = motor_root(mak_root)
    if motor is None:
        return link, None, "no_motor"
    if motor == link:
        return link, None, "no_motor"
    return link, motor, "creatable"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.link_motor_checkout",
        description="Link the FLUJO motor checkout to <mak_root>/flujo.",
    )
    parser.add_argument(
        "--mak-root",
        type=Path,
        default=MAK_ROOT,
        help="the MAK checkout to compose (default: this repository)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report the current state and change nothing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report the link that would be created and change nothing",
    )
    args = parser.parse_args(argv)

    mak_root = args.mak_root.expanduser().resolve()
    link, motor, situation = plan(mak_root)

    if situation == "already_linked":
        print(f"ok: {link} already points at the motor ({motor})")
        return NOTHING_TO_DO
    if situation == "already_present":
        print(f"ok: {link} is already a motor checkout")
        return NOTHING_TO_DO
    if situation == "conflict":
        print(
            f"refusing: {link} exists and is not a motor checkout ({_describe(link)}).\n"
            "This tool never deletes or overwrites. Move it aside yourself, or "
            "point MAK_FLUJO_ROOT at the motor instead of linking.",
            file=sys.stderr,
        )
        return CONFLICT
    if situation == "no_motor":
        print(
            "no motor checkout found. Set MAK_FLUJO_ROOT, install flujo in this "
            "environment, or place the FLUJO checkout beside this repository.",
            file=sys.stderr,
        )
        return NO_MOTOR

    assert motor is not None
    if args.check or args.dry_run:
        print(f"would create: {link} -> {motor}")
        return OK

    link.symlink_to(motor, target_is_directory=True)
    print(f"created: {link} -> {motor}")
    return OK


if __name__ == "__main__":
    raise SystemExit(main())
