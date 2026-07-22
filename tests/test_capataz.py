"""Tests para capataz.py -- F1a: LOCAL-first con escalada por riesgo.

capataz.py corre en MAK (fuera de este repo) e importa research_lib/junta
via sys.path a HOME/research y HOME/plataforma; en CI esos modulos no
existen, asi que el propio capataz.py deja LLM=None (try/except en el
import). Los tests monkeypatchean capataz.LLM con un stub que graba el
'order' recibido -- eso es exactamente lo que F1a cambia (quien contesta
primero), sin depender de red ni del box real.
"""
from __future__ import annotations

import pytest

from cultura.mak_plataforma import capataz


# ---------------------------------------------------------------------
# evaluar_riesgo() -- deterministico, 0 LLM
# ---------------------------------------------------------------------

def test_evaluar_riesgo_estado_sano_es_bajo_riesgo():
    estado = {
        "salud_sistema": {"load": 0.2},
        "prs_abiertos": {"total_abiertos": 1, "capataz_abiertos": 1},
        "salud_proveedores": {"cerebras": {"pct_exito": 95.0}},
        "backlog": {},
    }
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is False
    assert razones == []


def test_evaluar_riesgo_estado_no_dict_es_alto_riesgo():
    alto, razones = capataz.evaluar_riesgo(None)
    assert alto is True
    assert razones


def test_evaluar_riesgo_error_de_estado_top_level():
    estado = {"error": "junta.metricas() fallo: boom"}
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is True
    assert any("estado.error" in r for r in razones)


def test_evaluar_riesgo_salud_sistema_con_error():
    estado = {"salud_sistema": {"error": "salud.snapshot() fallo"}}
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is True
    assert any("salud_sistema.error" in r for r in razones)


def test_evaluar_riesgo_prs_abiertos_con_error_gh():
    estado = {"prs_abiertos": {"error": "gh no autenticado"}}
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is True
    assert any("prs_abiertos.error" in r for r in razones)


def test_evaluar_riesgo_backlog_capataz_sobre_umbral():
    estado = {
        "prs_abiertos": {"total_abiertos": 5,
                          "capataz_abiertos": capataz.UMBRAL_PRS_CAPATAZ_RIESGO + 1},
    }
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is True
    assert any("capataz_abiertos" in r for r in razones)


def test_evaluar_riesgo_backlog_capataz_en_umbral_no_escala():
    """Umbral es estricto (> no >=): justo en el umbral sigue siendo bajo riesgo."""
    estado = {
        "prs_abiertos": {"total_abiertos": 3,
                          "capataz_abiertos": capataz.UMBRAL_PRS_CAPATAZ_RIESGO},
    }
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is False
    assert razones == []


def test_evaluar_riesgo_proveedor_con_salud_baja():
    estado = {
        "salud_proveedores": {
            "cerebras": {"pct_exito": 95.0},
            "groq": {"pct_exito": capataz.UMBRAL_PCT_EXITO_PROVEEDOR - 1},
        },
    }
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is True
    assert any("salud_proveedores.groq" in r for r in razones)


def test_evaluar_riesgo_proveedor_sin_dato_pct_exito_no_escala():
    """pct_exito=None (sin intentos todavia) no debe contar como riesgo."""
    estado = {"salud_proveedores": {"cerebras": {"pct_exito": None}}}
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is False
    assert razones == []


def test_evaluar_riesgo_acumula_varias_razones():
    estado = {
        "error": "algo fallo",
        "prs_abiertos": {"capataz_abiertos": 99},
    }
    alto, razones = capataz.evaluar_riesgo(estado)
    assert alto is True
    assert len(razones) == 2


# ---------------------------------------------------------------------
# pedir_decision() -- orden de la cadena depende del riesgo
# ---------------------------------------------------------------------

class _FakeLLM:
    """Stub de research_lib.LLM: no llama red, graba el order con el que
    se lo invoco y devuelve una respuesta fija configurable por test."""

    texto_respuesta = '{"accion": "descansar", "args": {}, "razon": "ok"}'
    proveedor_respuesta = "ollama"
    excepcion = None
    ultimo_order = None
    ultimo_init_order = None

    def __init__(self, order_str):
        _FakeLLM.ultimo_init_order = order_str

    def call(self, system, user, max_tok, order=None):
        _FakeLLM.ultimo_order = list(order) if order is not None else None
        if _FakeLLM.excepcion is not None:
            raise _FakeLLM.excepcion
        return _FakeLLM.texto_respuesta, _FakeLLM.proveedor_respuesta


