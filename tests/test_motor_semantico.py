#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_motor_semantico.py -- el compilador semantico (spec cerrado ->
SVG animado), sobre specs REALES de lote.json y sobre el vocabulario real, sin
mockear nada. Cubre los cuatro modos de falla que el motor elimina POR
CONSTRUCCION (ver docstring de compilador.py): invisibilidad al frame 0,
desborde de texto, contraste WCAG y XML mal formado -- y el pegamento
esquema<->vocabulario<->compilador que hace que no puedan divergir.
"""
import copy
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cultura" / "mak_codex"))

from motor_semantico import algebra, compilador, esquema, vocabulario  # noqa: E402

LOTE_PATH = REPO / "cultura" / "mak_codex" / "motor_semantico" / "lote.json"
LOTE = json.loads(LOTE_PATH.read_text(encoding="utf-8"))

NS = "{http://www.w3.org/2000/svg}"


def _local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def _grupos_capa(svg_txt):
    """Devuelve la lista de elementos <g id="capa-N-rol"> del SVG, en orden."""
    root = ET.fromstring(svg_txt.split("?>", 1)[-1])
    return [el for el in root.iter() if _local(el.tag) == "g"
            and el.get("id", "").startswith("capa-")]


def _entra_invisible(svg_txt):
    """True si algun @keyframes del <style> define, para el selector "0%"
    (aislado o en una lista separada por comas: "0%,55%{...}"), una entrada
    con opacity:0 o transform:scale(0). Eso es exactamente lo que el
    invariante 3 del compilador prohibe."""
    estilo = "".join(re.findall(r"<style>(.*?)</style>", svg_txt, re.S))
    for cuerpo_kf in re.findall(r"@keyframes\s+[A-Za-z0-9_-]+\s*\{(.+?)\}\}",
                                estilo, re.S):
        for selectores, propiedades in re.findall(
                r"([\d.]+%(?:\s*,\s*[\d.]+%)*)\s*\{([^}]*)\}", cuerpo_kf):
            partes = [s.strip() for s in selectores.split(",")]
            if "0%" not in partes:
                continue
            if re.search(r"opacity\s*:\s*0(?:[;}]|$)", propiedades):
                return True
            if "scale(0)" in propiedades.replace(" ", ""):
                return True
    return False


# ---------------------------------------------------------------------------
# 1. el lote real: 9 compilan, 1 se rechaza con motivo
# ---------------------------------------------------------------------------
def _compilar_lote():
    compilados, rechazado = {}, None
    for spec in LOTE:
        try:
            svg, avisos = compilador.compilar(spec, spec["slug"])
            compilados[spec["slug"]] = (svg, avisos)
        except compilador.ErrorSemantico as e:
            assert rechazado is None, "mas de un spec del lote se rechazo"
            rechazado = (spec["slug"], e)
    return compilados, rechazado


def test_nueve_compilan_una_se_rechaza():
    compilados, rechazado = _compilar_lote()
    assert len(compilados) == 9
    assert rechazado is not None
    slug, error = rechazado
    assert slug == "10-inclusividad"


def test_el_rechazo_nombra_la_capa_faltante():
    _, (slug, error) = _compilar_lote()
    assert "protagonista" in str(error)


def test_los_nueve_compilados_son_xml_valido_con_viewbox_120():
    compilados, _ = _compilar_lote()
    for slug, (svg, _avisos) in compilados.items():
        root = ET.fromstring(svg.split("?>", 1)[-1])
        assert root.get("viewBox") == "0 0 120 120", slug


# ---------------------------------------------------------------------------
# 2a. nada invisible en el frame 0
# ---------------------------------------------------------------------------
def test_nada_invisible_al_frame_0():
    compilados, _ = _compilar_lote()
    for slug, (svg, _avisos) in compilados.items():
        # ningun elemento con opacidad/visibilidad estatica que lo oculte
        assert 'opacity="0"' not in svg, slug
        assert 'opacity=".0"' not in svg, slug
        assert 'visibility="hidden"' not in svg, slug
        # ninguna entrada de animacion arranca invisible/con escala 0 en 0%
        assert not _entra_invisible(svg), slug


def test_mutacion_frame0_gesto_roto_lo_atrapa():
    """Verificacion viva: si un gesto arrancara invisible en 0%, el test de
    arriba lo agarra. Rompemos 'aparecer_ciclico' (usado en el lote real, specs
    04 y 09... en realidad 04) para que el 0% empiece en opacity:0 y
    confirmamos que la asercion revienta -- despues restauramos EXACTO."""
    original = vocabulario.GESTOS["aparecer_ciclico"]
    # la plantilla usa llaves dobles ({{ }}) porque pasa por .format(); hay que
    # mutar sobre la plantilla cruda, no sobre el CSS ya expandido.
    roto_css = original[0].replace("0%,55%{{opacity:1", "0%,55%{{opacity:0")
    assert roto_css != original[0], "la plantilla cambio de forma, ajustar el replace"
    vocabulario.GESTOS["aparecer_ciclico"] = (roto_css, original[1])
    try:
        compilados, _ = _compilar_lote()
        assert "04-taz-efimera" in compilados
        svg, _ = compilados["04-taz-efimera"]
        assert _entra_invisible(svg), "la mutacion no se reflejo en el SVG compilado"
    finally:
        vocabulario.GESTOS["aparecer_ciclico"] = original
    # tras restaurar, el spec vuelve a pasar limpio
    svg, _ = compilador.compilar(
        next(s for s in LOTE if s["slug"] == "04-taz-efimera"), "04-taz-efimera")
    assert not _entra_invisible(svg)


# ---------------------------------------------------------------------------
# 2b. texto: rechazo por desborde y reduccion cuando aun cabe
# ---------------------------------------------------------------------------
def _spec_texto(texto):
    return {"slug": "t", "composicion": "centro_unico", "tono": "acido",
            "capas": [{"rol": "protagonista", "texto": texto}]}


def test_texto_demasiado_largo_se_rechaza_con_el_maximo_en_el_mensaje():
    texto = "X" * 40
    with pytest.raises(compilador.ErrorSemantico) as ei:
        compilador.compilar(_spec_texto(texto), "t")
    msg = str(ei.value)
    assert "40 caracteres" in msg
    assert "no cabe" in msg
    assert re.search(r"[Mm].ximo ~\d+ caracteres", msg)


def test_texto_que_desborda_pero_cabe_reducido_deja_aviso():
    texto = "X" * 20
    svg, avisos = compilador.compilar(_spec_texto(texto), "t")
    assert any("reducido" in a and "px" in a for a in avisos)
    root = ET.fromstring(svg.split("?>", 1)[-1])
    assert root.get("viewBox") == "0 0 120 120"


# ---------------------------------------------------------------------------
# 2c. contraste WCAG en las 9 paletas
# ---------------------------------------------------------------------------
def test_contraste_minimo_en_las_nueve_paletas():
    assert len(vocabulario.TONOS) == 9
    for nombre, pal in vocabulario.TONOS.items():
        c = compilador.contraste(pal["principal"], pal["fondo"])
        if c < compilador.CONTRASTE_MIN:
            alt = max(("principal", "acento", "tinta"),
                      key=lambda k: compilador.contraste(pal[k], pal["fondo"]))
            c = compilador.contraste(pal[alt], pal["fondo"])
        assert c >= compilador.CONTRASTE_MIN, nombre


def test_mutacion_contraste_forzado_activa_la_correccion():
    """Rompemos 'concreto' (el de menor contraste real, 5.57:1) bajando su
    'principal' a algo casi identico al fondo, y confirmamos que compilar()
    aplica la correccion y deja aviso -- despues restauramos EXACTO."""
    original = dict(vocabulario.TONOS["concreto"])
    vocabulario.TONOS["concreto"]["principal"] = vocabulario.TONOS["concreto"]["fondo"]
    try:
        assert compilador.contraste(
            vocabulario.TONOS["concreto"]["principal"],
            vocabulario.TONOS["concreto"]["fondo"]) < compilador.CONTRASTE_MIN
        spec = {"slug": "t", "composicion": "centro_unico", "tono": "concreto",
                "capas": [{"rol": "protagonista", "figura": "disco"}]}
        svg, avisos = compilador.compilar(spec, "t")
        assert any("contraste" in a for a in avisos)
    finally:
        vocabulario.TONOS["concreto"].clear()
        vocabulario.TONOS["concreto"].update(original)
    # restaurado: ya no hace falta corregir
    c = compilador.contraste(vocabulario.TONOS["concreto"]["principal"],
                             vocabulario.TONOS["concreto"]["fondo"])
    assert c >= compilador.CONTRASTE_MIN


# ---------------------------------------------------------------------------
# 2d. seguridad XML: texto con & < > no rompe el parseo ni se filtra crudo
# ---------------------------------------------------------------------------
def test_texto_con_caracteres_especiales_escapa_y_parsea():
    texto = "A & B <script>"
    svg, _avisos = compilador.compilar(_spec_texto(texto), "t")
    # parsea sin ParseError
    ET.fromstring(svg.split("?>", 1)[-1])
    # el texto crudo NUNCA aparece sin escapar
    assert "A & B <script>" not in svg
    assert "&amp;" in svg
    assert "&lt;script&gt;" in svg


def test_mutacion_sin_escapado_rompe_el_xml():
    """Verificacion viva de la asercion anterior: si el compilador dejara de
    escapar, el SVG producido no parsearia. Simulamos el string sin escapar
    directamente (no tocamos el compilador) para confirmar que el ParseError
    es real y no un artefacto del test."""
    crudo = ('<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
             'viewBox="0 0 120 120"><text>A & B <script></script></text></svg>')
    with pytest.raises(ET.ParseError):
        ET.fromstring(crudo.split("?>", 1)[-1])


# ---------------------------------------------------------------------------
# 3. vocabulario cerrado: cada eje fuera de rango se rechaza con opciones
# ---------------------------------------------------------------------------
BASE_VALIDA = {
    "slug": "t", "composicion": "centro_unico", "tono": "acido",
    "capas": [{"rol": "protagonista", "figura": "disco", "gesto": "girar",
               "ritmo": "medio"}],
}


@pytest.mark.parametrize("campo,valor", [
    ("composicion", "no-existe"),
    ("tono", "no-existe"),
])
def test_eje_de_spec_fuera_de_vocabulario_top_level(campo, valor):
    spec = copy.deepcopy(BASE_VALIDA)
    spec[campo] = valor
    fallos = compilador.validar_spec(spec)
    assert fallos
    assert any(valor in f and "Opciones" in f for f in fallos)


@pytest.mark.parametrize("campo,valor,marcador", [
    ("figura", "no-existe", "Opciones"),
    ("gesto", "no-existe", "Opciones"),
    ("ritmo", "no-existe", "Opciones"),
    ("rol", "no-existe", "Disponibles"),
])
def test_eje_de_capa_fuera_de_vocabulario(campo, valor, marcador):
    spec = copy.deepcopy(BASE_VALIDA)
    spec["capas"][0][campo] = valor
    fallos = compilador.validar_spec(spec)
    assert fallos
    assert any(valor in f and marcador in f for f in fallos), fallos


# ---------------------------------------------------------------------------
# 4. el esquema no puede divergir del compilador/vocabulario
# ---------------------------------------------------------------------------
def test_esquema_enums_igualan_al_vocabulario_real():
    sc = esquema.construir()
    props = sc["properties"]
    capa_props = props["capas"]["items"]["properties"]
    assert sorted(props["composicion"]["enum"]) == sorted(vocabulario.COMPOSICIONES)
    assert sorted(props["tono"]["enum"]) == sorted(vocabulario.TONOS)
    assert sorted(capa_props["figura"]["enum"]) == sorted(vocabulario.FIGURAS)
    assert sorted(capa_props["gesto"]["enum"]) == sorted(vocabulario.GESTOS)
    assert sorted(capa_props["ritmo"]["enum"]) == sorted(compilador.RITMOS)
    assert sorted(capa_props["rol"]["enum"]) == sorted(vocabulario.ROLES)


def test_resumen_para_prompt_menciona_cada_figura():
    resumen = esquema.resumen_para_prompt()
    for nombre in vocabulario.FIGURAS:
        assert nombre in resumen, nombre


def test_mutacion_esquema_desincronizado_lo_atrapa():
    """Si alguien agrega una figura nueva a vocabulario.py y se olvida de que
    esquema.py la exporta via FIGURAS (no copiada a mano), la asercion de
    arriba debe reventar. Simulamos el olvido quitando una figura del
    diccionario ANTES de construir el esquema, y restauramos despues."""
    quitada = vocabulario.FIGURAS.pop("anillo")
    try:
        sc = esquema.construir()
        enum_figuras = sorted(sc["properties"]["capas"]["items"]
                              ["properties"]["figura"]["enum"])
        # vocabulario ya no tiene 'anillo' pero el compilador viejo (import
        # cacheado) seguiria aceptandola si el esquema no leyera vocabulario
        # en vivo -- lo que probamos es que la funcion SI lee en vivo:
        assert "anillo" not in enum_figuras
    finally:
        vocabulario.FIGURAS["anillo"] = quitada
    sc2 = esquema.construir()
    assert "anillo" in sc2["properties"]["capas"]["items"]["properties"]["figura"]["enum"]


# ---------------------------------------------------------------------------
# 5. capas nombradas y auditables (tesis doublecup)
# ---------------------------------------------------------------------------
def test_cada_capa_declara_lo_que_codifica():
    compilados, _ = _compilar_lote()
    for spec in LOTE:
        if spec["slug"] not in compilados:
            continue
        svg, _avisos = compilados[spec["slug"]]
        grupos = _grupos_capa(svg)
        assert len(grupos) == len(spec["capas"]), spec["slug"]
        for i, (capa, grupo) in enumerate(zip(spec["capas"], grupos)):
            rol = capa["rol"]
            assert grupo.get("id") == "capa-%d-%s" % (i, rol), spec["slug"]
            assert grupo.get("data-rol") == rol, spec["slug"]
            assert grupo.get("data-gesto") == capa.get("gesto", "quieto"), spec["slug"]
            ritmo_esperado = compilador.RITMOS[capa.get("ritmo", "medio")]
            assert grupo.get("data-ritmo") == ritmo_esperado, spec["slug"]
            if capa.get("figura"):
                assert grupo.get("data-figura") == capa["figura"], spec["slug"]
            else:
                assert grupo.get("data-figura") == "texto", spec["slug"]
            titulo = grupo.find(NS + "title")
            assert titulo is not None and (titulo.text or "").strip(), spec["slug"]


def test_mutacion_capa_sin_titulo_no_pasaria(monkeypatch):
    """Verificacion viva: si _capa_abre dejara de emitir <title>, la asercion
    anterior deberia reventar. Monkeypatcheamos _capa_abre para que omita el
    titulo, recompilamos UN spec, confirmamos el fallo, y confiamos en que
    monkeypatch deshace el cambio solo al salir de la funcion (no se toca el
    modulo de forma permanente)."""
    original = compilador._capa_abre

    def _sin_titulo(i, capa, rol, cx, cy, gesto, ritmo):
        abierto = original(i, capa, rol, cx, cy, gesto, ritmo)
        return re.sub(r"<title>.*?</title>", "", abierto)

    monkeypatch.setattr(compilador, "_capa_abre", _sin_titulo)
    spec = next(s for s in LOTE if s["slug"] == "06-criminal-justice")
    svg, _ = compilador.compilar(spec, spec["slug"])
    grupos = _grupos_capa(svg)
    assert grupos, "deberia seguir habiendo grupos capa-"
    fallo = any(g.find(NS + "title") is None for g in grupos)
    assert fallo, "la mutacion no se reflejo: el guard no esta probando nada"


# ---------------------------------------------------------------------------
# 6. algebra.py: el spec como estructura role-filler
# ---------------------------------------------------------------------------
BERLIN = next(s for s in LOTE if s["slug"] == "03-berlin-muro")
TAZ = next(s for s in LOTE if s["slug"] == "04-taz-efimera")
ACID = next(s for s in LOTE if s["slug"] == "09-acid-trance")


def test_distancia_reflexiva_y_simetrica():
    assert algebra.distancia(BERLIN, BERLIN) == 0
    assert algebra.distancia(TAZ, ACID) == algebra.distancia(ACID, TAZ)
    assert algebra.distancia(BERLIN, TAZ) > 0


def test_sustituir_cambia_el_filler_preserva_los_roles():
    v = algebra.sustituir(BERLIN, "muro", "grieta")
    assert [c["rol"] for c in v["capas"]] == [c["rol"] for c in BERLIN["capas"]]
    figuras = [c.get("figura") for c in v["capas"]]
    assert "grieta" in figuras and "muro" not in figuras
    # el spec sustituido sigue siendo compilable
    svg, _ = compilador.compilar(v, "v")
    ET.fromstring(svg.split("?>", 1)[-1])


def test_interpolar_extremos():
    assert algebra.interpolar(TAZ, ACID, 0) == TAZ
    extremo = algebra.interpolar(TAZ, ACID, 1)
    assert extremo["tono"] == ACID["tono"]


def test_cada_paso_de_interpolacion_compila():
    for t in (0, .25, .5, .75, 1):
        spec = algebra.interpolar(TAZ, ACID, t)
        svg, _avisos = compilador.compilar(spec, "paso-%s" % t)
        root = ET.fromstring(svg.split("?>", 1)[-1])
        assert root.get("viewBox") == "0 0 120 120"


def test_mutacion_distancia_asimetrica_se_detecta():
    """Rompemos distancia() para que NO sea simetrica (solo cuenta lo que
    cambio de a->b, ignorando lo que aparece nuevo en b->a) y confirmamos que
    la asercion de simetria revienta -- despues restauramos EXACTO."""
    original = algebra.distancia

    def _asimetrica(a, b):
        # solo cuenta figuras de 'a' ausentes en 'b' -- ignora lo simetrico
        figs_a = [c.get("figura") for c in a["capas"] if c.get("figura")]
        figs_b = [c.get("figura") for c in b["capas"] if c.get("figura")]
        return sum(1 for f in figs_a if f not in figs_b)

    a_chico = {"slug": "a", "composicion": "capas", "tono": "acido",
               "capas": [{"rol": "protagonista", "figura": "disco"}]}
    b_chico = {"slug": "b", "composicion": "capas", "tono": "acido",
               "capas": [{"rol": "protagonista", "figura": "disco"},
                         {"rol": "detalle", "figura": "onda"}]}
    algebra.distancia = _asimetrica
    try:
        d1 = algebra.distancia(a_chico, b_chico)
        d2 = algebra.distancia(b_chico, a_chico)
        assert d1 != d2, "la mutacion no rompio la simetria, ajustar el caso"
    finally:
        algebra.distancia = original
    assert algebra.distancia(TAZ, ACID) == algebra.distancia(ACID, TAZ)
    assert algebra.distancia(a_chico, b_chico) == algebra.distancia(b_chico, a_chico)


def test_el_prompt_muestra_la_forma_y_no_solo_la_describe():
    """Medido con un modelo real (gpt-4.1-mini via GitHub Models, tres briefs):
    SIN el ejemplo, 1 de 3 llegaba a SVG y hacian falta hasta tres rondas de
    reparacion, porque el modelo usaba el vocabulario correcto colgado de otra
    estructura y `composicion`/`tono` llegaban vacios. CON el ejemplo, 3 de 3 en
    la PRIMERA ronda.

    El vocabulario cerrado impide inventar palabras; no alcanza para fijar la
    FORMA. Por eso el ejemplo no es adorno del prompt y este test existe: si
    alguien lo saca para acortar el prompt, el rendimiento se cae y no se nota
    hasta que un modelo real falla.
    """
    resumen = esquema.resumen_para_prompt()
    assert "LA FORMA EXACTA" in resumen
    for campo in ("slug", "titulo", "composicion", "tono", "capas"):
        assert '"%s"' % campo in resumen, "el ejemplo no muestra '%s'" % campo
    # y el ejemplo tiene que ser una spec que de verdad compila
    fallos = compilador.validar_spec(esquema.EJEMPLO)
    assert not fallos, "el ejemplo del prompt no pasa su propia validacion: %s" % fallos
    svg, _ = compilador.compilar(esquema.EJEMPLO, "ejemplo")
    ET.fromstring(svg)


def test_la_frontera_con_un_modelo_se_valida_por_tipo():
    """Lo encontro un modelo REAL en el primer intento: devolvio `composicion`
    como diccionario y `validar_spec` levantaba TypeError -- y el modo `iconos`
    solo atrapa ValueError, asi que no era un rechazo con su motivo sino el modo
    entero cayendose. Un mock nunca produce esto: devuelve los tipos esperados.
    """
    malformadas = [
        {"composicion": {"a": 1}, "tono": "acido", "capas": []},
        {"composicion": "centro_unico", "tono": ["acido"], "capas": []},
        {"composicion": "centro_unico", "tono": "acido", "capas": {"x": 1}},
        {"composicion": "centro_unico", "tono": "acido", "capas": ["protagonista"]},
        {"composicion": "centro_unico", "tono": "acido",
         "capas": [{"rol": "protagonista", "figura": ["onda"]}]},
        {"composicion": "centro_unico", "tono": "acido",
         "capas": [{"rol": "protagonista", "figura": "onda", "gesto": 7}]},
        ["ni siquiera es un objeto"],
        "un texto suelto",
    ]
    for spec in malformadas:
        fallos = compilador.validar_spec(spec)      # no puede levantar
        assert fallos, "acepto una spec malformada: %r" % (spec,)
        assert all(isinstance(f, str) and f for f in fallos)


def test_un_valor_de_otro_tipo_se_rechaza_y_no_cae_al_default():
    """`gesto: 7` no es "quieto": es un error del modelo. Caer al default en
    silencio devuelve un icono que nadie pidio y no dice por que."""
    spec = {"composicion": "centro_unico", "tono": "acido",
            "capas": [{"rol": "protagonista", "figura": "onda", "gesto": 7}]}
    fallos = compilador.validar_spec(spec)
    assert any("gesto" in f and "int" in f for f in fallos)
