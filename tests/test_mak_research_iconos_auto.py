#!/usr/bin/env python3
"""research worker -> Codex icon queue.

The important seam is autonomous, not aesthetic: when research.py finishes an
essay and prints an `ANEXO: *.conceptos.json`, worker.py must queue visual jobs
for Codex mode `iconos`. The essay remains valid even if Codex is down.
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("fcntl")

REPO = Path(__file__).resolve().parents[1]
MAK_RESEARCH = REPO / "cultura" / "mak_research"
sys.path.insert(0, str(MAK_RESEARCH))

import worker  # noqa: E402


def _annex(tmp_path):
    path = tmp_path / "ensayo.conceptos.json"
    path.write_text(json.dumps([
        {
            "n": "01",
            "slug": "berlin-muro-techno",
            "titulo": "Berlín: cae el muro, sale el techno",
            "descripcion": "Búnkeres y fábricas vacías como catedrales techno.",
            "estilo": "Brutalista concreto",
            "ancla": "### Berlín",
        },
        {
            "n": "02",
            "slug": "tb-303",
            "titulo": "Roland TB-303",
            "descripcion": "Un fracaso comercial convertido en voz acid.",
        },
    ], ensure_ascii=False), encoding="utf-8")
    return path


def test_extracts_annex_paths_from_research_stdout(tmp_path):
    annex = _annex(tmp_path)
    out = "STATUS: x\nANEXO: %s\nINFORME: /x/y.md\n" % annex
    assert worker._annex_paths_from_output(out) == [str(annex)]


def test_annex_concepts_are_queued_as_icon_jobs(tmp_path, monkeypatch):
    annex = _annex(tmp_path)
    prompts = []
    monkeypatch.setattr(worker, "_post_codex_icon",
                        lambda prompt, densidad: prompts.append((prompt, densidad)) or True)

    result = worker.enqueue_annex_icons(str(annex), densidad="medio")

    assert result == {"queued": 2, "errors": []}
    assert all(densidad == "medio" for _, densidad in prompts)
    assert "Berlín: cae el muro" in prompts[0][0]
    assert "Brutalista concreto" in prompts[0][0]
    assert "Debe ser representativo" in prompts[0][0]


def test_visual_queue_is_best_effort_not_research_failure(tmp_path, monkeypatch):
    annex = _annex(tmp_path)

    def fail_once(prompt, densidad):
        raise OSError("codex down")

    monkeypatch.setattr(worker, "_post_codex_icon", fail_once)

    result = worker.enqueue_annex_icons(str(annex), densidad="corto")

    assert result["queued"] == 0
    assert "codex down" in result["errors"][0]


def test_visual_queue_can_be_disabled(tmp_path, monkeypatch):
    annex = _annex(tmp_path)
    monkeypatch.setenv("MAK_AUTO_ICONOS", "0")

    result = worker.enqueue_annex_icons(str(annex))

    assert result["queued"] == 0
    assert "disabled" in result["errors"][0]


def test_visual_queue_respects_icon_limit(tmp_path, monkeypatch):
    annex = _annex(tmp_path)
    prompts = []
    monkeypatch.setattr(worker, "_post_codex_icon",
                        lambda prompt, densidad: prompts.append(prompt) or True)

    result = worker.enqueue_annex_icons(str(annex), max_icons=1)

    assert result["queued"] == 1
    assert len(prompts) == 1
