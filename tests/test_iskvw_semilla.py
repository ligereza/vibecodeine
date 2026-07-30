# -*- coding: utf-8 -*-
"""La sesion como semilla reproducible: `#semilla=&centro=&escala=`.

PROYECCION.md 6.2 pide que un gesto altere la lectura LOCAL y que una sesion se
comparta como URL, con un criterio que NO es de opinion: misma semilla + mismo
archivo = misma constelacion. Antes de esto el hash era solo un ancla (el id de
una pieza), asi que la lectura a la que alguien llegaba no se podia volver a
abrir ni pasarle a nadie.

Como se mide sin abrir un navegador: las dos funciones viven dentro de
`iskvw/piel/campo/index.html` (el sitio es estatico y no tiene build, asi que no
hay modulo que importar). Se EXTRAEN del archivo real y se evaluan en node con
un `location`, un `E` y unos `NODOS` de mentira. Lo que se prueba es el codigo
que se publica, no una copia: si alguien edita la piel y cambia el contrato de
la semilla, esto se pone rojo.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PIEL = REPO / "iskvw" / "piel" / "campo" / "index.html"

requiere_node = pytest.mark.skipif(shutil.which("node") is None,
                                   reason="node no esta en el PATH")


def _extraer(nombre: str) -> str:
    """El cuerpo de una funcion del HTML, con llaves balanceadas."""
    texto = PIEL.read_text(encoding="utf-8")
    inicio = texto.index("function %s(" % nombre)
    i = texto.index("{", inicio)
    nivel = 0
    for j in range(i, len(texto)):
        if texto[j] == "{":
            nivel += 1
        elif texto[j] == "}":
            nivel -= 1
            if nivel == 0:
                return texto[inicio:j + 1]
    raise AssertionError("no pude aislar %s()" % nombre)


def _correr(hash_: str, nodos: list, largo: int = 10000) -> dict:
    """Aplica la semilla en node y devuelve el estado resultante."""
    guion = """
%s
%s
const location = {hash: %s};
const NODOS = %s;
const LARGO = %d;
const E = {pos: -1, lat: 0, latObj: 0};
aplicarSemilla(leerSemilla());
console.log(JSON.stringify({pos: E.pos, lat: E.lat, latObj: E.latObj,
                            leido: leerSemilla()}));
""" % (_extraer("leerSemilla"), _extraer("aplicarSemilla"),
       json.dumps(hash_), json.dumps(nodos), largo)
    r = subprocess.run(["node", "--input-type=module", "-e", guion],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


NODOS = [{"obra": {"id": "una"}, "y": 100},
         {"obra": {"id": "dos"}, "y": 500},
         {"obra": {"id": "tres"}, "y": 900}]


@requiere_node
def test_la_misma_semilla_da_la_misma_lectura():
    """El criterio de PROYECCION 6.2, medido: dos aplicaciones de la misma
    semilla producen el mismo estado. Sin esto, compartir una URL no comparte
    nada."""
    a = _correr("#semilla=dos&centro=777&escala=0.4", NODOS)
    b = _correr("#semilla=dos&centro=777&escala=0.4", NODOS)
    assert a == b
    assert a["pos"] == 500        # la pieza nombrada manda sobre el centro
    assert a["lat"] == pytest.approx(0.4)


@requiere_node
def test_el_centro_se_usa_cuando_la_pieza_no_existe():
    """Una semilla que nombra algo que ya no esta en el archivo no puede
    inventar un lugar: cae al centro declarado."""
    r = _correr("#semilla=borrada&centro=777&escala=0", NODOS)
    assert r["pos"] == 777


@requiere_node
def test_sin_hash_se_entra_por_la_primera_obra():
    r = _correr("", NODOS)
    assert r["pos"] == 100        # la primera: es como se ve el sitio


@requiere_node
def test_un_enlace_viejo_de_solo_id_sigue_sirviendo():
    """El hash pelado era el contrato anterior. Romperlo seria romper cualquier
    enlace ya compartido."""
    r = _correr("#tres", NODOS)
    assert r["leido"] == {"semilla": "tres"}
    assert r["pos"] == 900


@requiere_node
def test_una_semilla_con_basura_no_afirma_una_posicion():
    """`centro=hola` no es un centro. Un NaN colandose seria una posicion
    afirmada sin dato, que es justo lo que el esquema prohibe."""
    r = _correr("#centro=hola&escala=chau", NODOS)
    assert r["leido"].get("centro") is None
    assert r["leido"].get("escala") is None
    assert r["pos"] == 100        # cae a la primera, no a NaN


@requiere_node
def test_el_centro_queda_dentro_del_campo():
    """Una semilla vieja de un archivo mas grande no puede dejar la lectura
    fuera del campo."""
    assert _correr("#centro=999999", NODOS, largo=10000)["pos"] == 10000
    assert _correr("#centro=-500", NODOS, largo=10000)["pos"] == 0


@requiere_node
def test_la_escala_queda_acotada():
    assert _correr("#centro=100&escala=9", NODOS)["lat"] == 1
    assert _correr("#centro=100&escala=-9", NODOS)["lat"] == -1


def test_la_piel_escribe_la_semilla_al_gesto():
    """El otro lado del contrato: si el gesto no la escribe, la URL nunca
    refleja la lectura y compartirla no sirve. Se mira el archivo publicado."""
    texto = PIEL.read_text(encoding="utf-8")
    assert "function escribirSemilla" in texto
    assert "escribirSemilla()" in texto.split("function escribirSemilla")[0] \
        or "escribirSemilla();" in texto
    # replaceState y no pushState: el boton atras sirve para salir del sitio,
    # no para deshacer un scroll.
    assert "history.replaceState" in texto
    assert "history.pushState" not in texto


def test_la_piel_pide_el_sustrato_y_degrada():
    """La piel pide archivo.json (piezas + vinculos) y, si no esta, sigue
    exactamente como antes. Hoy no se publica, asi que el camino vivo es el
    respaldo: la degradacion es el camino normal, no el excepcional."""
    texto = PIEL.read_text(encoding="utf-8")
    assert "datos/archivo.json" in texto
    assert "datos/campo.json" in texto
    assert "datos/obras.json" in texto
    assert "function delContrato" in texto
    # el dato existe antes de que se decida como se ve
    assert "let VINCULOS" in texto
