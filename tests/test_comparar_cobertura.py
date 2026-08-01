#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A comparison that can only compare what is actually comparable.

The tool exists because "the new engine sees better" is not a measurement, and
the way that sentence usually gets faked is by counting two different things:
coverage over one set of files versus coverage over another, or crediting the
new engine for rows a fallback answered. Both produce a number that looks like
progress and means nothing.

What is pinned here is exactly those two refusals, plus the third one this repo
learned the hard way on 2026-07-31: an EMPTY value and a value that NEVER
ARRIVED are different facts, and collapsing them is how a silent discard reads
as success.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOOL = RAIZ / "tools" / "comparar_cobertura_fichas.py"


def _ficha(fid, vision, motor="watsonx"):
    return {"id": fid, "fuente": "ig", "vision": vision,
            "medicion": {"vision": {"estado": "medido", "motor": motor}}}


def _escribir(ruta, fichas):
    ruta.write_text(
        "\n".join(json.dumps(f, ensure_ascii=False) for f in fichas) + "\n",
        encoding="utf-8")


def _correr(antes, despues, *extra):
    r = subprocess.run(
        [sys.executable, str(TOOL), str(antes), str(despues), "--json", *extra],
        capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


def test_only_the_files_present_in_both_passes_are_counted(tmp_path):
    """Coverage over different sets is not a comparison. The files the new pass
    added are reported as such, never folded into the score."""
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {"tecnica": "dibujo"})])
    _escribir(b, [_ficha("1", {"tecnica": "dibujo"}),
                  _ficha("2", {"tecnica": "tatuaje"})])
    d = _correr(a, b)
    assert d["comparadas"] == 1
    assert d["solo_en_la_nueva"] == 1
    assert d["campos"]["tecnica"]["despues"]["lleno"] == 1


def test_the_motor_filter_keeps_a_fallback_from_taking_the_credit(tmp_path):
    """A run with a fallback in it would otherwise credit the new engine for
    what the old one answered."""
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {}), _ficha("2", {})])
    _escribir(b, [_ficha("1", {"tecnica": "dibujo"}, motor="watsonx"),
                  _ficha("2", {"tecnica": "collage"}, motor="ollama")])
    d = _correr(a, b, "--motor", "watsonx")
    assert d["comparadas"] == 1
    assert d["motores_en_la_pasada_nueva"] == {"watsonx": 1, "ollama": 1}


def test_an_unsigned_row_is_reported_as_unsigned_not_as_the_default(tmp_path):
    """`sin_atribucion` is a value, not a gap to be filled with whichever engine
    was configured. Filling it would destroy the field that measures it."""
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    fila = {"id": "1", "vision": {"tecnica": "x"}, "medicion": {"vision": {}}}
    _escribir(a, [_ficha("1", {})])
    _escribir(b, [fila])
    d = _correr(a, b)
    assert d["motores_en_la_pasada_nueva"] == {"sin_atribucion": 1}


def test_empty_and_absent_are_counted_apart(tmp_path):
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {"tecnica": ""}), _ficha("2", {})])
    _escribir(b, [_ficha("1", {"tecnica": "dibujo"}),
                  _ficha("2", {"tecnica": "dibujo"})])
    d = _correr(a, b)
    campo = d["campos"]["tecnica"]["antes"]
    assert campo == {"lleno": 0, "vacio": 1, "ausente": 1}


def test_a_key_no_list_knows_about_is_still_counted(tmp_path):
    """The ordered key list is for the table's shape, not a whitelist. A key the
    model emitted that nobody declared gets counted anyway -- a hand-written
    list that silently drops the rest is the defect this repo hit three times in
    one day."""
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {})])
    _escribir(b, [_ficha("1", {"clave_que_nadie_declaro": "algo"})])
    d = _correr(a, b)
    assert d["campos"]["clave_que_nadie_declaro"]["despues"]["lleno"] == 1


def test_a_retry_row_wins_over_the_first_attempt(tmp_path):
    """The pipeline appends a ficha per attempt, so the same id shows up twice.
    The outcome that counts is the last one -- counting both would inflate the
    denominator with rows that were superseded."""
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {})])
    _escribir(b, [_ficha("1", {}), _ficha("1", {"tecnica": "dibujo"})])
    d = _correr(a, b)
    assert d["comparadas"] == 1
    assert d["campos"]["tecnica"]["despues"]["lleno"] == 1
