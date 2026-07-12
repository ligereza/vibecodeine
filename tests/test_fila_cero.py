"""Tests del libro mayor de contagio (projects/cultura/fila_cero.py).

Semilla (+)1: el que escribio no puede ser contagiado por lo que escribio. La
asimetria de acceso es el motor -- se testea que la Fila Cero (autor sobre su
propia rama) sea inconstruible con antes != despues, que un delta ajeno reporte
"causa NO verificada", y que la demo produzca una tabla estable.
"""

import sys
from pathlib import Path

import pytest

CULTURA_DIR = Path(__file__).resolve().parents[1] / "projects" / "cultura"
sys.path.insert(0, str(CULTURA_DIR))

from fila_cero import (  # noqa: E402
    LibroMayor,
    Lectura,
    Rama,
    _demo,
    render,
)


def test_autoletura_del_autor_con_delta_es_inconstruible():
    # (a) El motor de (+)1: intentar declarar un movimiento del autor sobre su
    # propia rama (antes != postura) levanta ValueError. La inmunidad es
    # estructural, no un filtro posterior.
    rama = Rama(id="rama_A", autor_id="autor_01", postura="Duda")
    with pytest.raises(ValueError):
        Lectura.registrar(rama, "autor_01", antes="neutral", despues="Duda")
    with pytest.raises(ValueError):
        Lectura.registrar(rama, "autor_01", antes="Duda", despues="Paranoia")


def test_fila_cero_se_deriva_congelada():
    # El autor sin argumentos: antes==despues==postura, derivado, delta False.
    rama = Rama(id="rama_B", autor_id="autor_01", postura="Duda")
    lec = Lectura.registrar(rama, "autor_01")
    assert lec.es_autor is True
    assert lec.antes == lec.despues == "Duda"
    assert lec.delta is False


def test_lector_ajeno_con_delta_reporta_causa_no_verificada():
    # (b) Un delta ajeno se renderiza con la nota Tilde exacta.
    libro = LibroMayor()
    libro.agregar_rama(Rama(id="rama_A", autor_id="autor_01", postura="Paranoia"))
    libro.leer("rama_A", "lector_gamma", antes="neutral", despues="Paranoia")
    salida = render(libro)
    assert "causa NO verificada" in salida
    assert "lector_gamma" in salida


def test_lector_ajeno_exige_antes_y_despues():
    # El ajeno debe declarar su propio antes/despues; no se infieren.
    rama = Rama(id="rama_A", autor_id="autor_01", postura="Paranoia")
    with pytest.raises(ValueError):
        Lectura.registrar(rama, "lector_gamma", antes="neutral")


def test_bifurcacion_no_se_resuelve():
    # Psicosis: la salida sostiene las dos lecturas incompatibles sin elegir.
    salida = render(_demo()).lower()
    assert "soberania" in salida
    assert "punto ciego" in salida
    assert "las dos lecturas se sostienen" in salida


def test_demo_produce_tabla_estable():
    # (c) El escenario de demo corre y produce una tabla estable y deterministica.
    salida_1 = render(_demo())
    salida_2 = render(_demo())
    assert salida_1 == salida_2
    # La Fila Cero del autor esta presente y congelada (delta 'no').
    lineas = salida_1.splitlines()
    filas_autor = [ln for ln in lineas if ln.startswith("rama_") and "autor_01" in ln]
    assert len(filas_autor) == 2
    for fila in filas_autor:
        assert fila.rstrip().endswith("no")  # el autor nunca muestra delta
    # Encabezado estable.
    assert lineas[0].split()[:5] == ["RAMA", "LECTOR", "ANTES", "DESPUES", "DELTA"]


def test_no_perfila_terceros_solo_postura_propia():
    # Limite duro psicosis: el modelo solo guarda la postura que el lector declara
    # sobre si mismo. No hay campo para inferir ni para hablar de un tercero.
    campos = set(Lectura.__dataclass_fields__.keys())
    assert campos == {"rama_id", "lector_id", "autor_id", "antes", "despues", "es_autor"}