@pytest.fixture(autouse=True)
def _reset_fake_llm():
    _FakeLLM.texto_respuesta = '{"accion": "descansar", "args": {}, "razon": "ok"}'
    _FakeLLM.proveedor_respuesta = "ollama"
    _FakeLLM.excepcion = None
    _FakeLLM.ultimo_order = None
    _FakeLLM.ultimo_init_order = None
    yield


ESTADO_SANO = {"salud_sistema": {"load": 0.1}, "prs_abiertos": {"capataz_abiertos": 0}}
ESTADO_RIESGOSO = {"error": "junta.metricas() fallo"}


def test_pedir_decision_llm_none_devuelve_motivo_falla(monkeypatch):
    monkeypatch.setattr(capataz, "LLM", None)
    decision, prov, motivo, nivel, escalado, razones = capataz.pedir_decision(ESTADO_SANO)
    assert decision is None
    assert prov is None
    assert motivo == "research_lib.LLM no importable"
    assert nivel is None
    assert escalado is False
    assert razones == []


def test_pedir_decision_riesgo_bajo_ordena_ollama_primero(monkeypatch):
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    capataz.pedir_decision(ESTADO_SANO)
    assert _FakeLLM.ultimo_order == capataz.ORDEN_LOCAL_PRIMERO
    assert _FakeLLM.ultimo_order[0] == "ollama"


def test_pedir_decision_riesgo_alto_ordena_nube_primero(monkeypatch):
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    capataz.pedir_decision(ESTADO_RIESGOSO)
    assert _FakeLLM.ultimo_order == capataz.ORDEN_NUBE_PRIMERO
    assert _FakeLLM.ultimo_order[0] == "cerebras"


def test_pedir_decision_riesgo_bajo_local_responde_no_escala(monkeypatch):
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    _FakeLLM.proveedor_respuesta = "ollama"
    decision, prov, motivo, nivel, escalado, razones = capataz.pedir_decision(ESTADO_SANO)
    assert prov == "ollama"
    assert nivel == "local"
    assert escalado is False
    assert razones == []
    assert decision["accion"] == "descansar"


def test_pedir_decision_riesgo_bajo_pero_cae_a_nube_cuenta_como_escalado(monkeypatch):
    """LOCAL primero en el orden, pero si ollama fallo/vacio dentro de
    LLM.call(), el proveedor real que contesta es de la nube -- eso SI es
    una escalada real aunque evaluar_riesgo() haya dicho riesgo bajo."""
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    _FakeLLM.proveedor_respuesta = "cerebras"
    decision, prov, motivo, nivel, escalado, razones = capataz.pedir_decision(ESTADO_SANO)
    assert prov == "cerebras"
    assert nivel == "cloud"
    assert escalado is True


def test_pedir_decision_riesgo_alto_siempre_escalado(monkeypatch):
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    _FakeLLM.proveedor_respuesta = "cerebras"
    decision, prov, motivo, nivel, escalado, razones = capataz.pedir_decision(ESTADO_RIESGOSO)
    assert nivel == "cloud"
    assert escalado is True
    assert razones


def test_pedir_decision_cadena_caida_propaga_motivo_y_riesgo(monkeypatch):
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    _FakeLLM.excepcion = RuntimeError("Todos los proveedores LLM fallaron")
    decision, prov, motivo, nivel, escalado, razones = capataz.pedir_decision(ESTADO_RIESGOSO)
    assert decision is None
    assert prov is None
    assert "cerebro caido" in motivo
    assert nivel is None
    assert escalado is True  # ESTADO_RIESGOSO -> alto_riesgo True se preserva


def test_pedir_decision_respuesta_no_parseable(monkeypatch):
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    _FakeLLM.texto_respuesta = "esto no es json"
    decision, prov, motivo, nivel, escalado, razones = capataz.pedir_decision(ESTADO_SANO)
    assert decision["accion"] is None
    assert "no parseable" in decision["razon"]
    assert prov == "ollama"
    assert nivel == "local"


def test_pedir_decision_usa_cadena_completa_como_init(monkeypatch):
    """LLM(...) siempre se instancia con la cadena completa (red de
    seguridad); es el 'order' de la llamada el que cambia por riesgo."""
    monkeypatch.setattr(capataz, "LLM", _FakeLLM)
    capataz.pedir_decision(ESTADO_SANO)
    assert _FakeLLM.ultimo_init_order == capataz.CADENA_COMPLETA


