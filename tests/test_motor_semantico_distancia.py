import pytest
from cultura.mak_codex.motor_semantico.algebra import distancia


def test_distancia_identicas_devuelve_cero():
    spec_a = {
        "composicion": "centro",
        "tono": "mayor",
        "capas": [
            {"figura": "circulo", "gesto": "rotar"},
            {"figura": "cuadrado", "gesto": "palpitar"}
        ]
    }
    spec_b = {
        "composicion": "centro",
        "tono": "mayor",
        "capas": [
            {"figura": "circulo", "gesto": "rotar"},
            {"figura": "cuadrado", "gesto": "palpitar"}
        ]
    }
    assert distancia(spec_a, spec_b) == 0


def test_composicion_distinta_suma_uno():
    spec_a = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo", "gesto": "rotar"}]}
    spec_b = {"composicion": "lateral", "tono": "mayor", "capas": [{"figura": "circulo", "gesto": "rotar"}]}
    assert distancia(spec_a, spec_b) == 1


def test_tono_distinto_suma_uno():
    spec_a = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo", "gesto": "rotar"}]}
    spec_b = {"composicion": "centro", "tono": "menor", "capas": [{"figura": "circulo", "gesto": "rotar"}]}
    assert distancia(spec_a, spec_b) == 1


def test_capas_distinto_largo_suma_diferencia():
    spec_a = {
        "composicion": "centro", "tono": "mayor",
        "capas": [{"figura": "circulo", "gesto": "rotar"}, {"figura": "cuadrado", "gesto": "palpitar"}]
    }
    spec_b = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo", "gesto": "rotar"}]}
    assert distancia(spec_a, spec_b) == 1


def test_gesto_faltante_usa_default_quieto():
    spec_a = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo"}]}
    spec_b = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo", "gesto": "quieto"}]}
    assert distancia(spec_a, spec_b) == 0


def test_gesto_faltante_compara_con_default_y_suma_si_distinto():
    spec_a = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo"}]}
    spec_b = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo", "gesto": "rotar"}]}
    assert distancia(spec_a, spec_b) == 1


def test_figura_distinta_en_capa_suma_uno():
    spec_a = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "circulo", "gesto": "rotar"}]}
    spec_b = {"composicion": "centro", "tono": "mayor", "capas": [{"figura": "triangulo", "gesto": "rotar"}]}
    assert distancia(spec_a, spec_b) == 1
