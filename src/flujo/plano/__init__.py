"""Módulo de planos de stands para eventos — constantes de realidad."""
from .engine import (
    CONSTANTES,
    Caja,
    reglas_rider,
    modulos_desde_evento,
    solve_layout,
    render_svg,
    render_rider,
    validate_evento,
    render_validation_report,
    load_evento,
)
from .costs import calcular_costos, resumen_costos

__all__ = [
    "CONSTANTES",
    "Caja",
    "reglas_rider",
    "modulos_desde_evento",
    "solve_layout",
    "render_svg",
    "render_rider",
    "validate_evento",
    "render_validation_report",
    "load_evento",
    "calcular_costos",
    "resumen_costos",
]
