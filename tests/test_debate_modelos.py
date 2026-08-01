#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A debate needs more than one voice, and the report has to say when it had one.

Measured on 2026-07-31: a `refutar` run reported `llm={'watsonx': 3}` -- the
same model played proponent, refuter and judge. That is not an adversarial
pass, it is a monologue with three headings: the refuter argued nuances of its
own thesis instead of whether the fact was true, and the judge agreed with it.
The file that came out was titled "Adversarial" and read as verified.

`LLM.call` already accepted a per-call model and its docstring already said
roles should use DIFFERENT models. Nothing assigned them, so nothing did.

Two things pinned here: the roles get distinct model FAMILIES by default, and
an informe that was not a debate says so in its first lines.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_research"))

research_lib = pytest.importorskip("research_lib")
REFUTAR = (RAIZ / "cultura" / "mak_research" / "refutar.py").read_text(
    encoding="utf-8")


def test_the_three_roles_get_three_different_models():
    m = research_lib.modelos_por_papel("watsonx")
    assert set(m) == {"proponente", "refutador", "juez"}
    assert len(set(m.values())) == 3, (
        "tres papeles con el mismo modelo son un monologo con tres titulos")


def test_they_come_from_different_families():
    """Two checkpoints of the same family argue like the same model. The
    families are mistral / llama / granite, and all three were PROBED against
    the real account on 2026-08-01 -- `mistral-large-2512` answers 404 and was
    left out for that reason, not by taste."""
    familias = {v.split("/")[0] for v in
                research_lib.modelos_por_papel("watsonx").values()}
    assert len(familias) == 3, familias


def test_a_provider_that_cannot_pick_a_model_gets_nothing():
    """Filling it with names that provider ignores would invent a diversity
    that does not exist."""
    assert research_lib.modelos_por_papel("ollama") == {}
    assert research_lib.modelos_por_papel("groq") == {}


def test_what_was_asked_by_hand_always_wins():
    m = research_lib.modelos_por_papel("watsonx", {"juez": "mio/modelo"})
    assert m["juez"] == "mio/modelo"
    assert m["proponente"] != "mio/modelo"


def test_an_empty_request_does_not_erase_the_default():
    """`--modelos ,,` produces empty strings; treating them as a choice would
    silently drop the roster."""
    m = research_lib.modelos_por_papel("watsonx", {"juez": "", "refutador": None})
    assert m["juez"] and m["refutador"]


def test_the_roster_is_probed_not_guessed():
    fuente = (RAIZ / "cultura" / "mak_research" / "research_lib.py").read_text(
        encoding="utf-8")
    assert "MODELOS_POR_PAPEL" in fuente
    assert "404" in fuente, (
        "la razon por la que un modelo quedo fuera se escribe, o el proximo "
        "que lo lea lo vuelve a poner")


# ------------------------------------------------- what the report declares

def test_the_run_records_how_many_models_really_spoke():
    assert '"modelos_distintos"' in REFUTAR
    assert '"es_debate"' in REFUTAR


def test_a_report_that_was_not_a_debate_says_so_first():
    """A document titled "Adversarial" that came out of one model arguing with
    itself is worse than not having it: it reads as verified."""
    assert "NO es un debate" in REFUTAR
    assert REFUTAR.index("NO es un debate") < REFUTAR.index("## Refutaciones")


def test_a_real_debate_names_who_played_each_part():
    assert "Debate entre %d modelos distintos" in REFUTAR
    for papel in ("proponente", "refutador", "juez"):
        assert papel in REFUTAR


def test_the_roles_are_assigned_before_the_thesis_is_written():
    """Assigning them afterwards would leave the proponent on the default and
    the whole point missed."""
    assert REFUTAR.index("modelos = modelos_por_papel(") < REFUTAR.index(
        "escribe la tesis")
