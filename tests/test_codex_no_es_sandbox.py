# -*- coding: utf-8 -*-
"""VCD-03: el filtro de codex es un ESCANEO, y decia ser un sandbox.

Del diagnostico de seguridad del 2026-07-27. `_PELIGRO` es una lista de
expresiones regulares; `-I -S`, setrlimit, un cwd temporal y un entorno reducido
acotan RECURSOS, no aislan red, filesystem, usuario ni syscalls.

Un sandbox es una frontera que el codigo de adentro no puede cruzar aunque
quiera. Esto reconoce las formas que ya vio.

Este test NO intenta arreglar el colador. Fija dos cosas: que el escaneo siga
atrapando lo obvio, y que el modulo siga diciendo la verdad sobre lo que es.
Se importan las regex del archivo sin cargar el modulo, porque codex_lib usa
`resource`, que no existe en Windows.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
LIB = REPO / "cultura" / "mak_codex" / "codex_lib.py"

pytestmark = pytest.mark.skipif(not LIB.is_file(), reason="codex_lib.py no esta")


def _patrones():
    src = LIB.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"_PELIGRO\s*=\s*\[(.*?)\n\]", src, re.S)
    assert m, "no encuentro _PELIGRO"
    return [re.compile(p) for p, _ in ast.literal_eval("[" + m.group(1) + "]")]


def _bloquea(codigo: str) -> bool:
    return any(p.search(codigo) for p in _patrones())


def test_atrapa_lo_obvio():
    """Es para lo que sirve: el descuido y el modelo que genera algo peligroso
    sin intencion."""
    assert _bloquea('import os\nos.system("id")')
    assert _bloquea("import subprocess")
    assert _bloquea("f = open('/etc/passwd')")
    assert _bloquea("__import__('os')")


def test_el_modulo_no_se_llama_a_si_mismo_sandbox():
    """El nombre importa porque hace que alguien confie. Si vuelve a decir que
    es un sandbox, o pasa a serlo de verdad, este test se cae y hay que mirar."""
    src = LIB.read_text(encoding="utf-8", errors="replace")
    assert "ESTO NO ES UN SANDBOX" in src
    assert "sandbox con limites duros" not in src


def test_la_medicion_de_las_evasiones_esta_escrita():
    """Cuatro de seis pasaron. Sin el numero, la advertencia es una opinion."""
    src = LIB.read_text(encoding="utf-8", errors="replace")
    assert "4 de 6 evasiones" in src
    assert "../../../etc/passwd" in src


def test_las_evasiones_medidas_siguen_pasando():
    """Se fija el estado REAL, no el deseado.

    Si alguien agrega regex para taparlas, este test se cae -- y eso es lo que
    se quiere: obliga a decidir si se tapo el sintoma o se construyo la frontera
    de verdad, en vez de que la ilusion se vuelva mas dificil de romper en
    silencio.
    """
    evasiones = [
        "g = getattr(__built" + "ins__, '__imp' + 'ort__')",
        "e = 'imp' + 'ort os'",
        "f = open('../../../etc/passwd')",
    ]
    pasan = [c for c in evasiones if not _bloquea(c)]
    assert len(pasan) == len(evasiones), (
        "alguna evasion ya no pasa: si se agregaron regex, revisar que no sea "
        "tapar el sintoma; si se construyo el aislamiento real, actualizar la "
        "nota del modulo y borrar este test")
