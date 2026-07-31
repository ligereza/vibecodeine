#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The coder chain leads with a machine that answers, and shares one endpoint.

Measured on the box 2026-07-31. The live chain was
`CODER_CHAIN=win,nim-pro,nim-flash,ollama`: `win` FIRST, and `win` is the
notebook the user retired -- probed from the box the same day, it does not
answer. Of the 109 codex jobs in FALLO, 22 read literally `timeout 900s`. The
department that writes code began every job by waiting on a machine that is
off, while `watsonx` -- paid, reachable and measured -- was not even an option
in the map.

The model is chosen by measurement (`tools/watsonx_coder_bench.py`): six
interval-merging cases actually EXECUTED, not eyeballed. Four of five
candidates scored 6/6; the one labelled `granite-8b-code-instruct` scored 5/6,
which is the reason the name of a model is not evidence about it.

These tests read the source rather than importing it: `codex_lib` inserts
`/home/mak/research` into `sys.path` at import time, a path that exists on the
box and nowhere else.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CODEX = (RAIZ / "cultura" / "mak_codex" / "codex_lib.py").read_text(
    encoding="utf-8")
RESEARCH = (RAIZ / "cultura" / "mak_research" / "research_lib.py").read_text(
    encoding="utf-8")


def _bloque(fuente, marcador):
    """El texto entre `marcador` y el primer `]` o `}` que lo cierra."""
    i = fuente.index(marcador)
    fin = min((fuente.index(c, i) for c in "]}" if c in fuente[i:]),
              default=len(fuente))
    return fuente[i:fin + 1]


def test_the_default_chain_leads_with_watsonx():
    """A provider that answers goes first. Anything else is a job that starts
    by waiting."""
    defecto = _bloque(CODEX, "_CODER_CHAIN_DEFAULT = [")
    assert '"wx-llama"' in defecto
    assert defecto.index('"wx-llama"') < defecto.index('"nim-pro"')


def test_the_retired_notebook_is_not_in_the_default_chain():
    """`win` stays in the MAP -- the notebook can come back -- but it is no
    longer the first thing every job waits on."""
    defecto = _bloque(CODEX, "_CODER_CHAIN_DEFAULT = [")
    assert '"win"' not in defecto, "win is back at the head of the queue"
    mapa = _bloque(CODEX, "_CODER_CHAIN_MAP = {")
    assert '"win":' in mapa, "win must remain available by CODER_CHAIN"


def test_every_provider_in_the_map_can_actually_be_called():
    """The dispatch table is derived from the map, so a chain entry cannot name
    a provider the coder has no method for."""
    mapa = _bloque(CODEX, "_CODER_CHAIN_MAP = {")
    proveedores = set()
    for linea in mapa.splitlines():
        if '": ("' in linea:
            proveedores.add(linea.split('": ("')[1].split('"')[0])
    for p in proveedores:
        assert "def _%s(" % p in CODEX, (
            "_CODER_CHAIN_MAP names %r and CoderLLM has no _%s" % (p, p))
    # and the table is not a second hand-written copy
    assert 'fns = {"nim"' not in CODEX
    assert "_CODER_CHAIN_MAP.values()" in CODEX


def test_the_watsonx_endpoint_is_shared_not_reimplemented():
    """One endpoint, one place. A duplicated provider list is exactly what left
    `refutar.py` unable to call the only provider with credentials."""
    assert "def watsonx_chat(" in RESEARCH
    assert "watsonx_chat" in CODEX
    # codex must not carry its own copy of the watsonx URL
    assert "ml/v1/text/chat" not in CODEX
    # and research's method delegates instead of holding a second copy
    assert RESEARCH.count("ml/v1/text/chat") == 1


def test_the_coder_asks_for_a_colder_temperature_than_research():
    """A warm coder invents APIs that do not exist, which is half of what the
    inert-file pile was made of."""
    assert "temperatura=0.1" in CODEX
    assert "temperatura=0.3" in RESEARCH
