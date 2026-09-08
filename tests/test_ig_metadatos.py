#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reading the artist's own words without touching anything that is not his work.

The Instagram export is one folder with two very different things in it: the
artist's published work, which is a PRODUCT, and private messages, likes and
story interactions, which are personal data. The repository privacy rule,
2026-07-31, the user's own correction): new input carrying personal data does
not enter; what is already a product can be reviewed.

So the reader is scoped by NAME, not by care. And the second half is the
encoding: Instagram writes UTF-8 bytes and the export decodes them as latin-1,
so "coleccion" arrives as "colecciA3n" and every emoji is garbage. Passing that
through would put the exact defect class of "reduciendo ano" into text the
artist shows people.
"""
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))

meta = pytest.importorskip("ig_metadatos")


# ------------------------------------------------------------- the encoding

def test_the_latin1_round_trip_recovers_the_accents():
    texto, sospechoso = meta.reparar("colecciÃ³n de animaciÃ³n")
    assert texto == "colección de animación"
    assert sospechoso is False


def test_text_that_was_already_fine_is_not_broken():
    """Repairing an already-correct string mangles it, and here that reaches a
    product. The version with FEWER mojibake marks wins."""
    texto, sospechoso = meta.reparar("colección de animación")
    assert texto == "colección de animación"
    assert sospechoso is False


def test_what_could_not_be_recovered_is_declared_suspect():
    texto, sospechoso = meta.reparar("algo � roto")
    assert sospechoso is True, (
        "un texto que sigue roto tiene que decirlo, no verse bien y no estarlo")


def test_empty_is_empty():
    assert meta.reparar("") == ("", False)


# ------------------------------------------------------------- the boundary

def test_a_path_through_personal_data_is_refused(tmp_path):
    ruta = tmp_path / "messages" / "media"
    ruta.mkdir(parents=True)
    with pytest.raises(SystemExit) as e:
        meta.leer_export(ruta)
    assert "datos personales" in str(e.value)


def test_only_the_artists_own_content_files_are_read():
    """A list written by hand here is the defect this repo keeps paying for --
    so what is pinned is the OPPOSITE side: nothing outside the artist's own
    published content may appear in it."""
    assert "messages.json" not in meta.ARCHIVOS
    assert "liked_posts.json" not in meta.ARCHIVOS
    assert "stories.json" not in meta.ARCHIVOS, (
        "las historias son efimeras y no son obra publicada")
    assert set(meta.PROHIBIDAS) >= {"messages", "likes", "story_interactions"}


# ------------------------------------------------------------- the mapping

def _export(tmp_path, archivos: dict):
    base = tmp_path / "info" / "your_instagram_activity" / "media"
    base.mkdir(parents=True)
    for nombre, dato in archivos.items():
        (base / nombre).write_text(json.dumps(dato, ensure_ascii=False),
                                   encoding="utf-8")
    return tmp_path


def test_a_post_title_reaches_every_media_of_the_carousel(tmp_path):
    raiz = _export(tmp_path, {"posts_1.json": [{
        "creation_timestamp": 1600000000,
        "title": "Serie de grabados",
        "media": [{"uri": "media/posts/a.jpg"}, {"uri": "media/posts/b.jpg"}],
    }]})
    mapa, _ = meta.leer_export(raiz)
    assert mapa["a.jpg"]["texto"] == "Serie de grabados"
    assert mapa["b.jpg"]["hereda_del_post"] is True
    assert mapa["a.jpg"]["fecha"] == "2020-09-13"
    assert mapa["a.jpg"]["publicacion_id"] == "posts_1.json:0"
    assert mapa["a.jpg"]["medio_indice"] == 0
    assert mapa["b.jpg"]["medio_indice"] == 1
    assert mapa["b.jpg"]["medio_total"] == 2


def test_a_media_title_wins_over_the_post_one(tmp_path):
    raiz = _export(tmp_path, {"reels.json": {"ig_reels_media": [{
        "media": [{"uri": "media/reels/x.mp4", "title": "lo suyo",
                   "creation_timestamp": 1600000000}],
        "title": "el del post",
    }]}})
    mapa, _ = meta.leer_export(raiz)
    assert mapa["x.mp4"]["texto"] == "lo suyo"
    assert mapa["x.mp4"]["hereda_del_post"] is False


def test_the_list_is_found_without_hardcoding_its_key(tmp_path):
    """The export wraps its lists under names like `ig_reels_media`. A key
    written by hand here goes stale at the next export."""
    raiz = _export(tmp_path, {"archived_posts.json": {
        "una_clave_que_nadie_predijo": [{
            "creation_timestamp": 1600000000, "title": "t",
            "media": [{"uri": "media/x.jpg"}]}]}})
    mapa, _ = meta.leer_export(raiz)
    assert "x.jpg" in mapa


def test_a_duplicate_entry_never_erases_the_text(tmp_path):
    """The same file shows up in more than one export file. Losing its text to
    an empty duplicate would silently drop the only data that matters."""
    raiz = _export(tmp_path, {
        "posts_1.json": [{"creation_timestamp": 1600000000, "title": "el bueno",
                          "media": [{"uri": "media/x.jpg"}]}],
        "posts.json": [{"creation_timestamp": 1600000000, "title": "",
                        "media": [{"uri": "media/x.jpg"}]}],
    })
    mapa, _ = meta.leer_export(raiz)
    assert mapa["x.jpg"]["texto"] == "el bueno"


def test_stories_are_opt_in_and_keep_published_media_scope(tmp_path):
    raiz = _export(tmp_path, {"stories.json": {"ig_stories": [{
        "creation_timestamp": 1600000000,
        "title": "VJ en Sala Demo",
        "uri": "media/stories/2020/scene.mp4",
    }]}})
    mapa, informe = meta.leer_export(raiz)
    assert mapa == {}
    mapa, informe = meta.leer_export(raiz, incluir_historias=True)
    assert mapa["scene.mp4"]["texto"] == "VJ en Sala Demo"
    assert mapa["scene.mp4"]["tipo_contenido"] == "story"
    assert mapa["scene.mp4"]["publicacion_archivo"] == "stories.json"


def test_a_missing_timestamp_leaves_the_date_empty(tmp_path):
    raiz = _export(tmp_path, {"posts_1.json": [{
        "title": "sin fecha", "media": [{"uri": "media/x.jpg"}]}]})
    mapa, _ = meta.leer_export(raiz)
    assert mapa["x.jpg"]["fecha"] == ""
    assert mapa["x.jpg"]["texto"] == "sin fecha"