# ---------------------------------------------------------------------
# ciclo() -- la bitacora queda con decisor_nivel/escalado/razones_riesgo
# ---------------------------------------------------------------------

def test_ciclo_loguea_decisor_nivel_y_escalado(monkeypatch):
    monkeypatch.setattr(capataz, "gather_state", lambda: dict(ESTADO_SANO))
    monkeypatch.setattr(
        capataz, "pedir_decision",
        lambda estado: ({"accion": "descansar", "args": {}, "razon": "nada pendiente"},
                         "ollama", None, "local", False, []),
    )
    monkeypatch.setattr(capataz, "ejecutar", lambda accion, args: {"ok": True})
    logged = {}
    monkeypatch.setattr(capataz, "log_bitacora", lambda entry: logged.update(entry))

    entry = capataz.ciclo()

    assert entry["decisor_nivel"] == "local"
    assert entry["escalado"] is False
    assert entry["razones_riesgo"] == []
    assert entry["accion"] == "descansar"
    assert entry["fallback_usado"] is False
    assert logged["decisor_nivel"] == "local"


def test_ciclo_riesgo_alto_escalado_queda_en_bitacora(monkeypatch):
    monkeypatch.setattr(capataz, "gather_state", lambda: dict(ESTADO_RIESGOSO))
    monkeypatch.setattr(
        capataz, "pedir_decision",
        lambda estado: ({"accion": "vetear", "args": {}, "razon": "estado con error"},
                         "cerebras", None, "cloud", True,
                         ["estado.error: junta.metricas() fallo"]),
    )
    monkeypatch.setattr(capataz, "ejecutar", lambda accion, args: {"ok": True})
    logged = {}
    monkeypatch.setattr(capataz, "log_bitacora", lambda entry: logged.update(entry))

    entry = capataz.ciclo()

    assert entry["decisor_nivel"] == "cloud"
    assert entry["escalado"] is True
    assert entry["razones_riesgo"] == ["estado.error: junta.metricas() fallo"]


def test_ciclo_cadena_caida_decisor_nivel_none_no_rompe_fallback(monkeypatch):
    """Fallback seguro (vetear) sigue funcionando cuando pedir_decision no
    pudo contestar -- el gap real que F0/F1a documentan: no hay como
    verificar desde este repo la tasa de exito de ollama respondiendo
    primero contra bitacora real, asi que este test solo fija que el
    camino de fallo sigue cayendo a 'vetear' bajo el nuevo retorno de
    6-tupla, no que el routing local-first sea infalible."""
    monkeypatch.setattr(capataz, "gather_state", lambda: dict(ESTADO_SANO))
    monkeypatch.setattr(
        capataz, "pedir_decision",
        lambda estado: (None, None, "cerebro caido: timeout", None, False, []),
    )
    ejecutado = {}

    def _fake_ejecutar(accion, args):
        ejecutado["accion"] = accion
        return {"ok": True, "rc": 0}

    monkeypatch.setattr(capataz, "ejecutar", _fake_ejecutar)
    logged = {}
    monkeypatch.setattr(capataz, "log_bitacora", lambda entry: logged.update(entry))

    entry = capataz.ciclo()

    assert entry["accion"] == "vetear"
    assert entry["fallback_usado"] is True
    assert entry["decisor_nivel"] is None
    assert ejecutado["accion"] == "vetear"


def test_ciclo_accion_invalida_del_modelo_cae_a_vetear_y_conserva_decisor_nivel(monkeypatch):
    """Si el modelo (local o nube) alucina una accion fuera del menu,
    validar() fuerza vetear, pero decisor_nivel/escalado de ESA respuesta
    real deben quedar en la bitacora (para poder correlacionar 'quien
    alucino' con metricas_capataz.py)."""
    monkeypatch.setattr(capataz, "gather_state", lambda: dict(ESTADO_SANO))
    monkeypatch.setattr(
        capataz, "pedir_decision",
        lambda estado: ({"accion": "borrar_todo", "args": {}, "razon": "??"},
                         "ollama", None, "local", False, []),
    )
    monkeypatch.setattr(capataz, "ejecutar", lambda accion, args: {"ok": True})
    logged = {}
    monkeypatch.setattr(capataz, "log_bitacora", lambda entry: logged.update(entry))

    entry = capataz.ciclo()

    assert entry["accion"] == "vetear"
    assert entry["fallback_usado"] is True
    assert entry["decisor_nivel"] == "local"
    assert "borrar_todo" in entry["razon"]
