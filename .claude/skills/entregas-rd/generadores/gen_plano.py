#!/usr/bin/env python3
"""Genera el plano generico 'servicio completo' replicando el SVG imprimible
del PlanoTool web (web/src/components/PlanoTool.tsx): mismo canvas 2970x2100,
misma simbologia tecnica (symbolIconMarkup) y misma LEYENDA TECNICA.
Preset MAINSTREAM extendido (servicio completo, 15 voluntarios).
"""
import html

ZONE_COLORS = {
    "testeo": "#2d5a4a", "contencion": "#7c3aed", "informativo": "#0369a1",
    "descanso": "#059669", "coordinacion": "#ca8a04", "power": "#f59e0b",
    "rack": "#4b5563", "water": "#2563eb", "sensory": "#8b5cf6",
    "tent": "#2d5a4a", "table": "#10b981", "chairs": "#ca8a04",
    "trash": "#71717a", "light": "#fde047", "contact": "#0ea5e9",
    "security": "#f97316", "medical": "#dc2626", "food": "#a16207",
}

esc = lambda s: html.escape(s, quote=True)


def icon(key, color, cx, cy, scale):
    sw = max(5, 7 * scale)
    c = color
    x = lambda n: cx + (n - 80) * scale
    y = lambda n: cy + (n - 80) * scale
    if key == "power":
        return f'<path d="M {x(88)} {y(28)} L {x(52)} {y(88)} H {x(82)} L {x(72)} {y(132)} L {x(112)} {y(70)} H {x(82)} Z" fill="{c}"/>'
    if key == "water":
        return f'<path d="M {x(80)} {y(24)} C {x(116)} {y(70)} {x(126)} {y(92)} {x(110)} {y(118)} C {x(94)} {y(144)} {x(58)} {y(144)} {x(48)} {y(116)} C {x(38)} {y(88)} {x(58)} {y(66)} {x(80)} {y(24)} Z" fill="none" stroke="{c}" stroke-width="{sw}"/>'
    if key == "table":
        return f'<rect x="{x(28)}" y="{y(54)}" width="{104*scale}" height="{42*scale}" rx="{6*scale}" fill="none" stroke="{c}" stroke-width="{sw}"/><path d="M {x(46)} {y(96)} V {y(130)} M {x(114)} {y(96)} V {y(130)}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>'
    if key == "chairs":
        return f'<path d="M {x(44)} {y(48)} V {y(112)} H {x(88)} M {x(88)} {y(112)} V {y(134)} M {x(94)} {y(48)} V {y(112)} H {x(128)} M {x(128)} {y(112)} V {y(134)}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>'
    if key == "tent":
        return f'<path d="M {x(22)} {y(122)} L {x(80)} {y(34)} L {x(138)} {y(122)} Z M {x(80)} {y(34)} V {y(122)}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round"/>'
    if key == "security":
        return f'<path d="M {x(80)} {y(22)} L {x(124)} {y(40)} V {y(76)} C {x(124)} {y(104)} {x(106)} {y(126)} {x(80)} {y(140)} C {x(54)} {y(126)} {x(36)} {y(104)} {x(36)} {y(76)} V {y(40)} Z" fill="none" stroke="{c}" stroke-width="{sw}"/><path d="M {x(62)} {y(80)} L {x(76)} {y(94)} L {x(102)} {y(62)}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>'
    if key == "medical":
        return f'<path d="M {x(80)} {y(58)} V {y(106)} M {x(56)} {y(82)} H {x(104)}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/><path d="M {x(80)} {y(136)} C {x(34)} {y(96)} {x(28)} {y(66)} {x(48)} {y(46)} C {x(62)} {y(32)} {x(78)} {y(42)} {x(80)} {y(54)} C {x(82)} {y(42)} {x(100)} {y(32)} {x(114)} {y(46)} C {x(134)} {y(66)} {x(126)} {y(98)} {x(80)} {y(136)} Z" fill="none" stroke="{c}" stroke-width="{sw}"/>'
    if key == "testeo":
        return f'<circle cx="{cx}" cy="{cy}" r="{58*scale}" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="{sw}"/><path d="M {x(60)} {y(42)} H {x(100)} M {x(80)} {y(42)} V {y(82)} L {x(112)} {y(126)} H {x(48)} L {x(80)} {y(82)}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
    if key == "contencion":
        return f'<circle cx="{cx}" cy="{cy}" r="{58*scale}" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="{sw}"/><path d="M {x(80)} {y(120)} C {x(44)} {y(88)} {x(44)} {y(62)} {x(62)} {y(52)} C {x(74)} {y(46)} {x(80)} {y(56)} {x(80)} {y(64)} C {x(80)} {y(56)} {x(90)} {y(46)} {x(102)} {y(52)} C {x(120)} {y(62)} {x(116)} {y(90)} {x(80)} {y(120)} Z" fill="{c}"/>'
    # default: circulo con iniciales (igual que el tool)
    return (f'<circle cx="{cx}" cy="{cy}" r="{48*scale}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<text x="{cx}" y="{cy + 11*scale}" text-anchor="middle" font-size="{36*scale}" font-family="Arial" font-weight="900" fill="{c}">{esc(key[:2].upper())}</text>')


