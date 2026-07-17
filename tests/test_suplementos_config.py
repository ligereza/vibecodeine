"""
Tests de src/flujo/comercial/suplementos_config.py -- seleccion de contenido de
suplemento para las piezas. Gap #5. Fija el match case-insensitive y el
KeyError (no un fallback silencioso con dosis vacia) cuando no existe.
"""
from __future__ import annotations

import pytest

from flujo.comercial.suplementos_config import (
    SUPLEMENTOS,
    Suplemento,
    get_suplemento,
    list_suplementos,
)


def test_get_suplemento_case_insensitive():
    a = get_suplemento("Impulso")
    b = get_suplemento("impulso")
    c = get_suplemento("IMPULSO")
    assert a is b is c
    assert isinstance(a, Suplemento)


def test_get_suplemento_devuelve_datos_reales():
    s = get_suplemento("Creatina")
    assert s.nombre
    assert s.descripcion
    assert s.info_nutricional          # una pieza sin info nutricional es un error


def test_get_suplemento_desconocido_lanza_keyerror():
    """No hay fallback silencioso: un suplemento inexistente falla fuerte, no
    devuelve una pieza con dosis/beneficios vacios."""
    with pytest.raises(KeyError, match="no encontrado"):
        get_suplemento("SustanciaQueNoExiste-xyz")


def test_list_suplementos_incluye_los_builtin():
    nombres = list_suplementos()
    assert set(SUPLEMENTOS.keys()) <= set(nombres)
