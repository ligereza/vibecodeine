# -*- coding: utf-8 -*-
"""La compuerta de fuente, fijada contra el caso real que la motivo.

El caso: `docs/rd/informes/ley_20000_marco_legal.md` (2026-07-22) afirma sobre
el ISP y el MINSAL citando -- segun su propio `meta:` -- un PDF de una escuela
de pedagogia peruana, uno de una universidad venezolana, y un agregador de
libros pirateados. Los tres URLs de este archivo son los tres reales de ese
informe. Si algun dia esta compuerta deja pasar ese caso, estos tests fallan.

Lo que NO se prueba aca: que la lista de hosts primarios sea completa. No lo es,
y no se afirma que lo sea; se afirma que los que estan, cuentan, y que los
buscadores y agregadores nunca cuentan.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cultura" / "mak_research"))

import fuentes  # noqa: E402

# Los tres URLs reales del informe malo.
FUENTES_DEL_INFORME_MALO = [
    "https://eesppnsrmadrededios.edu.pe/libros/1.pdf",
    "http://www.mriuc.bc.uc.edu.ve/bitstream/123456789/4300/3/tomo3.pdf",
    "https://dokumen.pub/estructura-social-de-chile-estudio-seleccion-de-textos-y-bibliografia.html",
]


def test_el_informe_malo_no_habria_pasado():
    """El caso que motivo el modulo: cero primarias sobre derecho chileno."""
    assert not fuentes.hay_primaria(FUENTES_DEL_INFORME_MALO, "cl_legal")
    ev = fuentes.evaluar("Ley 20.000 Chile y marco legal para una ONG", FUENTES_DEL_INFORME_MALO)
    assert ev["dominio"] == "cl_legal"
    assert ev["sin_fuente_primaria"] is True
    assert ev["marca"] == "SIN FUENTE PRIMARIA"
    assert ev["fuentes_primarias"] == []


def test_sin_primaria_el_encabezado_prohibe_citar():
    txt = fuentes.encabezado(FUENTES_DEL_INFORME_MALO, "cl_legal")
    assert "SIN FUENTE PRIMARIA" in txt
    assert "NO afirma" in txt
    assert "No citar como respaldo" in txt
    # y deja registrado que se consulto, para poder auditar despues
    assert "eesppnsrmadrededios" in txt


def test_sin_primaria_la_instruccion_cambia_la_tarea():
    """No alcanza con marcar el informe: hay que impedir que el modelo afirme."""
    ins = fuentes.instruccion_sintesis(FUENTES_DEL_INFORME_MALO, "cl_legal")
    assert "PROHIBIDO afirmar" in ins
    assert "reportar la ausencia" in ins


def test_con_primaria_el_encabezado_desaparece_y_pide_citar():
    urls = ["https://www.bcn.cl/leychile/navegar?idNorma=235507"] + FUENTES_DEL_INFORME_MALO
    assert fuentes.hay_primaria(urls, "cl_legal")
    assert fuentes.encabezado(urls, "cl_legal") == ""
    ins = fuentes.instruccion_sintesis(urls, "cl_legal")
    assert "fuente primaria" in ins and "citarla" in ins


def test_los_buscadores_y_agregadores_nunca_son_primaria():
    """El informe de becas listo `scholar.google.com.mx` como fuente: es una
    portada de buscador, no un documento. Que aparezca en `sources` significa
    que el fetch devolvio algo, no que contenga la respuesta."""
    urls = ["https://scholar.google.com.mx/", "https://es.wikipedia.org/wiki/Ley_20.000"]
    prim, sec = fuentes.clasificar(urls, "cl_legal")
    assert prim == []
    assert len(sec) == 2


def test_detecta_el_dominio_por_el_tema():
    assert fuentes.dominio_de_tema("Ley 20.000 Chile: marco legal para una ONG") == "cl_legal"
    assert fuentes.dominio_de_tema("Fondart convocatoria 2026 postulacion") == "cl_fondos"
    assert fuentes.dominio_de_tema("GDTF y MVR: DIN SPEC para intercambio") == "norma_tecnica"


def test_los_temas_culturales_no_pasan_por_la_compuerta():
    """La mayoria de las preguntas de research NO tienen fuente primaria y la
    compuerta no debe estorbarlas: sin dominio, no hay marca."""
    ev = fuentes.evaluar("iconografia del double cup en la cultura visual del trap", [])
    assert ev["dominio"] is None
    assert ev["sin_fuente_primaria"] is False
    assert ev["marca"] is None


def test_las_queries_sugeridas_agregan_site():
    qs = fuentes.sugerir_queries("Ley 21.817 agravantes", "cl_legal")
    assert qs[0] == "Ley 21.817 agravantes"
    assert any("site:bcn.cl" in q for q in qs)


def test_subdominio_de_una_primaria_cuenta():
    urls = ["https://www.leychile.cl/Navegar?idNorma=1234"]
    assert fuentes.hay_primaria(urls, "cl_legal")


def test_un_host_que_solo_contiene_el_nombre_no_cuenta():
    """`bcn.cl.malicioso.com` no es la Biblioteca del Congreso."""
    assert not fuentes.hay_primaria(["https://bcn.cl.otrositio.com/x"], "cl_legal")


def test_entradas_rotas_no_rompen():
    for malas in ([], None, ["", "no-es-url", None, 42]):
        prim, sec = fuentes.clasificar(malas, "cl_legal")
        assert prim == []
