"""Carga central de la identidad visual 'flujo'.

Uso:
    from flujo.brand import load_styles, get_color

    styles = load_styles()
    accent = get_color("accent")

Esto permite que todos los proyectos hereden el mismo estilo sin duplicar.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_styles() -> Dict[str, Any]:
    """Devuelve colores + tipografía + tono de flujo.json."""
    path = Path("projects/flujo/flujo.json")
    if not path.exists():
        return _defaults()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        colors = data.get("colors", {})
        typography = data.get("typography", {})
        tone = data.get("tone", {})
        return {**colors, **typography, "tone": tone}
    except Exception:
        return _defaults()


def get_color(name: str, default: str = "#000000") -> str:
    """Acceso rápido a un color."""
    return load_styles().get(name, default)


def _defaults() -> Dict[str, Any]:
    return {
        "ink": "#1f2a24",
        "accent": "#2d5a4a",
        "paper": "#f8f1e3",
        "support": "#675f55",
        "alert": "#c2410f",
        "tone": {"voice": "directo, útil, humano"}
    }
