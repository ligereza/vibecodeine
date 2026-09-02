"""Physical roots used by integration tests after the MAK/FLUJO split."""

from __future__ import annotations

import os
from pathlib import Path


MAK_ROOT = Path(__file__).resolve().parents[1]
FLUJO_ROOT = Path(os.environ.get("MAK_FLUJO_ROOT", MAK_ROOT / "flujo")).expanduser()
FLUJO_SRC = FLUJO_ROOT / "src"
FLUJO_TESTS = FLUJO_ROOT / "tests"

