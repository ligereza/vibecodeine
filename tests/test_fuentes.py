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


# --- dominio biomedico (2026-07-31) -----------------------------------------
# El caso que lo motivo: el lote watsonx de 8 informes cientificos de reduccion
# de danos (2026-07-30) -- seis de ocho salieron con `dominio: None` y por lo
# tanto SIN exigencia de fuente primaria. Estos tests fijan que los temas
# biomedicos pasan por la misma compuerta que cl_legal.

TEMAS_BIOMEDICOS = [
    "farmacologia de la MDMA y neurotoxicidad en consumo recreativo",
    "epidemiologia del consumo de estimulantes en Chile",
    "drug checking en eventos masivos: evidencia de reduccion de danos",
    "sobredosis por opioides sinteticos: deteccion temprana",
    "toxicidad de adulterantes en cocaina segun ensayo clinico",
]


def test_detecta_dominio_biomedico_por_el_tema():
    for tema in TEMAS_BIOMEDICOS:
        assert fuentes.dominio_de_tema(tema) == "biomedico", tema


def test_detecta_dominio_con_tildes():
    """Las preguntas cosechadas de informes vienen en castellano correcto, CON
    tildes; las pistas son ASCII. Sin plegado de diacriticos la compuerta se
    salta exactamente los temas que debe vigilar."""
    assert fuentes.dominio_de_tema(
        "farmacología y toxicología de la ketamina") == "biomedico"
    assert fuentes.dominio_de_tema(
        "reducción de daños en fiestas electrónicas") == "biomedico"
    # y el plegado tambien repara a los dominios viejos:
    assert fuentes.dominio_de_tema(
        "código penal chileno y sanciones por microtráfico") == "cl_legal"


def test_cl_legal_gana_sobre_biomedico_en_tema_legal():
    """Un tema legal que menciona reduccion de danos sigue siendo cl_legal:
    el orden del dict decide y biomedico va ultimo a proposito."""
    tema = ("Ley 20.000 Chile y marco legal para servicios de analisis de "
            "sustancias y reduccion de danos")
    assert fuentes.dominio_de_tema(tema) == "cl_legal"


def test_biomedico_exige_primaria_igual_que_cl_legal():
    """Sin primaria: mismo mecanismo que cl_legal -- marca, encabezado que
    prohibe citar e instruccion que cambia la tarea."""
    tema = TEMAS_BIOMEDICOS[0]
    ev = fuentes.evaluar(tema, FUENTES_DEL_INFORME_MALO)
    assert ev["dominio"] == "biomedico"
    assert ev["sin_fuente_primaria"] is True
    assert ev["marca"] == "SIN FUENTE PRIMARIA"
    txt = fuentes.encabezado(FUENTES_DEL_INFORME_MALO, "biomedico")
    assert "SIN FUENTE PRIMARIA" in txt
    assert "No citar como respaldo" in txt
    ins = fuentes.instruccion_sintesis(FUENTES_DEL_INFORME_MALO, "biomedico")
    assert "PROHIBIDO afirmar" in ins


def test_biomedico_reconoce_sus_primarias():
    urls = [
        "https://pubmed.ncbi.nlm.nih.gov/31013837/",
        "https://www.scielo.cl/scielo.php?pid=S0034-98872020000700123",
        "https://www.who.int/publications/i/item/9789240088254",
        "https://www.euda.europa.eu/publications/european-drug-report/2025_en",
        "https://www.ispch.gob.cl/anamed/farmacovigilancia/",
        "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012021",
        "https://eesppnsrmadrededios.edu.pe/libros/1.pdf",
    ]
    prim, sec = fuentes.clasificar(urls, "biomedico")
    assert len(prim) == 6
    assert sec == ["https://eesppnsrmadrededios.edu.pe/libros/1.pdf"]
    ev = fuentes.evaluar(TEMAS_BIOMEDICOS[1], urls)
    assert ev["dominio"] == "biomedico"
    assert ev["sin_fuente_primaria"] is False
    assert ev["marca"] is None
    assert fuentes.encabezado(urls, "biomedico") == ""


def test_biomedico_scholar_no_es_primaria():
    """scholar.google indexa PubMed pero no ES PubMed: sigue en NUNCA_PRIMARIA."""
    assert not fuentes.hay_primaria(
        ["https://scholar.google.com/scholar?q=mdma+neurotoxicity"], "biomedico")


def test_biomedico_queries_sugeridas_agregan_site():
    qs = fuentes.sugerir_queries("farmacologia de la ketamina", "biomedico")
    assert qs[0] == "farmacologia de la ketamina"
    assert any("site:pubmed.ncbi.nlm.nih.gov" in q for q in qs)
    assert any("site:scielo.org" in q for q in qs)


def test_los_temas_culturales_siguen_sin_dominio():
    """La compuerta nueva no debe estorbar la investigacion cultural: un tema
    de estetica que no habla de farmacologia ni epidemiologia queda sin dominio."""
    assert fuentes.dominio_de_tema(
        "iconografia del double cup en la cultura visual del trap") is None
    assert fuentes.dominio_de_tema(
        "historia del vjing y el mapping en la escena de Santiago") is None


# --- event/producer domain (2026-08-05) -------------------------------------

def test_event_producer_questions_use_the_event_domain():
    assert fuentes.dominio_de_tema(
        "Quien organizo el evento del 2023-10-28 con headliner Nina Kraviz"
    ) == "cl_eventos"
    assert fuentes.dominio_de_tema(
        "Que productora llevo ese line up al Club Hípico"
    ) == "cl_eventos"


def test_event_domain_recognizes_promoter_and_ticketing_sources():
    urls = [
        "https://www.instagram.com/p/C0REAL/",
        "https://www.passline.com/eventos/fiesta-real",
        "https://noticias.example.com/nota-sobre-la-fiesta",
    ]
    prim, sec = fuentes.clasificar(urls, "cl_eventos")
    assert prim == urls[:2]
    assert sec == urls[2:]
    ev = fuentes.evaluar("quien organizo el evento del viernes", urls)
    assert ev["dominio"] == "cl_eventos"
    assert ev["sin_fuente_primaria"] is False


def test_event_domain_without_primary_source_reports_absence():
    ev = fuentes.evaluar(
        "quien organizo el evento con lineup PARTIBOI69",
        ["https://noticias.example.com/resena"],
    )
    assert ev["dominio"] == "cl_eventos"
    assert ev["sin_fuente_primaria"] is True
    assert ev["fuentes_primarias"] == []
    assert ev["marca"] == "SIN FUENTE PRIMARIA"
