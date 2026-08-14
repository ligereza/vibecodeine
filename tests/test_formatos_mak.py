#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The three things MAK produces now declare what a consumer needs.

All three were OUTPUT formats, not contracts: a ficha whose empty field had no
reason, a report that was prose, and a `.py` where a tested piece and one that
explodes look identical in the directory. Nothing downstream -- a skin, a
button, or an agent that does not know this repo -- could consume any of them
without knowing who produced it.

Measured the same day, and these are the numbers the changes answer to:
`ocr_texto` empty in 76% of 3.138 fichas, `datos_evento` empty in 69%; the last
generated codex piece does `node.name.value` on a `str` and raises on the first
call, while carrying its own unrun asserts.

The functions under test are PURE on purpose: no path, no model, no network.
That is what lets them be tested off the box, and what keeps a change in them
from breaking a live run.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
for sub in ("mak_curatoria", "mak_research", "mak_codex"):
    sys.path.insert(0, str(RAIZ / "cultura" / sub))


# ------------------------------------------------------------------ ficha

percepcion = pytest.importorskip("percepcion")


def test_an_empty_field_now_carries_its_reason():
    """The distinction that did not exist: measured-and-empty vs never tried."""
    nunca = percepcion.estado_medicion(False, "")
    vacio = percepcion.estado_medicion(True, "")
    assert nunca["estado"] == "no_intentado"
    assert vacio["estado"] == "vacio"
    assert nunca["estado"] != vacio["estado"], (
        "an untried measurement must not look like an empty result")


def test_a_measurement_that_blew_up_is_neither_empty_nor_untried():
    e = percepcion.estado_medicion(True, "", error="tesseract murio")
    assert e["estado"] == "fallo"
    assert "tesseract" in e["detalle"]


def test_a_real_value_is_measured_and_says_how_much():
    e = percepcion.estado_medicion(True, "Citrato de Magnesio")
    assert e["estado"] == "medido"
    assert e["detalle"] == "19"


@pytest.mark.parametrize("valor", ["", "   ", None, [], {}])
def test_every_shape_of_empty_reads_as_empty(valor):
    """`""`, `[]` and `{}` were all being written as 'there is nothing here'."""
    assert percepcion.estado_medicion(True, valor)["estado"] == "vacio"


def test_the_file_type_decides_what_was_even_attempted():
    """`otro` runs no measurement at all: for those fichas every field is
    `no_intentado`, and that is the honest answer, not an empty one."""
    assert percepcion.APLICA["otro"] == ()
    assert "ocr" in percepcion.APLICA["imagen"]
    # a video is never OCR'd -- claiming its empty ocr means "no text" would be
    # asserting something nobody looked for
    assert "ocr" not in percepcion.APLICA["video"]


# ---------------------------------------------------------------- informe

research = pytest.importorskip("research")


def test_findings_become_claims_with_their_source_attached():
    """Prose cannot be consumed. A skin or a button asking 'where does this
    come from' needs the source next to the claim, not inside a markdown."""
    h = research.hallazgos_de([
        {"type": "web_analysis", "iteration": 1, "query": "q",
         "title": "BCN", "url": "https://www.bcn.cl/leychile/navegar?i=1",
         "analysis": {"dice": "algo"}},
    ])
    assert len(h) == 1
    assert h[0]["fuente"].startswith("https://www.bcn.cl")
    assert "algo" in h[0]["contenido"]


def test_a_source_is_marked_primary_only_when_a_domain_says_so():
    """`primaria` is None with no domain: most cultural questions have no
    primary source to demand, and marking them would be an invented charge."""
    findings = [{"type": "web_analysis", "url": "https://www.bcn.cl/leychile/x",
                 "content": "c"},
                {"type": "web_analysis", "url": "https://academia.edu/y",
                 "content": "c"}]
    sin_dominio = research.hallazgos_de(findings)
    assert [x["primaria"] for x in sin_dominio] == [None, None]

    con_dominio = research.hallazgos_de(findings, dominio="cl_legal")
    assert con_dominio[0]["primaria"] is True, "bcn.cl is primary for cl_legal"
    assert con_dominio[1]["primaria"] is False, (
        "academia.edu is not a source on Chilean law -- that confusion is the "
        "most serious defect found in this repo")


def test_never_reviewed_is_not_the_same_as_survived_review():
    """`refutado: null` means NOBODY looked. Collapsing it into False would let
    an unreviewed report read as one that held up."""
    class _LLM:
        stats, order, errors = {}, [], []

    r = research._armar_resultado("tema", "# t\n\ncuerpo", 0.0, [], [], [], _LLM())
    assert r["verificacion"]["refutado"] is None
    assert "hallazgos" in r and "verificacion" in r


