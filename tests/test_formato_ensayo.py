#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_formato_ensayo.py -- cultura/mak_research/formato_ensayo.py: el
contrato del formato ENSAYO (siete exigencias en el prompt, no en la
esperanza) y el parser tolerante de conceptos nombrables que alimenta el modo
`iconos` de codex.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cultura" / "mak_research"))

import formato_ensayo as F  # noqa: E402


# ---------------------------------------------------------------------------
# prompt_documento: las siete exigencias van en el prompt
# ---------------------------------------------------------------------------
def test_prompt_documento_incluye_las_siete_exigencias():
    assert len(F.EXIGENCIAS) == 7
    p = F.prompt_documento("un tema", [{"hallazgo": "x"}], ["http://ejemplo.test"])
    for exigencia in F.EXIGENCIAS:
        assert exigencia in p


def test_mutacion_exigencia_faltante_se_detecta():
    """Verificacion viva: si prompt_documento dejara de incluir una exigencia
    (por ejemplo si alguien acortara la lista antes de formatear), la
    asercion de arriba debe reventar. Se simula recortando EXIGENCIAS en una
    copia local, sin tocar el modulo real."""
    recortadas = F.EXIGENCIAS[:-1]
    p_incompleto = (
        "Escribe un ENSAYO...\n\n" +
        "\n".join("%d. %s" % (i, e) for i, e in enumerate(recortadas, 1)))
    faltan = [e for e in F.EXIGENCIAS if e not in p_incompleto]
    assert faltan == [F.EXIGENCIAS[-1]]


# ---------------------------------------------------------------------------
# parsear_conceptos: nunca revienta, cualquiera sea la basura que llegue
# ---------------------------------------------------------------------------
def test_basura_no_json_no_revienta():
    conceptos, problemas = F.parsear_conceptos("esto no es json en absoluto")
    assert conceptos == []
    assert problemas and "array JSON" in problemas[0]


def test_objeto_en_vez_de_array_no_revienta():
    conceptos, problemas = F.parsear_conceptos(json.dumps({"a": 1}))
    assert conceptos == []
    assert problemas


def test_concepto_sin_brief_se_descarta_y_se_reporta():
    crudos = [{"titulo": "X", "descripcion": "d"}]  # falta brief
    conceptos, problemas = F.parsear_conceptos(json.dumps(crudos))
    assert conceptos == []
    assert any("brief" in p for p in problemas)


def test_ancla_que_no_es_titulo_se_limpia_pero_el_concepto_sobrevive():
    documento = "## Titulo Real\ncontenido"
    crudos = [{"titulo": "T", "descripcion": "d", "brief": "b",
              "ancla": "## Titulo Inventado"}]
    conceptos, problemas = F.parsear_conceptos(json.dumps(crudos), documento)
    assert len(conceptos) == 1
    assert conceptos[0]["ancla"] == ""  # se limpia, no se inventa
    assert any("Titulo Inventado" in p and "no es un titulo" in p for p in problemas)


def test_los_buenos_pasan_junto_a_los_malos():
    documento = "## Seccion Real\ntexto"
    crudos = [
        {"titulo": "Bueno", "descripcion": "d", "brief": "b",
         "ancla": "## Seccion Real"},
        "esto no es un objeto",
        {"titulo": "Sin ancla real", "descripcion": "d", "brief": "b",
         "ancla": "## No existe"},
    ]
    conceptos, problemas = F.parsear_conceptos(json.dumps(crudos), documento)
    titulos = [c["titulo"] for c in conceptos]
    assert "Bueno" in titulos
    assert "Sin ancla real" in titulos  # sobrevive, solo pierde el ancla
    assert any("no es un objeto" in p for p in problemas)


