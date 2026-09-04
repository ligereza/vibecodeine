"""Locate the FLUJO motor checkout from the MAK box.

MAK carries no ``src/flujo`` copy: the motor is consumed from a separate
checkout (contract 2026-09-02). Both ``tests/conftest.py`` and
``tests/integration_paths.py`` used to hardcode ``<mak_root>/flujo``, which is
true in the operator's home checkout and false in a git worktree, a CI clone,
or a side-by-side layout. Collection then failed on paths that never existed.

This module is the single resolver both of them consult. It is read-only: it
creates nothing, and returns ``None`` rather than guessing when no checkout
can be found.

Resolution order, first hit wins:

1. ``MAK_FLUJO_ROOT`` -- explicit operator override, honored verbatim.
2. ``<mak_root>/flujo`` -- the co-located checkout.
3. the installed ``flujo`` distribution, walked back from ``src/flujo``.
4. ``<mak_root>/../flujo`` -- the side-by-side sibling layout.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

MAK_ROOT = Path(__file__).resolve().parents[1]

__all__ = [
    "MAK_ROOT",
    "is_motor_checkout",
    "legacy_motor_root",
    "motor_root",
    "motor_src",
    "motor_tests",
]


def is_motor_checkout(candidate: Path) -> bool:
    """A motor checkout is the directory holding ``src/flujo/__init__.py``."""
    try:
        return (candidate / "src" / "flujo" / "__init__.py").is_file()
    except OSError:
        return False


def legacy_motor_root(mak_root: Path | None = None) -> Path:
    """The historical assumption, returned when nothing else resolves."""
    return (mak_root or MAK_ROOT) / "flujo"


def _installed_motor_root() -> Path | None:
    """Locate the motor through the installed ``flujo`` package, if any."""
    try:
        spec = importlib.util.find_spec("flujo")
    except (ImportError, ValueError):
        return None
    if spec is None or not spec.origin:
        return None
    origin = Path(spec.origin).resolve()
    # <root>/src/flujo/__init__.py -> parents[0]=flujo, [1]=src, [2]=<root>
    if len(origin.parents) < 3:
        return None
    candidate = origin.parents[2]
    return candidate if is_motor_checkout(candidate) else None


def motor_root(mak_root: Path | None = None) -> Path | None:
    """Return the motor checkout, or ``None`` when none can be found."""
    root = mak_root or MAK_ROOT

    override = os.environ.get("MAK_FLUJO_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    candidates = (root / "flujo", _installed_motor_root(), root.parent / "flujo")
    for candidate in candidates:
        if candidate is not None and is_motor_checkout(candidate):
            return candidate.resolve()
    return None


def motor_src(mak_root: Path | None = None) -> Path | None:
    """The importable ``src`` directory of the motor checkout."""
    root = motor_root(mak_root)
    return None if root is None else root / "src"


def motor_tests(mak_root: Path | None = None) -> Path | None:
    """The motor's own tests directory, home of the shared fixture helpers."""
    root = motor_root(mak_root)
    if root is None:
        return None
    tests = root / "tests"
    return tests if tests.is_dir() else None
