"""Tests de MARCA SIN PRECIO (projects/cultura/marca_sin_precio.py).

Semilla (+)5: el costo de significado del residuo NO cruza a codigo. La pieza pone
el juicio curado (a mano) y un proxy mecanico lado a lado, en dos lentes de
vocabulario, y se NIEGA a fusionarlos. Estos tests fijan esa negativa, la identidad
de datos entre lentes, el determinismo del proxy, y un guarda contra el
operational-overreach (moneda / imports del flujo de cotizacion).
"""

import re
import sys
from pathlib import Path

import pytest

CULTURA_DIR = Path(__file__).resolve().parents[1] / "projects" / "cultura"
MODULO = CULTURA_DIR / "marca_sin_precio.py"
sys.path.insert(0, str(CULTURA_DIR))

from marca_sin_precio import (  # noqa: E402
    CostoNoTraducible,
    Entrada,
    filas_de_datos,
    proxy_mecanico,
    render,
    tabla,
    tasar_por_ley,
    _self_check,
)
from tilde_residuo import _COSTO_POR_CHAR  # noqa: E402


def test_tasar_por_ley_se_niega():
    # El nucleo de (+)5 hecho codigo: fusionar juicio curado + proxy no cruza.
    e = tabla()[0]
    with pytest.raises(CostoNoTraducible):
        tasar_por_ley(e)


def test_los_dos_lentes_tienen_los_mismos_datos():
    # La bifurcacion (Psicosis) vive en los MISMOS datos: solo cambia el vocabulario.
    filas = tabla()
    ling = render(filas, "linguistico")
    marca = render(filas, "marca")
    # Las lineas de datos son identicas byte a byte.
    assert filas_de_datos(ling) == filas_de_datos(marca)
    # Pero el render completo difiere: los encabezados cambian.
    assert ling != marca
    # Y concretamente el titulo/columnas difieren.
    assert "lente linguistico" in ling and "lente marca" in marca


def test_self_check_pasa():
    # Condicion Omega11 secundaria (estructural): el reencuadre no agrega contenido.
    _self_check()  # no debe levantar


def test_proxy_es_determinista():
    assert proxy_mecanico("ñ") == proxy_mecanico("ñ")
    assert tabla() == tabla()  # Entrada es frozen dataclass -> comparables por valor


def test_proxy_es_formal_no_semantico():
    # El proxy es distancia de codepoint: ord del caracter menos ord de su plegado.
    # 'n con virgulilla' (U+00F1=241) -> 'n' (110) = 131. Es formal, no mide el dolor.
    assert proxy_mecanico("ñ") == abs(0x00F1 - ord("n"))
    # Aperturas: el plegado las borra -> destino en la posicion nula (0).
    assert proxy_mecanico("¿") == 0x00BF


def test_tabla_reusa_la_tabla_curada_sin_reescribir():
    # El costo curado se importa tal cual de _COSTO_POR_CHAR; no se re-escribe.
    for e in tabla():
        assert isinstance(e, Entrada)
        assert e.costo_curado == _COSTO_POR_CHAR[e.marca]


def test_guarda_sin_moneda_ni_flujo_de_cotizacion():
    # Operational-overreach = violacion de limite duro. El lente "marca" es SOLO
    # vocabulario: nunca una cifra monetaria, nunca cableado al flujo de cotizacion.
    fuente = MODULO.read_text(encoding="utf-8")

    # (a) ningun simbolo de moneda en ninguna parte del modulo.
    simbolos_moneda = ["$", "€", "£", "¥", "¢"]  # $ EUR GBP JPY cent
    for sig in simbolos_moneda:
        assert sig not in fuente, f"simbolo de moneda prohibido en el modulo: {sig!r}"
    for codigo in ["USD", "EUR", "GBP"]:
        assert not re.search(rf"\b{codigo}\b", fuente), f"codigo de moneda prohibido: {codigo}"

    # (b) ninguna LINEA de import cablea el flujo comercial de cotizacion.
    tokens_operativos = ["cotiz", "paquete", "brief", "suplement", "resolume", "eventos"]
    for linea in fuente.splitlines():
        s = linea.strip()
        if s.startswith("import ") or s.startswith("from "):
            bajo = s.lower()
            for tok in tokens_operativos:
                assert tok not in bajo, f"import operativo prohibido: {s!r}"


def test_render_nunca_dimensiona_el_proxy_como_dinero():
    # En AMBOS lentes el proxy se rotula como distancia formal, no como dinero.
    filas = tabla()
    for lente in ("linguistico", "marca"):
        salida = render(filas, lente)
        assert "distancia de codepoint" in salida
        for sig in ["$", "€", "£"]:
            assert sig not in salida
