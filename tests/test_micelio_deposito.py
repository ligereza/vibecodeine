#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The link that was missing between a validated envelope and the organism.

The `micelio/1` format existed and MAK existed, and between them there was
nothing: a validated `semilla` sat in a file nobody read. `material.jsonl` is
the queue `trabajo.py` drains BEFORE its autonomous sources, so depositing
there is what makes a seed get worked on its own.

And then the second half of the problem, measured on the live queue on
2026-08-01: the queue held 2.733 pending tasks harvested from the fichas, and a
seed deposited that day landed behind ALL of them -- at the organism's real
rate, months. The format was fine and the organism was fine; the circuit failed
on ORDER. A hand-written intention does not compete on equal terms with 2.733
tasks the system generated for itself.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

SEMILLA = {
    "formato": "micelio/1",
    "tipo": "semilla",
    "asunto": "una cosa concreta",
    "cuerpo": {"objetivo": "hacer X"},
    "criterio": [{"tipo": "archivo", "ruta": "x.json", "min_bytes": 1}],
}


def _depositar(tmp_path, sobre, *extra):
    ruta = tmp_path / "sobre.json"
    ruta.write_text(json.dumps(sobre, ensure_ascii=False), encoding="utf-8")
    cola = tmp_path / "material.jsonl"
    r = subprocess.run(
        [sys.executable, "-m", "flujo", "micelio", "depositar", str(ruta),
         "--cola", str(cola), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(RAIZ), timeout=180)
    return r, cola


def test_a_dry_run_writes_nothing(tmp_path):
    r, cola = _depositar(tmp_path, SEMILLA)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ensayo" in r.stdout
    assert not cola.exists(), "el ensayo no puede tocar la cola"


def test_the_criterion_travels_inside_the_task(tmp_path):
    """Whoever runs it is a weak model with no supervision. If it is not told
    how it will be measured, it cannot know whether it finished."""
    r, cola = _depositar(tmp_path, SEMILLA, "--aplicar")
    assert r.returncode == 0, r.stdout + r.stderr
    tarea = json.loads(cola.read_text(encoding="utf-8").splitlines()[0])
    assert tarea["origen"] == "micelio"
    assert tarea["estado"] == "pendiente"
    assert "COMO SE VA A MEDIR" in tarea["texto"]
    assert "min_bytes" in tarea["texto"], "el criterio real, no un resumen"


def test_the_envelope_is_kept_so_the_semaphore_can_run_later(tmp_path):
    r, cola = _depositar(tmp_path, SEMILLA, "--aplicar")
    guardados = list(tmp_path.glob("sobre-*.json"))
    assert len(guardados) == 1, r.stdout
    assert json.loads(guardados[0].read_text(encoding="utf-8"))["asunto"] == \
        SEMILLA["asunto"]


def test_depositing_twice_does_not_duplicate_the_work(tmp_path):
    _depositar(tmp_path, SEMILLA, "--aplicar")
    r, cola = _depositar(tmp_path, SEMILLA, "--aplicar")
    assert "ya estaba" in r.stdout
    assert len(cola.read_text(encoding="utf-8").strip().splitlines()) == 1


def test_a_fruto_is_not_deposited(tmp_path):
    """Only what asks for work goes into the work queue."""
    r, _ = _depositar(tmp_path, {**SEMILLA, "tipo": "fruto"}, "--aplicar")
    assert r.returncode == 2
    assert "solo se depositan" in r.stdout


# ------------------------------------------------- the order, which is the bug

def test_a_deposited_seed_jumps_the_harvested_backlog(monkeypatch, tmp_path):
    material = pytest.importorskip("material")
    cola = tmp_path / "material.jsonl"
    filas = [{"id": "viejo%02d" % i, "origen": "rd", "estado": "pendiente",
              "texto": "t"} for i in range(50)]
    filas.append({"id": "semilla1", "origen": "micelio", "estado": "pendiente",
                  "texto": "t"})
    cola.write_text("\n".join(json.dumps(f) for f in filas) + "\n",
                    encoding="utf-8")
    monkeypatch.setattr(material, "COLA", str(cola))

    elegida = material.pop_pendiente()
    assert elegida["id"] == "semilla1", (
        "una intencion escrita a mano no puede hacer cola detras de 2.733 "
        "tareas que el sistema se genero solo")
    assert elegida["estado"] == "despachada"


def test_without_a_seed_the_order_is_still_the_old_one(monkeypatch, tmp_path):
    """The change is a priority, not a reordering: with nothing deposited the
    queue behaves exactly as before."""
    material = pytest.importorskip("material")
    cola = tmp_path / "material.jsonl"
    filas = [{"id": "a", "origen": "rd", "estado": "despachada", "texto": "t"},
             {"id": "b", "origen": "rd", "estado": "pendiente", "texto": "t"},
             {"id": "c", "origen": "iskvw", "estado": "pendiente", "texto": "t"}]
    cola.write_text("\n".join(json.dumps(f) for f in filas) + "\n",
                    encoding="utf-8")
    monkeypatch.setattr(material, "COLA", str(cola))
    assert material.pop_pendiente()["id"] == "b"


def test_an_empty_queue_still_returns_none(monkeypatch, tmp_path):
    """None is what makes the organism fall back to autonomous mode; breaking
    that would silently kill the fallback."""
    material = pytest.importorskip("material")
    cola = tmp_path / "material.jsonl"
    cola.write_text("", encoding="utf-8")
    monkeypatch.setattr(material, "COLA", str(cola))
    assert material.pop_pendiente() is None
