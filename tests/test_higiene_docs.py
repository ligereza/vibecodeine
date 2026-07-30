"""Ratchet de higiene documental: cifras de la doc vs cifras medidas.

Regla (2026-07-25). Causa concreta: `context/WALKTHROUGH.md` es la puerta de
entrada que `CLAUDE.md` manda leer primero, y afirmaba "394 tests", "I1-I8" y
"v0.52.0 live" cuando lo real era 1156 tests, I1-I10 y 0.56.1. Las tres cifras
SUBESTIMAN el repo, e inducen a un agente nuevo a reimplementar lo que ya
existe (viola el invariante I3). El mismo drift estaba en PLAN_SEMANAL_OPUS.md
(950) y PLAN_SIGUIENTE_AGENTE.md (899): tres valores distintos, ninguno cierto.

`CLAUDE.md` ya pide "ninguna cifra en prosa", pero nadie la hacia cumplir. Esto
la convierte en gate: la doc no puede afirmar un total de tests, un rango de
invariantes ni una version que contradiga lo medido.

Alcance deliberadamente chico: se prohibe afirmar el TOTAL de la suite, no
registrar deltas historicos ("+24 tests", "26 tests nuevos"), que son hechos
fechados y no se pudren.

Condicion de retiro: cuando la doc de entrada se genere desde el repo en vez de
escribirse a mano, este ratchet sobra.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent

ZONA_MUERTA = (
    ".archive/",
    "_archive/",
    "docs/handoffs/archive/",
    "projects/cultura/corpus_olvido/",
)

# Documentacion AJENA: el README que viaja al lado de cada libreria
# vendorizada (`tools/vendorizar_iskvw.py` lo copia a proposito, porque el
# bundle minificado no dice como se llama a nada). No la escribimos nosotros y
# no habla de este repo, asi que las reglas de higiene de una doc VIVA no le
# aplican: `hiccup.README.md` cita la version 2.0.0 DE ESA LIBRERIA y el
# ratchet de version la leia como si afirmara la version de flujo (CI rojo,
# 2026-07-30). Retiro: si algun dia dejamos de versionar los README ajenos.
ZONA_AJENA = (
    "docs/cultura/lib/",
    "iskvw/piel/lib/",
)

# "394 green tests", "Suite >= 950 tests", "~950 tests"
CIFRA_TESTS = re.compile(r"\b(\d{2,5})\s*(?:green\s+|verdes\s+)?tests?\b", re.I)
# Marca de delta historico: no es una afirmacion sobre el total de la suite.
# Incluye el caso "tests/test_x.py (N tests verdes)": una cifra pegada a un
# modulo concreto cuenta ESE modulo, no la suite, y por eso no se pudre.
DELTA = re.compile(
    r"[+]\s*\d{1,5}\s*(?:green\s+|verdes\s+)?tests?\b"
    r"|\bnuev[oa]s?\b"
    r"|\btest_[A-Za-z0-9_]+\.py\b",
    re.I,
)
# Palabras que convierten la cifra en una afirmacion sobre la suite entera.
ALCANCE_SUITE = re.compile(r"\bsuite\b|green\s+tests?|tests?\s+verdes|todo\s+verde|0\s+rojos|exit\s+0", re.I)

RANGO_INVARIANTES = re.compile(r"\bI1\s*-\s*I(\d+)\b")
INVARIANTE_CONTRATO = re.compile(r"^-\s*I(\d+)\b", re.M)

VERSION_AFIRMADA = re.compile(r"\bv(\d+\.\d+\.\d+)\s+live\b|\bversion\s+(\d+\.\d+\.\d+)\b", re.I)
VERSION_PYPROJECT = re.compile(r'^version\s*=\s*"([^"]+)"', re.M)


def _docs_vivos() -> list[Path]:
    """Todos los .md versionados fuera de zona muerta y de zona ajena.

    OJO, medido el 2026-07-30: esto lee `git ls-files`, asi que un .md NUEVO y
    todavia sin commitear es INVISIBLE para este ratchet. Una corrida local
    verde antes del commit no dice nada sobre los archivos que el commit va a
    agregar -- fue asi como cuatro README vendorizados pasaron el pytest local y
    tumbaron el CI. Si agregas docs, `git add` primero y despues corre esto.
    """
    r = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        pytest.skip("no es un checkout git usable")
    return [
        RAIZ / f
        for f in r.stdout.split("\n")
        if f and not f.startswith(ZONA_MUERTA) and not f.startswith(ZONA_AJENA)
    ]


def _lineas(p: Path):
    try:
        texto = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return list(enumerate(texto.splitlines(), 1))


def _rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def test_ningun_doc_vivo_afirma_el_total_de_la_suite():
    """El conteo de tests se mide, no se escribe. Deltas historicos si valen."""
    ofensas = []
    for p in _docs_vivos():
        lineas = _lineas(p)
        previa = ""
        for n, linea in lineas:
            if not CIFRA_TESTS.search(linea):
                previa = linea
                continue
            # La marca de delta puede venir en la linea anterior: la prosa del
            # repo envuelve a ~75 columnas y parte "tests/test_x.py +\n18 tests".
            if not DELTA.search(previa + " " + linea) and ALCANCE_SUITE.search(linea):
                ofensas.append(f"{_rel(p)}:{n}: {linea.strip()}")
            previa = linea

    assert not ofensas, (
        "Cifra del total de la suite escrita en prosa (se pudre sola).\n"
        "Reemplazala por el comando que la mide: `py -m pytest tests/ -q`.\n"
        + "\n".join(ofensas)
    )


def test_el_rango_de_invariantes_citado_coincide_con_el_contrato():
    contrato = RAIZ / "context" / "DIRECTOR_CONTRACT.md"
    if not contrato.exists():
        pytest.skip("no hay DIRECTOR_CONTRACT.md")
    ids = [int(x) for x in INVARIANTE_CONTRATO.findall(contrato.read_text(encoding="utf-8"))]
    assert ids, "DIRECTOR_CONTRACT.md no lista invariantes con el formato '- IN '"
    maximo = max(ids)

    ofensas = []
    for p in _docs_vivos():
        for n, linea in _lineas(p):
            for m in RANGO_INVARIANTES.finditer(linea):
                if int(m.group(1)) != maximo:
                    ofensas.append(
                        f"{_rel(p)}:{n}: dice I1-I{m.group(1)}, el contrato llega a I{maximo}"
                    )

    assert not ofensas, (
        "Rango de invariantes desactualizado (un agente que lo crea opera sin "
        "las reglas nuevas).\n" + "\n".join(ofensas)
    )


def test_la_version_afirmada_coincide_con_pyproject():
    pyproject = RAIZ / "pyproject.toml"
    if not pyproject.exists():
        pytest.skip("no hay pyproject.toml")
    m = VERSION_PYPROJECT.search(pyproject.read_text(encoding="utf-8"))
    assert m, "pyproject.toml sin version"
    real = m.group(1)

    ofensas = []
    for p in _docs_vivos():
        for n, linea in _lineas(p):
            for hit in VERSION_AFIRMADA.finditer(linea):
                afirmada = hit.group(1) or hit.group(2)
                if afirmada != real:
                    ofensas.append(
                        f"{_rel(p)}:{n}: afirma {afirmada}, pyproject dice {real}"
                    )

    assert not ofensas, (
        "Version afirmada en doc viva distinta de pyproject.toml (la version "
        "manda).\n" + "\n".join(ofensas)
    )
