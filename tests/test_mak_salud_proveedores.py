#!/usr/bin/env python3
"""tests/test_mak_salud_proveedores.py -- Tests para el reordenamiento por
salud de proveedores en cultura/mak_research/research_lib.py (fix: Groq
free-tier 429 envenenando la cabeza de la cadena).

No network, ollama, ni system deps. Pure logic + I/O en tmp_path.
"""
import json
import os
import sys

# Add cultura/mak_research to path for imports (mismo patron que
# tests/test_mak_fallback.py, pero apuntando a mak_research).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_research"))

import pytest

import research_lib
from research_lib import (
    LLM,
    SALUD_VENTANA,
    _salud_cargar,
    _salud_registrar,
    orden_por_salud,
)


# ---------------------------------------------------------------------------
# orden_por_salud (pura, sin I/O)
# ---------------------------------------------------------------------------
class TestOrdenPorSalud:
    def test_demota_proveedor_con_3_fallos_score_0(self):
        stats = {"groq": {"successes": 0, "timeouts": 0, "api_errors": 3, "errors": 0}}
        orden = orden_por_salud(["groq", "cerebras", "azure", "ollama"], stats)
        assert orden == ["cerebras", "azure", "ollama", "groq"]

    def test_no_demota_con_solo_2_intentos(self):
        stats = {"groq": {"successes": 0, "timeouts": 0, "api_errors": 2, "errors": 0}}
        orden = orden_por_salud(["groq", "cerebras", "azure", "ollama"], stats)
        assert orden == ["groq", "cerebras", "azure", "ollama"]

    def test_no_demota_con_score_exactamente_0_5(self):
        # 2 exitos + 2 fallos = 4 intentos, score 0.5 -> estrictamente NO < 0.5
        stats = {"groq": {"successes": 2, "timeouts": 0, "api_errors": 2, "errors": 0}}
        orden = orden_por_salud(["groq", "cerebras", "azure", "ollama"], stats)
        assert orden == ["groq", "cerebras", "azure", "ollama"]

    def test_orden_relativo_estable_entre_demotados_y_no_demotados(self):
        stats = {
            "groq": {"successes": 0, "timeouts": 0, "api_errors": 3, "errors": 0},
            "azure": {"successes": 0, "timeouts": 3, "api_errors": 0, "errors": 0},
        }
        orden = orden_por_salud(["groq", "cerebras", "azure", "ollama", "win"], stats)
        # no-demotados en su orden original: cerebras, ollama, win
        # demotados en su orden original: groq, azure
        assert orden == ["cerebras", "ollama", "win", "groq", "azure"]

    def test_proveedor_ausente_de_stats_nunca_se_demota(self):
        stats = {"groq": {"successes": 0, "timeouts": 0, "api_errors": 3, "errors": 0}}
        orden = orden_por_salud(["groq", "win"], stats)
        assert orden == ["win", "groq"]

    def test_stats_vacio_devuelve_orden_sin_cambios(self):
        orden = orden_por_salud(["groq", "cerebras", "azure"], {})
        assert orden == ["groq", "cerebras", "azure"]

    def test_score_provider_health_none_devuelve_orden_sin_cambios(self, monkeypatch):
        monkeypatch.setattr(research_lib, "score_provider_health", None)
        stats = {"groq": {"successes": 0, "timeouts": 0, "api_errors": 3, "errors": 0}}
        orden = orden_por_salud(["groq", "cerebras", "azure"], stats)
        assert orden == ["groq", "cerebras", "azure"]


