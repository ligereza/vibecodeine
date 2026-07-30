#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_ensayo_rave.py -- el producto en si: docs/cultura/ensayos/rave/.

No prueba codigo, prueba el CONTENIDO: que el anexo iconografico no reclame
pasajes que el ensayo nunca escribio (la tesis doublecup aplicada al anexo,
ver FORMATO_ENSAYO.md), que el manifiesto y los archivos en disco coincidan
en las dos direcciones, y que el espanol conserve sus tildes -- un titulo
mutilado ("Berlin" en vez de "Berlín") es exactamente el defecto que le costo
el puesto a alguien segun CLAUDE.md, y aca es medible.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAVE = REPO / "docs" / "cultura" / "ensayos" / "rave"
CULTURA = REPO / "docs" / "cultura"

ENSAYO = (RAVE / "ensayo.md").read_text(encoding="utf-8")
MANIFIESTO = json.loads((RAVE / "iconos.json").read_text(encoding="utf-8"))

TITULOS_ENSAYO = set(re.findall(r"^#{2,4} .+$", ENSAYO, re.MULTILINE))


def test_hay_16_conceptos_en_el_manifiesto():
    assert len(MANIFIESTO) == 16


def test_cada_ancla_es_un_titulo_real_del_ensayo():
    huerfanas = [it["ancla"] for it in MANIFIESTO if it["ancla"] not in TITULOS_ENSAYO]
    assert huerfanas == [], (
        "estas anclas reclaman un pasaje que el ensayo no escribio: %s" % huerfanas)


def test_mutacion_ancla_inventada_se_detecta():
    """Verificacion viva: un ancla que no existe en el ensayo debe fallar la
    asercion de arriba. Probamos sobre una copia del manifiesto en memoria,
    sin tocar el archivo real."""
    manifiesto_roto = [dict(it) for it in MANIFIESTO]
    manifiesto_roto[0]["ancla"] = "### Esta seccion no existe en el ensayo"
    huerfanas = [it["ancla"] for it in manifiesto_roto
                if it["ancla"] not in TITULOS_ENSAYO]
    assert huerfanas, "la mutacion no se detecto: el guard no prueba nada"


def test_cada_archivo_del_manifiesto_existe_en_disco():
    faltantes = [it["archivo"] for it in MANIFIESTO
                if not (RAVE / "iconos" / it["archivo"]).is_file()]
    assert faltantes == []


def test_cada_svg_en_disco_esta_en_el_manifiesto():
    en_disco = {p.name for p in (RAVE / "iconos").glob("*.svg")}
    en_manifiesto = {it["archivo"] for it in MANIFIESTO}
    assert en_disco == en_manifiesto, (
        "en disco y no en manifiesto: %s | en manifiesto y no en disco: %s"
        % (en_disco - en_manifiesto, en_manifiesto - en_disco))


# ---------------------------------------------------------------------------
# espanol correcto: las tildes no se mutilan (mangled diacritics = defecto)
# ---------------------------------------------------------------------------
# palabras que aparecen REALMENTE en ensayo.md/iconos.json y que DEBEN llevar
# tilde (verificado contra el texto real, ver sesion): la forma capitalizada
# "Berlín"/"Ácido" es la que ocurre, no siempre la minuscula.
PALABRAS_CON_TILDE_REALES = [
    ("Berlín", "Berlin"),
    ("música", "musica"),
    ("Máquina", "Maquina"),
    ("Conexión", "Conexion"),
    ("Ilegalidad", None),  # sin tilde, se usa solo como control de que el
                           # texto realmente esta presente (no mide tilde)
]


def test_el_ensayo_conserva_diacriticos_reales():
    texto_completo = ENSAYO + json.dumps(MANIFIESTO, ensure_ascii=False)
    assert "á" in texto_completo or "é" in texto_completo or "í" in texto_completo \
        or "ó" in texto_completo or "ú" in texto_completo or "ñ" in texto_completo
    for con_tilde, sin_tilde in PALABRAS_CON_TILDE_REALES:
        assert con_tilde in texto_completo, con_tilde
        if sin_tilde:
            # la forma mutilada NO debe aparecer como palabra suelta
            assert not re.search(r"\b%s\b" % re.escape(sin_tilde), texto_completo), (
                "aparece la forma sin tilde de %r: defecto de mangled diacritics"
                % con_tilde)


def test_mutacion_tilde_mutilada_se_detecta():
    """Verificacion viva: si 'Berlín' se degradara a 'Berlin' en el texto (el
    defecto real de CLAUDE.md), la asercion de arriba debe reventar. Se prueba
    sobre una copia en memoria del texto, sin tocar el archivo real."""
    texto_mutilado = ENSAYO.replace("Berlín", "Berlin")
    assert "Berlín" not in texto_mutilado
    assert re.search(r"\bBerlin\b", texto_mutilado)


# ---------------------------------------------------------------------------
# los otros dos documentos: existen y sus links relativos resuelven
# ---------------------------------------------------------------------------
def _links_relativos(md_path):
    txt = md_path.read_text(encoding="utf-8")
    todos = re.findall(r"\]\(([^)]+)\)", txt)
    return [l for l in todos if not re.match(r"^[a-zA-Z]+://", l) and not l.startswith("#")]


def test_formato_ensayo_y_motor_semantico_existen():
    assert (CULTURA / "FORMATO_ENSAYO.md").is_file()
    assert (CULTURA / "MOTOR_SEMANTICO.md").is_file()


def test_links_relativos_de_formato_ensayo_resuelven():
    for link in _links_relativos(CULTURA / "FORMATO_ENSAYO.md"):
        destino = (CULTURA / link).resolve()
        assert destino.is_file(), link


def test_links_relativos_de_motor_semantico_resuelven():
    for link in _links_relativos(CULTURA / "MOTOR_SEMANTICO.md"):
        destino = (CULTURA / link).resolve()
        assert destino.is_file(), link


def test_mutacion_link_roto_se_detectaria():
    """Verificacion viva: un link relativo que apunte a un archivo inexistente
    debe fallar. Se agrega un link falso a una copia del texto en memoria."""
    txt = (CULTURA / "MOTOR_SEMANTICO.md").read_text(encoding="utf-8")
    txt_roto = txt + "\n[ver](ARCHIVO_QUE_NO_EXISTE.md)\n"
    links = [l for l in re.findall(r"\]\(([^)]+)\)", txt_roto)
            if not re.match(r"^[a-zA-Z]+://", l) and not l.startswith("#")]
    rotos = [l for l in links if not (CULTURA / l).resolve().is_file()]
    assert rotos == ["ARCHIVO_QUE_NO_EXISTE.md"]
