"""Tests de mecanismo_residuo.py -- cosecha del residuo entre RAZONES (semilla (+)4).

(+)4 se usa SOLO como patron abstracto (misma salida, razones inconmensurables). NO
toca el test de bifurcacion de OBRA_01 (vedado). Mismo esqueleto que
test_tilde_residuo.py: tres veredictos + determinismo.
"""

import sys
from pathlib import Path

CULTURA_DIR = Path(__file__).resolve().parents[1] / "projects" / "cultura"
sys.path.insert(0, str(CULTURA_DIR))

from mecanismo_residuo import Veredicto, comparar, render  # noqa: E402


def _v(agente, salida, *razones):
    return Veredicto(agente=agente, salida=salida, razones=list(razones))


def test_salidas_distintas_no_aplica():
    # Sin coincidencia de salida no hay fondo: es desacuerdo comun, no el fenomeno de (+)4.
    c = comparar([
        _v("A", "rama izquierda", "por el motivo uno"),
        _v("B", "rama derecha", "por el motivo dos"),
    ])
    assert c.veredicto == "no_aplica"
    assert not c.es_residuo


def test_misma_salida_alto_solape_es_eco():
    # Misma salida y razones que se solapan -> convergieron tambien en el mecanismo.
    c = comparar([
        _v("A", "misma salida", "preservar el ritmo y la cadencia del verso"),
        _v("B", "misma salida", "preservar el ritmo y la cadencia del verso original"),
    ])
    assert c.veredicto == "eco"
    assert not c.es_residuo
    assert c.solape >= 0.5


def test_misma_salida_bajo_solape_es_mecanismo_residuo():
    # Misma salida, razones que no se solapan -> el residuo real.
    c = comparar([
        _v("A", "lingering after-meal conversation",
           "preservar el registro formal", "mantener la duracion temporal"),
        _v("B", "lingering after-meal conversation",
           "conservar el vinculo ritual social", "la costumbre comunitaria"),
    ])
    assert c.veredicto == "mecanismo_residuo"
    assert c.es_residuo
    assert c.solape < 0.5
    # cada agente aporto razones privadas nombradas (no un diff pelado)
    assert c.privados["A"] and c.privados["B"]


def test_mecanismo_residuo_imprime_las_dos_glosas_incompatibles():
    c = comparar([
        _v("A", "misma salida", "razon alfa distinta"),
        _v("B", "misma salida", "razon beta diferente"),
    ])
    salida = render(c).lower()
    assert c.veredicto == "mecanismo_residuo"
    assert "robustez" in salida
    assert "falso acuerdo" in salida
    assert "no elige" in salida  # el instrumento sostiene ambas, no resuelve


def test_no_devuelve_conteo_de_tokens_como_veredicto():
    # El nucleo heredado de (+)3: el residuo no es un numero; el veredicto es cualitativo.
    salida = render(comparar([
        _v("A", "x igual", "una razon cualquiera"),
        _v("B", "x igual", "otra razon distinta"),
    ])).lower()
    assert "token" not in salida


def test_determinismo():
    args = [
        _v("A", "misma salida", "preservar el registro formal del termino"),
        _v("B", "misma salida", "conservar el vinculo ritual de la mesa"),
    ]
    assert render(comparar(args)) == render(comparar(args))
