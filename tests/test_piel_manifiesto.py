#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every skin declares what it needs, and every skin passes the same battery.

Measured 2026-07-31: there were THREE skins -- `campo` (1323 lines), `terminal`
(772) and `venue` (505) -- and both `tools/iskvw_piel_smoke.mjs` and
`tools/iskvw_piel_medir.mjs` read the literal path `.../piel/campo/index.html`.
So two of the three had NO verification of any kind and could have been broken
for months without a word. When the battery was finally pointed at them, three
things broke, and none of them was the skin:

    terminal   canvas.getContext is not a function   (its canvas has another id)
    venue      L.querySelectorAll is not a function  (element query never stubbed)
    venue      per-node draw code never executed     (the metric counted
                                                      gradients and glyphs --
                                                      how CAMPO draws; venue
                                                      draws polylines)

The instrument was shaped like one skin and called that a verification. Both
skins turned out to work: `venue` draws 503 edges, `terminal` 3.480 marks.

That is what `piel.json` is for. The battery cannot guess the name of a skin's
variables, so the skin declares what it fetches and HOW WHAT IT DREW IS
COUNTED. Then "the skin is swappable" stops being an intention: a skin is valid
if it passes the same battery as the published one.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PIELES_DIR = RAIZ / "iskvw" / "piel"
ESQUEMA = json.loads((RAIZ / "schemas" / "piel.schema.json").read_text(encoding="utf-8"))

# A skin is a directory with an index.html. `lib/`, `trazos/` and `animadas/`
# are assets, not skins, and are excluded by that rule rather than by a list
# somebody has to remember to update.
PIELES = sorted(p.name for p in PIELES_DIR.iterdir()
                if p.is_dir() and (p / "index.html").exists())

NODE = shutil.which("node")
sin_node = pytest.mark.skipif(NODE is None, reason="node no esta instalado")


def test_there_is_more_than_one_skin_and_the_list_is_discovered():
    """The list is not hardcoded anywhere: a fourth skin joins the battery by
    existing, which is the whole point of swappable."""
    assert len(PIELES) >= 3, PIELES
    assert {"campo", "terminal", "venue"} <= set(PIELES)


@pytest.mark.parametrize("piel", PIELES)
def test_every_skin_declares_a_manifest(piel):
    """A skin with no manifest cannot be verified, so it is not a skin yet."""
    ruta = PIELES_DIR / piel / "piel.json"
    assert ruta.exists(), (
        f"{piel} no declara piel.json -- sin manifiesto la bateria tendria que "
        f"adivinar el nombre de sus variables, que es como dos de tres pieles "
        f"quedaron sin verificar")
    m = json.loads(ruta.read_text(encoding="utf-8"))
    for campo in ESQUEMA["required"]:
        assert campo in m, f"{piel}/piel.json no declara `{campo}`"
    assert m["formato"] == "piel/1"
    assert m["nombre"] == piel, "el nombre del manifiesto y el del directorio"


@pytest.mark.parametrize("piel", PIELES)
def test_declared_data_paths_exist_or_are_optional(piel):
    """Declaring a file that is not there is allowed ONLY as optional -- that is
    how a skin says 'I keep drawing without this'. Declaring a mandatory file
    that does not exist is a manifest that lies."""
    m = json.loads((PIELES_DIR / piel / "piel.json").read_text(encoding="utf-8"))
    for d in m.get("datos", []):
        destino = (PIELES_DIR / piel / d["ruta"]).resolve()
        if d["obligatorio"]:
            assert destino.exists(), f"{piel} exige {d['ruta']} y no esta"
        assert RAIZ in destino.parents or destino == RAIZ, (
            f"{piel} pide {d['ruta']}, que sale del checkout")


@pytest.mark.parametrize("piel", PIELES)
def test_every_declared_layer_names_the_datum_it_encodes(piel):
    """The doublecup thesis, as a check: a layer that says it encodes `tilde`
    can be argued with; one that says 'more organic' cannot. This is what makes
    one layer or a thousand safe -- each answers for its own datum."""
    m = json.loads((PIELES_DIR / piel / "piel.json").read_text(encoding="utf-8"))
    for capa in m.get("capas", []):
        assert capa.get("nombre"), f"{piel}: una capa sin nombre"
        assert capa.get("codifica"), (
            f"{piel}: la capa {capa.get('nombre')} no dice que dato codifica")


@sin_node
@pytest.mark.parametrize("piel", PIELES)
def test_every_skin_passes_the_battery(piel):
    """The same battery for all of them. This is the assertion that would have
    caught, months ago, whatever `terminal` and `venue` might have been."""
    r = subprocess.run([NODE, str(RAIZ / "tools" / "iskvw_piel_smoke.mjs"), piel],
                       capture_output=True, text=True, encoding="utf-8",
                       cwd=str(RAIZ), timeout=180)
    assert r.returncode == 0, (
        f"la piel {piel} no pasa la bateria:\n{r.stdout}\n{r.stderr}")
    assert "OK: nucleo" in r.stdout, r.stdout


@sin_node
def test_a_manifest_that_lies_about_its_data_fails():
    """Declaring a mandatory file the skin never asks for must FAIL, not pass.
    A manifest nobody checks is documentation, and documentation rots."""
    piel = "campo"
    ruta = PIELES_DIR / piel / "piel.json"
    original = ruta.read_text(encoding="utf-8")
    m = json.loads(original)
    m["datos"].append({"ruta": "../../datos/no_existe.json", "obligatorio": True,
                       "para": "mentira deliberada, para probar el guardian"})
    try:
        ruta.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        r = subprocess.run([NODE, str(RAIZ / "tools" / "iskvw_piel_smoke.mjs"), piel],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=str(RAIZ), timeout=180)
        assert r.returncode != 0, "un manifiesto que miente tiene que fallar"
        assert "nunca lo pidio" in (r.stdout + r.stderr)
    finally:
        ruta.write_text(original, encoding="utf-8")
