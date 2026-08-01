#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What the micelio actually relates, and who said it.

The micelio is the semantic index: one document per work under
`~/research/corpus/`, embedded and related. Measured on 2026-08-01, that corpus
held 697 documents against 1.401 fichas -- half the archive was not a node --
and every document was shaped by the July schema, carrying an `Estilo` field the
current one does not have.

The builder itself was fine; the CORPUS was stale. What the builder genuinely
did not know about is what arrived that night: the artist's own words and the
exact publication date, taken from the Instagram export rather than from any
model.

That distinction is the point of this file. An embedding built on the artist's
language is not the same object as one built on a model describing pixels, so
the document keeps them apart and labelled. A reader -- or an agent -- has to be
able to tell who said what.

One assumption killed by counting before changing anything: OCR garbage
presented as "Texto en la obra" looked like a problem, and it is 6 fichas of
1.401. It is not worth a rule.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_research"))

corpus = pytest.importorskip("corpus_a_micelio")


def _ficha(**kw):
    f = {"id": "abc", "ruta_rel": "posts/1.jpg", "tipo": "imagen",
         "categoria": "obra", "mtime": "2026-07-22",
         "vision": {"descripcion": "Render 3D de dulces."}}
    f.update(kw)
    return f


def test_the_artists_words_are_labelled_as_his():
    d = corpus.documento(_ficha(
        texto_autor="Meses de ensayo y error para @sweettoothskully."))
    assert "Lo que escribio el artista" in d
    assert "Meses de ensayo y error" in d


def test_his_words_are_not_mixed_into_the_model_description():
    """One is a reading of pixels, the other is the author. A document that
    blends them cannot be audited."""
    d = corpus.documento(_ficha(texto_autor="mis palabras"))
    cuerpo, _, autor = d.partition("Lo que escribio el artista")
    assert "Render 3D de dulces." in cuerpo
    assert "mis palabras" in autor
    assert "mis palabras" not in cuerpo


def test_the_publication_date_reaches_the_document_and_the_meta():
    d = corpus.documento(_ficha(fecha_publicacion="2026-06-16"))
    assert "**Publicada:** 2026-06-16" in d
    assert '"fecha_publicacion": "2026-06-16"' in d


def test_the_date_is_not_the_file_mtime():
    """`mtime` is when the file touched this disk. Treating it as the date of
    the work would put 1.401 pieces in July 2026."""
    d = corpus.documento(_ficha(fecha_publicacion="2019-03-01",
                                mtime="2026-07-22"))
    assert '"fecha_publicacion": "2019-03-01"' in d
    assert '"mtime": "2026-07-22"' in d


def test_a_ficha_without_those_fields_invents_nothing():
    """Everything perceived before 2026-08-01 lacks them, and an absence filled
    with a plausible value destroys the field that measures it."""
    d = corpus.documento(_ficha())
    assert "Publicada" not in d
    assert "Lo que escribio el artista" not in d
    assert '"fecha_publicacion": null' in d
    assert '"texto_autor": false' in d


def test_the_meta_says_whether_there_were_words_not_the_words():
    """The body carries the text; the meta carries whether it exists. Repeating
    it would double what gets embedded and skew every distance."""
    d = corpus.documento(_ficha(texto_autor="una frase distintiva"))
    _, _, meta = d.rpartition("meta: ")
    assert "una frase distintiva" not in meta
    assert '"texto_autor": true' in meta


def test_the_title_is_the_perceived_phrase_and_the_id_stays_below():
    """The 18-digit Instagram id says nothing to anyone, and this is NOT
    presented as a title by the artist."""
    d = corpus.documento(_ficha())
    assert d.startswith("# Render 3D de dulces")
    assert "posts/1.jpg" in d
