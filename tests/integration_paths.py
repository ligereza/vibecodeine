"""Physical roots used by integration tests after the MAK/FLUJO split.

The motor lives in a separate checkout. This module used to assume it sat at
``<mak_root>/flujo``, which is true in the operator's home checkout and false
everywhere else: a git worktree, a CI clone, or a side-by-side layout. Tests
that read motor sources then failed with ``FileNotFoundError`` on a path that
never existed, which reads like a broken contract instead of a missing
checkout.

``tools.motor_checkout`` owns the resolution order and is shared with
``tests/conftest.py``. When nothing resolves, ``FLUJO_ROOT`` keeps the
historical ``<mak_root>/flujo`` value so callers see the path they always did,
and ``FLUJO_ROOT_RESOLVED`` reports ``False`` for tests that prefer to skip
rather than fail.
"""

from __future__ import annotations

from pathlib import Path

from tools.motor_checkout import legacy_motor_root, motor_root

MAK_ROOT = Path(__file__).resolve().parents[1]

_RESOLVED = motor_root(MAK_ROOT)
FLUJO_ROOT_RESOLVED = _RESOLVED is not None
FLUJO_ROOT = _RESOLVED if _RESOLVED is not None else legacy_motor_root(MAK_ROOT)
FLUJO_SRC = FLUJO_ROOT / "src"
FLUJO_TESTS = FLUJO_ROOT / "tests"
