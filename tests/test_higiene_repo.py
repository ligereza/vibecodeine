# -*- coding: utf-8 -*-
"""Ratchet de higiene del repo (2026-07-25).

Dos reglas que evitan repetir el problema medido en la sesion de
orquestacion: el handoff crecio a 1554 lineas sin tope, y tools/ acumula
scripts sin registro de si estan vivos o muertos. Ninguna de las dos
reglas se relaja "arreglando" el archivo que la dispara con contenido
falso: se comprime/archiva (handoff) o se declara en el registro
(tools/), nunca se edita el test.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LAST_HANDOFF = REPO_ROOT / "context" / "LAST_HANDOFF.md"
CAPACIDADES = REPO_ROOT / "CAPACIDADES.md"
TOOLS_DIR = REPO_ROOT / "tools"

MAX_HANDOFF_LINES = 350


def test_handoff_dentro_del_tope():
    contenido = LAST_HANDOFF.read_text(encoding="utf-8")
    lineas = contenido.splitlines()
    assert len(lineas) <= MAX_HANDOFF_LINES, (
        "LAST_HANDOFF.md excede 350 lineas: comprimir y archivar a "
        "docs/handoffs/archive/ (regla 2026-07-25, causa: llego a 1554 "
        "lineas; retiro: cuando el handoff viva en un sistema con "
        "rotacion automatica)"
    )


def test_tools_en_registro():
    capacidades = CAPACIDADES.read_text(encoding="utf-8")
    archivos = sorted(p for p in TOOLS_DIR.glob("*.py") if p.is_file())
    faltantes = [
        p.name for p in archivos if p.name not in capacidades
    ]
    assert not faltantes, (
        "tools/<x>.py sin entrada en registro VIVO/MUERTO de "
        "CAPACIDADES.md: toda herramienta declara consumidor o no entra "
        "(regla 2026-07-25). Faltan: " + ", ".join(faltantes)
    )
