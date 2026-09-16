#!/usr/bin/env python3
"""Los detectores. Funciones puras: entran `Registro`, salen `Hallazgo`.

Sin red, sin base de datos, sin escritura. Todo lo que lee viene por
parametro, para que cada regla se pueda probar con ocho filas inventadas.

Las constantes de este archivo no son preferencias: cada una tiene detras una
medicion sobre `Testeo 2025` que esta citada en su docstring. Cuando otra area
las mueva, que las mueva con su propia medicion al lado.
"""
from __future__ import annotations

import statistics
from collections import Counter, defaultdict

try:
    from .registro import Analisis, Cobertura, Hallazgo, Registro
except ImportError:  # direct execution through forense.py
    from registro import Analisis, Cobertura, Hallazgo, Registro

# Un tramo compartido con otro grupo tiene que medir esto para contar.
#
# Medido: con 4 se marcaron 3 filas de `Fiesta Dame 504 mesa 1` como copiadas
# de `Cachorros 35`, y eran falsas -- el supuesto origen era 28 dias POSTERIOR
# y las tres filas eran MDMA «tesla rosada» con resultados distintos entre si.
# Los tramos verdaderos del corpus miden 16, 17, 28 y 71: 6 los deja pasar a
# todos y deja fuera la coincidencia generica.
MINIMO_TRAMO = 6

# Un bloque pegado se reconoce porque MUCHOS contenidos distintos se repiten
# a la MISMA distancia. Ese es su periodo.
#
# Medido: `Mamisonga 8225` da delta 22 en 396 de sus ~640 repeticiones. El
# resto de las hojas del corpus da delta 1 -- filas identicas una debajo de
# otra, que es como se ve una tanda real de muestras iguales, no un pegado.
MINIMO_BLOQUE = 8
FRACCION_BLOQUE = 0.5

# Ventana en que se acepta que una captura pertenezca al evento que declara.
# Una jornada RD empieza antes de la fiesta y los datos se suben despues; lo
# que esta fuera de esto no es tarde, es otro evento.
MARGEN_PREVIO_H = 12.0
MARGEN_POSTERIOR_H = 24.0

# Corte robusto para "esta captura esta lejos del cumulo de su propio grupo".
# 3.5 es el corte de Iglewicz-Hoaglin sobre el z modificado por MAD; el piso
# en horas evita marcar una jornada que simplemente fue corta y pareja.
Z_FUERA_DE_JORNADA = 3.5
PISO_FUERA_DE_JORNADA_H = 12.0

# Dos cargas separadas por menos de esto no las tipeo una persona.
PISO_RAFAGA_S = 3.0
MINIMO_RAFAGA = 4

_HORA = 3600.0


# --------------------------------------------------------------------------
# repeticiones dentro de un mismo grupo
# --------------------------------------------------------------------------

def periodo_dominante(posiciones_por_contenido,
                      minimo=MINIMO_BLOQUE,
                      fraccion=FRACCION_BLOQUE) -> int | None:
    """El periodo de un bloque pegado dentro del grupo, o None.

    Un bloque pegado N veces deja, por cada contenido repetido, una distancia
    constante igual al largo del bloque. Una tanda real de muestras iguales
    deja distancia 1. Por eso solo se consideran distancias mayores a 1, y se
    exige que la distancia modal explique la mitad de las repeticiones: una
    coincidencia no manda sobre el grupo entero.
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
    """Clasifica las repeticiones de un grupo segun su GEOMETRIA.

    Esta es la correccion que costo mas cara del analisis original: contar
    "filas identicas" y llamarlas duplicadas inflaba el dano. De las 904
    repeticiones del corpus, 645 eran un pegado real (periodo 22) y 139 eran
    filas contiguas -- `DAME 1503` tiene 37 de sus 39 repeticiones pegadas una
    debajo de otra, que es exactamente como se ve una mesa donde llegaron
    cinco ketaminas seguidas con el mismo reactivo y el mismo color.

    La forma distingue lo que el contenido no puede:

      lote_contiguo        delta <= 1   probablemente muestras reales
      bloque_periodico     delta == P   pegado, confirmado por el periodo
      repeticion_dispersa  el resto     sin explicacion, queda pendiente
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
# tramos que vienen de OTRO grupo
# --------------------------------------------------------------------------

def _fecha_de(registros: list[Registro]) -> str | None:
    for r in registros:
        if r.fecha_declarada:
            return r.fecha_declarada
    return None