# ── Elementos: preset MAINSTREAM del tool + simbolos de requerimientos ──
RECTS = [
    ("ENTRADA", 1250, 100, 500, 120, "#6366f1"),
    ("Mesa 1", 300, 500, 600, 250, "#10b981"),
    ("Mesa 2", 1300, 900, 600, 250, "#10b981"),
    ("Mesa 3", 1850, 1500, 600, 250, "#10b981"),
    ("Stand", 300, 900, 400, 300, "#8b5cf6"),
    ("Stand 2", 800, 900, 400, 300, "#8b5cf6"),
    ("Zona Descanso", 300, 1350, 700, 350, ZONE_COLORS["descanso"]),
]
SYMBOLS = [
    ("testeo", "Testeo", 1000, 550, 200, 200),
    ("contencion", "Contención", 1900, 550, 200, 200),
    ("testeo", "Testeo 2", 1400, 1230, 200, 200),
    ("contencion", "Contención 2", 1650, 1230, 200, 200),
    ("tent", "Toldo 3x3", 1120, 1480, 190, 170),
    ("sensory", "Baja Estim.", 780, 260, 170, 150),
    ("rack", "Rack", 150, 260, 160, 160),
    ("trash", "Basureros", 380, 260, 160, 160),
    ("power", "Electricidad", 2420, 850, 160, 160),
    ("light", "Iluminación", 2690, 850, 160, 160),
    ("water", "Agua", 2420, 1110, 160, 160),
    ("contact", "Producción", 2690, 1110, 160, 160),
    ("security", "Seguridad", 2420, 1370, 160, 160),
    ("medical", "Equipo Médico", 2690, 1370, 160, 160),
    ("food", "Alimentación", 2555, 1630, 160, 160),
]
LEGEND_POS = (2060, 120)

parts = []
parts.append('<svg viewBox="0 0 2970 2100" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">')
parts.append('<rect width="2970" height="2100" fill="#fafafa"/>')
parts.append('<rect x="50" y="50" width="2870" height="1800" fill="none" stroke="#555" stroke-width="5" stroke-dasharray="30 20" rx="20"/>')

for label, x0, y0, w, h, color in RECTS:
    parts.append(f'<g><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="{color}" fill-opacity="0.48" stroke="{color}" stroke-width="8"/>'
                 f'<text x="{x0 + w/2}" y="{y0 + h/2}" text-anchor="middle" dominant-baseline="middle" font-size="42" font-family="Arial, sans-serif" font-weight="900" fill="#111">{esc(label.upper())}</text></g>')

for key, label, x0, y0, w, h in SYMBOLS:
    color = ZONE_COLORS[key]
    cx, cy = x0 + w / 2, y0 + h / 2
    scale = max(0.7, min(w, h) / 170)
    parts.append(f'<g>{icon(key, color, cx, cy, scale)}'
                 f'<text x="{cx}" y="{y0 + h + 34}" text-anchor="middle" font-size="28" font-family="Arial, sans-serif" font-weight="700" fill="{color}">{esc(label.upper())}</text></g>')

# leyenda tecnica (simbolos unicos, 2 columnas, igual que el tool)
seen, legend = set(), []
for key, label, *_ in SYMBOLS:
    if key not in seen:
        seen.add(key)
        legend.append((key, label))
lx, ly = LEGEND_POS
legend_h = min(760, max(190, 120 + -(-len(legend) // 2) * 68))
parts.append(f'<g><rect x="{lx}" y="{ly}" width="760" height="{legend_h}" rx="30" fill="#f4f4f5" fill-opacity="0.96" stroke="#222" stroke-width="5"/>'
             f'<text x="{lx + 380}" y="{ly + 70}" text-anchor="middle" font-size="36" font-family="Arial, sans-serif" font-weight="900" fill="#333">LEYENDA TÉCNICA</text>')
for i, (key, label) in enumerate(legend):
    col, row = i % 2, i // 2
    x0 = lx + 44 + col * 360
    y0 = ly + 138 + row * 68
    color = ZONE_COLORS[key]
    parts.append(f'<g>{icon(key, color, x0 + 20, y0 - 14, 0.32)}'
                 f'<text x="{x0 + 58}" y="{y0}" font-size="22" font-family="Arial, sans-serif" font-weight="800" fill="#333">{esc(label.upper()[:18])}</text></g>')
parts.append('</g>')

parts.append('<text x="100" y="2010" font-size="34" font-family="Arial, sans-serif" font-weight="900" fill="#222">SERVICIO COMPLETO RD · EVENTO MASIVO (GENÉRICO) · LUGAR Y FECHA POR DEFINIR</text>')
parts.append('</svg>')

out = "datadrops/cotizacion_general_eventos/plano_servicio_completo_generico.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(parts) + "\n")
print("OK", out, f"({len(legend)} simbolos en leyenda)")
