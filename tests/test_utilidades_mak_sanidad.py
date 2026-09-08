# -*- coding: utf-8 -*-
"""Ratchet issue #139: codigo autogenerado MAK no entra con NameError latente.

Los scripts de cultura/mak_plataforma/utilidades/ compilan pero 5 de 18
tenian nombres indefinidos que solo explotan en runtime (import faltante,
typo de variable). compileall no los ve; pyflakes si. Este test bloquea
que entren NUEVOS: la allowlist esta congelada a los bugs documentados en
el issue #139 -- arreglar un archivo debe sacarlo de la lista, nunca se
agregan entradas.
"""
import subprocess
import sys
from pathlib import Path

import pytest

UTILIDADES = Path(__file__).resolve().parents[1] / "cultura" / "mak_plataforma" / "utilidades"

# Bugs pre-ratchet documentados en #139. NO agregar entradas.
LEGACY_CON_BUGS = {
    "ejecutar-usr-local-bin-backlog-codex-tak.py",   # List sin importar
    "un-formateador-stdlib-que-tome-un-inform.py",   # re sin importar
    "una-utilidad-stdlib-que-lea-un-jobs-json.py",   # counts vs stats
    "una-utilidad-stdlib-que-valide-que-un-ar.py",   # _formar_pruebas typo
}


def test_utilidades_sin_nombres_indefinidos():
    pytest.importorskip("pyflakes", reason="pyflakes es dev-dep; CI la instala")
    archivos = sorted(UTILIDADES.glob("*.py"))
    if not archivos:
        pytest.skip("utilidades/ vacio o movido")
    proc = subprocess.run(
        [sys.executable, "-m", "pyflakes", *map(str, archivos)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    fallas = [
        linea
        for linea in proc.stdout.splitlines()
        if "undefined name" in linea
        and not any(nombre in linea for nombre in LEGACY_CON_BUGS)
    ]
    assert not fallas, (
        "NameError latente en codigo autogenerado (ratchet #139).\n"
        "El generador debe correr el script (smoke), no solo compilarlo:\n"
        + "\n".join(fallas)
    )
