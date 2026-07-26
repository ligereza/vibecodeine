# -*- coding: utf-8 -*-
"""Adding a symbol from the app, not by editing a file.

The user, 2026-07-26, looking at the finished catalogue: "en que parte puede
agregar el icono? donde debe presionar". There was no button -- she had to edit
data/plano_simbolos.json by hand and drop the .svg in a folder. By his own
acceptance criterion that is not "she can add an icon".

These tests exercise the save path the button calls.
"""
from __future__ import annotations

import json

import pytest

from flujo.web.hub import HubRequestHandler
from flujo.plano import iconos

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
       '<path d="M10 10 H190 V190 H10 Z" fill="none" stroke="currentColor"/></svg>')


@pytest.fixture()
def guardar(tmp_path, monkeypatch):
    """Llama al guardado real contra una raiz descartable."""
    (tmp_path / "data" / "plano_simbolos").mkdir(parents=True)
    (tmp_path / "data" / "plano_simbolos.json").write_text(
        json.dumps({"simbolos": []}), encoding="utf-8")
    monkeypatch.setattr("flujo.web.hub.repo_root", lambda: tmp_path)
    iconos.recargar_catalogo(tmp_path)

    handler = HubRequestHandler.__new__(HubRequestHandler)

    def llamar(**datos):
        return handler._guardar_simbolo_plano(datos), tmp_path

    yield llamar
    iconos._RAIZ_FIJA = None
    iconos.recargar_catalogo()


def test_guarda_el_archivo_y_lo_declara(guardar):
    res, raiz = guardar(etiqueta="Punto de hidratación", color="#38bdf8",
                        zona="INFRAESTRUCTURA", svg=SVG)
    assert res["ok"], res
    assert res["id"] == "punto_de_hidratacion"  # id ASCII, usable como archivo

    assert (raiz / "data" / "plano_simbolos" / "punto_de_hidratacion.svg").exists()
    catalogo = json.loads((raiz / "data" / "plano_simbolos.json").read_text(encoding="utf-8"))
    entrada = catalogo["simbolos"][0]
    # La etiqueta se IMPRIME en el plano: el acento tiene que sobrevivir.
    assert entrada["etiqueta"] == "Punto de hidratación"
    assert entrada["zona"] == "INFRAESTRUCTURA"

    # Y queda disponible al instante, sin reiniciar nada.
    assert "punto_de_hidratacion" in iconos.CATALOGO
    assert iconos.ETIQUETAS["punto_de_hidratacion"] == "Punto de hidratación"


def test_se_dibuja_en_el_plano_recien_guardado(guardar):
    guardar(etiqueta="Punto de hidratación", svg=SVG)
    marca = iconos.icono("punto_de_hidratacion", 100, 100, 1.0)
    assert "M10 10 H190 V190 H10 Z" in marca
    assert "currentColor" not in marca


def test_guardar_dos_veces_el_mismo_no_lo_duplica(guardar):
    guardar(etiqueta="Hidratación", svg=SVG)
    res, raiz = guardar(etiqueta="Hidratación", color="#ff0000", svg=SVG)
    assert res["ok"]
    catalogo = json.loads((raiz / "data" / "plano_simbolos.json").read_text(encoding="utf-8"))
    assert len(catalogo["simbolos"]) == 1
    assert catalogo["simbolos"][0]["color"] == "#ff0000"  # gana el ultimo


@pytest.mark.parametrize("datos,esperado", [
    ({"etiqueta": "", "svg": SVG}, "nombre"),
    ({"etiqueta": "Algo", "svg": ""}, "SVG"),
    ({"etiqueta": "Algo", "svg": "esto no es un svg"}, "no es un SVG"),
    ({"etiqueta": "Algo", "svg": "<svg>" + "x" * (600 * 1024) + "</svg>"}, "512 KB"),
])
def test_rechaza_con_un_motivo_legible(guardar, datos, esperado):
    """Quien lo usa no lee logs: un fallo mudo se siente como 'no guarda'."""
    res, _ = guardar(**datos)
    assert not res["ok"]
    assert esperado in res["error"]


def test_zona_invalida_no_rompe_y_cae_en_la_de_por_defecto(guardar):
    res, raiz = guardar(etiqueta="Algo", zona="INVENTADA", svg=SVG)
    assert res["ok"]
    catalogo = json.loads((raiz / "data" / "plano_simbolos.json").read_text(encoding="utf-8"))
    assert catalogo["simbolos"][0]["zona"] == iconos.ZONA_POR_DEFECTO


def test_el_boton_existe_en_la_app():
    """Regresion del pedido: el alta se hace desde la app, no editando un archivo."""
    from pathlib import Path

    panel = (Path(__file__).resolve().parents[1] / "web" / "src" / "components"
             / "PlanoTool.tsx").read_text(encoding="utf-8")
    assert "guardarSimbolo(" in panel, "el panel ya no guarda simbolos"
    assert 'accept=".svg,image/svg+xml"' in panel, "desaparecio el selector de archivo"
