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

FORMATOS = ("informe", "ensayo", "revision", "exposicion", "curatoria")

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

SISTEMA_REVISION = (
    "Eres auditor critico de un organismo autonomo llamado MAK. Escribes en "
    "espanol correcto CON TILDES, en Markdown. No produces una investigacion "
    "nueva: revisas calidad, formato, deuda, riesgos y siguiente accion "
    "verificable. Tu tono es sobrio, desconfiado y ejecutivo.")

SISTEMA_EXPOSICION = (
    "Eres editor de exposicion para un artista/director. Escribes en espanol "
    "correcto CON TILDES, en Markdown. Tu tarea no es investigar mas ni "
    "vender: convertir material ya observado en una pieza clara para lectura "
    "humana, separando evidencia, interpretacion y uso posible.")

SISTEMA_CURATORIA = (
    "Eres curador de archivo para iskvw. Escribes en espanol correcto CON "
    "TILDES, en Markdown. No haces un informe academico ni un ensayo: lees "
    "obra, archivo, familia visual, montaje posible y limites de publicacion. "
    "Separas descripcion, interpretacion y decision curatorial.")

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


def prompt_revision(tema: str, findings, sources, consultas=None) -> str:
    """Prompt for MAK introspection/review mode.

    This is deliberately not an essay and not a normal report. It is a control
    surface for idle autonomy: when no real user/backlog task is pending, MAK
    should inspect itself instead of fabricating more cultural output.
    """
    import json as _json
    return (
        "Escribe una REVISION OPERATIVA de MAK sobre el tema indicado. "
        "No rehagas investigaciones antiguas y no conviertas esto en ensayo.\n\n"
        "La revision debe tener exactamente estas secciones:\n"
        "1. VEREDICTO: una frase que diga si el sistema debe confiar, revisar "
        "o detener la linea observada.\n"
        "2. EVIDENCIA OBSERVADA: 3 a 6 bullets, cada uno con fuente o con "
        "'sin fuente: inferido de los hallazgos'.\n"
        "3. RIESGOS DE FORMATO: lista concreta de mezclas peligrosas "
        "(ensayo/informe/curatoria/codex/research) si aparecen.\n"
        "4. NODOS EJECUTIVOS: hasta 5 acciones atomicas clasificadas como "
        "repasar, discutir, exponer, refutar o archivar.\n"
        "5. SIGUIENTE ACCION VERIFICABLE: una sola accion, con archivo o "
        "comando si corresponde.\n\n"
        "Reglas:\n"
        "- Si no hay evidencia suficiente, el veredicto es revisar, no confiar.\n"
        "- No propongas producir mas piezas si antes falta validar calidad.\n"
        "- No inventes fuentes internas que no aparezcan en HALLAZGOS o FUENTES.\n\n"
        'TEMA: "%s"\n\nHALLAZGOS:\n%s\n\nFUENTES:\n%s%s'
        % (tema,
           _json.dumps(findings, ensure_ascii=False, indent=1)[:14000],
           "\n".join(sources),
           ("\n\nCONSULTAS REALIZADAS:\n"
            + "\n".join("- %s" % c for c in consultas))
           if consultas else
           "\n\nCONSULTAS REALIZADAS: no se registraron.")
    )


def prompt_exposicion(tema: str, findings, sources, consultas=None) -> str:
    """Prompt for human-facing exposition.

    This differs from `informe`: it is not a factual answer first. It differs
    from `ensayo`: it does not need a thesis or icon annex. It is a bridge from
    internal material to something the user can read, curate, post, or reject.
    """
    import json as _json
    return (
        "Escribe una EXPOSICION clara del material observado. No investigues "
        "mas, no inventes un cierre comercial y no lo conviertas en ensayo.\n\n"
        "Estructura obligatoria:\n"
        "1. QUE HAY AQUI: descripcion breve y legible.\n"
        "2. EVIDENCIA: bullets con fuente o marca '(sin fuente: inferido)'.\n"
        "3. LECTURA POSIBLE: interpretacion util para artista/disenador, "
        "marcada como interpretacion.\n"
        "4. USOS POSIBLES: hasta 4 formatos concretos (post, ficha, icono, "
        "pieza SVG, archivo, informe RD, curatoria), sin prometer que esten "
        "listos.\n"
        "5. QUE NO SE DEBE AFIRMAR: limites y huecos.\n\n"
        'TEMA: "%s"\n\nHALLAZGOS:\n%s\n\nFUENTES:\n%s%s'
        % (tema,
           _json.dumps(findings, ensure_ascii=False, indent=1)[:14000],
           "\n".join(sources),
           ("\n\nCONSULTAS REALIZADAS:\n"
            + "\n".join("- %s" % c for c in consultas))
           if consultas else
           "\n\nCONSULTAS REALIZADAS: no se registraron.")
    )


