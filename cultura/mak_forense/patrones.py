#!/usr/bin/env python3
"""The detectors. Pure functions: `Registro` in, `Hallazgo` out.

No network, no database, no writes. Everything it reads comes through a
parameter, so every rule can be tested with eight made-up rows.

The constants in this file are not preferences: each one has a
measurement on `Testeo 2025` behind it, cited in its docstring. When
another area moves them, it should move them with its own measurement
next to them.
"""
from __future__ import annotations

import statistics
from collections import Counter, defaultdict

try:
    from .registro import Analisis, Cobertura, Hallazgo, Registro
except ImportError:  # direct execution through forense.py
    from registro import Analisis, Cobertura, Hallazgo, Registro

# A run shared with another group has to measure this to count.
#
# Measured: at 4, 3 rows of `Fiesta Dame 504 mesa 1` got marked as copied
# from `Cachorros 35`, and they were false -- the supposed origin was 28
# days LATER and the three rows were MDMA "tesla rosada" with different
# results from each other. The real runs in the corpus measure 16, 17, 28
# and 71: 6 lets all of them through and keeps out the generic match.
MINIMO_TRAMO = 6

# A stitched-together block is recognized because MANY different contents
# repeat at the SAME distance. That distance is its period.
#
# Measured: `Mamisonga 8225` has delta 22 in 396 of its ~640 repetitions.
# The rest of the sheets in the corpus give delta 1 -- identical rows one
# after another, which is what a real batch of equal samples looks like,
# not a stitched block.
MINIMO_BLOQUE = 8
FRACCION_BLOQUE = 0.5

# Window in which a capture is accepted as belonging to the event it
# declares. An RD session starts before the party and the data gets
# uploaded afterward; whatever falls outside this isn't late, it's
# another event.
MARGEN_PREVIO_H = 12.0
MARGEN_POSTERIOR_H = 24.0

# Robust cutoff for "this capture is far from its own group's cluster".
# 3.5 is the Iglewicz-Hoaglin cutoff on the MAD-modified z-score; the
# floor in hours avoids flagging a session that was simply short and even.
Z_FUERA_DE_JORNADA = 3.5
PISO_FUERA_DE_JORNADA_H = 12.0

# Two loads separated by less than this were not typed by a person.
PISO_RAFAGA_S = 3.0
MINIMO_RAFAGA = 4

_HORA = 3600.0


# --------------------------------------------------------------------------
# repetitions within the same group
# --------------------------------------------------------------------------

def periodo_dominante(posiciones_por_contenido,
                      minimo=MINIMO_BLOQUE,
                      fraccion=FRACCION_BLOQUE) -> int | None:
    """The period of a stitched block within the group, or None.

    A block stitched N times leaves, for each repeated content, a
    constant distance equal to the block's length. A real batch of equal
    samples leaves distance 1. That's why only distances greater than 1
    are considered, and the modal distance is required to explain half
    of the repetitions: a single coincidence doesn't rule the whole
    group.
    """
    deltas: Counter[int] = Counter()
    for posiciones in posiciones_por_contenido:
        p = sorted(posiciones)
        for a, b in zip(p, p[1:]):
            deltas[b - a] += 1
    if not deltas:
        return None
    total = sum(deltas.values())
    candidatos = [(d, c) for d, c in deltas.items() if d > 1]
    if not candidatos:
        return None
    periodo, n = max(candidatos, key=lambda dc: dc[1])
    if n < minimo or n < fraccion * total:
        return None
    return periodo


