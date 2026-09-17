"""Motor reusable de procedencia para registros de VIBECODEINE."""

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
    # La FORMA de la tabla, anterior al contenido de sus filas: si el lector
    # supone una estructura que la fuente no tiene, todo lo demas es basura.
    "analizar_estructura",
    "bloques_desprendidos",
    "columnas_divergentes",
    "grupos_duplicados",
    "rotulos_intercalados",
]