def prompt_curatoria(tema: str, findings, sources, consultas=None) -> str:
    """Prompt for iskvw/art archive curation.

    Curation is not a report with nicer adjectives. It decides how a work or
    family of works can be read, grouped, shown or kept in quarantine.
    """
    import json as _json
    return (
        "Escribe una CURATORIA de archivo sobre el material observado. No lo "
        "conviertas en informe tecnico ni en ensayo cultural general.\n\n"
        "Estructura obligatoria:\n"
        "1. NUCLEO DE OBRA: que aparece, con descripcion visual concreta.\n"
        "2. FAMILIA / CONSTELACION: con que piezas, gestos, materiales o "
        "motivos dialoga.\n"
        "3. LECTURA CURATORIAL: interpretacion marcada como interpretacion, "
        "sin afirmar biografia ni intencion no documentada.\n"
        "4. POSIBLE MONTAJE O PUBLICACION: archivo, ficha, post, sala, SVG, "
        "serie o descarte razonado.\n"
        "5. PRUEBA VISUAL: icono, gesto SVG, paleta o composicion minima que "
        "demuestre comprension del tema; si falta material visual, declaralo.\n"
        "6. LIMITES: que no se debe mezclar con RD ni presentar como fuente "
        "factual.\n\n"
        'TEMA: "%s"\n\nHALLAZGOS:\n%s\n\nFUENTES:\n%s%s'
        % (tema,
           _json.dumps(findings, ensure_ascii=False, indent=1)[:14000],
           "\n".join(sources),
           ("\n\nCONSULTAS REALIZADAS:\n"
            + "\n".join("- %s" % c for c in consultas))
           if consultas else
           "\n\nCONSULTAS REALIZADAS: no se registraron.")
    )


# --------------------------------------------------- preguntas abiertas
# El loop del organismo se alimenta de lo que un informe deja sin responder:
# `backlog.cosechar` lo saca del informe y vuelve como tema. Hasta el
# 2026-08-01 lo sacaba PARSEANDO LA PROSA -- buscaba la seccion "LAGUNAS DE
# INFORMACION" con una regex sobre el Markdown renderizado.
#
# Eso ata el loop a como se VE el texto. Dos consecuencias medidas el mismo
# dia: un tema entro al backlog llamado literalmente "**Detalles del Evento:**
# No se encontraron detalles especificos" -- con los asteriscos del render
# adentro -- y produjo un informe por cron; y al cambiar el formato del
# informe esa manana, esa seccion dejo de existir, asi que el parser habria
# devuelto vacio y el backlog se habria dejado de llenar SIN QUE NADIE SE
# ENTERE. El loop no se rompe por un bug: se rompe por un cambio de estilo.
#
# Por eso ahora se piden APARTE y como dato. El `.json` del informe ya es la
# fuente de verdad ("`report` es un RENDER de lo de abajo", dice research.py);
# esto agrega el campo que faltaba. Es una llamada corta con salida corta: la
# contesta cualquier proveedor de la cadena, incluido el ollama local cuando
# el credito de IBM se termine.
SISTEMA_PREGUNTAS = (
    "Extraes las preguntas que un informe deja ABIERTAS. Devuelves UNICAMENTE "
    "un array JSON de strings, sin markdown ni explicaciones.")


def prompt_preguntas(tema: str, documento: str) -> str:
    """Las preguntas abiertas del informe ya escrito, como DATO.

    Se piden sobre el texto final y no antes: lo que quedo abierto se sabe
    cuando el informe termino, no cuando empezo."""
    return (
        "Del informe que sigue, extrae entre 0 y 5 preguntas que quedaron "
        "ABIERTAS: lo que habria que averiguar despues. Devolve un array JSON "
        "de strings.\n\n"
        "REGLAS:\n"
        "- Cada pregunta se tiene que poder BUSCAR sola, sin haber leido este "
        "informe. \"Quien organizo el evento del 24/08/2023 en Club Hipico\" "
        "sirve; \"la falta de informacion detallada\" no, porque no dice sobre "
        "que.\n"
        "- Sin marcado: ni asteriscos, ni almohadillas, ni vinnetas. Es un "
        "dato, no un renglon de documento.\n"
        "- Si el informe respondio lo que se pregunto y no deja nada abierto, "
        "devolve []. Una lista vacia es una respuesta valida y frecuente; "
        "inventar preguntas para llenarla es como una cola de trabajo se llena "
        "de trabajo que nadie pidio.\n"
        "- No repitas la pregunta que el informe ya contesto.\n\n"
        'TEMA: "%s"\n\nINFORME:\n%s'
        % (tema, documento[:20000]))


