# -*- coding: utf-8 -*-
"""El filtro del campo de iskvw: configuracion, no una puerta que espera.

Por que existe este test (2026-07-27). El tramo anterior cerro pidiendole al
usuario que decidiera cuales de las 697 obras del archivo eran obra, y su
correccion fue de una linea: el objetivo era que el sistema TRAGUE lo que le
llegue y que el criterio sea configuracion. Lo que se protege aca es
exactamente eso -- que el default entre en TODO y que nadie tenga que decidir
nada para que el generador funcione.

Prueba comportamiento real del modulo, no un mock: si `gen_campo_iskvw` cambia
la forma del filtro, esto se cae.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "tools"))

import gen_campo_iskvw as G  # noqa: E402


def test_el_archivo_del_repo_entra_en_todo():
    """El default que viaja en el repo no descarta nada. Es la regla."""
    f = G.cargar_filtro()
    assert f["incluir"] == [], "'incluir' con contenido = alguien decidio por el usuario"
    assert f["excluir"] == []
    assert f["sin_clasificar"] == "incluir"
    for tipo in ("obra", "tatuaje", "foto_evento", "logo", "flyer_evento", ""):
        assert G.entra(G.normalizar(tipo, f["sinonimos"]), f), tipo


def test_sin_archivo_entra_en_todo_y_avisa(tmp_path, capsys):
    """Falta el archivo: se entra en todo y se dice. Nunca en silencio."""
    f = G.cargar_filtro(tmp_path / "no_existe.json")
    assert G.entra("obra", f) and G.entra("", f)
    assert "entra TODO" in capsys.readouterr().err


def test_sinonimos_juntan_lo_que_la_percepcion_vieja_partio():
    """Medido el 2026-07-27: tatuaje(42) y tattoo(16) eran el mismo tipo."""
    f = G.cargar_filtro()
    s = f["sinonimos"]
    assert G.normalizar("Tattoo", s) == "tatuaje"
    assert G.normalizar("obras", s) == "obra"
    assert G.normalizar("obra", s) == "obra"
    # 'incluir' pedido en un sinonimo alcanza a las dos escrituras
    solo = {**f, "incluir": ["tattoo"]}
    assert G.entra(G.normalizar("tatuaje", s), solo)
    assert not G.entra(G.normalizar("obra", s), solo)


def test_incluir_restringe_y_excluir_saca(tmp_path):
    escrito = {"incluir": ["obra"], "excluir": [], "sin_clasificar": "incluir",
               "sinonimos": {}}
    p = tmp_path / "f.json"
    p.write_text(json.dumps(escrito), encoding="utf-8")
    f = G.cargar_filtro(p)
    assert G.entra("obra", f)
    assert not G.entra("logo", f)
    # sin tipo sigue entrando: 'incluir' habla de tipos, no de los sin tipo
    assert G.entra("", f)

    escrito["incluir"], escrito["excluir"] = [], ["logo"]
    p.write_text(json.dumps(escrito), encoding="utf-8")
    f = G.cargar_filtro(p)
    assert G.entra("obra", f) and not G.entra("logo", f)


def test_sin_clasificar_es_una_decision_explicita(tmp_path):
    """Un cuarto del archivo no tiene tipo: sacarlo se pide, no se asume."""
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"sin_clasificar": "excluir"}), encoding="utf-8")
    f = G.cargar_filtro(p)
    assert not G.entra("", f)
    assert G.entra("obra", f), "excluir los sin tipo no toca a los que si tienen"


def test_un_filtro_roto_no_decide_en_silencio(tmp_path, capsys):
    p = tmp_path / "roto.json"
    p.write_text("{esto no es json", encoding="utf-8")
    f = G.cargar_filtro(p)
    assert G.entra("obra", f) and G.entra("", f)
    assert "entra TODO" in capsys.readouterr().err