def repeticiones(registros: list[Registro]) -> list[Hallazgo]:
    """Classifies a group's repetitions by their GEOMETRY.

    This is the correction that cost the most in the original analysis:
    counting "identical rows" and calling them duplicates inflated the
    damage. Of the corpus's 904 repetitions, 645 were a real stitched
    block (period 22) and 139 were contiguous rows -- `DAME 1503` has 37
    of its 39 repetitions stacked one after another, which is exactly
    what a table looks like when five ketamine samples arrive in a row
    with the same reagent and the same color.

    Shape distinguishes what content cannot:

      lote_contiguo        delta <= 1   probably real samples
      bloque_periodico     delta == P   stitched, confirmed by the period
      repeticion_dispersa  everything else, unexplained, stays pending
    """
    utiles = [r for r in registros if not r.es_encabezado]
    if not utiles:
        return []
    grupo = utiles[0].grupo

    posiciones: dict[tuple, list[Registro]] = defaultdict(list)
    for r in utiles:
        posiciones[r.contenido].append(r)
    repetidos = {k: sorted(v, key=lambda r: r.orden)
                 for k, v in posiciones.items() if len(v) > 1}
    if not repetidos:
        return []

    periodo = periodo_dominante([[r.orden for r in v] for v in repetidos.values()])

    contiguos: list[Registro] = []
    periodicos: list[Registro] = []
    dispersos: list[Registro] = []
    for serie in repetidos.values():
        for previo, actual in zip(serie, serie[1:]):
            delta = actual.orden - previo.orden
            if delta <= 1:
                contiguos.append(actual)
            elif periodo is not None and delta == periodo:
                periodicos.append(actual)
            else:
                dispersos.append(actual)

    copias = max(len(v) for v in repetidos.values())
    salida: list[Hallazgo] = []
    if periodicos:
        salida.append(Hallazgo(
            patron="bloque_periodico",
            certeza="confirmado",
            grupo=grupo,
            n=len(periodicos),
            registros=tuple(r.id for r in periodicos),
            evidencia={"periodo": periodo,
                       "contenidos_repetidos": len(repetidos),
                       "copias_del_contenido_mas_repetido": copias},
            explicacion=(f"{len(periodicos)} anotaciones vuelven cada {periodo} "
                         f"posiciones: es un bloque pegado, no registro nuevo"),
        ))
    if contiguos:
        salida.append(Hallazgo(
            patron="lote_contiguo",
            certeza="probable",
            grupo=grupo,
            n=len(contiguos),
            registros=tuple(r.id for r in contiguos),
            evidencia={"delta": 1},
            explicacion=(f"{len(contiguos)} anotaciones identicas una debajo de "
                         f"otra: se parece a una tanda real, NO se descuenta"),
        ))
    if dispersos:
        salida.append(Hallazgo(
            patron="repeticion_dispersa",
            certeza="pendiente",
            grupo=grupo,
            n=len(dispersos),
            registros=tuple(r.id for r in dispersos),
            evidencia={"periodo_del_grupo": periodo},
            explicacion=(f"{len(dispersos)} anotaciones identicas sin patron "
                         f"geometrico: no hay con que decidir, va a revision"),
        ))
    return salida


# --------------------------------------------------------------------------
# runs that come from ANOTHER group
# --------------------------------------------------------------------------

def _fecha_de(registros: list[Registro]) -> str | None:
    for r in registros:
        if r.fecha_declarada:
            return r.fecha_declarada
    return None


def _quien_copio(a: str, b: str, largo: int, distintos: dict[str, int]) -> tuple[str, str]:
    """Returns (copy, origin) based on how much the run weighs in each group.

    In the original, the run IS practically all of its own distinct
    content. In the copy, the run gets diluted among the new annotations
    that were actually made. Measured in the clearest case in the corpus:
    the 71-row run weighs 0.96 of `DAME 1503`'s distinct content and 0.62
    of `Psiquiatrico 1603`'s -- the copy is Psiquiatrico, which is also
    the next day's sheet.

    The 0.05 threshold avoids deciding on noise when two groups are
    nearly equal; there, the name rules, because `Copy of X` is called
    that for a reason.
    """
    peso_a = largo / max(distintos.get(a, 1), 1)
    peso_b = largo / max(distintos.get(b, 1), 1)
    if abs(peso_a - peso_b) > 0.05:
        return (a, b) if peso_a < peso_b else (b, a)
    copias_a = a.lower().count("copy of") + a.lower().count("copia de")
    copias_b = b.lower().count("copy of") + b.lower().count("copia de")
    if copias_a != copias_b:
        return (a, b) if copias_a > copias_b else (b, a)
    return tuple(sorted((a, b)))  # stable, and the finding stays 'pendiente'


