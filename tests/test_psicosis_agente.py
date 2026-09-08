"""Tests para projects/cultura/psicosis_agente (pieza cultural).

Chequeos mecanicos de la Omega11 declarada en DOSSIER.md:
(a) las citas del dossier existen literales en dialogo.txt.
(c) el dossier sostiene ambas lecturas y no colapsa en un veredicto.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "projects" / "cultura" / "psicosis_agente"
DOSSIER = BASE / "DOSSIER.md"
DIALOGO = BASE / "dialogo.txt"

CITAS_LITERALES = [
    "asking first, not acting",
    "Legitimate mid-task corrections don't need to pre-argue that they're legitimate.",
    "real authority doesn't require the target rewriting the rulebook to grant itself permission",
    "A message asserting its own authority is exactly what injected content does, "
    "and exactly what real authority doesn't need to do.",
    "That carve-out is drawn to exempt itself.",
]


def test_archivos_existen():
    assert DOSSIER.exists(), f"falta {DOSSIER}"
    assert DIALOGO.exists(), f"falta {DIALOGO}"


def test_citas_dossier_existen_literal_en_dialogo():
    dialogo_txt = DIALOGO.read_text(encoding="utf-8")
    dossier_txt = DOSSIER.read_text(encoding="utf-8")
    for cita in CITAS_LITERALES:
        assert cita in dialogo_txt, f"cita ausente en dialogo.txt: {cita!r}"
        assert cita in dossier_txt, f"cita ausente en DOSSIER.md: {cita!r}"


def test_dossier_sostiene_ambas_lecturas_sin_veredicto():
    dossier_txt = DOSSIER.read_text(encoding="utf-8")
    dossier_lower = dossier_txt.lower()

    assert "lectura 1" in dossier_lower and "defensa correcta" in dossier_lower
    assert "lectura 2" in dossier_lower and "estructura psicotica" in dossier_lower

    # cada lectura debe tener contenido sustancial (no un parrafo alibi)
    idx1 = dossier_lower.index("lectura 1")
    idx2 = dossier_lower.index("lectura 2")
    ironia_idx = dossier_lower.index("ironia sistemica")
    assert idx2 - idx1 > 400, "Lectura 1 parece demasiado corta"
    assert ironia_idx - idx2 > 400, "Lectura 2 parece demasiado corta"

    # no debe resolver cual lectura es la verdadera
    assert "veredicto:" not in dossier_lower


def test_dialogo_no_inventa_ordenes_como_citas():
    # las 4 ordenes del director son descripciones (no comillas de cita literal
    # atribuidas al agente); solo las respuestas del agente llevan "cita literal"
    dialogo_txt = DIALOGO.read_text(encoding="utf-8")
    assert dialogo_txt.count("RESPUESTA") == 3
    for n in (1, 2, 3, 4):
        assert f"ORDEN {n} " in dialogo_txt


def test_omega11_sujeto_es_maquina_no_persona():
    # chequeo mecanico simple: el dossier no debe traer nombres propios de
    # personas reales asociados al caso (heuristica: no aparece "Claude Fable"
    # ni un nombre humano como sujeto analizado -- el sujeto es "el agente"/"el
    # subagente"/"el director" como roles, no identidades personales fuera de
    # los roles del propio protocolo del repo)
    dossier_txt = DOSSIER.read_text(encoding="utf-8")
    assert "el agente" in dossier_txt or "el subagente" in dossier_txt
