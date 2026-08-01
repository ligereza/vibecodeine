#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A report that imitates the SHAPE of a report is not a report.

Measured on 2026-08-01 over the 102 real informes on the box: 36 of them (35%)
carry an unfilled template marker, almost always "**Investigador:** [Tu
Nombre]". The model did not fail at investigating -- it reproduced the template
of an investigation document, author placeholder included, and the file came out
looking finished.

It is the same defect as an HTTP 200 with zero results or a gate that prints
"campos perdidos: 0": something that reads as done and is not. And it is the one
the user named directly when he said the research reports had to be of quality.

The rule here is the repo's: mark, retry once, and if it comes back the same,
say so at the top rather than pretend.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_research"))

research_lib = pytest.importorskip("research_lib")
RESEARCH = (RAIZ / "cultura" / "mak_research" / "research.py").read_text(
    encoding="utf-8")


def test_the_marker_that_appeared_36_times_is_caught():
    assert research_lib.marcadores_de_plantilla(
        "**Investigador:** [Tu Nombre] - Investigador Senior")


def test_a_finished_report_passes_clean():
    assert research_lib.marcadores_de_plantilla(
        "## Resumen\n\nLa productora fue X segun https://ejemplo.cl") == []


def test_it_says_WHICH_marker_it_found():
    """A rejection with no reason sends whoever reads it to guess. This repo
    already paid for that."""
    huecos = research_lib.marcadores_de_plantilla("Fecha: [fecha] y [insertar]")
    assert "[fecha]" in huecos
    assert any(h.startswith("[insertar") for h in huecos)


def test_empty_text_is_not_a_finding():
    assert research_lib.marcadores_de_plantilla("") == []
    assert research_lib.marcadores_de_plantilla(None) == []


def test_a_square_bracket_that_is_not_a_placeholder_does_not_trip_it():
    """Crying wolf costs the same as silence: a citation in brackets is normal
    prose, and flagging it would make the real alarm unbelievable."""
    assert research_lib.marcadores_de_plantilla(
        "Segun el estudio [1], el consumo bajo un 12%.") == []


# ------------------------------------------------------- what research does

def test_research_retries_once_before_giving_up():
    assert "marcadores_de_plantilla(report)" in RESEARCH
    assert "lo pido de" in RESEARCH, "el reintento se anuncia, no es silencioso"


def test_a_report_that_stays_broken_says_so_at_the_top():
    """A reader opening the file has to see it before any claim."""
    i = RESEARCH.index("quedo con plantilla sin rellenar")
    j = RESEARCH.index('resultado = _armar_resultado(')
    assert i < j, "la marca se pone ANTES de armar el resultado"


def test_the_retry_tells_the_model_what_to_do_instead():
    """"Rewrite it" alone gets the same template back. The instruction names
    the actual confusion: there is no author to fill in later."""
    assert "sos vos quien" in RESEARCH
    assert "no con un corchete" in RESEARCH
