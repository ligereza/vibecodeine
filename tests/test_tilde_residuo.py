"""Tests del cosechador de Tilde (projects/cultura/tilde_residuo.py).

Semilla (+)3: la Tilde es residuo intraducible, no conteo de tokens. Los
literales acentuados van con escapes \\uXXXX para no depender de como el editor
guarde NFC/NFD.
"""

import sys
from pathlib import Path

CULTURA_DIR = Path(__file__).resolve().parents[1] / "projects" / "cultura"
sys.path.insert(0, str(CULTURA_DIR))

from tilde_residuo import cosechar, plegar, render  # noqa: E402


def test_ano_pierde_la_virgulilla():
    # "ano" (con virgulilla) -> "ano": el residuo mas filoso.
    c = cosechar("año")
    assert c.fondo == "ano"
    assert c.veredicto == "tilde" and c.es_tilde
    assert len(c.residuos) == 1
    r = c.residuos[0]
    assert r.plegado == "n"
    assert r.marca == "COMBINING TILDE"
    assert "ano" in r.costo  # nombra el par minimo con costo de significado


def test_acento_agudo_es_residuo():
    c = cosechar("papá")  # "papa" (dad)
    assert c.fondo == "papa"
    assert c.veredicto == "tilde"
    assert any(r.marca == "COMBINING ACUTE ACCENT" for r in c.residuos)


def test_apertura_invertida_es_residuo():
    c = cosechar("¿qué?")  # "¿que?"
    marcas = [r.marca for r in c.residuos]
    assert "INVERTED QUESTION MARK" in marcas
    assert "que" in c.fondo  # el fondo sigue legible


def test_traduccion_total_no_tiene_residuo():
    c = cosechar("hola mundo")
    assert c.veredicto == "traduccion_total"
    assert c.residuos == []
    assert not c.es_tilde


def test_sin_fondo_legible_es_ruido_no_tilde():
    # Restriccion de Davidson: sin fondo de traduccion, es ruido, no Tilde.
    c = cosechar("\U0001F3B5\U0001F3B6")
    assert c.veredicto == "ruido"
    assert not c.es_tilde
    assert c.residuos == []


def test_cosecha_es_invariante_a_la_normalizacion():
    # "n con virgulilla" precompuesta (NFC) o descompuesta (NFD) es el mismo
    # caracter -> misma cosecha. (Este era el bug que el run destapo.)
    nfc = cosechar("ñ")       # n con virgulilla precompuesta (NFC)
    nfd = cosechar("ñ")      # n + COMBINING TILDE (NFD)
    assert nfc.fondo == nfd.fondo == "n"
    assert [r.marca for r in nfc.residuos] == [r.marca for r in nfd.residuos] == ["COMBINING TILDE"]


def test_no_devuelve_conteo_de_tokens():
    # El nucleo de (+)3: la Tilde NO es un numero. Ni la cosecha ni el render
    # hablan de tokens.
    salida = render(cosechar("El año pasado hablás español")).lower()
    assert "token" not in salida


def test_plegar_deja_fondo_legible():
    # "¿Aún hablás español?" -> fondo ASCII legible.
    assert plegar("¿Aún hablás español?") == "Aun hablas espanol?"
