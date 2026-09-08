#!/usr/bin/env python3
"""tests/test_mak_grafo_fallback.py -- Tests para _nodo_con_fallback en
cultura/mak_research/grafo.py (unificacion con el fallback de dos fases
de cadena.py:_paso_con_fallback: 1) intenta SOLO el proveedor asignado
al nodo, 2) si ese falla con RuntimeError, reintenta con el resto de
llm.order excluyendo ese proveedor; si tambien falla, propaga).

No network, ollama, ni system deps. Pure logic con un LLM-like stub.
"""
import os
import sys

# Add cultura/mak_research to path for imports (mismo patron que
# tests/test_mak_salud_proveedores.py).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_research"))

import pytest

from grafo import _nodo_con_fallback


class FakeLLM:
    """LLM-like stub: .order fijo, .errors acumula fallos (como research_lib.LLM),
    .call(system, user, max_tok, order=...) registra cada intento en .llamadas
    y responde/falla segun .respuestas (proveedor -> texto | Exception)."""

    def __init__(self, order, respuestas):
        self.order = order
        self.errors = []
        self.llamadas = []  # lista de order tuples pedidos, en orden de llamada
        self.respuestas = respuestas

    def call(self, system, user, max_tok, order=None):
        orden = list(order or self.order)
        self.llamadas.append(tuple(orden))
        last = None
        for name in orden:
            resp = self.respuestas.get(name)
            if isinstance(resp, Exception):
                last = str(resp)
                self.errors.append("%s: %s" % (name, last))
                continue
            if resp:
                return resp, name
        raise RuntimeError(last or "todos los proveedores vacios/fallidos")


class TestNodoConFallback:
    def test_exito_en_primer_intento_solo_prueba_m(self):
        llm = FakeLLM(order=["groq", "cerebras", "azure"],
                      respuestas={"groq": "texto-groq"})
        texto, real = _nodo_con_fallback(llm, "groq", "sys", "ctx", 100)
        assert (texto, real) == ("texto-groq", "groq")
        # Solo se intento [m]; nunca se toco cerebras/azure.
        assert llm.llamadas == [("groq",)]
        assert llm.errors == []

    def test_fallo_reintenta_excluyendo_m_preserva_orden_relativo(self):
        llm = FakeLLM(order=["groq", "cerebras", "azure", "ollama"],
                      respuestas={"groq": RuntimeError("429"),
                                  "azure": "texto-azure"})
        texto, real = _nodo_con_fallback(llm, "groq", "sys", "ctx", 100)
        assert (texto, real) == ("texto-azure", "azure")
        # Primer intento solo groq; segundo intento el resto SIN groq,
        # preservando el orden relativo de llm.order.
        assert llm.llamadas == [("groq",), ("cerebras", "azure", "ollama")]

    def test_ambos_fallan_propaga_runtimeerror(self):
        llm = FakeLLM(order=["groq", "cerebras"],
                      respuestas={"groq": RuntimeError("429"),
                                  "cerebras": RuntimeError("500")})
        with pytest.raises(RuntimeError):
            _nodo_con_fallback(llm, "groq", "sys", "ctx", 100)
        assert llm.llamadas == [("groq",), ("cerebras",)]

    def test_fallback_registra_el_primer_fallo_en_errors(self):
        # El primer intento (solo groq) falla y su error queda en llm.errors
        # ANTES de que el segundo intento (resto) tenga exito -- visible,
        # a diferencia del comportamiento viejo donde el fallo de groq
        # jamas se distinguia porque el primer llm.call() ya probaba todo
        # el resto en un solo intento.
        llm = FakeLLM(order=["groq", "cerebras", "azure"],
                      respuestas={"groq": RuntimeError("429 rate limit"),
                                  "cerebras": "texto-cerebras"})
        texto, real = _nodo_con_fallback(llm, "groq", "sys", "ctx", 100)
        assert (texto, real) == ("texto-cerebras", "cerebras")
        assert len(llm.errors) == 1
        assert "groq" in llm.errors[0]
        assert "429" in llm.errors[0]

    def test_m_no_esta_en_order_agota_resto_sin_excluir_nada_extra(self):
        # Caso limite: m no pertenece a llm.order (no deberia pasar en
        # produccion, pero _nodo_con_fallback no debe romperse) -- el
        # resto es simplemente llm.order completo.
        llm = FakeLLM(order=["cerebras", "azure"],
                      respuestas={"win": RuntimeError("no existe"),
                                  "azure": "texto-azure"})
        texto, real = _nodo_con_fallback(llm, "win", "sys", "ctx", 100)
        assert (texto, real) == ("texto-azure", "azure")
        assert llm.llamadas == [("win",), ("cerebras", "azure")]