def _quien_copio(a: str, b: str, largo: int, distintos: dict[str, int]) -> tuple[str, str]:
    """Devuelve (copia, origen) segun cuanto pesa el tramo en cada grupo.

    En el original, el tramo ES practicamente todo su contenido propio. En la
    copia, el tramo queda diluido entre las anotaciones nuevas que si se
    hicieron. Medido en el caso mas claro del corpus: el tramo de 71 filas
    pesa 0,96 del contenido distinto de `DAME 1503` y 0,62 del de
    `Psiquiatrico 1603` -- la copia es Psiquiatrico, que es ademas la hoja del
    dia siguiente.

    El umbral de 0,05 evita decidir por ruido cuando dos grupos son casi
    iguales; ahi manda el nombre, porque `Copy of X` se llama asi por algo.
    """
    peso_a = largo / max(distintos.get(a, 1), 1)
    peso_b = largo / max(distintos.get(b, 1), 1)
    if abs(peso_a - peso_b) > 0.05:
        return (a, b) if peso_a < peso_b else (b, a)
    copias_a = a.lower().count("copy of") + a.lower().count("copia de")
    copias_b = b.lower().count("copy of") + b.lower().count("copia de")
    if copias_a != copias_b:
        return (a, b) if copias_a > copias_b else (b, a)
    return tuple(sorted((a, b)))  # estable, y el hallazgo queda en 'pendiente'


def tramos_ajenos(grupos: dict[str, list[Registro]],
                  minimo: int = MINIMO_TRAMO) -> list[Hallazgo]:
    """Tramos contiguos que un grupo comparte con otro: el pegado entre hojas.

    A diferencia del detector original, compara TODOS los grupos que reciba,
    sin importar de que archivo o periodo vengan. Esa era la ceguera: 2024 y
    2025 se importaban por separado, asi que una jornada que heredaba de la
    del año anterior no se veia. La cobertura declara igual que solo se
    compara lo que esta en esta corrida.

    La direccion se decide por peso (`_quien_copio`) y se CORROBORA con la
    fecha: el grupo posterior es el que copio. Si ambas senales coinciden el
    hallazgo queda `confirmado`; si solo hay una, `probable`; si se
    contradicen queda `pendiente` con las dos hipotesis escritas, porque las
    fechas del corpus vienen del nombre de la hoja y no son confiables solas.
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
                        continue  # el hallazgo se emite del lado de la copia
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
    """El grupo sin sus propias repeticiones, en orden.

    Un tramo se trae de otra jornada UNA vez; lo que pasa despues dentro de la
    hoja ya lo explica `repeticiones`. Sin esto, las 31 replicas internas de
    `Mamisonga 8225` vuelven a matchear contra `Cachorros 18125` y el mismo
    tramo de 20 filas se informa 31 veces -- 780 filas "ajenas" donde hay 20.
    Los totales por patron dejarian de poder sumarse entre si.
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
    """Dias entre dos fechas ISO, sin pedir datetime si no hacen falta."""
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
# el tiempo: lo que la planilla no podia detectar y una app si
# --------------------------------------------------------------------------

def anacronismos(registros: list[Registro],
                 margen_previo_h: float = MARGEN_PREVIO_H,
                 margen_posterior_h: float = MARGEN_POSTERIOR_H) -> list[Hallazgo]:
    """Capturas cuyo instante real no cabe en el evento que declaran.

    Es el detector que la planilla nunca pudo tener y que XIO-RD si: una hoja
    de calculo no sabe cuando se escribio una celda, una app sabe exactamente
    cuando se guardo una muestra. Cubre los dos errores que se anticipan:

      registro_en_evento_futuro  -- se cargo ANTES de que el evento ocurriera;
                                    el voluntario eligio una jornada que
                                    todavia no pasa
      registro_en_evento_pasado  -- se cargo mucho DESPUES; el voluntario
                                    eligio una jornada anterior de la lista

    Un registro sin instante no se marca ni se absuelve: no se ve. Eso lo
    cuenta la cobertura.
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
    """Capturas lejos del cumulo temporal de su propio grupo.

    Sirve donde `anacronismos` no llega: cuando el evento no tiene fecha
    declarada, el grupo igual la tiene implicita -- casi todas sus capturas
    caen en unas pocas horas. La que no, se separa sola.

    Usa mediana y MAD, no promedio y desviacion: si el grupo ya trae varias
    capturas erradas, el promedio se corre hacia ellas y deja de verlas. El
    piso en horas evita marcar dispersion normal en una jornada pareja.
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
    """Cargas demasiado seguidas para haberse tipeado.

    El caso que se quiere anticipar: la jornada se llena, nadie alcanza a
    cargar en la app, y al final alguien vuelca todo de una. Los datos pueden
    ser ciertos, pero no se observaron cuando dicen -- y eso cambia lo que se
    puede afirmar de ellos. Por eso es un hallazgo, no un error.
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
    """Un encabezado en medio del grupo marca la costura de un pegado.

    En el corpus hay 94. Cada uno es el borde superior de un bloque que
    alguien trajo de otra hoja, y ninguno se habia usado como señal.
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
# la corrida completa
# --------------------------------------------------------------------------

def analizar(registros: list[Registro],
             minimo_tramo: int = MINIMO_TRAMO,
             limites_extra: tuple[str, ...] = ()) -> Analisis:
    """Corre todos los detectores y devuelve hallazgos + cobertura.

    El orden de la salida es por cantidad, no por patron: lo primero que se
    lee tiene que ser lo mas grande, que en el corpus real fue una sola hoja
    explicando el 70% del dano.
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
