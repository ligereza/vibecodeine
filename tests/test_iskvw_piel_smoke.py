"""The campo skin's JS actually runs, or CI goes red.

Cause (2026-07-30): PR #403 refactored the node loop into posicionDe() and
left `destino`/`dy` referenced out of scope. Every python test stayed green
while the portfolio died on frame one with a ReferenceError -- nothing
executed the skin's JS. tools/iskvw_piel_smoke.mjs runs the real inline
script in node with DOM stubs, walks the field so the per-node draw code
executes, and exits non-zero on any uncaught error (including async ones).
Retirement: if the skin ever gains a real browser test in CI.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SMOKE = RAIZ / "tools" / "iskvw_piel_smoke.mjs"
TABLERO = RAIZ / "iskvw" / "datos" / "tablero.json"
PIEL = RAIZ / "iskvw" / "piel" / "campo" / "index.html"


def _correr_smoke():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH (CI runners ship it; install node locally)")
    return subprocess.run(
        [node, str(SMOKE)], capture_output=True, text=True, timeout=180,
        cwd=RAIZ,
    )


def test_campo_skin_js_runs_without_throwing():
    proc = _correr_smoke()
    assert proc.returncode == 0, (
        "the campo skin threw while booting/drawing:\n"
        + proc.stdout + proc.stderr
    )


def test_the_smoke_still_measures_the_effects_patch():
    """The smoke's exit code is not enough on its own.

    A master flag that ships OFF is code nobody looks at: if someone trims the
    patch checks out of the tool, every test here stays green while the
    effects rot. So the four measurements are demanded by name.
    """
    proc = _correr_smoke()
    salida = proc.stdout + proc.stderr
    for esperado in ("flag off draws exactly as before",
                     "patch on deforms",
                     "gravedad pulls the reading"):
        assert esperado in salida, (
            "the smoke no longer measures the effects patch (%r missing):\n%s"
            % (esperado, salida)
        )


def test_the_board_is_wiring_and_ships_off():
    """`datos/tablero.json` is the artist's patch bay, and it is DATA.

    Every route names a signal and an effect the skin knows; the master flag
    ships off, because turning the portfolio's rendering on is the artist's
    decision and not a side effect of merging a branch.
    """
    t = json.loads(TABLERO.read_text(encoding="utf-8"))
    piel = PIEL.read_text(encoding="utf-8")
    assert t["mejoras"]["patch_efectos"] is False, (
        "tablero.json ships with the effects patch ON: that changes how the "
        "portfolio looks for everyone, and it is not this file's call")
    # The names have to exist in the skin, or the route is a wire to nowhere.
    for fila in t["patch"]:
        assert "'%s'" % fila["dato"] in piel, "unknown signal: %s" % fila["dato"]
        assert "'%s'" % fila["efecto"] in piel, "unknown effect: %s" % fila["efecto"]
        assert isinstance(fila["ganancia"], (int, float)) and fila["ganancia"] > 0
    # The five effects the skin implements are all wired: a board that quietly
    # drops one is how an effect stops being maintained.
    assert {f["efecto"] for f in t["patch"]} == {
        "pulso", "curvatura", "sangrado", "desgarro", "gravedad"}


def test_the_skin_reads_the_board_and_survives_its_absence():
    piel = PIEL.read_text(encoding="utf-8")
    assert "datos/tablero.json" in piel
    # graceful 404: the fetch is guarded and the flag starts false
    assert "function aplicarTablero" in piel
    assert "const PATCH = {on:false" in piel
