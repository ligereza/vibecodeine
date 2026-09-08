"""Tests for projects/cultura/borradura_ascii/ (borradura.py + tapiz.py).

Runs against the REAL repo at HEAD (git show), never a throwaway repo --
the Omega11 requires every minimal pair to be verifiable against real,
dated repo history, so the test must exercise the real corpus.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "projects" / "cultura" / "borradura_ascii"

sys.path.insert(0, str(PKG))
import borradura  # noqa: E402
import tapiz  # noqa: E402


def _git_show(repo: Path, sha: str, ruta: str) -> str:
    resultado = subprocess.run(
        ["git", "show", f"{sha}:{ruta}"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return resultado.stdout


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_determinismo_dos_corridas():
    """Dos corridas sobre el mismo HEAD producen el mismo reporte, byte a byte."""
    sha1, reportes1 = borradura.escanear_corpus(ROOT)
    sha2, reportes2 = borradura.escanear_corpus(ROOT)

    assert sha1 == sha2
    texto1 = borradura.render_reporte(sha1, reportes1)
    texto2 = borradura.render_reporte(sha2, reportes2)
    assert texto1 == texto2

    # el conteo por archivo tambien es identico
    conteo1 = [(r.archivo, len(r.hallazgos)) for r in reportes1]
    conteo2 = [(r.archivo, len(r.hallazgos)) for r in reportes2]
    assert conteo1 == conteo2


def test_pares_verificables_contra_git_show():
    """Toma hasta 3 hallazgos reales y confirma la palabra via git show."""
    sha, reportes = borradura.escanear_corpus(ROOT)
    hallazgos = [h for r in reportes for h in r.hallazgos]
    assert hallazgos, "el corpus operativo real debe tener al menos una borradura"

    muestra = hallazgos[:3]
    for h in muestra:
        assert h.sha_corto == sha
        contenido = _git_show(ROOT, sha, h.archivo)
        lineas = contenido.splitlines()
        assert 1 <= h.linea <= len(lineas), f"{h.archivo}:{h.linea} fuera de rango"
        linea_real = lineas[h.linea - 1]
        assert h.palabra in linea_real, (
            f"'{h.palabra}' no esta literal en {h.archivo}:{h.linea} @ {sha}"
        )


def test_solo_ano_puede_cambiar_significado():
    """
    El diccionario excluye palabras funcionales (el/si/mas/de/se/tu/mi) a
    proposito -- solo 'ano' (de 'año') puede marcarse cambia_significado.
    Si esto deja de cumplirse, alguien reintrodujo un falso positivo
    masivo (ver DOSSIER.md).
    """
    _, reportes = borradura.escanear_corpus(ROOT)
    hallazgos_cambian = [
        h for r in reportes for h in r.hallazgos if h.cambia_significado
    ]
    for h in hallazgos_cambian:
        assert h.con_marca == "año"
        assert h.palabra.lower() == "ano"


def test_no_escribe_fuera_de_su_salida(tmp_path):
    """
    Correr el escaneo + el tapiz no debe alterar NINGUN archivo del corpus
    operativo real (lectura pura, Omega11-c). Se hashea cada archivo del
    corpus antes y despues de la corrida completa.
    """
    hashes_antes = {}
    for ruta in borradura.ARCHIVOS_OPERATIVOS:
        p = ROOT / ruta
        if p.exists():
            hashes_antes[ruta] = _sha256(p)

    sha, reportes = borradura.escanear_corpus(ROOT)
    borradura.render_reporte(sha, reportes)
    tapiz.render_tapiz(ROOT, reportes, sha)

    hashes_despues = {}
    for ruta in borradura.ARCHIVOS_OPERATIVOS:
        p = ROOT / ruta
        if p.exists():
            hashes_despues[ruta] = _sha256(p)

    assert hashes_antes == hashes_despues


def test_archivo_ausente_en_commit_no_rompe():
    """leer_operativo devuelve None (no excepcion) si el archivo no existe en ese ref."""
    resultado = borradura.leer_operativo(ROOT, "context/ARCHIVO_QUE_NO_EXISTE.md")
    assert resultado is None


def test_huecos_de_palabra_mapea_por_longitud_igual():
    huecos = tapiz._huecos_de_palabra("código", "codigo")
    assert huecos == [1]  # la 'o' con tilde esta en indice 1


def test_huecos_de_palabra_longitud_distinta_marca_palabra_entera():
    huecos = tapiz._huecos_de_palabra("diseño", "disenio")
    assert huecos == list(range(len("disenio")))
