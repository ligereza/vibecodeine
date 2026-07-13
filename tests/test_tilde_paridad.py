"""Tests de la auditoria de paridad (projects/cultura/tilde_paridad.py).

Semilla (+)3: la Tilde es residuo intraducible, no conteo. Esta pieza pone al
medidor (tilde_meter, conteo) en el banco contra el instrumento honesto
(tilde_residuo, costo) y cosecha donde sus rankings se invierten. Los literales
con marcas van con escapes \\uXXXX para no depender de como el editor guarde
NFC/NFD (mismo criterio que test_tilde_residuo.py).
"""

import sys
from pathlib import Path

CULTURA_DIR = Path(__file__).resolve().parents[1] / "projects" / "cultura"
sys.path.insert(0, str(CULTURA_DIR))

from tilde_paridad import (  # noqa: E402
    analizar_texto,
    auditar,
    corpus_desde_archivo,
    detectar_inversiones,
    render,
)

# "ano" con virgulilla: pierde 1 marca (la n con ~), pero es FILOSO (ano/ano,
# inversion de sentido; su costo curado lleva la flecha '->' mas glosa entre
# parentesis).
_ANIO = "año"
# "Vamos? Ya!" con aperturas: pierde 2 marcas (inv. question + inv. exclamation),
# pero NINGUNA es filosa (las aperturas marcan posicion, su costo no lleva '->').
_APERTURAS = "¿Vamos? ¡Ya!"
# "pinguino" con dieresis: su unica marca es la u con dieresis. Su costo curado
# lleva '->' (pinguino/pinguino) pero NO glosa entre parentesis: es perdida
# fonetica, la MISMA palabra, no inversion de sentido. NO debe contar como filoso.
_DIERESIS = "pingüino"


def test_inversion_detectada():
    # El medidor dice que _ANIO se perdio MENOS (1 < 2 marcas) que _APERTURAS,
    # pero el honesto dice que _ANIO cuesta MAS (carga residuo filoso, el otro no).
    # Ese desacuerdo es la Tilde de esta pieza.
    casos, veredicto, motivo = auditar([_ANIO, _APERTURAS])
    assert veredicto == "auditable"
    inversiones = detectar_inversiones(casos)
    assert len(inversiones) == 1
    x, y = inversiones[0]
    assert x.texto == _ANIO
    assert y.texto == _APERTURAS
    assert x.marcas_perdidas < y.marcas_perdidas   # medidor: X menos degradado
    assert x.tiene_filoso and not y.tiene_filoso    # honesto: X cuesta mas
    salida = render(casos, veredicto, motivo)
    assert "INVERSION" in salida


def test_loud_fail_corpus_sin_marcas():
    # Corpus dominado por ASCII/ingles (como los commits reales del repo): solo un
    # texto marcado -> no hay senal para comparar rankings. La pieza NO inventa:
    # dice ruido (restriccion tipo Davidson), no un resultado.
    casos, veredicto, motivo = auditar(["chore: merge origin/main", "fix build", _ANIO])
    assert veredicto == "ruido"
    assert "insufficient signal" in motivo
    salida = render(casos, veredicto, motivo)
    assert "[ruido]" in salida


def test_determinismo():
    # Mismo corpus -> misma salida exacta (orden estable por (marcas, texto)).
    corpus = [_ANIO, _APERTURAS, "café y más"]
    r1 = render(*auditar(corpus))
    r2 = render(*auditar(corpus))
    assert r1 == r2


def test_no_colapsa_a_un_puntaje():
    # El nucleo de (+)3: la auditoria no puede reducirse a un unico numero (eso
    # seria el dialecto degradado que audita). El detalle por caso queda primario.
    salida = render(*auditar([_ANIO, _APERTURAS]))
    assert "por caso" in salida
    assert "token" not in salida.lower()


def test_dieresis_no_es_filoso():
    # La u con dieresis tiene costo curado (entra al banco) pero su perdida es
    # fonetica -- la misma palabra, sin glosa entre parentesis -- asi que NO es
    # filosa. El fix de _es_filoso exige '->' MAS '(' para no confundirla con una
    # inversion de sentido.
    caso = analizar_texto(_DIERESIS)
    assert caso is not None            # tiene marca: no queda fuera del banco
    assert caso.curados                # la dieresis SI tiene costo curado
    assert caso.filosos == []          # pero su costo no es de inversion de sentido
    assert caso.tiene_filoso is False


def test_corpus_desde_archivo(tmp_path):
    # Exercita el override --file: un asunto por linea, lineas en blanco se
    # descartan. Corpus portable para correr sin git.
    p = tmp_path / "corpus.txt"
    p.write_text(f"{_ANIO}\n{_APERTURAS}\n\nfix build\n", encoding="utf-8")
    textos = corpus_desde_archivo(str(p))
    assert textos == [_ANIO, _APERTURAS, "fix build"]
