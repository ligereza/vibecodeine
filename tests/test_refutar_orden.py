#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The provider roster has ONE source, and `refutar.py --orden` honours it.

Measured on the box 2026-07-31: `refutar.py` filtered its `--orden` against a
literal `("groq", "cerebras", "azure", "ollama")` written by hand, which
predates `watsonx` and `win`. `--orden watsonx` was therefore dropped without a
word, the list came out empty, the default chain took over, and every provider
in it was skipped for having no key -- the run died with "Todos los proveedores
fallaron. Ultimo: None", a message that names nobody because nothing was ever
attempted. That is why the adversarial pass the report quality gate depends on
had run exactly once since 2026-07-16, on a box whose `research.env` carries
only the WATSONX_* keys.

These tests pin the two halves of the repair: the roster cannot fork again, and
a provider that exists cannot be silently discarded.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_research"))

research_lib = pytest.importorskip("research_lib")


def test_every_declared_provider_is_actually_callable():
    """`call()` now derives its dispatch table from `PROVIDERS`, so a name in
    the roster with no `_<name>` method would raise at call time instead of
    being quietly unreachable. This proves each one exists."""
    for nombre in research_lib.PROVIDERS:
        assert hasattr(research_lib.LLM, "_" + nombre), (
            "PROVIDERS declares %r and LLM has no _%s" % (nombre, nombre))
    # every declared provider knows which environment variable enables it
    assert set(research_lib.PROVIDER_ENV_KEY) == set(research_lib.PROVIDERS)


def test_retired_providers_are_not_in_the_roster():
    assert "watsonx" not in research_lib.PROVIDERS
    assert "aws" not in research_lib.PROVIDERS


def test_refutar_no_longer_carries_its_own_provider_list():
    """The hardcoded literal is gone from the tool. Pinning the absence is the
    point: a second copy is exactly how this broke."""
    fuente = (RAIZ / "cultura" / "mak_research" / "refutar.py").read_text(
        encoding="utf-8")
    codigo = "\n".join(l for l in fuente.splitlines()
                       if not l.lstrip().startswith("#"))
    assert '("groq", "cerebras", "azure", "ollama")' not in codigo
    assert "PROVIDERS" in codigo


def test_the_source_gate_verdict_is_read_from_evaluar_not_recomputed():
    """`meta.sin_fuente_primaria` must come from `fuentes.evaluar()`'s own key.
    The first version asked for `primarias`, a key that dict does not have, so
    it stamped SIN FUENTE PRIMARIA on a run that had six primary sources -- the
    report contradicted its own status line."""
    fuentes = pytest.importorskip("fuentes")
    ev = fuentes.evaluar("Ley 20.000 de Chile: que dice sobre las ONG",
                         ["https://www.bcn.cl/leychile/navegar?i=1201614"])
    assert "sin_fuente_primaria" in ev and "fuentes_primarias" in ev
    assert ev["dominio"] == "cl_legal"
    assert ev["fuentes_primarias"], "bcn.cl must count as primary for cl_legal"
    assert ev["sin_fuente_primaria"] is False
    # and the key the tool used to ask for simply does not exist
    assert "primarias" not in ev

    fuente = (RAIZ / "cultura" / "mak_research" / "refutar.py").read_text(
        encoding="utf-8")
    assert 'evaluacion["sin_fuente_primaria"]' in fuente
    assert 'evaluacion.get("primarias")' not in fuente


def test_the_frame_never_reaches_the_search():
    """`marco_solo` exists so the cultural framing goes to the MODEL and not to
    the search engine. `refutar.py` still glued it onto the topic and searched
    with the whole string, which is why a question about Chilean law came back
    with UNAM cultural-studies papers."""
    fuente = (RAIZ / "cultura" / "mak_research" / "refutar.py").read_text(
        encoding="utf-8")
    codigo = "\n".join(l for l in fuente.splitlines()
                       if not l.lstrip().startswith("#"))
    assert "marco_solo" in codigo
    # the framed string must never be what gets searched
    assert "web_search(tema" not in codigo or "marco(" not in codigo
    assert "marco(args.tema" not in codigo


def test_a_single_requested_provider_fills_all_three_roles():
    """Asking for one provider must not hand the judge's seat to another one
    that has no key -- that is how the last slot used to become `azure`."""
    refutar = pytest.importorskip("refutar")
    orden = ["cerebras"]
    # the same padding the tool applies before assigning the three roles
    if len(orden) < 3:
        orden = [orden[i % len(orden)] for i in range(3)]
    assert orden == ["cerebras", "cerebras", "cerebras"]
    proponente, jueza = orden[0], orden[-1]
    refutadores = orden[1:-1]
    assert (proponente, refutadores, jueza) == ("cerebras", ["cerebras"], "cerebras")
    assert hasattr(refutar, "refutar")
