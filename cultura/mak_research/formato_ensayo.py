#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""formato_ensayo.py -- el formato de salida largo de research: ENSAYO.

Un nivel arriba del informe. El informe (`1. RESUMEN EJECUTIVO / 2. HALLAZGOS /
3. ANALISIS CRITICO / 4. LAGUNAS / 5. PROXIMOS PASOS`) produce un documento
correcto que nadie lee dos veces: enumera, no argumenta, y no deja nada que se
pueda mirar. El contrato completo, con el ejemplo canonico, esta en
`docs/cultura/FORMATO_ENSAYO.md`.

Modulo APARTE a proposito: `research.py` es del 2026-07-20 y su prompt de
informe vive incrustado ahi. La regla de la sesion que escribio esto
(2026-07-30, orden del usuario) es que nada de mas de una semana se parchea a
ciegas -- se reconstruye al lado, con test propio. Asi el formato se puede
cambiar y medir sin tocar el camino que ya funciona.

Dos salidas:
  - el PROMPT del documento final (las siete exigencias van en el prompt, no en
    la esperanza)
  - el PROMPT de los conceptos nombrables, cuya respuesta JSON alimenta el modo
    `iconos` de codex sin traduccion intermedia
"""
from __future__ import annotations

import json
import re

FORMATOS = ("informe", "ensayo")

# Las siete exigencias, en el orden en que un lector las encuentra.
EXIGENCIAS = (
    "PARTES NARRADAS, no secciones enumeradas: cada parte tiene titulo que dice "
    "de que se trata y anticipa una tesis (\"PARTE IV: EL ACIDO - La doble "
    "helice del movimiento\", nunca \"4. HALLAZGOS\"). Entre 5 y 8 partes, con "
    "subsecciones numeradas (1.1, 1.2) para poder citarlas.",
    "UNA TESIS QUE SE PUEDE NEGAR: afirma algo discutible y sostenelo. No "
    "describas: argumenta.",
    "AL MENOS UNA TABLA DONDE DOS LECTURAS COMPITEN. No una tabla de datos: una "
    "que distingue dos formas de leer el mismo objeto.",
    "UNA CRONOLOGIA con fechas y hechos, para que el ensayo sea material "
    "reutilizable.",
    "UN CIERRE QUE ARGUMENTA, no que resume. Si el cierre repite el resumen, no "
    "habia tesis.",
    "FUENTES CON URL en cada afirmacion verificable, y cita textual cuando "
    "entrecomilles. Si una fuente falta, DECLARA la deuda; jamas inventes una "
    "URL.",
    "ANEXO ICONOGRAFICO: cerra con la lista de conceptos nombrables del ensayo "
    "(entre 6 y 24), uno por frase nominal.",
)

SISTEMA = ("Eres un ensayista cultural. Escribes en espanol correcto CON TILDES, "
           "en Markdown. Argumentas: no enumeras. Cada afirmacion verificable "
           "lleva su fuente.")

SISTEMA_CONCEPTOS = (
    "Extraes los conceptos NOMBRABLES de un ensayo. Un concepto nombrable se "
    "dice con una frase nominal ('la zona autonoma temporal', 'la Roland "
    "TB-303'). Si algo suena como 'la relacion entre X e Y bajo Z', partelo o "
    "fundilo. Devuelves UNICAMENTE un array JSON.")

# Cuantos conceptos tiene sentido pedir. Menos de 6 y el anexo no es un anexo;
# mas de 24 y dejaron de ser nombrables.
MIN_CONCEPTOS, MAX_CONCEPTOS = 6, 24


def prompt_documento(tema: str, findings, sources) -> str:
    """El prompt del ensayo. `findings`/`sources` llegan como los arma
    research.py (lista de dicts y lista de urls)."""
    numeradas = "\n".join("%d. %s" % (i, e)
                          for i, e in enumerate(EXIGENCIAS, 1))
    return (
        "Escribe un ENSAYO sobre el tema. Un ensayo cumple SIETE exigencias y "
        "se mide contra ellas:\n\n%s\n\n"
        'TEMA: "%s"\n\nHALLAZGOS:\n%s\n\nFUENTES:\n%s'
        % (numeradas, tema,
           json.dumps(findings, ensure_ascii=False, indent=1)[:14000],
           "\n".join(sources)))


def prompt_conceptos(tema: str, documento: str) -> str:
    """El prompt que saca los conceptos nombrables del ensayo ya escrito.

    Se pide DESPUES y sobre el texto final, no antes: los conceptos que
    importan son los que el ensayo termino sosteniendo, no los que se
    anticiparon."""
    return (
        "Del ensayo que sigue, extrae entre %d y %d conceptos NOMBRABLES, en el "
        "orden en que aparecen. Devuelve un array JSON; cada objeto:\n"
        '  "n": numero de dos digitos como texto ("01")\n'
        '  "slug": minusculas-con-guiones, ASCII, sin tildes\n'
        '  "titulo": como se nombra en el ensayo, en espanol CON tildes\n'
        '  "descripcion": una frase de por que importa, en espanol CON tildes\n'
        '  "brief": la metafora visual en una frase (que se veria)\n'
        '  "ancla": el titulo EXACTO de la seccion del ensayo que lo justifica, '
        "copiado tal cual, con sus almohadillas\n\n"
        'TEMA: "%s"\n\nENSAYO:\n%s'
        % (MIN_CONCEPTOS, MAX_CONCEPTOS, tema, documento[:24000]))


def parsear_conceptos(bruto: str, documento: str = "") -> tuple[list, list]:
    """(conceptos, problemas). No levanta: un anexo mal formado no puede tumbar
    el ensayo, que es lo que de verdad costo producir.

    Si llega `documento`, verifica que cada `ancla` sea un titulo REAL. Un icono
    cuya ancla no existe reclama un pasaje que el ensayo no escribio -- la
    tesis doublecup aplicada al anexo.
    """
    problemas: list[str] = []
    m = re.search(r"\[.*\]", bruto or "", re.S)
    if not m:
        return [], ["la respuesta no traia un array JSON"]
    try:
        crudos = json.loads(m.group(0))
    except ValueError as e:
        return [], ["array JSON invalido: %s" % e]
    if not isinstance(crudos, list):
        return [], ["la respuesta no era una lista"]

    titulos = set(re.findall(r"^#{2,4} .+$", documento, re.MULTILINE))
    obligatorios = ("titulo", "descripcion", "brief")
    conceptos = []
    for i, c in enumerate(crudos):
        if not isinstance(c, dict):
            problemas.append("concepto %d: no es un objeto" % i)
            continue
        faltan = [k for k in obligatorios if not str(c.get(k, "")).strip()]
        if faltan:
            problemas.append("concepto %d: sin %s" % (i, ", ".join(faltan)))
            continue
        n = str(c.get("n") or "").strip() or "%02d" % (len(conceptos) + 1)
        slug = _slug(c.get("slug") or c["titulo"])
        ancla = str(c.get("ancla") or "").strip()
        if titulos and ancla and ancla not in titulos:
            problemas.append(
                "concepto %s (%s): el ancla %r no es un titulo del ensayo"
                % (n, slug, ancla[:70]))
            ancla = ""
        conceptos.append({
            "n": n.zfill(2), "archivo": "%s-%s.svg" % (n.zfill(2), slug),
            "slug": "%s-%s" % (n.zfill(2), slug),
            "titulo": str(c["titulo"]).strip(),
            "descripcion": str(c["descripcion"]).strip(),
            "brief": str(c["brief"]).strip(),
            "estilo": str(c.get("estilo") or "").strip(),
            "ancla": ancla,
        })
    if len(conceptos) < MIN_CONCEPTOS:
        problemas.append("solo %d conceptos utiles (el minimo es %d)"
                         % (len(conceptos), MIN_CONCEPTOS))
    if len(conceptos) > MAX_CONCEPTOS:
        problemas.append("%d conceptos: dejaron de ser nombrables, se recortan "
                         "a %d" % (len(conceptos), MAX_CONCEPTOS))
        conceptos = conceptos[:MAX_CONCEPTOS]
    return conceptos, problemas


def _slug(texto: str) -> str:
    """Slug ASCII. Es una CLAVE de maquina (nombre de archivo, id), asi que aca
    si corresponde perder la tilde -- al contrario de `titulo` y `descripcion`,
    que un humano lee y conservan su espanol."""
    import unicodedata
    plano = unicodedata.normalize("NFKD", texto)
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    plano = re.sub(r"[^a-zA-Z0-9]+", "-", plano).strip("-").lower()
    return (plano or "concepto")[:48]
