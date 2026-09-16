"""Motor reusable de procedencia para registros de VIBECODEINE."""

from .patrones import analizar
from .registro import Analisis, Cobertura, Hallazgo, Registro

__all__ = [
    "Analisis",
    "Cobertura",
    "Hallazgo",
    "Registro",
    "analizar",
]
