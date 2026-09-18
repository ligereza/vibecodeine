import pytest
from cultura.mak_plataforma.capataz import _extraer_json


def test_json_valido_simple_embebido():
    resultado = _extraer_json('aqui esta: {"a": 1} gracias')
    assert resultado == {"a": 1}


def test_texto_sin_llaves():
    assert _extraer_json("sin llaves") is None


def test_texto_vacio():
    assert _extraer_json("") is None


def test_texto_none():
    assert _extraer_json(None) is None


def test_solo_llave_apertura():
    assert _extraer_json("texto { sin cierre") is None


def test_json_malformado():
    assert _extraer_json("{a: 1,}") is None


def test_json_anidado_primera_apertura_ultima_clausura():
    resultado = _extraer_json('inicio {"a": {"b": 1}} fin')
    assert resultado == {"a": {"b": 1}}


def test_espacios_inicio_fin_no_afectan():
    resultado = _extraer_json('   {"x": 10}   ')
    assert resultado == {"x": 10}
