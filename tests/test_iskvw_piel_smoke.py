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
    for esperado in (# 2026-08-01: el mensaje decia "flag off draws exactly as
                     # before" y comparaba contra "sin tablero". Al encender
                     # `nodo_glifo` el dibujo cambio por OTRA llave y ese
                     # control acusaba al patch, asi que ahora compara contra el
                     # mismo tablero con el patch apagado. Este test fijaba el
                     # texto literal, o sea una cadena escrita a mano que dejo
                     # de coincidir con lo que existe -- la forma que este repo
                     # ya encontro siete veces esta semana.
                     # With the patch shipped ON the bench takes the other road: it
                     # asserts the published board CHANGES the drawing, which is
                     # the same claim measured from the other side.
                     "el tablero publicado cambia el dibujo",
                     "patch on deforms",
                     "gravedad pulls the reading",
                     # Per-effect switches: each effect is measured ALONE by
                     # the signature only it can leave, and the all-off run
                     # proves every switch gates to exactly zero.
                     "curvatura alone displaces",
                     "sangrado alone recolours",
                     "desgarro alone tears x-only",
                     "pulso alone bends glyph time",
                     "gravedad alone pulls the reading",
                     "every switch off under master on draws exactly the base",
                     # luz is the only effect that touches SIZE, and reading it
                     # took teaching this bench to record radii at all.
                     "luz alone dilates",
                     # The venue layer rides the SAME tablero fetch: its flag
                     # must gate the sala link in both states.
                     "venue layer gates on venue3d"):
        assert esperado in salida, (
            "the smoke no longer measures the effects patch (%r missing):\n%s"
            % (esperado, salida)
        )


def test_the_board_is_wiring_and_ships_on():
    """`datos/tablero.json` is the artist's patch bay, and it is DATA.

    Every route names a signal and an effect the skin knows.

    The master flag used to be pinned OFF here, because turning the
    portfolio's rendering on is the artist's decision and not a side effect of
    merging a branch. That reason still holds and the assertion flipped anyway:
    on 2026-08-01 the artist took the decision, the same way he took it for
    `nodo_glifo` in #433. What this test defends is not the value -- it is that
    the value is HIS. Pinned on, an agent that silently turns it off is caught
    just as an agent that silently turned it on used to be.
    """
    t = json.loads(TABLERO.read_text(encoding="utf-8"))
    piel = PIEL.read_text(encoding="utf-8")
    assert t["mejoras"]["patch_efectos"] is True, (
        "tablero.json ships with the effects patch OFF: the artist turned it "
        "on on 2026-08-01 and the portfolio draws with it. Turning it back "
        "off changes what every visitor sees and is not this file's call")
    # The names have to exist in the skin, or the route is a wire to nowhere.
    for fila in t["patch"]:
        assert "'%s'" % fila["dato"] in piel, "unknown signal: %s" % fila["dato"]
        assert "'%s'" % fila["efecto"] in piel, "unknown effect: %s" % fila["efecto"]
        assert isinstance(fila["ganancia"], (int, float)) and fila["ganancia"] > 0
    # The five effects the skin implements are all wired: a board that quietly
    # drops one is how an effect stops being maintained.
    assert {f["efecto"] for f in t["patch"]} == {
        "pulso", "curvatura", "sangrado", "desgarro", "gravedad", "luz"}
    # Every effect has its own switch under the master, and all ship ON: with
    # only the master flag the patch behaves exactly as it always did. A
    # switch the board silently drops would freeze that effect's default in
    # the skin, unreadable from the file the artist actually edits.
    assert set(t["efectos"]) == {
        "pulso", "curvatura", "sangrado", "desgarro", "gravedad", "luz"}
    for efecto, encendido in t["efectos"].items():
        assert encendido is True, (
            "tablero.json ships with effect %r off: shipped defaults preserve "
            "current behaviour, per-effect curation is the artist's edit"
            % efecto)


def test_the_skin_reads_the_board_and_survives_its_absence():
    piel = PIEL.read_text(encoding="utf-8")
    assert "datos/tablero.json" in piel
    # graceful 404: the fetch is guarded and the flag starts false
    assert "function aplicarTablero" in piel
    assert "const PATCH = {on:false" in piel
