"""Ratchet de higiene documental: cifras de la doc vs cifras medidas.

Regla (2026-07-25). Causa concreta: `context/WALKTHROUGH.md` era una puerta de
entrada operativa y afirmaba "394 tests", "I1-I8" y
"v0.52.0 live" cuando lo real era 1156 tests, I1-I10 y 0.56.1. Las tres cifras
SUBESTIMAN el repo, e inducen a un agente nuevo a reimplementar lo que ya
existe (viola el invariante I3). El mismo drift estaba en PLAN_SEMANAL_OPUS.md
(950) y PLAN_SIGUIENTE_AGENTE.md (899): tres valores distintos, ninguno cierto.

La política documental ya pide "ninguna cifra en prosa", pero nadie la hacia
cumplir. Esto la convierte en gate: la doc no puede afirmar un total de tests, un rango de
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

from repo_scan import versionable_files
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent

ZONA_MUERTA = (
    ".archive/",
    "_archive/",
    "context-history/",
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
ALCANCE_SUITE = re.compile(r"\bsuites?\b|green\s+tests?|tests?\s+verdes|todo\s+verde|0\s+rojos|exit\s+0", re.I)
MEASUREMENT_DATE = re.compile(r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b")
LIVE_STATE = re.compile(
    r"\b(?:now|currently|current|today|hoy|actual(?:ly|mente)?|live|"
    r"activo|active|carries|lleva)\b",
    re.I,
)
CONTEXTO_TEST_LOCAL = re.compile(
    r"\b(?:test_[A-Za-z0-9_]+\.py|m[oó]dulo|module|"
    r"caso|case|funci[oó]n|function|family|familia|coverage|cobertura|"
    r"invariant|invariante|lane|carril|plugin|unit|unidad)\b",
    re.I,
)
REGISTROS_HISTORICOS = (
    "context/HANDOFF_HISTORICO.md",
    "docs/handoffs/archive/",
    "work/",
    "xio/imported_root/",
)

RANGO_INVARIANTES = re.compile(r"\bI1\s*-\s*I(\d+)\b")
INVARIANTE_CONTRATO = re.compile(r"^-\s*I(\d+)\b", re.M)

VERSION_AFIRMADA = re.compile(
    r"\bversion\b\s*(?:[:=]\s*)?v?(\d+\.\d+\.\d+)\b"
    r"|\bv(\d+\.\d+\.\d+)\s+live\b",
    re.I,
)
VERSION_PYPROJECT = re.compile(r'^version\s*=\s*"([^"]+)"', re.M)


def _docs_vivos() -> list[Path]:
    """Todos los .md que pueden entrar al repo, fuera de zona muerta y ajena.

    Antes esto leia `git ls-files` a secas, o sea SOLO lo rastreado, y su propio
    docstring documentaba el precio: "cuatro README vendorizados pasaron el
    pytest local y tumbaron el CI", con el workaround manual de hacer `git add`
    antes de correr los tests. Un workaround que vive en la memoria de una
    persona vuelve a fallar. Ahora la enumeracion la hace `versionable_files()`,
    que suma los archivos nuevos no ignorados: el ratchet mira lo que esta por
    entrar, que es contra lo que protege.
    """
    nombres = versionable_files(("*.md",))
    if not nombres:
        pytest.skip("no es un checkout git usable")
    return [
        RAIZ / f
        for f in nombres
        if not f.startswith(ZONA_MUERTA) and not f.startswith(ZONA_AJENA)
    ]


def _lineas(p: Path):
    try:
        texto = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return list(enumerate(texto.splitlines(), 1))


def _rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def _is_suite_count(line: str, previous: str = "", path: Path | None = None) -> bool:
    """Catch an unscoped live total without accusing dated evidence."""
    context = previous + " " + line
    if DELTA.search(context) or MEASUREMENT_DATE.search(context):
        return False
    if path is not None and any(
        _rel(path) == prefix or _rel(path).startswith(prefix)
        for prefix in REGISTROS_HISTORICOS
    ):
        return False
    if ALCANCE_SUITE.search(line):
        return True
    return bool(LIVE_STATE.search(context)) and not CONTEXTO_TEST_LOCAL.search(context)


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
            if _is_suite_count(linea, previa, p):
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
        ofensas = []
        for p in _docs_vivos():
            for n, linea in _lineas(p):
                if RANGO_INVARIANTES.search(linea):
                    ofensas.append(
                        f"{_rel(p)}:{n}: cita invariantes de un contrato archivado"
                    )
        assert not ofensas, (
            "El contrato del director fue archivado; ninguna doc viva puede "
            "seguir citando su rango de invariantes.\n" + "\n".join(ofensas)
        )
        return
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


@pytest.mark.parametrize("line", ["Version: v0.52.0", "version = v0.52.0"])
def test_version_gate_reads_colon_and_v_prefix(line):
    """Punctuation must not create a hole in the version claim gate."""
    match = VERSION_AFIRMADA.search(line)
    assert match and (match.group(1) or match.group(2)) == "0.52.0"


def test_suite_gate_catches_live_unscoped_counts_but_keeps_records():
    """Live totals fail; dated, local and handoff counts remain evidence."""
    assert _is_suite_count("The runtime currently carries 20 tests")
    assert not _is_suite_count("The runtime carries 20 tests measured 2026-08-28")
    assert not _is_suite_count("test_hub.py: 20 tests")
    assert not _is_suite_count(
        "The handoff carries 20 tests", path=RAIZ / "context/HANDOFF_HISTORICO.md"
    )