def parsear_preguntas(bruto: str) -> list:
    """Las preguntas del array JSON. No levanta: un array mal formado no puede
    tumbar el informe, que es lo que de verdad costo producir. Devuelve [] y
    quien llame decide -- hoy `research.py` cae al parseo de prosa de siempre,
    asi que el loop nunca se queda sin alimento."""
    m = re.search(r"\[.*\]", bruto or "", re.S)
    if not m:
        return []
    try:
        crudos = json.loads(m.group(0))
    except ValueError:
        return []
    if not isinstance(crudos, list):
        return []
    salida = []
    for q in crudos:
        if not isinstance(q, str):
            continue
        # Se limpia el marcado igual que `backlog._limpiar_render`: un modelo
        # que ignora la regla no puede meter formato dentro de la cola.
        t = re.sub(r"\*\*|__|`|^#+\s*|^[-*]\s+", "", q).strip()
        if len(t) >= 12 and any(c.isalpha() for c in t):
            salida.append(t[:300])
    return salida[:5]


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


# Cuanto de cada exigencia alcanza para decir que se cumplio. Son minimos
# BAJOS a proposito: el verificador esta para atrapar el documento que no
# intento, no para pelear con el que intento y le salio corto. Un ensayo con
# 4 partes y una tabla pasa; el que salio con 0 y 0 no es un ensayo, es un
# informe con otro nombre.
MIN_PARTES = 3
MIN_TABLAS = 1
MIN_FECHAS = 2


def exigencias_incumplidas(texto: str) -> list[str]:
    """Que exigencias del ensayo NO se cumplieron, en palabras.

    Devuelve una lista vacia cuando el documento pasa. Cada elemento es el
    pedido concreto que se le va a repetir al modelo, asi que se escribe como
    instruccion y no como diagnostico.

    Solo mira lo que se puede CONTAR sobre el texto. La tesis, el argumento y
    la calidad de la prosa no entran: un verificador que pretenda medir eso
    con una regex termina rechazando lo bueno y aprobando lo que imita la
    forma. Lo que se cuenta son las cuatro exigencias que dejan huella
    estructural, y con eso alcanza para separar el ensayo del informe
    disfrazado -- que es lo que se midio el 2026-08-01: 0 partes, 0 tablas.
    """
    t = texto or ""
    faltan = []

    partes = len(re.findall(r"^#{2,3} +\S", t, re.M))
    if partes < MIN_PARTES:
        faltan.append(
            "PARTES NARRADAS: hay %d y el ensayo pide entre 5 y 8. Cada parte "
            "lleva un titulo que dice de que se trata y anticipa una tesis "
            "(\"PARTE IV: EL ACIDO - La doble helice del movimiento\"), nunca "
            "\"4. HALLAZGOS\"" % partes)

    # Una tabla markdown se reconoce por su linea de separacion.
    tablas = len(re.findall(r"^\s*\|?[\s:-]*-{3,}[\s:|-]*$", t, re.M))
    if tablas < MIN_TABLAS:
        faltan.append(
            "TABLA DONDE DOS LECTURAS COMPITEN: no hay ninguna. No es una "
            "tabla de datos: es una que distingue dos formas de leer el mismo "
            "objeto, una por columna")

    # Cronologia: anos de cuatro digitos o fechas. Se cuentan distintos para
    # que repetir el mismo ano cinco veces no la de por cumplida.
    # Desde el ano 1000: un ensayo cultural cita cualquier siglo, y con el
    # rango pegado a 1800 la genealogia de un signo diacritico -- que empieza
    # en la imprenta -- quedaba sin cronologia. Lo atrapo la prueba con 1492.
    fechas = set(re.findall(r"\b(1\d{3}|20[0-2]\d)\b", t))
    if len(fechas) < MIN_FECHAS:
        faltan.append(
            "CRONOLOGIA: aparecen %d fechas distintas. El ensayo pide una "
            "linea de tiempo con fechas y hechos, para que sirva como "
            "material reutilizable" % len(fechas))

    if "http" not in t:
        faltan.append(
            "FUENTES CON URL: no hay una sola. Cada afirmacion verificable "
            "lleva su fuente; si falta, se DECLARA la deuda y jamas se "
            "inventa una URL")

    return faltan


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
