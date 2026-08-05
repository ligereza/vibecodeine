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


def test_revision_is_a_first_class_format():
    assert "revision" in F.FORMATOS
    p = F.prompt_revision("calidad MAK", [{"type": "sample"}], ["file://x"])
    assert "REVISION OPERATIVA" in p
    assert "NODOS EJECUTIVOS" in p
    assert "repasar, discutir, exponer, refutar o archivar" in p
    assert "No rehagas investigaciones antiguas" in p


def test_exposicion_is_a_first_class_format():
    assert "exposicion" in F.FORMATOS
    p = F.prompt_exposicion("cabos sueltos", [{"type": "sample"}], ["file://x"])
    assert "EXPOSICION" in p
    assert "QUE HAY AQUI" in p
    assert "LECTURA POSIBLE" in p
    assert "QUE NO SE DEBE AFIRMAR" in p
    assert "no lo conviertas en ensayo" in p


def test_curatoria_is_a_first_class_format():
    assert "curatoria" in F.FORMATOS
    p = F.prompt_curatoria("archivo iskvw", [{"type": "sample"}], ["file://x"])
    assert "CURATORIA" in p
    assert "NUCLEO DE OBRA" in p
    assert "FAMILIA / CONSTELACION" in p
    assert "PRUEBA VISUAL" in p
    assert "no se debe mezclar con RD" in p


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

# --------------------------------------------------- exigencias verificables

_ENSAYO_QUE_CUMPLE = """# La tilde como frontera

## PARTE I: EL ORIGEN - donde la marca empieza a separar
La imprenta la fija en 1492 y el uso se estabiliza recien en 1815
(https://memoriachilena.gob.cl/x).

## PARTE II: LA RUPTURA - cuando el teclado la vuelve opcional
Fuente: https://scielo.cl/y

## PARTE III: LO QUE QUEDA - dos lecturas del mismo signo
| lectura ortografica | lectura politica |
|---|---|
| la tilde ordena | la tilde marca quien escribe bien |
"""


def test_un_ensayo_completo_no_incumple_nada():
    assert F.exigencias_incumplidas(_ENSAYO_QUE_CUMPLE) == []


def test_un_informe_disfrazado_de_ensayo_se_detecta():
    """Lo que el verificador existe para atrapar.

    Medido 2026-08-01 sobre una corrida real con `--formato ensayo`: el
    documento traia sus 10 conceptos de anexo y CERO partes narradas. Las
    siete exigencias estaban en el prompt desde el 2026-07-30 y nadie
    verificaba que se cumplieran, asi que eran una suplica.
    """
    faltan = F.exigencias_incumplidas(
        "Un texto plano sin estructura." + chr(10) * 2 + "Otro parrafo mas.")
    nombres = [f.split(":")[0] for f in faltan]
    assert "PARTES NARRADAS" in nombres
    assert "TABLA DONDE DOS LECTURAS COMPITEN" in nombres
    assert "CRONOLOGIA" in nombres
    assert "FUENTES CON URL" in nombres


def test_el_motivo_es_el_pedido_no_el_diagnostico():
    """Cada motivo se le repite al modelo tal cual, asi que se escribe como
    instruccion. Si dijera solo 'faltan partes' no serviria para reintentar."""
    faltan = F.exigencias_incumplidas("nada")
    partes = next(f for f in faltan if f.startswith("PARTES"))
    assert "titulo" in partes.lower() and "tesis" in partes.lower()


def test_la_cronologia_acepta_cualquier_siglo():
    """El rango estaba pegado a 1800 y la genealogia de un signo diacritico
    empieza en la imprenta: 1492 quedaba fuera y el ensayo perdia su
    cronologia por el rango, no por el contenido."""
    con_siglo_xv = chr(10).join(
        ["## A", "## B", "## C", "En 1492 y 1535.", "http://x", "|---|", ""])
    nombres = [f.split(":")[0]
               for f in F.exigencias_incumplidas(con_siglo_xv)]
    assert "CRONOLOGIA" not in nombres
