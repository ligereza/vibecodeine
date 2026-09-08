"""The MAK renderer must import Blender nodes from the physical FLUJO checkout."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "render_flyer_mak", ROOT / "tools" / "render_flyer_mak.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_motor_directory_uses_the_sibling_flujo_checkout():
    expected = ROOT / "flujo" / "src" / "flujo" / "eventos"
    assert MODULE.EVENTOS_DIR == expected
    assert MODULE.EVENTOS_DIR != ROOT / "src" / "flujo" / "eventos"
