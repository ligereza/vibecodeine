# -*- coding: utf-8 -*-
"""La posicion como campo del contrato, y el titulo que no miente.

Dos defectos medidos el 2026-07-27 contra el micelio real de la caja, ambos
dentro de `gen_archivo_iskvw.py`:

1. El micelio nombra sus nodos con el archivo completo
   ("<hash>-<mediaid>.md") y el campo usa el stem, asi que las claves nunca
   empalmaban: 1004 piezas, 0 con posicion. Con el arreglo, 697.
2. Lo que MAK percibio de una obra entraba como `titulo`, asi que el contrato
   afirmaba que una obra del artista se llama "Una mujer sentada bajo una
   estructura de madera". Es voz de maquina firmando como autoria -- el mismo
   defecto que la piel tenia con el id de Instagram, un nivel mas abajo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "tools"))

import gen_archivo_iskvw as G  # noqa: E402


def test_el_sufijo_de_archivo_no_es_parte_de_la_identidad():
    """Es lo que rompia el empalme. El id del campo y el del micelio coinciden."""
    assert G._id_pieza("b7fd4e77b4a2-17926032902806396.md") == \
           G._id_pieza("b7fd4e77b4a2-17926032902806396")
    for ext in (".md", ".JSON", ".jpg", ".webp"):
        assert not G._id_pieza("abc-123" + ext).endswith(ext.strip(".").lower())
    # sin extension no se toca nada
    assert G._id_pieza("campo-motor-diagnostico") == "campo-motor-diagnostico"


def test_posiciones_lee_el_campo_del_repo():
    pos, vecindad = G.posiciones()
    assert pos, "campo.json del repo deberia traer posiciones"
    assert isinstance(vecindad, float) and 0 < vecindad <= 1, vecindad
    algun = next(iter(pos.values()))
    assert set(algun) == {"x", "y"}


def test_sin_archivo_de_posiciones_no_se_inventa_nada(tmp_path):
    pos, vecindad = G.posiciones(tmp_path / "no_existe.json")
    assert pos == {} and vecindad is None


def test_la_posicion_es_opcional_pieza_por_pieza(tmp_path):
    """Una pieza sin posicion NO la lleva en cero: un cero seria una posicion
    afirmada sin medir, que es lo que este archivo entero existe para evitar."""
    salida = tmp_path / "archivo.json"
    assert G.main.__module__  # el modulo carga
    sys.argv = ["gen", "--fuente", "obras", "--salida", str(salida)]
    assert G.main() == 0
    d = json.loads(salida.read_text(encoding="utf-8"))
    assert d["meta"]["con_posicion"] == 0, (
        "las piezas de obras.json no estan en el campo, asi que ninguna deberia "
        "traer posicion")
    assert all("posicion" not in p for p in d["piezas"])
    # la metrica de la proyeccion viaja igual, porque describe el campo entero
    assert d["meta"]["vecindad_conservada"] is not None


def test_el_contrato_declara_la_metrica_en_meta_no_en_la_pieza():
    pos, vecindad = G.posiciones()
    assert vecindad is not None
    algun = next(iter(pos.values()))
    assert "vecindad" not in algun, (
        "la vecindad describe la proyeccion entera, no una pieza suelta")
