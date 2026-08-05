# -*- coding: utf-8 -*-
"""The campo skin's frame cost, measured in numbers that cannot drift silently.

The 2026-07-30 handoff pinned the defect class (all pairs every frame) with
static tests and left one honest gap: "NOT measured: fps on a phone". A phone
cannot be measured from CI -- but the WORK per frame can, deterministically:
tools/iskvw_piel_medir.mjs runs the PUBLISHED skin's own inline script in node
(same technique as tools/iskvw_piel_smoke.mjs), enters real scenarios through
the skin's own seed model (#semilla=&centro=&escala= plus pinch aperture), and
counts drawn segments, canvas geometry ops and the neighbour-index size.

What is pinned here: COUNTS, never milliseconds. Counts are properties of the
published code plus the repo's data; ms belong to whichever machine ran it and
are reported as context only. The phone number remains the user's to take --
now with a fixed math-cost baseline to compare against.

Retirement: if the skin gains a real browser perf test in CI.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MEDIR = RAIZ / "tools" / "iskvw_piel_medir.mjs"
GENERADOR = RAIZ / "tools" / "gen_archivo_iskvw.py"

# Measured 2026-08-05 on the published skin with the repo's real data:
# archivo.json generated exactly like the publish workflow does
# (gen_archivo_iskvw.py --fuente todo; the micelio is unreachable in CI and
# the generator degrades by design, same as at publish time; essays are an
# explicit research view, not default public substrate), and campo.json as the
# live fallback. If these numbers change because the DATA changed
# (new curated works, new public links), re-run
# `node tools/iskvw_piel_medir.mjs` and re-pin. If the data did NOT change,
# the skin's frame cost changed: that is the regression this file exists for.
PIN_ARCHIVO = {
    "nodos": 1976,
    "vinculos_indexados": 5158,
    # Re-pinned 2026-08-05 after the micelio snapshot reached the public
    # archive. The substrate now includes the measured semantic links from MAK
    # through iskvw/datos/micelio.json, while MAK essays remain opt-in research.
    # The laser bloom from 2026-08-01 still paints every kept link twice.
    "segmentos": {
        "entrada cerrada": 68,
        "entrada abierta": 2126,
        "medio abierto": 2492,
        "denso cerrado": 110,
        "denso medio": 1286,
        "denso abierto": 2282,
        "denso escalado": 2282,
    },
}
PIN_CAMPO = {
    "nodos": 219,
    "vinculos_indexados": 0,
    # campo.json ships no vinculos and its pieces carry no tags: today's live
    # fallback draws ZERO link segments. If this stops being 0, links started
    # being drawn on a substrate that declares none -- that is an affirmation
    # without data, not a feature.
    "segmentos": 0,
    # The dense worst case of per-node work, and since 2026-08-01 it is a
    # different one. With `mejoras.nodo_glifo` on the node stopped being a
    # circle -- one radial gradient plus two arcs per drawn node, 217 gradients
    # and 434 arcs in the dense band -- and became a glyph: ZERO gradients, ZERO
    # arcs, one `fillText` per node that does not land on the ramp's empty slot.
    #
    # It is not only cheaper: it is the technique the artist asked for, written
    # in `iskvw/piel/campo/ASCII_REFERENCIA.md` since 2026-07-30 and applied
    # only to the resolved work. If these numbers go back to non-zero, the
    # circle came back.
    "denso_abierto_gradientes": 0,
    "denso_abierto_arcos": 0,
}

# The documented reference cost this instrument guards against: all-against-all
# on the 219 works is 23,871 pairs per frame (n*(n-1)/2), and 1,951,300 on the
# 1976-piece micelio substrate. Worst measured across the whole grid today:
# 2492 segments per frame. The ceiling is 6000: enough headroom for more
# curated links, still 325x below the all-pairs cost, so a return of the
# every-pair-every-frame defect turns this red long before a phone stutters.
TECHO_SEGMENTOS = 6000


@pytest.fixture(scope="module")
def medida(tmp_path_factory):
    """Generate the substrate offline and run the instrument once."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH (CI runners ship it; install node locally)")
    tmp = tmp_path_factory.mktemp("medir")
    archivo = tmp / "archivo.json"
    gen = subprocess.run(
        [sys.executable, str(GENERADOR), "--fuente", "todo",
         "--salida", str(archivo)],
        capture_output=True, text=True, timeout=180, cwd=RAIZ,
        # A dead port: the generator must degrade (no micelio in CI, same as
        # the publish workflow) instead of picking up a live micelio on a dev
        # machine and making the pinned numbers environment-dependent.
        env={**os.environ, "FLUJO_MAK_RESEARCH_URL": "http://127.0.0.1:9"},
    )
    assert gen.returncode == 0, "substrate generation failed:\n" + gen.stdout + gen.stderr
    assert archivo.is_file() and archivo.stat().st_size > 0
    proc = subprocess.run(
        [node, str(MEDIR), "--archivo", str(archivo), "--json"],
        capture_output=True, text=True, timeout=180, cwd=RAIZ,
    )
    assert proc.returncode == 0, "the instrument failed:\n" + proc.stdout + proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _sustrato(medida: dict, nombre: str) -> dict:
    filas = [e for e in medida["escenarios"] if e["sustrato"] == nombre]
    assert filas, f"no scenarios measured for substrate {nombre}"
    return {e["escenario"]: e for e in filas}