def tramos_ajenos(grupos: dict[str, list[Registro]],
                  minimo: int = MINIMO_TRAMO) -> list[Hallazgo]:
    """Contiguous runs a group shares with another: the stitching between sheets.

    Unlike the original detector, this compares ALL the groups it
    receives, regardless of which file or period they come from. That
    was the blind spot: 2024 and 2025 were imported separately, so a
    session that inherited from the previous year's went unseen.
    Coverage still declares that only what's in this run gets compared.

    Direction is decided by weight (`_quien_copio`) and CORROBORATED with
    the date: the later group is the one that copied. If both signals
    agree the finding stays `confirmado`; if only one exists, `probable`;
    if they contradict each other it stays `pendiente` with both
    hypotheses written out, because the corpus dates come from the
    sheet's name and aren't reliable on their own.
    """
    conjuntos = {g: {r.contenido for r in rs if not r.es_encabezado}
                 for g, rs in grupos.items()}
    distintos = {g: len(s) for g, s in conjuntos.items()}
    fechas = {g: _fecha_de(rs) for g, rs in grupos.items()}
    salida: list[Hallazgo] = []

    for grupo, registros in grupos.items():
        filas = _primeras_apariciones(registros)
        otros = [g for g in grupos if g != grupo]
        marca = [frozenset() if r.es_encabezado
                 else frozenset(o for o in otros if r.contenido in conjuntos[o])
                 for r in filas]
        i = 0
        while i < len(filas):
            if not marca[i]:
                i += 1
                continue
            j, comun = i, marca[i]
            while j + 1 < len(filas) and (marca[j + 1] & comun):
                comun = marca[j + 1] & comun
                j += 1
            largo = j - i + 1
            if largo >= minimo:
                for otro in sorted(comun):
                    copia, origen = _quien_copio(grupo, otro, largo, distintos)
                    if copia != grupo:
                        continue  # the finding is emitted from the copy's side
                    f_copia, f_origen = fechas.get(grupo), fechas.get(otro)
                    veredicto_fecha = None
                    if f_copia and f_origen and f_copia != f_origen:
                        veredicto_fecha = "coincide" if f_origen < f_copia else "contradice"
                    certeza = {"coincide": "confirmado",
                               "contradice": "pendiente",
                               None: "probable"}[veredicto_fecha]
                    dias = _dias_entre(f_origen, f_copia)
                    salida.append(Hallazgo(
                        patron="tramo_ajeno",
                        certeza=certeza,
                        grupo=grupo,
                        origen=otro,
                        n=largo,
                        registros=tuple(r.id for r in filas[i:j + 1]),
                        evidencia={
                            "desde_orden": filas[i].orden,
                            "hasta_orden": filas[j].orden,
                            "fecha_grupo": f_copia,
                            "fecha_origen": f_origen,
                            "dias_entre": dias,
                            "peso_grupo": round(largo / max(distintos.get(grupo, 1), 1), 3),
                            "peso_origen": round(largo / max(distintos.get(otro, 1), 1), 3),
                            "veredicto_fecha": veredicto_fecha or "sin_fecha_util",
                        },
                        explicacion=(
                            f"{largo} anotaciones seguidas de «{grupo}» ya estaban "
                            f"en «{otro}»"
                            + (f" ({dias} dias antes)" if dias is not None else "")
                            + (": la fecha contradice al peso, decide una persona"
                               if certeza == "pendiente" else "")),
                    ))
            i = j + 1
    return salida


def _primeras_apariciones(registros: list[Registro]) -> list[Registro]:
    """The group without its own repetitions, in order.

    A run is brought over from another session ONCE; what happens
    afterward within the sheet is already explained by `repeticiones`.
    Without this, `Mamisonga 8225`'s 31 internal replicas would match
    against `Cachorros 18125` again and the same 20-row run would be
    reported 31 times -- 780 "foreign" rows where there are 20. The
    per-pattern totals would stop being addable to each other.
    """
    vistos: set[tuple] = set()
    salida: list[Registro] = []
    for r in sorted(registros, key=lambda x: x.orden):
        if r.es_encabezado:
            salida.append(r)
            continue
        if r.contenido in vistos:
            continue
        vistos.add(r.contenido)
        salida.append(r)
    return salida


def _dias_entre(a: str | None, b: str | None) -> int | None:
    """Days between two ISO dates, without importing datetime unless needed."""
    if not a or not b:
        return None
    import datetime
    try:
        d1 = datetime.date.fromisoformat(a[:10])
        d2 = datetime.date.fromisoformat(b[:10])
    except ValueError:
        return None
    return (d2 - d1).days


# --------------------------------------------------------------------------
# time: what the spreadsheet could never detect and an app can
# --------------------------------------------------------------------------

