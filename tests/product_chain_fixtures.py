"""One named seam onto the product/portfolio fixture builders.

``tests/test_product_view.py`` needs ``_inputs``, ``_chain`` and
``_technical_context``. Those builders belong to the FLUJO motor, in
``<motor>/tests/test_artistic_program_evaluator.py``,
``<motor>/tests/test_product_plan.py`` and
``<motor>/tests/test_portfolio_dossier.py``. ``tests/conftest.py`` puts that
directory on ``sys.path`` so MAK integration tests can compose the two
checkouts.

The importing test used to reach for those modules with three bare
``from test_* import`` lines, which look like sibling MAK modules and fail with
a plain ``ModuleNotFoundError`` when the motor checkout is missing. This module
keeps the motor as the single source of truth -- nothing is copied here, so
nothing can drift -- while naming the dependency and failing with a message
that says what is actually absent.
"""

from __future__ import annotations

from tools.motor_checkout import motor_root

__all__ = [
    "_candidate",
    "_chain",
    "_hash",
    "_inputs",
    "_opportunity",
    "_payload",
    "_practice",
    "_technical_context",
]

try:  # pragma: no cover - exercised through the importing test module
    from test_artistic_program_evaluator import (  # noqa: F401
        _candidate,
        _hash,
        _inputs,
        _opportunity,
        _payload,
        _practice,
    )
    from test_portfolio_dossier import _technical_context  # noqa: F401
    from test_product_plan import _chain  # noqa: F401
except ImportError as error:  # pragma: no cover - only without a motor checkout
    _found = motor_root()
    _where = f"resolved motor checkout: {_found}" if _found else "no motor checkout resolved"
    raise ImportError(
        "the product chain fixtures live in the FLUJO motor's own tests "
        f"directory ({_where}). Set MAK_FLUJO_ROOT to the motor checkout, or "
        "place it beside this repository, so tests/conftest.py can put it on "
        f"sys.path. Original error: {error}"
    ) from error
