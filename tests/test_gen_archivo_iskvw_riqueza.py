import pytest
from tools.gen_archivo_iskvw import _riqueza


def test_vacio_da_cero():
    assert _riqueza({}) == 0


def test_cuatro_campos_presentes_con_valor_real_dan_cuatro():
    p = {
        "fecha": "2023-01-01",
        "resumen": "resumen texto",
        "medio": "email",
        "extra": "extra info"
    }
    assert _riqueza(p) == 4


def test_ninguno_no_cuenta():
    p = {
        "fecha": None,
        "resumen": "resumen texto",
        "medio": "email",
        "extra": "extra info"
    }
    assert _riqueza(p) == 3


def test_cadena_vacia_no_cuenta():
    p = {
        "fecha": "2023-01-01",
        "resumen": "",
        "medio": "email",
        "extra": "extra info"
    }
    assert _riqueza(p) == 3


def test_lista_vacia_no_cuenta():
    p = {
        "fecha": "2023-01-01",
        "resumen": "resumen texto",
        "medio": [],
        "extra": "extra info"
    }
    assert _riqueza(p) == 3


def test_dict_vacio_no_cuenta():
    p = {
        "fecha": "2023-01-01",
        "resumen": "resumen texto",
        "medio": "email",
        "extra": {}
    }
    assert _riqueza(p) == 3


def test_dict_tipo_ninguno_no_cuenta():
    p = {
        "fecha": "2023-01-01",
        "resumen": "resumen texto",
        "medio": {"tipo": "ninguno"},
        "extra": "extra info"
    }
    assert _riqueza(p) == 3


def test_campos_no_relevantes_no_afectan_conteo():
    p = {
        "fecha": "2023-01-01",
        "resumen": "resumen texto",
        "medio": "email",
        "extra": "extra info",
        "otro_campo": "valor",
        "otro_mas": None
    }
    assert _riqueza(p) == 4


def test_valor_falsy_cero_cuenta():
    p = {
        "fecha": 0,
        "resumen": "resumen texto",
        "medio": "email",
        "extra": "extra info"
    }
    assert _riqueza(p) == 4


def test_valor_falsy_false_cuenta():
    p = {
        "fecha": "2023-01-01",
        "resumen": False,
        "medio": "email",
        "extra": "extra info"
    }
    assert _riqueza(p) == 4