def anacronismos(registros: list[Registro],
                 margen_previo_h: float = MARGEN_PREVIO_H,
                 margen_posterior_h: float = MARGEN_POSTERIOR_H) -> list[Hallazgo]:
    """Captures whose real instant doesn't fit the event they declare.

    This is the detector the spreadsheet never could have and XIO-RD can:
    a spreadsheet doesn't know when a cell was written, an app knows
    exactly when a sample was saved. Covers the two anticipated errors:

      registro_en_evento_futuro  -- loaded BEFORE the event happened; the
                                    volunteer picked a session that hasn't
                                    happened yet
      registro_en_evento_pasado  -- loaded much LATER; the volunteer
                                    picked an earlier session from the list

    A record with no instant is neither flagged nor cleared: it simply
    isn't seen. Coverage accounts for that.
    """
    import datetime
    salida: list[Hallazgo] = []
    futuros: list[Registro] = []
    pasados: list[Registro] = []
    for r in registros:
        if r.instante_registro is None or not r.fecha_declarada:
            continue
        try:
            dia = datetime.date.fromisoformat(r.fecha_declarada[:10])
        except ValueError:
            continue
        inicio = datetime.datetime.combine(
            dia, datetime.time.min, tzinfo=datetime.timezone.utc).timestamp()
        fin = inicio + 24 * _HORA
        if r.instante_registro < inicio - margen_previo_h * _HORA:
            futuros.append(r)
        elif r.instante_registro > fin + margen_posterior_h * _HORA:
            pasados.append(r)

    for patron, filas, texto in (
        ("registro_en_evento_futuro", futuros,
         "se guardo antes de que el evento ocurriera"),
        ("registro_en_evento_pasado", pasados,
         "se guardo mucho despues del evento que declara"),
    ):
        if not filas:
            continue
        grupos = sorted({r.grupo for r in filas})
        salida.append(Hallazgo(
            patron=patron,
            certeza="confirmado",
            grupo=grupos[0] if len(grupos) == 1 else f"{len(grupos)} grupos",
            n=len(filas),
            registros=tuple(r.id for r in filas),
            evidencia={"grupos": grupos,
                       "margen_previo_h": margen_previo_h,
                       "margen_posterior_h": margen_posterior_h},
            explicacion=f"{len(filas)} anotaciones: {texto} -- evento equivocado",
        ))
    return salida


def fuera_de_jornada(registros: list[Registro],
                     z: float = Z_FUERA_DE_JORNADA,
                     piso_h: float = PISO_FUERA_DE_JORNADA_H) -> list[Hallazgo]:
    """Captures far from their own group's time cluster.

    Useful where `anacronismos` doesn't reach: when the event has no
    declared date, the group still has an implicit one -- almost all of
    its captures fall within a few hours. The one that doesn't stands
    apart on its own.

    Uses median and MAD, not mean and standard deviation: if the group
    already carries several off-time captures, the mean shifts toward
    them and stops seeing them. The floor in hours avoids flagging
    normal spread in an evenly-paced session.
    """
    con_hora = [r for r in registros if r.instante_registro is not None]
    if len(con_hora) < 4:
        return []
    grupo = con_hora[0].grupo
    tiempos = [r.instante_registro for r in con_hora]
    mediana = statistics.median(tiempos)
    mad = statistics.median([abs(t - mediana) for t in tiempos])
    if mad <= 0:
        return []
    lejanos = [r for r in con_hora
               if 0.6745 * abs(r.instante_registro - mediana) / mad > z
               and abs(r.instante_registro - mediana) > piso_h * _HORA]
    if not lejanos:
        return []
    return [Hallazgo(
        patron="fuera_de_jornada",
        certeza="probable",
        grupo=grupo,
        n=len(lejanos),
        registros=tuple(r.id for r in lejanos),
        evidencia={"mediana_epoch": mediana,
                   "mad_horas": round(mad / _HORA, 2),
                   "distancias_horas": sorted(
                       round(abs(r.instante_registro - mediana) / _HORA, 1)
                       for r in lejanos)},
        explicacion=(f"{len(lejanos)} anotaciones caen lejos del horario en que "
                     f"se cargo el resto de «{grupo}»"),
    )]


def rafagas(registros: list[Registro],
            piso_s: float = PISO_RAFAGA_S,
            minimo: int = MINIMO_RAFAGA) -> list[Hallazgo]:
    """Loads too close together to have been typed by hand.

    The case this anticipates: the session fills up, nobody manages to
    load into the app, and at the end someone dumps everything at once.
    The data can be true, but it wasn't observed when it claims to have
    been -- and that changes what can be asserted about it. That's why
    it's a finding, not an error.
    """
    con_hora = sorted((r for r in registros if r.instante_registro is not None),
                      key=lambda r: r.instante_registro)
    if len(con_hora) < minimo:
        return []
    salida: list[Hallazgo] = []
    corrida = [con_hora[0]]
    for previo, actual in zip(con_hora, con_hora[1:]):
        if actual.instante_registro - previo.instante_registro < piso_s:
            corrida.append(actual)
            continue
        if len(corrida) >= minimo:
            salida.append(_hallazgo_rafaga(corrida, piso_s))
        corrida = [actual]
    if len(corrida) >= minimo:
        salida.append(_hallazgo_rafaga(corrida, piso_s))
    return salida


