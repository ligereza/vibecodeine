import pytest
from cultura.mak_plataforma.cuotas import _aplanar_llmcalls


def test_dict_plano_simple():
    acc = {}
    _aplanar_llmcalls({"groq": 3}, acc)
    assert acc == {"groq": 3}


def test_dict_anidado_suma_modelos():
    acc = {}
    _aplanar_llmcalls({"planner": {"groq": 2}, "coder": {"groq": 1}}, acc)
    assert acc == {"groq": 3}


def test_lista_de_dicts():
    acc = {}
    _aplanar_llmcalls([{"groq": 2}, {"groq": 4}], acc)
    assert acc == {"groq": 6}


def test_acc_con_valores_previos_suma_encima():
    acc = {"groq": 5, "openai": 2}
    _aplanar_llmcalls({"groq": 3}, acc)
    assert acc == {"groq": 8, "openai": 2}


def test_dict_vacio_no_cambia_acc():
    acc = {"groq": 5}
    _aplanar_llmcalls({}, acc)
    assert acc == {"groq": 5}


def test_lista_vacia_no_cambia_acc():
    acc = {"groq": 5}
    _aplanar_llmcalls([], acc)
    assert acc == {"groq": 5}


def test_floats_se_convierten_a_int():
    acc = {}
    _aplanar_llmcalls({"groq": 3.7}, acc)
    assert acc == {"groq": 3}


def test_estructura_mixta_lista_y_dicts_anidados():
    acc = {}
    _aplanar_llmcalls(
        [
            {"planner": {"groq": 1, "openai": 2}},
            {"coder": {"groq": 3}},
            {"groq": 4},
        ],
        acc,
    )
    assert acc == {"groq": 8, "openai": 2}


def test_anidamiento_profundo():
    acc = {}
    _aplanar_llmcalls({"a": {"b": {"c": {"groq": 1}}}}, acc)
    assert acc == {"groq": 1}


def test_multiples_modelos_anidados():
    acc = {}
    _aplanar_llmcalls(
        {"planner": {"groq": 2, "openai": 1}, "coder": {"groq": 3, "anthropic": 1}},
        acc,
    )
    assert acc == {"groq": 5, "openai": 1, "anthropic": 1}
