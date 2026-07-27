# -*- coding: utf-8 -*-
"""Las capas del archivo de iskvw: datos que se suman sin rehacer nada.

La idea es del usuario, y es la del micelio: que esto CREZCA en vez de
rehacerse. Sumar una capa es una entrada en `data/iskvw_capas.json` y una
funcion en el generador -- ni la piel ni la proyeccion se tocan.

Lo que se protege aca es que eso siga siendo cierto y que ninguna capa invente
un dato: si una obra no tiene con que medirse, la clave NO se escribe, porque un
cero fingido es una medicion que nadie hizo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "tools"))

import gen_capas_iskvw as C  # noqa: E402
import tilde_meter  # noqa: E402


def _ctx():
    return {"tilde": tilde_meter, "trazos": _REPO / "iskvw" / "piel" / "trazos"}


def test_toda_capa_declarada_tiene_funcion():
    """Una capa en el manifiesto sin funcion es una promesa que no corre."""
    for c in C.leer_manifiesto():
        assert c["nombre"] in C.CAPAS, c["nombre"]


def test_una_capa_sin_funcion_se_dice(tmp_path):
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"capas": [
        {"nombre": "inventada", "escribe": "x", "para": "algo"}]}),
        encoding="utf-8")
    with pytest.raises(ValueError, match="no tiene"):
        C.leer_manifiesto(p)


def test_una_capa_sin_para_no_entra(tmp_path):
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"capas": [{"nombre": "tilde", "escribe": "t"}]}),
                 encoding="utf-8")
    with pytest.raises(ValueError, match="para"):
        C.leer_manifiesto(p)


def test_tilde_mide_el_residuo_real():
    ctx = _ctx()
    con = C.capa_tilde({"percibido": "Una ilustracion con ñ, á y ¿que?"}, ctx)
    assert con["marcas"] >= 3 and con["por_cien"] > 0
    # sin diacriticos hay texto pero cero residuo: eso NO es "sin dato"
    sin = C.capa_tilde({"percibido": "Tatuaje floral en el antebrazo."}, ctx)
    assert sin is not None and sin["marcas"] == 0


def test_sin_texto_no_hay_dato_inventado():
    ctx = _ctx()
    assert C.capa_tilde({"percibido": ""}, ctx) is None
    assert C.capa_tilde({}, ctx) is None


def test_trazo_mide_el_svg_real():
    ctx = _ctx()
    algun = next(ctx["trazos"].glob("*.svg"))
    d = C.capa_trazo({"id": algun.stem + "-000"}, ctx)
    assert d and d["subtrazos"] > 0 and d["puntos"] > 0
    assert d["bytes"] == algun.stat().st_size


def test_una_obra_sin_trazo_no_escribe_la_clave():
    ctx = _ctx()
    assert C.capa_trazo({"id": "no-existe-este-hash-000"}, ctx) is None


def test_aplicar_borra_lo_que_dejo_de_medirse():
    """Si una obra deja de tener dato, la clave se va. Un dato viejo que
    sobrevive a la medicion que lo produjo es peor que no tenerlo."""
    campo = {"piezas": [
        {"id": "no-existe-000", "percibido": "", "tilde": {"marcas": 99},
         "trazo": {"subtrazos": 5}},
    ]}
    C.aplicar(campo, C.leer_manifiesto(), _ctx())
    assert "tilde" not in campo["piezas"][0]
    assert "trazo" not in campo["piezas"][0]


def test_el_campo_del_repo_lleva_las_capas():
    campo = json.loads((_REPO / "iskvw" / "datos" / "campo.json")
                       .read_text(encoding="utf-8"))
    capas = (campo.get("meta") or {}).get("capas") or {}
    assert capas, "campo.json deberia declarar en meta que capas corrieron"
    con_tilde = sum(1 for p in campo["piezas"] if "tilde" in p)
    con_trazo = sum(1 for p in campo["piezas"] if "trazo" in p)
    assert con_tilde > 500 and con_trazo > 500, (con_tilde, con_trazo)
    # y la cuenta declarada coincide con lo que hay
    assert capas.get("tilde") == con_tilde
    assert capas.get("trazo") == con_trazo
