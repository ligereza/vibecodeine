#!/usr/bin/env python3
"""Modelo minimo para analizar la PROCEDENCIA de un registro.

Nace del analisis de `Testeo 2025` (2026-09-16): una planilla donde cada
voluntario armaba la hoja de su jornada copiando la del evento anterior y
sobrescribiendo filas. Lo que no alcanzaba a sobrescribir quedaba como
muestra que nadie testeo. 2.856 filas, de las cuales 645 eran un bloque
pegado 31 veces y 132 venian de OTRA jornada.

El modulo no es de la planilla. Es de la forma del problema, que se repite
en cualquier registro humano bajo urgencia:

    anotacion + otra anotacion de otra fecha -> ¿son la misma?
    y si lo son, ¿cual es el original y cual la copia?

Por eso el registro aca es abstracto: un `contenido` comparable, un `grupo`
al que pertenece, un `orden` dentro de ese grupo, y -- cuando existe -- el
instante real en que se anoto. Con eso alcanza para XIO-RD (una muestra
cargada en el evento equivocado), para la planilla vieja, y para cualquier
otra area de MAK que registre hechos en el tiempo.

Tres reglas del dominio RD que aca son estructura, no comentario:

1. Nada se descarta. Un hallazgo MARCA un registro, nunca lo borra. La
   decision de excluirlo es humana y posterior.
2. La certeza se declara. `confirmado` / `probable` / `pendiente` no son
   decoracion: separan lo que la matematica probo de lo que solo sugiere.
3. El analisis declara lo que NO pudo ver. `Cobertura.limites` existe para
   que un total nunca se lea como completo. Un detector silencioso sobre
   sus puntos ciegos miente por omision.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict

# Lo que el analisis pudo probar sobre un hallazgo.
#
#   confirmado -- dos senales independientes coinciden (p.ej. el peso del
#                 tramo y la fecha dicen lo mismo sobre quien copio a quien)
#   probable   -- una sola senal, sin nada que la contradiga
#   pendiente  -- hay senal, y las senales se contradicen, o falta el dato
#                 que decidiria. Es un hallazgo igual: el pendiente se
#                 muestra, no se esconde.
CERTEZAS = ("confirmado", "probable", "pendiente")


@dataclass(frozen=True)
class Registro:
    """Una anotacion, con lo minimo para juzgar si se repite y de donde viene.

    `contenido` es la tupla de campos que definen "la misma anotacion". Que
    campos entran es una decision del area, no de este modulo: en los testeos
    son sustancia/formato/reactivos/resultados; en otra area seran otros. Lo
    que este modulo garantiza es que dos registros con el mismo `contenido`
    se traten como el mismo hecho anotado dos veces.

    `orden` es la posicion dentro del grupo (fila de la planilla, id
    correlativo, indice de carga). Es el eje sobre el que se mide si una
    repeticion es contigua o periodica, y por eso tiene que ser comparable
    dentro del grupo -- no necesita ser global.

    `fecha_declarada` es lo que el registro DICE de si mismo (la fecha del
    evento). `instante_registro` es cuando se anoto DE VERDAD (epoch). La
    distancia entre ambos es el detector mas util que existe para un registro
    hecho en una app: si no coinciden, alguien eligio el evento equivocado.
    """

    id: str
    grupo: str
    orden: int
    contenido: tuple
    fecha_declarada: str | None = None
    instante_registro: float | None = None
    es_encabezado: bool = False
    etiqueta: str = ""


@dataclass(frozen=True)
class Hallazgo:
    """Un patron encontrado, con la evidencia que lo sostiene.

    `explicacion` esta en castellano y en una linea porque el destinatario no
    es un log: es la persona que tiene que decidir que hacer con el registro.
    """

    patron: str
    certeza: str
    grupo: str
    n: int
    explicacion: str
    registros: tuple[str, ...] = ()
    origen: str | None = None
    evidencia: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.certeza not in CERTEZAS:
            raise ValueError(f"certeza desconocida: {self.certeza!r}")


@dataclass(frozen=True)
class Cobertura:
    """Lo que el analisis vio, y sobre todo lo que NO pudo ver.

    Esto existe por una equivocacion concreta y reciente: el detector de
    tramos copiados solo comparaba hojas dentro de una misma corrida, asi que
    una hoja de 2025 copiada de una de 2024 le era invisible -- y el informe
    no lo decia. Un numero sin su cobertura se lee como un total, y no lo era.
    """

    registros: int
    grupos: int
    pares_comparados: int
    sin_fecha_declarada: int
    sin_instante_registro: int
    limites: tuple[str, ...] = ()


@dataclass(frozen=True)
class Analisis:
    hallazgos: tuple[Hallazgo, ...]
    cobertura: Cobertura

    def por_patron(self) -> dict[str, int]:
        cuenta: dict[str, int] = {}
        for h in self.hallazgos:
            cuenta[h.patron] = cuenta.get(h.patron, 0) + h.n
        return dict(sorted(cuenta.items(), key=lambda kv: -kv[1]))

    def por_certeza(self) -> dict[str, int]:
        cuenta = {c: 0 for c in CERTEZAS}
        for h in self.hallazgos:
            cuenta[h.certeza] += h.n
        return cuenta

    def como_dict(self) -> dict:
        return {
            "hallazgos": [asdict(h) for h in self.hallazgos],
            "cobertura": asdict(self.cobertura),
            "por_patron": self.por_patron(),
            "por_certeza": self.por_certeza(),
            "principio": (
                "un hallazgo marca un registro, nunca lo borra; "
                "la exclusion es una decision humana posterior"
            ),
        }

    def como_json(self, indent: int | None = None) -> str:
        return json.dumps(self.como_dict(), ensure_ascii=False, indent=indent,
                          default=str)
