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


def test_el_filtro_por_carpeta_manda_sobre_el_tipo():
    """El origen decide antes que el tipo, y la razon no es tecnica.

    Medido el 2026-07-27 con el sitio YA publicado: de 640 obras servidas en
    iskvw.cl solo 208 venian de `posts/`. Habia 141 de `archived_posts/` --
    publicaciones que el usuario archivo, o sea que decidio sacar de su perfil
    -- y 291 de `other/`, que en un export de Instagram no es el feed.
    Publicar lo archivado revierte una decision suya, y eso no lo arregla
    ninguna prueba verde.
    """
    f = G.cargar_filtro()
    assert G.entra_carpeta("posts/123.jpg", f)
    assert not G.entra_carpeta("archived_posts/202009/123.jpg", f)
    assert not G.entra_carpeta("other/123.jpg", f)
    # sin lista, entra todo: el default nunca descarta
    libre = {**f, "carpetas": []}
    for ruta in ("posts/1.jpg", "other/1.jpg", "archived_posts/x/1.jpg", ""):
        assert G.entra_carpeta(ruta, libre), ruta
    # con lista, una obra sin ruta no se puede ubicar y no entra
    assert not G.entra_carpeta("", f)


def test_reels_esta_declarado_aunque_hoy_sume_cero():
    """La percepcion todavia no llego a `reels` (34 archivos sin procesar el
    2026-07-27). Esta declarado igual para que entren SOLOS cuando pase por ahi,
    sin que nadie tenga que acordarse."""
    f = G.cargar_filtro()
    assert G.entra_carpeta("reels/123.mp4", f)


def test_ningun_trazo_publicado_es_de_una_obra_excluida():
    """El ratchet de esto: los SVG viajan al sitio, asi que un trazo de una obra
    filtrada seria material publicado que el filtro dice que no se publica. Ya
    paso: quedaron 441 trazos de obras que el filtro dejaba fuera."""
    import glob
    campo = json.loads((_REPO / "iskvw" / "datos" / "campo.json")
                       .read_text(encoding="utf-8"))
    en_campo = {p["id"].split("-")[0] for p in campo["piezas"]}
    en_disco = {Path(p).stem for p in
                glob.glob(str(_REPO / "iskvw" / "piel" / "trazos" / "*.svg"))}
    # El cero silencioso (memoria de direccion 2.3): si el directorio de trazos
    # se mueve o se renombra, el glob devuelve vacio, `huerfanos` queda vacio y
    # este ratchet informa "todo limpio" para siempre mientras los trazos reales
    # viven sin vigilancia en otra parte. Cero medido es un ERROR, no silencio.
    assert en_campo, "campo.json no declaro ninguna pieza: nada que contrastar"
    assert en_disco, (
        "no se encontro ningun .svg en iskvw/piel/trazos/: el ratchet no midio "
        "nada, que no es lo mismo que estar limpio")
    huerfanos = sorted(en_disco - en_campo)
    assert not huerfanos, (
        "hay trazos publicados de obras que el filtro excluye: "
        + ", ".join(huerfanos[:5]) + f" ({len(huerfanos)} en total)")


def test_el_indice_de_trazos_dice_la_verdad():
    import glob
    idx = json.loads((_REPO / "iskvw" / "piel" / "trazos" / "_indice.json")
                     .read_text(encoding="utf-8"))
    en_disco = {Path(p).stem for p in
                glob.glob(str(_REPO / "iskvw" / "piel" / "trazos" / "*.svg"))}
    assert en_disco, (
        "no se encontro ningun .svg en iskvw/piel/trazos/: comparar dos "
        "conjuntos vacios no prueba que el indice diga la verdad")
    assert set(idx["trazos"]) == en_disco, (
        "el indice y el disco no coinciden: correr "
        "py tools/gen_campo_iskvw.py --indice-trazos iskvw/piel/trazos")
