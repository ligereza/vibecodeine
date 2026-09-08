#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The safety frame goes to the MODEL, never to the search engine.

The defect, measured 2026-07-30 across the whole RD batch of reports: `marco()`
returns frame+topic, and that whole string was being handed to Tavily. So every
query started with 148 characters of "Investigacion cultural DESCRIPTIVA
(historia, estetica, derecho, contexto social; nada operativo...)" before the
real subject. A search engine matches words, and those were the dominant ones,
so it returned research-methodology papers:

- the SAME Peruvian pedagogy PDF appears in FOUR of the five reports, on four
  subjects with nothing in common (board metrics, public-app feasibility, harm
  reduction databases, colorimetric reagents),
- plus a thesis-writing guide, a dictionary definition of "descriptive
  research", a didactics guide from Universidad Veracruzana, an accountability
  report from Colombia's environment ministry, and two Google Scholar landing
  pages listed as sources.

`docs/rd/informes/ley_20000_marco_legal.md` -- about CHILEAN law -- cites a
Peruvian teaching school, a Venezuelan university and a pirated-book aggregator.

The frame is right and it protects for a real reason: the model is the one that
could write a consumption guide. The search engine only ever needed the subject.
Proof the mechanism works once the prefix stops covering it: the feasibility
report DID find uchile.cl, medicina.udd.cl and portal.saludarica.cl.

`fuentes.py` catches the symptom (asserting without a primary source) and is
still needed. This is the cause.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cultura" / "mak_research"))

import research_lib  # noqa: E402

TEMA_RD = ("Ley 20.000 Chile y marco legal para servicios de analisis de "
           "sustancias y reduccion de danos")

# Words that only exist in the frame, never in a real subject.
PALABRAS_DEL_MARCO = ("investigacion cultural", "descriptiva", "estetica",
                      "contexto social", "sintesis quimica", "perfilar")


def test_marco_solo_no_trae_el_tema_pegado():
    frame = research_lib.marco_solo(TEMA_RD)
    assert frame, "sin encuadre el modelo pierde el limite que si hace falta"
    assert TEMA_RD not in frame, (
        "marco_solo devolvio encuadre+tema: eso es `marco()`, y es lo que "
        "terminaba dentro de la query del buscador")


def test_sin_marco_no_deja_encuadre():
    assert research_lib.marco_solo(TEMA_RD, activo=False) == ""


def test_un_tema_de_sustancias_recibe_el_marco_fuerte():
    """La exclusion `and not _es_tema_sustancia` sigue viva, pero ahora decide
    solo QUE se le dice al modelo -- no a donde busca."""
    frame = research_lib.marco_solo(TEMA_RD)
    assert "sintesis quimica" in frame.lower(), (
        "un tema de sustancias perdio el limite operativo en el system")


@pytest.mark.parametrize("palabra", PALABRAS_DEL_MARCO)
def test_la_query_que_sale_a_buscar_no_lleva_el_encuadre(monkeypatch, palabra):
    """El test que importa: se intercepta `web_search` y se mira QUE se pidio.

    Se prueba palabra por palabra porque un encuadre que se filtra a medias es
    igual de malo: basta con "investigacion descriptiva" para que el buscador
    conteste con guias de metodologia.
    """
    import research

    consultas = []

    def _falso_search(query, depth, errors=None):
        consultas.append(query)
        return {"results": [], "answer": ""}

    monkeypatch.setattr(research, "web_search", _falso_search)

    class _LLMMudo:
        def __init__(self, *a, **k):
            self.errors = []
            self.order = []
            self.stats = {}

        def call(self, system, user, max_tok=1024, order=None):
            return ("FINALIZAR: sin datos", "falso")

    monkeypatch.setattr(research, "LLM", _LLMMudo)
    research.investigar(TEMA_RD, iteraciones=1, depth="basic")

    assert consultas, "no se llamo al buscador: el test no midio nada"
    for q in consultas:
        assert palabra not in q.lower(), (
            "la query al buscador lleva %r del encuadre: %r" % (palabra, q[:120]))
    assert TEMA_RD[:30].lower() in consultas[0].lower(), (
        "la query perdio el tema real: %r" % consultas[0][:120])