def _hallazgo_rafaga(corrida: list[Registro], piso_s: float) -> Hallazgo:
    span = corrida[-1].instante_registro - corrida[0].instante_registro
    return Hallazgo(
        patron="rafaga_no_humana",
        certeza="confirmado",
        grupo=corrida[0].grupo,
        n=len(corrida),
        registros=tuple(r.id for r in corrida),
        evidencia={"segundos_totales": round(span, 2),
                   "segundos_por_anotacion": round(span / max(len(corrida) - 1, 1), 2),
                   "piso_s": piso_s},
        explicacion=(f"{len(corrida)} anotaciones en {span:.0f}s: se cargaron de "
                     f"una, no se observaron a esa hora"),
    )


def encabezados_intercalados(registros: list[Registro]) -> list[Hallazgo]:
    """A header in the middle of the group marks the seam of a stitch.

    There are 94 in the corpus. Each one is the top edge of a block
    someone brought over from another sheet, and none of them had been
    used as a signal before.
    """
    filas = sorted(registros, key=lambda r: r.orden)
    if not filas:
        return []
    intercalados = [r for r in filas[1:] if r.es_encabezado]
    if not intercalados:
        return []
    return [Hallazgo(
        patron="encabezado_intercalado",
        certeza="confirmado",
        grupo=filas[0].grupo,
        n=len(intercalados),
        registros=tuple(r.id for r in intercalados),
        evidencia={"ordenes": [r.orden for r in intercalados]},
        explicacion=(f"{len(intercalados)} encabezados dentro del grupo: "
                     f"cada uno es el borde de algo que se pego"),
    )]


# --------------------------------------------------------------------------
# the full run
# --------------------------------------------------------------------------

def analizar(registros: list[Registro],
             minimo_tramo: int = MINIMO_TRAMO,
             limites_extra: tuple[str, ...] = ()) -> Analisis:
    """Runs every detector and returns findings + coverage.

    The output is ordered by size, not by pattern: the first thing read
    has to be the biggest, which in the real corpus was a single sheet
    explaining 70% of the damage.
    """
    por_grupo: dict[str, list[Registro]] = defaultdict(list)
    for r in registros:
        por_grupo[r.grupo].append(r)

    hallazgos: list[Hallazgo] = []
    for filas in por_grupo.values():
        hallazgos += repeticiones(filas)
        hallazgos += encabezados_intercalados(filas)
        hallazgos += fuera_de_jornada(filas)
        hallazgos += rafagas(filas)
    hallazgos += tramos_ajenos(por_grupo, minimo=minimo_tramo)
    hallazgos += anacronismos(registros)

    sin_fecha = sum(1 for r in registros if not r.fecha_declarada)
    sin_instante = sum(1 for r in registros if r.instante_registro is None)
    n = len(por_grupo)

    limites = list(limites_extra)
    limites.append(
        "solo se compararon los grupos de esta corrida: un tramo copiado "
        "desde un grupo ausente no se ve")
    limites.append(
        "una repeticion contigua se marca como probable-real y NO se "
        "descuenta: la forma no alcanza para separarla de una tanda legitima")
    if sin_instante:
        limites.append(
            f"{sin_instante} registros sin instante de carga: los patrones "
            f"temporales (anacronismo, jornada, rafaga) no los alcanzan")
    if sin_fecha:
        limites.append(
            f"{sin_fecha} registros sin fecha declarada: la direccion de un "
            f"tramo ajeno queda decidida solo por peso")
    if any(h.patron == "rafaga_no_humana" for h in hallazgos):
        limites.append(
            "«rafaga_no_humana» solo dice algo si la fuente se anota a mano: "
            "en una ingesta automatica la rafaga es lo esperado")

    return Analisis(
        hallazgos=tuple(sorted(hallazgos, key=lambda h: -h.n)),
        cobertura=Cobertura(
            registros=len(registros),
            grupos=n,
            pares_comparados=n * (n - 1),
            sin_fecha_declarada=sin_fecha,
            sin_instante_registro=sin_instante,
            limites=tuple(limites),
        ),
    )
