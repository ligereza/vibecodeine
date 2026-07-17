"""Loader central de identidad visual flujo.

Historia: este modulo quedo vaciado ("migrado a knowledge/logos") en una
migracion previa, pero projects/cotizaciones/engine.py y render/piezas.py
seguian importando load_styles/get_color de aqui -- engine.py reventaba con
ImportError (flujo cotizaciones roto) y piezas.py lo tragaba en un
try/except pass. Restaurado 2026-07-16 (checkpoint Ola 3) leyendo la fuente
de verdad declarada: projects/flujo/flujo.json (colors).

El grupo CLI `flujo brand` sigue LEGACY (usar knowledge/logos); este modulo
solo hospeda el loader de identidad.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# Valores espejo de projects/flujo/flujo.json (colors) -- fallback si el
# JSON no esta (p. ej. paquete instalado fuera del repo). Si cambias la
# identidad, cambia el JSON; esto es solo red de seguridad.
_DEFAULT_COLORS: dict[str, str] = {
    "ink": "#1f2a24",
    "accent": "#2d5a4a",
    "paper": "#f8f1e3",
    "support": "#675f55",
    "alert": "#c2410f",
}

_FLUJO_JSON = Path(__file__).resolve().parents[2] / "projects" / "flujo" / "flujo.json"


@lru_cache(maxsize=1)
def load_styles() -> dict[str, str]:
    """Colores de identidad flujo como dict plano {ink, accent, paper, ...}.

    Lee projects/flujo/flujo.json (seccion colors); si no existe o esta
    corrupto cae a los defaults espejo. Nunca lanza.
    """
    try:
        data: Any = json.loads(_FLUJO_JSON.read_text(encoding="utf-8"))
        colors = data.get("colors")
        if isinstance(colors, dict) and colors:
            return {str(k): str(v) for k, v in colors.items()}
    except (OSError, ValueError):
        pass
    return dict(_DEFAULT_COLORS)


def get_color(key: str, default: str = "#000000") -> str:
    """Un color de la identidad por nombre (ink/accent/paper/support/alert)."""
    return load_styles().get(key, default)
