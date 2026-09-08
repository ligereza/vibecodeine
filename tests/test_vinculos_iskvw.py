#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A link that cannot say why it exists is decoration.

`gen_archivo_iskvw.py` builds links from shared tags and says so in its own
comment: "se declara `clase: etiqueta` y NO `semantico`: nadie midio que se
parezcan, comparten una palabra". Correct -- and it left the 7.985 concept
mentions the perception pass extracted completely unused.

Measured over the 1.401 ig fichas before any of this was written:

    vocabulary                     1.662 concepts, 1.541 after folding
    concepts in exactly one work     819 (53%) -- they link nothing
    pairs sharing >=1 specific    31.846 -- a hairball
    pairs sharing >=2              1.830, reaching 860 works (63%)

So the threshold is not taste. And every exclusion is reported, because a cap
nobody mentions reads as "that was everything there was".
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOOL = RAIZ / "tools" / "gen_vinculos_iskvw.py"


def _mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("genvin", TOOL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _obras(**kw):
    """Claves ya plegadas, como las entrega `conceptos_por_obra`."""
    return {k: set(v) for k, v in kw.items()}


# ------------------------------------------------------------- the folding

def test_singular_and_plural_are_one_idea():
    """`figura humana`(113) and `figuras humanas`(112) were two entries for one
    idea -- exactly half the signal thrown away."""
    m = _mod()
    assert m.plegar("figuras humanas") == m.plegar("figura humana")


def test_accents_do_not_split_a_concept():
    m = _mod()
    assert m.plegar("geometría") == m.plegar("geometria")


def test_a_short_word_keeps_its_s():
    """The fold is deliberately dumb, and dumb has to stay bounded: turning
    `mes` into `me` would invent a concept."""
    m = _mod()
    assert m.plegar("mes") == "mes"


# ------------------------------------------------------------- the reason

def test_every_link_carries_the_concepts_that_produced_it():
    m = _mod()
    vs, _ = m.vinculos(_obras(a=["dragon", "mitologia", "simetria"],
                              b=["dragon", "mitologia", "otra"]), comunes=0)
    assert len(vs) == 1
    assert vs[0]["porque"] == ["dragon", "mitologia"]
    assert vs[0]["clase"] == "concepto", (
        "`semantico` afirmaria que se parecen, y nadie lo midio")


def test_one_shared_concept_is_not_a_link():
    """One produces 31.846 pairs over 1.359 works: a hairball, not a graph."""
    m = _mod()
    vs, _ = m.vinculos(_obras(a=["dragon", "x"], b=["dragon", "y"]), comunes=0)
    assert vs == []


# ------------------------------------------------------------- the exclusions

def test_a_concept_in_a_single_work_links_nothing_and_is_counted():
    m = _mod()
    _, d = m.vinculos(_obras(a=["solo_mio", "compartido", "otro"],
                             b=["compartido", "otro"]), comunes=0)
    assert d["en_una_sola_obra"] == 1


def test_the_most_frequent_concepts_are_excluded_and_named():
    """A concept in 305 works is a CATEGORY. Letting it in connects everything
    to everything, which is the same as connecting nothing."""
    m = _mod()
    obras = {str(i): {"naturaleza", "propio%d" % i} for i in range(10)}
    obras["0"].add("raro"); obras["1"].add("raro")
    _, d = m.vinculos(obras, comunes=1)
    assert d["demasiado_comunes"] == ["naturaleza"]


def test_nothing_is_capped_in_silence():
    """A cap nobody reports reads as 'that was everything there was'."""
    m = _mod()
    _, d = m.vinculos(_obras(a=["x", "y"], b=["x", "y"]), comunes=0)
    for clave in ("vocabulario", "en_una_sola_obra", "demasiado_comunes",
                  "sobre_el_tope", "usables", "pares_con_al_menos_uno"):
        assert clave in d, clave


def test_a_concept_over_the_width_cap_is_dropped_as_a_category():
    m = _mod()
    obras = {str(i): {"ancho", "par%d" % (i // 2)} for i in range(8)}
    _, d = m.vinculos(obras, comunes=0, tope_obras=4)
    assert d["sobre_el_tope"] == 1


def test_the_reason_shows_what_the_model_wrote_not_the_fold_key():
    """The fold is for GROUPING. `patrones` folds to `patrone`, which is a key
    and not a word: letting it out would put "patrone geometrico" in front of a
    human. Same rule as the accent -- normalise to join, display what was
    written."""
    m = _mod()
    filas = [{"id": "a", "vision": {"conceptos": ["patrones geometricos", "dragon"]}},
             {"id": "b", "vision": {"conceptos": ["patrones geometricos", "dragon"]}}]
    obras, canon = m.conceptos_por_obra(filas)
    vs, _ = m.vinculos(obras, comunes=0, canon=canon)
    assert vs[0]["porque"] == ["dragon", "patrones geometricos"]
    assert not any("patrone " in p for p in vs[0]["porque"])


def test_the_most_used_spelling_represents_the_group():
    m = _mod()
    filas = ([{"id": str(i), "vision": {"conceptos": ["colores"]}} for i in range(5)]
             + [{"id": "x", "vision": {"conceptos": ["color"]}}])
    _, canon = m.conceptos_por_obra(filas)
    assert canon[m.plegar("colores")] == "colores"


# ------------------------------------------------------------- end to end

def test_it_reports_and_writes_nothing_by_default(tmp_path):
    fichas = tmp_path / "f.jsonl"
    filas = [{"id": "a", "vision": {"conceptos": ["dragon", "mitologia", "z"]}},
             {"id": "b", "vision": {"conceptos": ["dragon", "mitologia", "w"]}}]
    fichas.write_text("\n".join(json.dumps(f) for f in filas) + "\n",
                      encoding="utf-8")
    r = subprocess.run([sys.executable, str(TOOL), str(fichas), "--comunes", "0"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "vinculos con >= 2 conceptos: 1" in r.stdout
    assert "informe solamente" in r.stdout
    assert not list(tmp_path.glob("*.json"))


def test_fichas_with_no_concepts_say_so_instead_of_writing_an_empty_graph(tmp_path):
    fichas = tmp_path / "f.jsonl"
    fichas.write_text(json.dumps({"id": "a", "vision": {}}) + "\n",
                      encoding="utf-8")
    r = subprocess.run([sys.executable, str(TOOL), str(fichas)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    assert r.returncode == 1
    assert "ninguna ficha trae conceptos" in r.stdout
