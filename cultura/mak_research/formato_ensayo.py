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

# ---------------------------------------------------------------- informe
# El otro formato. Hasta el 2026-08-01 su prompt era UNA LINEA pidiendo cinco
# secciones enumeradas -- resumen ejecutivo, hallazgos, analisis, lagunas,
# proximos pasos -- y es el formato POR DEFECTO, asi que era lo que el
# organismo producia todos los dias. Un informe de consultora generica sobre
# un corpus que nadie encargo.
#
# No se convierte en un ensayo: son cosas distintas y el ensayo ya existe. Un
# informe responde una pregunta con lo que se encontro, y lo que lo vuelve
# util no es la prosa, es que se pueda REFUTAR: que cada afirmacion diga de
# donde sale, que lo que no se encontro se diga como ausencia y no se rellene,
# y que la confianza sea un dato y no un tono.
#
# Las exigencias salen de defectos medidos en el corpus vivo (70 informes,
# 2026-08-01): 46 decian NO SE ENCONTRO y 0 de 70 traian una sola fuente
# primaria, mientras el texto sonaba igual de seguro en los dos casos.
EXIGENCIAS_INFORME = (
    "TITULO que diga el hallazgo, no el tema. \"Tres productoras comparten "
    "venue y ninguna declara vinculo\" es un titulo; \"Informe sobre "
    "productoras\" es una carpeta.",

    "Abre con la RESPUESTA, en dos o tres lineas, antes de cualquier metodo o "
    "contexto. Si la respuesta es que no se encontro, eso ES la respuesta y va "
    "primero: nadie tiene que leer cuatro secciones para descubrirlo.",

    "Cada afirmacion verificable lleva su fuente PEGADA, con la URL entre "
    "parentesis al final de la frase. Una afirmacion sin fuente se escribe "
    "igual, pero marcada: \"(sin fuente: inferido de X)\". Lo que no se puede "
    "atribuir se declara, no se omite ni se disfraza.",

    "Distingue TRES estados y nunca los mezcla: lo que las fuentes DICEN, lo "
    "que vos INFERIS de ellas, y lo que NO SE ENCONTRO. Un informe que suena "
    "igual de seguro en los tres casos es peor que no tenerlo, porque manda a "
    "actuar sobre una suposicion.",

    "Lo que NO SE ENCONTRO va con el mismo peso que lo encontrado, y dice "
    "DONDE se busco -- pero SOLO con las consultas que estan listadas abajo en "
    "CONSULTAS REALIZADAS. Si no hay lista, escribis \"no se encontro\" a "
    "secas. NUNCA inventes donde se busco: en la primera prueba de este "
    "formato el modelo escribio \"buscado en registros municipales y archivos "
    "de la municipalidad\" y ahi no busco nadie. Una busqueda inventada es "
    "peor que no declarar ninguna, porque cierra la pregunta en falso.",

    "Si hay lecturas que se contradicen, van LAS DOS, una al lado de la otra, "
    "con su fuente cada una. No se promedian ni se elige la mas comoda.",

    "CIERRA con lo que cambiaria el resultado: que dato falta, donde estaria, "
    "y que decision distinta se tomaria si apareciera. Sin lista de \"proximos "
    "pasos\" generica -- una accion concreta o ninguna.",

    "Nada de relleno: sin 'es importante destacar', sin 'en conclusion', sin "
    "parrafo de contexto que no aporte un dato. Si una frase se puede borrar "
    "sin perder informacion, sobra.",
)


def prompt_informe(tema: str, findings, sources, consultas=None) -> str:
    """El prompt del informe.

    `consultas` son las busquedas que de verdad se hicieron (`query_history`).
    Van al prompt porque sin ellas el modelo INVENTA donde se busco: medido en
    la primera prueba de este formato, escribio "buscado en registros
    municipales y archivos de la municipalidad" sobre una corrida que solo
    consulto la web. Una ausencia sostenida por una busqueda que no ocurrio
    cierra la pregunta en falso, y eso es peor que dejarla abierta."""
    import json as _json
    numeradas = "\n".join("%d. %s" % (i, e)
                          for i, e in enumerate(EXIGENCIAS_INFORME, 1))
    return (
        "Escribe un INFORME sobre el tema. Un informe cumple OCHO exigencias y "
        "las cumple TODAS; si una no se puede cumplir con el material que "
        "tenes, decilo en el texto en vez de simularla.\n\n"
        "%s\n\n"
        "Estructura libre: no hay secciones obligatorias y NO las numeres. Lo "
        "que manda es la exigencia 2 (la respuesta primero) y la 5 (la "
        "ausencia pesa igual). Si el material da para tres parrafos, son tres "
        "parrafos -- estirar un informe corto para que parezca completo es la "
        "unica falta que no tiene arreglo.\n\n"
        'TEMA: "%s"\n\nHALLAZGOS:\n%s\n\nFUENTES:\n%s%s'
        % (numeradas, tema,
           _json.dumps(findings, ensure_ascii=False, indent=1)[:14000],
           "\n".join(sources),
           ("\n\nCONSULTAS REALIZADAS (las UNICAS que podes citar como "
            "\"donde se busco\"):\n"
            + "\n".join("- %s" % c for c in consultas))
           if consultas else
           "\n\nCONSULTAS REALIZADAS: no se registraron. Entonces NO declares "
           "donde se busco -- escribi \"no se encontro\" a secas.")
    )


SISTEMA_INFORME = (
    "Eres un investigador senior. Escribes en espanol correcto CON TILDES, en "
    "Markdown. Tu informe se juzga por si se puede REFUTAR: cada afirmacion "
    "dice de donde sale, y lo que no se encontro se declara como ausencia en "
    "vez de rellenarse con algo plausible.")

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
