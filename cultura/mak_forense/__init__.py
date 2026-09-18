"""Reusable provenance engine for VIBECODEINE records."""

from .estructura import (
    analizar_estructura,
    bloques_desprendidos,
    columnas_divergentes,
    grupos_duplicados,
    rotulos_intercalados,
)
from .patrones import analizar
from .registro import Analisis, Cobertura, Hallazgo, Registro

__all__ = [
    "Analisis",
    "Cobertura",
    "Hallazgo",
    "Registro",
    "analizar",
    # The SHAPE of the table, prior to the content of its rows: if the reader
    # assumes a structure the source doesn't have, everything else is garbage.
    "analizar_estructura",
    "bloques_desprendidos",
    "columnas_divergentes",
    "grupos_duplicados",
    "rotulos_intercalados",
]