def test_the_grid_covers_both_substrates_and_reports_ms(medida):
    """Both real data paths are measured (publish-time archivo.json and the
    live campo.json fallback), each across the full scenario grid, and every
    row carries an informative ms figure -- present, never pinned."""
    assert medida["archivo"] is True
    por = {}
    for e in medida["escenarios"]:
        por.setdefault(e["sustrato"], []).append(e)
    assert set(por) == {"archivo", "campo"}
    for filas in por.values():
        assert len(filas) == 7
        for e in filas:
            assert isinstance(e["ms_mediana"], (int, float)) and e["ms_mediana"] >= 0
            # the cross-check the instrument carries: one lineTo per stroke
            assert e["lineas"] == e["segmentos"]


def test_segment_counts_are_the_pinned_numbers(medida):
    """Counts are pinned by their WORST frame. Until 2026-08-01 every frame was
    required to do identical work, which held while the node was an arc -- 764
    arcs whatever the time was. The glyph comes from a field that evolves, and a
    node landing on the ramp's empty slot is not drawn, so the count moves
    between frames BY DESIGN. What this meter exists to catch is a cost
    regression, and for that the worst frame rules; the range is published
    whenever a counter moves."""
    archivo = _sustrato(medida, "archivo")
    assert {n: e["segmentos"] for n, e in archivo.items()} == PIN_ARCHIVO["segmentos"]
    for e in archivo.values():
        assert e["nodos"] == PIN_ARCHIVO["nodos"]

    campo = _sustrato(medida, "campo")
    for e in campo.values():
        assert e["nodos"] == PIN_CAMPO["nodos"]
        assert e["segmentos"] == PIN_CAMPO["segmentos"]
    # With the node as a glyph neither a gradient nor an arc is created: the
    # halo and the solid circle are exactly what got replaced. A non-zero value
    # here means the node went back to being a circle.
    assert campo["denso abierto"]["gradientes"] == PIN_CAMPO["denso_abierto_gradientes"]
    assert campo["denso abierto"]["arcos"] == PIN_CAMPO["denso_abierto_arcos"]
    # And there are real glyphs: if this were 0, the node would not be drawn.
    assert campo["denso abierto"]["textos"] > 0


def test_the_neighbour_index_is_built_once_and_sized_right(medida):
    """The index the skin builds in sembrar(): every kept link appears in both
    endpoints' lists as (index, weight), so entries == 4 * links. Its size is
    the once-per-load cost that replaces the per-frame pair scan."""
    archivo = _sustrato(medida, "archivo")
    for e in archivo.values():
        assert e["vinculos_indexados"] == PIN_ARCHIVO["vinculos_indexados"]
        assert e["indice_entradas"] == 4 * PIN_ARCHIVO["vinculos_indexados"]
    for e in _sustrato(medida, "campo").values():
        assert e["vinculos_indexados"] == PIN_CAMPO["vinculos_indexados"]


def test_the_worst_scenario_stays_far_from_all_against_all(medida):
    """The ceiling: see TECHO_SEGMENTOS above. The all-against-all pair count
    must never be approached."""
    assert medida["peor_segmentos"] <= TECHO_SEGMENTOS, (
        "%d segments in one frame: the link culling stopped working"
        % medida["peor_segmentos"]
    )
    for e in medida["escenarios"]:
        pares = e["nodos"] * (e["nodos"] - 1) // 2
        assert e["todos_los_pares"] == pares
        assert e["segmentos"] < pares / 10

