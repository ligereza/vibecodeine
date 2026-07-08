"""Iconos operativos del stand de reduccion de danos (glyphs SVG line-art).

Portados 1:1 desde web/src/components/PlanoTool.tsx (symbolIconMarkup) para que
el plano del PDF y el editor web muestren los mismos simbolos. Cada glyph es una
funcion (cx, cy, scale, color) -> str con el markup SVG del icono centrado en
(cx, cy). La paleta COLORES espeja ZONE_COLORS del web.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List

from .engine import es_masivo

# Espejo de ZONE_COLORS (PlanoTool.tsx) — misma paleta neon en web y PDF.
COLORES: Dict[str, str] = {
    "tent": "#2d5a4a", "table": "#10b981", "power": "#f59e0b", "light": "#fde047",
    "water": "#2563eb", "extinguisher": "#dc2626", "medical": "#dc2626",
    "security": "#f97316", "testeo": "#f59e0b", "contencion": "#7c3aed",
    "food": "#a16207", "heating": "#ef4444", "trash": "#71717a",
    "contact": "#0ea5e9", "sensory": "#8b5cf6",
}

ETIQUETAS: Dict[str, str] = {
    "tent": "Toldo 3x3", "table": "Mesas", "power": "Electricidad", "light": "Iluminacion",
    "water": "Agua", "extinguisher": "Extintor", "medical": "Equipo Medico",
    "security": "Seguridad", "testeo": "Testeo", "contencion": "Contencion",
    "food": "Alimentacion", "heating": "Calefaccion", "trash": "Basureros",
    "contact": "Produccion", "sensory": "Baja Estim.",
}


def _hx(cx: float, n: float, s: float) -> float:
    return cx + (n - 80) * s


def _hy(cy: float, n: float, s: float) -> float:
    return cy + (n - 80) * s


def _glyph_power(cx, cy, s, c):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return f'<path d="M {x(88)} {y(28)} L {x(52)} {y(88)} H {x(82)} L {x(72)} {y(132)} L {x(112)} {y(70)} H {x(82)} Z" fill="{c}"/>'


def _glyph_water(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(80)} {y(24)} C {x(116)} {y(70)} {x(126)} {y(92)} {x(110)} {y(118)} '
            f'C {x(94)} {y(144)} {x(58)} {y(144)} {x(48)} {y(116)} C {x(38)} {y(88)} {x(58)} {y(66)} {x(80)} {y(24)} Z" '
            f'fill="none" stroke="{c}" stroke-width="{sw}"/>')


def _glyph_table(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<rect x="{x(28)}" y="{y(54)}" width="{104*s:.1f}" height="{42*s:.1f}" rx="{6*s:.1f}" '
            f'fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M {x(46)} {y(96)} V {y(130)} M {x(114)} {y(96)} V {y(130)}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


def _glyph_tent(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(22)} {y(122)} L {x(80)} {y(34)} L {x(138)} {y(122)} Z M {x(80)} {y(34)} V {y(122)}" '
            f'fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round"/>')


def _glyph_security(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(80)} {y(22)} L {x(124)} {y(40)} V {y(76)} C {x(124)} {y(104)} {x(106)} {y(126)} {x(80)} {y(140)} '
            f'C {x(54)} {y(126)} {x(36)} {y(104)} {x(36)} {y(76)} V {y(40)} Z" fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M {x(62)} {y(80)} L {x(76)} {y(94)} L {x(102)} {y(62)}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


def _glyph_medical(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(80)} {y(58)} V {y(106)} M {x(56)} {y(82)} H {x(104)}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<path d="M {x(80)} {y(136)} C {x(34)} {y(96)} {x(28)} {y(66)} {x(48)} {y(46)} C {x(62)} {y(32)} {x(78)} {y(42)} {x(80)} {y(54)} '
            f'C {x(82)} {y(42)} {x(100)} {y(32)} {x(114)} {y(46)} C {x(134)} {y(66)} {x(126)} {y(98)} {x(80)} {y(136)} Z" '
            f'fill="none" stroke="{c}" stroke-width="{sw}"/>')


def _glyph_extinguisher(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<rect x="{x(60)}" y="{y(50)}" width="{42*s:.1f}" height="{88*s:.1f}" rx="{9*s:.1f}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M {x(70)} {y(50)} V {y(34)} H {x(94)} V {y(50)} M {x(94)} {y(62)} H {x(120)} L {x(134)} {y(52)}" '
            f'stroke="{c}" fill="none" stroke-width="{sw}" stroke-linecap="round"/>')


def _glyph_testeo(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{58*s:.1f}" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M {x(60)} {y(42)} H {x(100)} M {x(80)} {y(42)} V {y(82)} L {x(112)} {y(126)} H {x(48)} L {x(80)} {y(82)}" '
            f'fill="none" stroke="{c}" stroke-width="{sw}"/>')


def _glyph_contencion(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{58*s:.1f}" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M {x(80)} {y(120)} C {x(44)} {y(88)} {x(44)} {y(62)} {x(62)} {y(52)} C {x(74)} {y(46)} {x(80)} {y(56)} {x(80)} {y(64)} '
            f'C {x(80)} {y(56)} {x(90)} {y(46)} {x(102)} {y(52)} C {x(120)} {y(62)} {x(116)} {y(90)} {x(80)} {y(120)} Z" fill="{c}"/>')


def _glyph_light(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(80)} {y(30)} C {x(52)} {y(30)} {x(38)} {y(54)} {x(50)} {y(80)} C {x(58)} {y(96)} {x(66)} {y(100)} {x(66)} {y(114)} '
            f'H {x(94)} C {x(94)} {y(100)} {x(102)} {y(96)} {x(110)} {y(80)} C {x(122)} {y(54)} {x(108)} {y(30)} {x(80)} {y(30)} Z" '
            f'fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M {x(66)} {y(126)} H {x(94)} M {x(70)} {y(138)} H {x(90)}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


def _glyph_food(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(56)} {y(34)} V {y(74)} M {x(56)} {y(74)} C {x(56)} {y(86)} {x(48)} {y(88)} {x(48)} {y(100)} V {y(132)} '
            f'M {x(56)} {y(34)} M {x(64)} {y(34)} V {y(74)} C {x(64)} {y(86)} {x(72)} {y(88)} {x(72)} {y(100)} V {y(132)}" '
            f'stroke="{c}" stroke-width="{sw}" fill="none" stroke-linecap="round"/>'
            f'<path d="M {x(108)} {y(34)} C {x(96)} {y(34)} {x(92)} {y(52)} {x(92)} {y(70)} C {x(92)} {y(84)} {x(108)} {y(84)} {x(108)} {y(84)} '
            f'V {y(132)}" stroke="{c}" stroke-width="{sw}" fill="none" stroke-linecap="round"/>')


def _glyph_trash(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(48)} {y(52)} H {x(112)} M {x(66)} {y(52)} V {y(42)} H {x(94)} V {y(52)} '
            f'M {x(56)} {y(52)} L {x(60)} {y(130)} H {x(100)} L {x(104)} {y(52)}" '
            f'fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="M {x(72)} {y(66)} V {y(118)} M {x(88)} {y(66)} V {y(118)}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


def _glyph_contact(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<circle cx="{cx:.1f}" cy="{_hy(cy, 56, s):.1f}" r="{22*s:.1f}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M {x(44)} {y(134)} C {x(44)} {y(102)} {x(64)} {y(90)} {x(80)} {y(90)} C {x(96)} {y(90)} {x(116)} {y(102)} {x(116)} {y(134)}" '
            f'fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


def _glyph_sensory(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(112)} {y(96)} C {x(96)} {y(112)} {x(64)} {y(110)} {x(52)} {y(84)} C {x(42)} {y(62)} {x(54)} {y(38)} {x(76)} {y(32)} '
            f'C {x(62)} {y(52)} {x(70)} {y(84)} {x(112)} {y(96)} Z" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round"/>')


def _glyph_heating(cx, cy, s, c, sw):
    x = lambda n: _hx(cx, n, s); y = lambda n: _hy(cy, n, s)  # noqa: E731
    return (f'<path d="M {x(80)} {y(34)} C {x(64)} {y(54)} {x(96)} {y(66)} {x(80)} {y(92)} '
            f'M {x(64)} {y(70)} C {x(54)} {y(84)} {x(70)} {y(96)} {x(62)} {y(112)} "'
            f' fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


_GLYPHS: Dict[str, Callable[..., str]] = {
    "power": lambda cx, cy, s, c, sw: _glyph_power(cx, cy, s, c),
    "water": _glyph_water, "table": _glyph_table, "tent": _glyph_tent,
    "security": _glyph_security, "medical": _glyph_medical,
    "extinguisher": _glyph_extinguisher, "testeo": _glyph_testeo,
    "contencion": _glyph_contencion, "light": _glyph_light, "food": _glyph_food,
    "trash": _glyph_trash, "contact": _glyph_contact, "sensory": _glyph_sensory,
    "heating": _glyph_heating,
}


def icono(key: str, cx: float, cy: float, scale: float = 1.0, color: str | None = None) -> str:
    """Devuelve el markup SVG del icono `key` centrado en (cx, cy)."""
    c = color or COLORES.get(key, "#9ca3af")
    sw = max(3.0, 5.0 * scale)
    fn = _GLYPHS.get(key)
    if fn is None:
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{34*scale:.1f}" fill="none" stroke="{c}" stroke-width="{sw}"/>')
    if key == "power":
        return fn(cx, cy, scale, c, sw)
    return fn(cx, cy, scale, c, sw)


def simbolos_de_evento(ev: Dict[str, Any]) -> List[str]:
    """Iconos operativos que corresponden al evento (regla logica del rider).

    Base siempre presente + condicionales por testeo / jornada / masivo. Sillas
    quedan fuera a proposito (confunden el plano; el conteo va en el rider).
    """
    base = ["tent", "table", "power", "light", "water", "extinguisher",
            "medical", "security", "trash", "contact"]
    if bool(ev.get("incluye_testeo", False)):
        base.append("testeo")
    if float(ev.get("duracion_horas", 0) or 0) > 5:
        base.append("food")
    if es_masivo(ev):
        base += ["contencion", "sensory"]
    return base