# ---------------------------------------------------------------------------
# _salud_registrar / _salud_cargar round-trip
# ---------------------------------------------------------------------------
class TestSaludRoundTrip:
    def test_exito_y_cada_tipo_de_fallo_mapean_al_contador_correcto(self, tmp_path):
        ruta = str(tmp_path / "salud.json")
        t0 = 1000.0
        _salud_registrar("groq", True, ruta=ruta, ahora=t0)
        _salud_registrar("groq", False, "timeout", ruta=ruta, ahora=t0)
        _salud_registrar("groq", False, "api_error", ruta=ruta, ahora=t0)
        _salud_registrar("groq", False, "other", ruta=ruta, ahora=t0)
        _salud_registrar("groq", False, "unknown-tipo", ruta=ruta, ahora=t0)

        proveedores = _salud_cargar(ruta=ruta, ahora=t0)
        contadores = proveedores["groq"]
        assert contadores["successes"] == 1
        assert contadores["timeouts"] == 1
        assert contadores["api_errors"] == 1
        # "other" y cualquier tipo desconocido caen en "errors"
        assert contadores["errors"] == 2

    def test_ventana_expira_y_cargar_devuelve_vacio(self, tmp_path):
        ruta = str(tmp_path / "salud.json")
        t0 = 1000.0
        _salud_registrar("groq", True, ruta=ruta, ahora=t0)
        assert _salud_cargar(ruta=ruta, ahora=t0) != {}
        despues = t0 + SALUD_VENTANA + 1
        assert _salud_cargar(ruta=ruta, ahora=despues) == {}

    def test_ventana_expirada_hace_que_registrar_arranque_de_cero(self, tmp_path):
        ruta = str(tmp_path / "salud.json")
        t0 = 1000.0
        _salud_registrar("groq", False, "api_error", ruta=ruta, ahora=t0)
        despues = t0 + SALUD_VENTANA + 1
        _salud_registrar("cerebras", True, ruta=ruta, ahora=despues)
        proveedores = _salud_cargar(ruta=ruta, ahora=despues)
        assert "groq" not in proveedores
        assert proveedores["cerebras"]["successes"] == 1

    def test_archivo_corrupto_da_vacio_y_registrar_se_recupera(self, tmp_path):
        ruta = str(tmp_path / "salud.json")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("{esto no es json valido")
        assert _salud_cargar(ruta=ruta) == {}
        _salud_registrar("groq", True, ruta=ruta)
        proveedores = _salud_cargar(ruta=ruta)
        assert proveedores["groq"]["successes"] == 1

    def test_archivo_con_forma_invalida_da_vacio(self, tmp_path):
        ruta = str(tmp_path / "salud.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump({"algo": "distinto"}, f)
        assert _salud_cargar(ruta=ruta) == {}

    def test_archivo_faltante_da_vacio(self, tmp_path):
        ruta = str(tmp_path / "no_existe.json")
        assert _salud_cargar(ruta=ruta) == {}


# ---------------------------------------------------------------------------
# Escenario Groq: 3 fallos de api_error empujan a groq al final
# ---------------------------------------------------------------------------
class TestEscenarioGroq:
    def test_groq_429_repetido_se_degrada_al_final(self, tmp_path):
        ruta = str(tmp_path / "salud.json")
        for _ in range(3):
            _salud_registrar("groq", False, "api_error", ruta=ruta)
        stats = _salud_cargar(ruta=ruta)
        orden = orden_por_salud(["groq", "cerebras", "azure", "ollama"], stats)
        assert orden == ["cerebras", "azure", "ollama", "groq"]


# ---------------------------------------------------------------------------
# Integracion: LLM.call() reordena y registra salud a traves del ciclo real
# ---------------------------------------------------------------------------
class TestIntegracionLLMCall:
    def test_call_registra_salud_y_termina_demotando_al_proveedor_fallido(
        self, tmp_path, monkeypatch
    ):
        ruta = str(tmp_path / "salud.json")
        monkeypatch.setattr(research_lib, "SALUD_RUTA", ruta)
        # red_ok() hace sockets reales; forzar True para no reordenar por red.
        monkeypatch.setattr(research_lib, "red_ok", lambda ttl=60: True)

        llm = LLM(order="groq,cerebras")
        llm._has_key = lambda name: True

        llamadas = []

        def _groq_boom(system, user, max_tok):
            llamadas.append("groq")
            raise RuntimeError("boom")

        def _cerebras_ok(system, user, max_tok):
            llamadas.append("cerebras")
            return "respuesta ok"

        llm._groq = _groq_boom
        llm._cerebras = _cerebras_ok

        # Llamada 1 y 2: groq falla, cerebras responde. groq acumula fallos.
        for _ in range(2):
            texto, proveedor = llm.call("sys", "user", 100)
            assert texto == "respuesta ok"
            assert proveedor == "cerebras"

        proveedores = _salud_cargar(ruta=ruta)
        assert proveedores["groq"]["errors"] >= 2 or proveedores["groq"]["api_errors"] >= 2
        assert proveedores["cerebras"]["successes"] == 2

        # Llamada 3: todavia < 3 intentos de groq al INICIO de esta llamada
        # (2 fallos acumulados), asi que groq sigue yendo primero y se
        # invoca (deja el fallo #3 registrado).
        llamadas.clear()
        llm.call("sys", "user", 100)
        assert "groq" in llamadas

        proveedores = _salud_cargar(ruta=ruta)
        total_fallos_groq = (
            proveedores["groq"].get("errors", 0) + proveedores["groq"].get("api_errors", 0)
            + proveedores["groq"].get("timeouts", 0)
        )
        assert total_fallos_groq >= 3

        # Llamada 4: ahora groq tiene >=3 intentos y score 0.0 -> demotado.
        # cerebras se prueba primero y responde -> groq NUNCA se invoca.
        llamadas.clear()
        texto, proveedor = llm.call("sys", "user", 100)
        assert proveedor == "cerebras"
        assert "groq" not in llamadas
        assert llamadas == ["cerebras"]


# ---------------------------------------------------------------------------
# Drift ratchet: mak_research/fallback_util.py debe ser espejo byte-a-byte
# de mak_codex/fallback_util.py (fuente de verdad).
# ---------------------------------------------------------------------------
class TestEspejoFallbackUtil:
    def test_fallback_util_es_espejo_byte_a_byte_de_mak_codex(self):
        base = os.path.join(os.path.dirname(__file__), "..", "cultura")
        ruta_codex = os.path.join(base, "mak_codex", "fallback_util.py")
        ruta_research = os.path.join(base, "mak_research", "fallback_util.py")
        with open(ruta_codex, "rb") as f:
            contenido_codex = f.read()
        with open(ruta_research, "rb") as f:
            contenido_research = f.read()
        assert contenido_codex == contenido_research, (
            "drift detectado: cultura/mak_research/fallback_util.py se "
            "desincronizo de cultura/mak_codex/fallback_util.py (fuente "
            "de verdad); volver a copiar byte a byte"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