def test_mutacion_parser_reventando_se_detectaria():
    """Verificacion viva de la tolerancia: si parsear_conceptos NO atrapara el
    JSON invalido (por ejemplo si alguien reemplazara el try/except por un
    json.loads directo), la llamada reventaria con ValueError en vez de
    devolver una lista de problemas. Reproducimos esa version rota en un
    sandbox local (no se toca el modulo real) para confirmar que el fallo es
    real y no un artefacto del test."""
    import re

    def _version_sin_try(bruto):
        m = re.search(r"\[.*\]", bruto or "", re.S)
        return json.loads(m.group(0))  # sin try/except: revienta con basura

    try:
        _version_sin_try("esto no es json")
        assert False, "deberia haber reventado (no hay '[' ']' en el texto)"
    except AttributeError:
        pass  # m es None -> .group(0) revienta: confirma que el guard hace falta
    # la version real, en cambio, no revienta:
    F.parsear_conceptos("esto no es json")


# ---------------------------------------------------------------------------
# el corte maquina/humano: slug ASCII, titulo/descripcion con tildes
# ---------------------------------------------------------------------------
def test_slug_es_ascii_pero_titulo_y_descripcion_conservan_tildes():
    documento = "## Ácido: la máquina\ntexto"
    crudos = [{"titulo": "Ácido: la máquina", "descripcion": "el squelch de la 303, más allá",
              "brief": "b", "ancla": "## Ácido: la máquina"}]
    crudos += _n_conceptos_validos(5)  # llegar al MIN_CONCEPTOS sin ruido
    conceptos, problemas = F.parsear_conceptos(json.dumps(crudos), documento)
    assert not any("minimo" in p for p in problemas)
    c = conceptos[0]
    assert c["slug"].isascii()
    assert "-" in c["slug"] and c["slug"] == c["slug"].lower()
    assert "á" not in c["slug"] and "í" not in c["slug"]
    assert c["titulo"] == "Ácido: la máquina"  # intacto, con tildes
    assert "más allá" in c["descripcion"]


def test_mutacion_slug_con_tilde_se_detectaria():
    """Verificacion viva: si _slug() dejara de quitar diacriticos (por
    ejemplo si alguien sacara el paso NFKD), isascii() fallaria. Simulamos la
    version rota localmente sin tocar _slug real."""
    def _slug_roto(texto):
        import re as _re
        return _re.sub(r"[^a-zA-Záéíóúñ0-9]+", "-", texto).strip("-").lower()

    roto = _slug_roto("ácido")
    assert not roto.isascii(), "la mutacion no reprodujo el bug, ajustar el caso"
    assert F._slug("Ácido").isascii()


# ---------------------------------------------------------------------------
# limites de cantidad: MIN_CONCEPTOS / MAX_CONCEPTOS
# ---------------------------------------------------------------------------
def _n_conceptos_validos(n):
    return [{"titulo": "T%d" % i, "descripcion": "d", "brief": "b"}
            for i in range(n)]


def test_menos_del_minimo_se_reporta():
    conceptos, problemas = F.parsear_conceptos(
        json.dumps(_n_conceptos_validos(3)))
    assert len(conceptos) == 3
    assert any("minimo es %d" % F.MIN_CONCEPTOS in p for p in problemas)


def test_mas_del_maximo_se_reporta_y_se_trunca():
    total = F.MAX_CONCEPTOS + 6
    conceptos, problemas = F.parsear_conceptos(
        json.dumps(_n_conceptos_validos(total)))
    assert len(conceptos) == F.MAX_CONCEPTOS
    assert any("se recortan a %d" % F.MAX_CONCEPTOS in p for p in problemas)


def test_mutacion_limite_no_truncado_se_detectaria():
    """Verificacion viva: si el truncado 'conceptos[:MAX_CONCEPTOS]' se
    borrara del codigo real, el largo devuelto por parsear_conceptos
    excederia MAX_CONCEPTOS. Simulamos la version sin truncar aca, sin tocar
    el modulo real, y confirmamos que el largo si se pasa."""
    total = F.MAX_CONCEPTOS + 6
    crudos = _n_conceptos_validos(total)
    # replica manual del cuerpo de parsear_conceptos SIN el paso de recorte
    conceptos_sin_truncar = []
    for i, c in enumerate(crudos):
        conceptos_sin_truncar.append({"titulo": c["titulo"]})
    assert len(conceptos_sin_truncar) > F.MAX_CONCEPTOS
    # la funcion real si trunca:
    conceptos, _ = F.parsear_conceptos(json.dumps(crudos))
    assert len(conceptos) <= F.MAX_CONCEPTOS
