#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A question is work. An aside about a photo is not.

Measured on the live queue on 2026-08-01: 2.812 tasks, of which 2.696 (95,9%)
were born from two fields of the artist's own archive -- `oportunidad_codigo`
(1.342 tasks to codex) and `linea_investigacion` (1.354 to research), with 1.342
works generating BOTH. Those are fields where the vision model is asked
EXPLICITLY to speculate: "si la obra sugiere un procedimiento que podria
automatizarse, describi que programa la generaria".

`material.py` turned each of them, verbatim, into a work order. At the
organism's real rate (~15/day) that is 177 days of queue, refilled every hour by
cron. One of them sent MAK to "generar una base de datos de tatuajes por tipo de
imagen y elementos" at 02:00, from a photo taken in 2020. Nobody decided it.

The variable that holds them has been called `propuestas` since the file was
written, and then they were appended as orders. They go back to being what their
name says.

The user's rule, in his words (2026-08-01): inventing what to do is fine;
DECIDING it without a format is not. So they are not deleted -- an aside can be
a good one and the archive is the artist's -- they simply stop being dispatched
until something answers the three questions of `evaluar_propuesta`.
"""
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

material = pytest.importorskip("material")


def _cola(tmp_path, filas):
    ruta = tmp_path / "material.jsonl"
    ruta.write_text("\n".join(json.dumps(f, ensure_ascii=False) for f in filas)
                    + "\n", encoding="utf-8")
    return ruta


# --------------------------------------------------------- how they are born

def test_an_rd_triangulation_is_born_as_work():
    """The flyer defines the question -- date plus headliner -- and the answer
    is a name with a URL or NO SE ENCONTRO. That is a question."""
    assert material.ESTADO_INICIAL["rd"] == "pendiente"


def test_an_iskvw_aside_is_born_as_a_proposal():
    assert material.ESTADO_INICIAL["ig"] == "propuesta"


def test_a_proposal_is_never_dispatched(monkeypatch, tmp_path):
    """This is the whole point: it exists, it is counted, and nobody works on
    it until someone decides."""
    cola = _cola(tmp_path, [
        {"id": "a", "origen": "ig", "estado": "propuesta", "texto": "una idea"},
        {"id": "b", "origen": "rd", "estado": "pendiente", "texto": "una pregunta"},
    ])
    monkeypatch.setattr(material, "COLA", str(cola))
    assert material.pop_pendiente()["id"] == "b"


def test_with_only_proposals_the_queue_looks_empty(monkeypatch, tmp_path):
    """And that is correct: the organism falls back to autonomous mode, which
    is what that mode is for. Better idle than working on an aside."""
    cola = _cola(tmp_path, [
        {"id": "a", "origen": "ig", "estado": "propuesta", "texto": "una idea"}])
    monkeypatch.setattr(material, "COLA", str(cola))
    assert material.pop_pendiente() is None


# --------------------------------------------------- the ones already queued

def test_the_migration_reports_before_it_writes(monkeypatch, tmp_path):
    cola = _cola(tmp_path, [
        {"id": "a", "origen": "ig", "estado": "pendiente", "texto": "x"},
        {"id": "b", "origen": "ig", "estado": "pendiente", "texto": "y"},
    ])
    monkeypatch.setattr(material, "COLA", str(cola))
    n, total = material.degradar_ocurrencias(aplicar=False)
    assert (n, total) == (2, 2)
    estados = {json.loads(l)["estado"]
               for l in cola.read_text(encoding="utf-8").splitlines() if l.strip()}
    assert estados == {"pendiente"}, "el ensayo no escribe"


def test_applying_degrades_only_what_has_not_run_yet(monkeypatch, tmp_path):
    """What was dispatched is not touched: it was already worked, and rolling
    it back would be rewriting what happened."""
    cola = _cola(tmp_path, [
        {"id": "a", "origen": "ig", "estado": "pendiente", "texto": "x"},
        {"id": "b", "origen": "ig", "estado": "despachada", "texto": "y"},
        {"id": "c", "origen": "rd", "estado": "pendiente", "texto": "z"},
    ])
    monkeypatch.setattr(material, "COLA", str(cola))
    n, _ = material.degradar_ocurrencias(aplicar=True)
    assert n == 1
    por_id = {json.loads(l)["id"]: json.loads(l)["estado"]
              for l in cola.read_text(encoding="utf-8").splitlines() if l.strip()}
    assert por_id == {"a": "propuesta", "b": "despachada", "c": "pendiente"}


def test_the_rd_question_survives_the_migration(monkeypatch, tmp_path):
    """Pruning the asides must not prune the one source that asks something."""
    cola = _cola(tmp_path, [
        {"id": "c", "origen": "rd", "estado": "pendiente", "texto": "z"}])
    monkeypatch.setattr(material, "COLA", str(cola))
    material.degradar_ocurrencias(aplicar=True)
    assert material.pop_pendiente()["id"] == "c"


def test_a_hand_deposited_seed_still_goes_first(monkeypatch, tmp_path):
    """A hand-written intention does not compete on equal terms with what the
    system generated for itself -- and even less now that the asides are out."""
    cola = _cola(tmp_path, [
        {"id": "rd1", "origen": "rd", "estado": "pendiente", "texto": "z"},
        {"id": "s", "origen": "micelio", "estado": "pendiente", "texto": "semilla"},
    ])
    monkeypatch.setattr(material, "COLA", str(cola))
    assert material.pop_pendiente()["id"] == "s"