# ------------------------------------------------------------------ pieza

# `codex_lib` importa `resource`, que es solo-Unix: en Windows se saltan SOLO
# estos tres tests, no el archivo entero. Un importorskip a nivel de modulo se
# llevaba puestos tambien los de ficha e informe, que si corren en todas partes
# -- y un archivo que se saltea entero es un guardian que no guarda nada.
try:
    import codex_lib
except Exception:                                # noqa: BLE001 - se reporta
    codex_lib = None

sin_codex = pytest.mark.skipif(
    codex_lib is None, reason="codex_lib importa `resource` (solo Unix)")


def _meta():
    return {"codigo_por": "watsonx", "plan_por": "watsonx", "reparado": False,
            "ms": 1200}


@sin_codex
def test_a_piece_that_ran_and_one_that_never_ran_are_distinguishable():
    """The whole point. In `piezas/` both are a `.py` and look identical."""
    corrio = codex_lib.manifiesto_de("x", "print(1)\n",
                                     {"ok": True, "rc": 0}, _meta())
    bloqueada = codex_lib.manifiesto_de(
        "x", "import os\n", {"bloqueado": True, "motivos": ["os.system"], "rc": -1},
        _meta())
    assert corrio["ejecutado"] is True
    assert bloqueada["ejecutado"] is None, (
        "a piece that never ran must not report False -- False means it ran "
        "and failed, and collapsing them makes 'untested' read as 'tested'")
    assert "os.system" in bloqueada["motivo_no_ejecutado"]


@sin_codex
def test_a_piece_that_ran_and_failed_says_so_with_its_stderr():
    m = codex_lib.manifiesto_de(
        "x", "def f(): return 1\n",
        {"ok": False, "rc": 1, "stderr": "AttributeError: 'str' object has no "
                                         "attribute 'value'"}, _meta())
    assert m["ejecutado"] is False
    assert "AttributeError" in m["stderr_cola"]
    assert m["motivo_no_ejecutado"] is None, "it DID run; it just failed"


@sin_codex
def test_the_manifest_carries_the_request_that_produced_it():
    """A piece with no origin cannot be judged: nobody can say whether it did
    what was asked."""
    m = codex_lib.manifiesto_de("listar funciones publicas de un modulo",
                                "x\n", {"ok": True, "rc": 0}, _meta())
    assert m["pedido"] == "listar funciones publicas de un modulo"
    assert m["codigo_por"] == "watsonx"
    assert m["formato"] == "pieza/1"


# ------------------------------------------------- el selector de vision

def test_without_the_env_var_perception_still_uses_ollama():
    """The safety property, pinned. A corpus run must not change engine by
    accident: without PERCEPCION_VISION the behaviour is byte for byte the one
    that produced the 3.138 fichas. This is the guarantee that the watsonx path
    can exist without anybody having to be around to watch it."""
    fuente = (RAIZ / "cultura" / "mak_curatoria" / "percepcion.py").read_text(
        encoding="utf-8")
    assert 'os.environ.get("PERCEPCION_VISION", "ollama")' in fuente, (
        "el default tiene que ser ollama en el propio getenv, no en un if suelto")
    # y la rama de watsonx solo se toma con la variable puesta en watsonx
    assert '.lower() == "watsonx"' in fuente


def test_the_watsonx_vision_path_falls_back_instead_of_dying():
    """The cloud failing must not kill a corpus run: percepcion catches and
    continues to ollama. A run that dies halfway through 3.138 images because
    a token expired is a run nobody can leave unattended."""
    fuente = (RAIZ / "cultura" / "mak_curatoria" / "percepcion.py").read_text(
        encoding="utf-8")
    i = fuente.index('PERCEPCION_VISION')
    fin = fuente.index("\n    payload =", i)
    bloque = fuente[i:fin]
    assert "except Exception" in bloque, "sin captura, la nube tumba la corrida"
    assert "caigo a ollama" in bloque, "y tiene que DECIR que cayo"


def test_the_watsonx_endpoint_lives_in_exactly_one_place():
    """Two copies of the same URL is how `refutar.py` cost an afternoon. This
    counts them, and it already caught the author of this very change adding a
    second one while writing the vision transport."""
    lib = (RAIZ / "cultura" / "mak_research" / "research_lib.py").read_text(
        encoding="utf-8")
    assert lib.count("ml/v1/text/chat") == 1, (
        "el endpoint de watsonx aparece mas de una vez: chat y vision tienen "
        "que compartir _watsonx_llamar")
    for fn in ("def watsonx_chat(", "def watsonx_vision(", "def _watsonx_llamar("):
        assert fn in lib
