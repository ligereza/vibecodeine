#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Not finding is not the same as not seeing.

Measured on the box 2026-08-01: SearXNG answered HTTP 200 with `results: []`
for 7 of 10 real queries, and the reason was in a field nobody read --
`unresponsive_engines` listed all four general engines down at once (brave and
google cse "Suspended: too many requests", duckduckgo and startpage "CAPTCHA").
There is no TAVILY_API_KEY on that box, so the fallback does not exist either.

`web_search` returned the same empty dict for both facts. Downstream that reads
as "the web says nothing about this topic", and the machinery built on top --
`refutar.py`, which signs its output as adversarially verified -- would write a
report concluding a claim has no sources when in truth nobody looked. A false
"unverifiable" is the same defect class as a false "verified": both assert a
measurement that was never taken.

These tests pin the distinction and the two behaviours that depend on it.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_research"))

research_lib = pytest.importorskip("research_lib")


@pytest.fixture(autouse=True)
def sin_llave(monkeypatch):
    """The box has no Tavily key. Tests must not depend on the machine running
    them having one."""
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)


def _respuesta(monkeypatch, payload):
    monkeypatch.setattr(research_lib, "_http_json",
                        lambda *a, **k: payload)


def test_a_real_result_set_is_not_blind(monkeypatch):
    _respuesta(monkeypatch, {"results": [{"url": "https://x.cl", "title": "t",
                                          "content": "c"}]})
    r = research_lib.searxng_search("algo")
    assert len(r["results"]) == 1
    assert r["ciego"] is False


def test_zero_results_with_every_engine_down_is_blind(monkeypatch):
    """The exact payload the box returns."""
    _respuesta(monkeypatch, {"results": [], "unresponsive_engines": [
        ["brave", "Suspended: too many requests"],
        ["duckduckgo", "CAPTCHA"],
        ["google cse", "Suspended: too many requests"],
        ["startpage", "Suspended: CAPTCHA"]]})
    r = research_lib.searxng_search("algo")
    assert r["results"] == []
    assert r["ciego"] is True
    assert "brave" in r["motivo"] and "CAPTCHA" in r["motivo"]


def test_zero_results_with_every_engine_healthy_is_just_empty(monkeypatch):
    """A search that ran and found nothing is a real answer, and must not be
    reported as a broken searcher -- crying wolf costs the same as silence."""
    _respuesta(monkeypatch, {"results": [], "unresponsive_engines": []})
    r = research_lib.searxng_search("algo que no existe")
    assert r["results"] == []
    assert r["ciego"] is False


def test_a_transport_failure_is_blind_too(monkeypatch):
    def explota(*a, **k):
        raise OSError("connection refused")
    monkeypatch.setattr(research_lib, "_http_json", explota)
    r = research_lib.searxng_search("algo")
    assert r["ciego"] is True
    assert "refused" in r["motivo"]


def test_without_a_fallback_key_the_blindness_survives(monkeypatch):
    """`web_search` cannot quietly turn a blind search into an empty one just
    because it has nowhere else to ask."""
    _respuesta(monkeypatch, {"results": [], "unresponsive_engines": [
        ["brave", "Suspended: too many requests"]]})
    errores = []
    r = research_lib.web_search("algo", errors=errores)
    assert r["ciego"] is True
    assert "TAVILY_API_KEY" in r["motivo"]
    assert any("TAVILY_API_KEY" in e for e in errores), (
        "el motivo tiene que llegar a la lista de errores del job, no solo al "
        "valor de retorno")


def test_the_errors_list_names_the_engines(monkeypatch):
    _respuesta(monkeypatch, {"results": [], "unresponsive_engines": [
        ["duckduckgo", "CAPTCHA"]]})
    errores = []
    research_lib.searxng_search("algo", errors=errores)
    assert any("duckduckgo" in e for e in errores)


def test_health_records_a_blind_search_as_a_failure(monkeypatch):
    """Until now a 200 with zero results registered as a SUCCESS, so the hub's
    health panel showed searxng green while it could not see."""
    visto = {}
    monkeypatch.setattr(research_lib, "_salud_registrar",
                        lambda p, ok, tipo="other", **k: visto.update(
                            {"p": p, "ok": ok, "tipo": tipo}))
    _respuesta(monkeypatch, {"results": [], "unresponsive_engines": [
        ["brave", "Suspended"]]})
    research_lib.searxng_search("algo")
    assert visto == {"p": "searxng", "ok": False, "tipo": "ciego"}


# --------------------------------------------------- what depends on it

def test_refutar_stops_instead_of_signing_an_unsourced_report():
    """`refutar` writes files that carry the weight of "adversarially
    verified". With no sources it must produce NOTHING -- a file in `out/` is
    indistinguishable from a good one for whoever reads it later."""
    fuente = (RAIZ / "cultura" / "mak_research" / "refutar.py").read_text(
        encoding="utf-8")
    assert 'if ciegas and not resultados:' in fuente
    assert 'MURO:' in fuente
    assert 'if result is None:' in fuente and 'return 3' in fuente
    # and the wall happens BEFORE any model is asked to write a thesis
    assert fuente.index("if ciegas and not resultados:") < fuente.index(
        "Proponente (%s) escribe la tesis")


def test_research_pauses_on_a_blind_search():
    """The checkpoint exists for exactly this: wait for the searcher to come
    back instead of spending tokens on air."""
    fuente = (RAIZ / "cultura" / "mak_research" / "research.py").read_text(
        encoding="utf-8")
    assert 'search.get("ciego")' in fuente
    assert 'busqueda ciega' in fuente
