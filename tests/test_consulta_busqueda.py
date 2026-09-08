#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What the SEARCHER gets is not what the model gets.

Measured against the Tavily API on 2026-08-01: a query over 400 characters
answers HTTP 400 "Query is too long" and zero results. The RD triangulation
tasks are 530 characters, because the question and the rules for the model live
in the same string:

    "...que productora organizo el evento del 21 DE MARZO 2026 con ADRIATIQUE,
    COLYN, JOHN CALA en el cartel en CLUB HIPICO? REGLAS: el evento es en
    Chile, si lo que encontras es de otro pais NO sirve. Solo se acepta
    respuesta con FUENTE VERIFICABLE..."

A search engine matches words. We were sending it behaviour instructions as if
they were terms -- and then the chain correctly reported itself blind, so the
whole queue looked like a blocked searcher when the searcher was fine.

It is the SAME defect `marco_solo()` fixed on 2026-07-26, when 148 characters of
framing travelled to Tavily and brought back the same Peruvian methodology PDF
for four unrelated topics. It came back in through the material queue, written
by hand in another file.

Real effect: 8 of 8 tasks paused blind before, 8 of 8 completed after, 530
characters down to 151.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_research"))

research_lib = pytest.importorskip("research_lib")

TAREA_REAL = (
    "En CHILE (Santiago y alrededores), que productora organizo el evento del "
    "21 DE MARZO 2026 con ADRIATIQUE, COLYN, JOHN CALA en el cartel en CLUB "
    "HIPICO? REGLAS: el evento es en Chile, si lo que encontras es de otro "
    "pais NO sirve. Solo se acepta respuesta con FUENTE VERIFICABLE (URL de la "
    "productora, del recinto, de venta de entradas o de prensa que nombre ese "
    "evento en esa fecha). Los nombres del cartel son DATO DE ENTRADA, no "
    "respuesta: repetirlos no identifica a nadie. Si no hay fuente, responder "
    "exactamente NO SE ENCONTRO."
)


def test_the_real_task_fits_after_the_cut():
    assert len(TAREA_REAL) > research_lib.TOPE_CONSULTA
    c = research_lib.consulta_de(TAREA_REAL)
    assert len(c) <= research_lib.TOPE_CONSULTA


def test_the_rules_do_not_travel_to_the_searcher():
    """They are instructions for the model. An engine matches words."""
    c = research_lib.consulta_de(TAREA_REAL)
    assert "REGLAS" not in c.upper()
    assert "FUENTE VERIFICABLE" not in c.upper()


def test_the_question_survives_whole():
    """Cutting the datum instead of the instruction would lose exactly what
    identifies the event."""
    c = research_lib.consulta_de(TAREA_REAL)
    for dato in ("ADRIATIQUE", "COLYN", "CLUB HIPICO", "21 DE MARZO 2026"):
        assert dato in c, dato


def test_a_short_topic_is_left_exactly_as_it_is():
    """Most topics are short. Touching them would change every measurement
    taken so far for nothing."""
    tema = "reduccion de dano en fiestas electronicas Chile"
    assert research_lib.consulta_de(tema) == tema


def test_no_word_is_cut_in_half():
    """Half a word is a term nobody wrote."""
    tema = "palabra " * 200
    c = research_lib.consulta_de(tema)
    assert len(c) <= research_lib.TOPE_CONSULTA
    assert not c.endswith("pal") and not c.endswith("palab")
    assert c.split()[-1] == "palabra"


def test_a_rules_marker_at_the_very_start_is_not_a_cut_point():
    """A topic that BEGINS with the word would be cut to nothing, and an empty
    query returns everything or nothing -- both useless."""
    c = research_lib.consulta_de("REGLAS: como se escriben las reglas de un juego")
    assert len(c) > 10


def test_empty_stays_empty():
    assert research_lib.consulta_de("") == ""
    assert research_lib.consulta_de(None) == ""


def test_the_shortening_is_announced(monkeypatch):
    """A query silently rewritten is a measurement nobody can reproduce."""
    monkeypatch.setattr(research_lib, "_http_json",
                        lambda *a, **k: {"results": [{"url": "https://x.cl"}]})
    errores = []
    research_lib.web_search(TAREA_REAL, errors=errores)
    assert any("acortada" in e for e in errores)


def test_a_short_query_says_nothing(monkeypatch):
    monkeypatch.setattr(research_lib, "_http_json",
                        lambda *a, **k: {"results": [{"url": "https://x.cl"}]})
    errores = []
    research_lib.web_search("algo corto", errors=errores)
    assert not any("acortada" in e for e in errores)
