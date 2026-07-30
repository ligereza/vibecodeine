"""The campo skin's JS actually runs, or CI goes red.

Cause (2026-07-30): PR #403 refactored the node loop into posicionDe() and
left `destino`/`dy` referenced out of scope. Every python test stayed green
while the portfolio died on frame one with a ReferenceError -- nothing
executed the skin's JS. tools/iskvw_piel_smoke.mjs runs the real inline
script in node with DOM stubs, walks the field so the per-node draw code
executes, and exits non-zero on any uncaught error (including async ones).
Retirement: if the skin ever gains a real browser test in CI.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SMOKE = RAIZ / "tools" / "iskvw_piel_smoke.mjs"


def test_campo_skin_js_runs_without_throwing():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH (CI runners ship it; install node locally)")
    proc = subprocess.run(
        [node, str(SMOKE)], capture_output=True, text=True, timeout=120,
        cwd=RAIZ,
    )
    assert proc.returncode == 0, (
        "the campo skin threw while booting/drawing:\n"
        + proc.stdout + proc.stderr
    )
