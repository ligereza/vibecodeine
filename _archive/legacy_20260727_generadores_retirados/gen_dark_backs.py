#!/usr/bin/env python3
"""Variantes DARK/NEON de los reversos QR de suplementos (11 y 12).

Sistema rave oficial de linea_editorial/v4.1.md: Negro RD #0A0A0A, Blanco
ceramico #F2F2F2, Magenta RD #C800C8, Amarillo RD #FFD21F + paleta de apoyo
(naranja #E67E22, violeta #8B4DFF). Logo RD Version A real (raster extraido
del composite oficial, assets/logo/RD_logo_A_transparente.png) embebido como
imagen — NUNCA regenerado. QR mantiene tarjeta blanca para escaneo.
Sin filtros SVG (compatibilidad Illustrator).
"""
import base64
import textwrap
import qrcode

FONT = "Arial, Helvetica, sans-serif"
NEGRO = "#0A0A0A"
PANEL = "#161318"
BLANCO = "#F2F2F2"
MUTED = "#A79FA8"
MAGENTA = "#C800C8"
MAGENTA_LOGO = "#B100B8"
AMARILLO = "#FFD21F"
NARANJA = "#E67E22"
VIOLETA = "#8B4DFF"
LINE = "#3A2F3D"
WHITE = "#FFFFFF"
INK = "#161513"

LOGO_B64 = base64.b64encode(open("assets/logo/RD_logo_A_transparente.png", "rb").read()).decode()
LOGO_W, LOGO_H = 216, 171  # px reales del asset

CONTENT = {
    "post_fiesta_dark": {
        "accent": NARANJA,
        "tag": "RECUPERACIÓN POST",
        "tag_w": 360,
        "kicker": "PRODUCTO",
        "title": "POST FIESTA",
        "title_size": 85,
        "desc_title": "Descripción",
        "desc_paras": [
            "Suplemento alimenticio diseñado para complementar la alimentación en contextos de alta exigencia fisiológica, donde el organismo puede requerir apoyo en su equilibrio y funcionamiento normal.",
            "Una alternativa práctica dentro de un enfoque de autocuidado, orientado a acompañar al organismo en momentos de mayor demanda.",
        ],
        "list_title": "Nutrientes",
        "items": [
            "Electrolitos (sodio, potasio, magnesio y calcio): reponen minerales esenciales.",
            "Vitamina C: apoya la función inmune y tiene efecto antioxidante.",
            "Vitaminas del complejo B (B1, B6, B12): contribuyen al metabolismo energético.",
            "N-acetilcisteína (NAC): precursor del glutatión para la detoxificación.",
            "Cardo mariano (silimarina): tradicionalmente asociado a la salud hepática.",
            "Coenzima Q10: antioxidante clave en la producción de energía celular.",
        ],
        "glow": NARANJA,
        "meta": "11_post_fiesta_back_qr_dark",
        "out": "svg/suplementos_rd/02_editables_svg/11_post_fiesta_back_qr_dark_editable.svg",
        "box1": (620, 800), "box2": (1480, 700),
        "desc_size": 46, "desc_lead": 66, "desc_wrap": 60,
        "item_size": 36, "item_lead": 52, "item_gap": 26, "item_wrap": 82,
    },
    "linea_dark": {
        "accent": MAGENTA,
        "tag": "INFORMACIÓN GENERAL",
        "tag_w": 400,
        "kicker": "LÍNEA",
        "title": "Línea de Suplementos RD",
        "title_size": 76,
        "desc_title": "Descripción",
        "desc_paras": [
            "Suplementos alimenticios desarrollados por Reduciendo Daño para acompañar al organismo desde una perspectiva de reducción de daños.",
            "Cada producto tiene un perfil diferenciado de nutrientes, pensado para contextos concretos de la vida cotidiana.",
        ],
        "list_title": "Productos",
        "items": [
            "Pre Fiesta: apoya el metabolismo energético y la respuesta al estrés antes de situaciones de alta demanda.",
            "Post Fiesta: complementa la recuperación nutricional tras contextos de alta exigencia fisiológica.",
            "Impulso: contribuye al estado de alerta y la concentración en actividades que requieren foco sostenido.",
            "Hongos Adaptógenos: acompaña procesos de regulación y bienestar en rutinas exigentes.",
            "Citrato y Bisglicinato de Magnesio: complementa la ingesta diaria de magnesio, mineral esencial.",
            "Creatina: la molécula más estudiada en suplementación nutricional. En polvo (1 kg) y en gomitas.",
            "Proteína: proteína de suero de leche para apoyar la recuperación muscular y el aporte proteico diario.",
        ],
        "glow": MAGENTA,
        "meta": "12_linea_suplementos_back_qr_dark",
        "out": "svg/suplementos_rd/02_editables_svg/12_linea_suplementos_back_qr_dark_editable.svg",
        "box1": (620, 560), "box2": (1240, 940),
        "desc_size": 44, "desc_lead": 62, "desc_wrap": 62,
        "item_size": 33, "item_lead": 46, "item_gap": 14, "item_wrap": 88,
    },
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size, fill=BLANCO, weight=400, cls=' class="txt"', anchor=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text{cls} x="{x}" y="{y}"{a} fill="{fill}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}">{esc(s)}</text>')


def inline_logo_svg(variant, x, y, w):
    """Logo RD vectorial inline (crisp a cualquier zoom)."""
    raw = open(f"assets/logo/RD_logo_vector_{variant}.svg", encoding="utf-8").read()
    inner = raw[raw.index("<svg"):]
    h = round(w * 817.61 / 1060, 1)
    return inner.replace("<svg ", f'<svg x="{x}" y="{y}" width="{w}" height="{h}" ', 1)


def qr_svg(x, y, size_px, url="https://reduciendodano.cl"):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=1, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    m = qr.modules
    n = len(m)
    mod = size_px / n
    parts = [f'<rect x="{x-48}" y="{y-48}" width="{size_px+96}" height="{size_px+96}" rx="18" fill="{WHITE}"/>']
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            if v:
                parts.append(f'<rect x="{x + c*mod:.1f}" y="{y + r*mod:.1f}" width="{mod:.2f}" height="{mod:.2f}" fill="{INK}"/>')
    return "\n".join(parts), n


def neon_ring(cx, cy, r, color):
    """Halo neon sin filtros: anillos concentricos con opacidad decreciente."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="34" opacity=".05"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="18" opacity=".12"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="6" opacity=".55"/>')


def build(key):
    c = CONTENT[key]
    acc = c["accent"]
    b1y, b1h = c["box1"]
    b2y, b2h = c["box2"]
    S = []
    S.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="2000px" height="2800px" viewBox="0 0 2000 2800">')
    S.append(f'<metadata>{c["meta"]} / editable dark-neon / 2000x2800 px</metadata>')
    # fondo
    S.append('<g id="fondo_editable">')
    S.append(f'<rect x="0" y="0" width="2000" height="2800" rx="0" fill="{NEGRO}"/>')
    S.append(neon_ring(280, 320, 330, c["glow"]))
    S.append(neon_ring(1780, 180, 260, VIOLETA))
    S.append(neon_ring(1920, 2620, 380, MAGENTA))
    S.append(f'<circle cx="-40" cy="2400" r="230" fill="{c["glow"]}" opacity=".07"/>')
    S.append('</g>')
    # marco y deco
    S.append('<g id="marco_y_decoracion_editable">')
    S.append(f'<rect x="70" y="70" width="1860" height="2660" rx="70" fill="none" stroke="{MAGENTA}" stroke-width="10" opacity=".16"/>')
    S.append(f'<rect x="70" y="70" width="1860" height="2660" rx="70" fill="none" stroke="{MAGENTA}" stroke-width="4" opacity=".55"/>')
    S.append(f'<rect x="1600" y="210" width="210" height="92" rx="46" fill="none" stroke="{AMARILLO}" stroke-width="6" transform="rotate(-14 1705 256)" opacity=".8"/>')
    S.append(f'<rect x="1435" y="315" width="158" height="76" rx="38" fill="none" stroke="{MAGENTA}" stroke-width="5" transform="rotate(18 1514 353)" opacity=".8"/>')
    S.append('</g>')
    # header con logo real (raster oficial extraido, no regenerado)
    tag_x = 1880 - c["tag_w"]
    lw = 176
    lh = round(lw * LOGO_H / LOGO_W)
    S.append('<g id="header_marca">')
    S.append(inline_logo_svg("blanco", 112, 86, lw))
    S.append(txt(310, 175, "Reduciendo Daño", 42, BLANCO, 700))
    S.append(f'<rect x="{tag_x}" y="116" width="{c["tag_w"]}" height="60" rx="30" fill="{PANEL}" stroke="{acc}" stroke-width="3" opacity=".95"/>')
    S.append(txt(tag_x + 35, 148, c["tag"], 24, acc, 700))
    S.append('</g>')
    # titulo con eco neon (sin filtros)
    CX = 1000  # centro del canvas 2000
    S.append('<g id="titulo">')
    S.append(txt(CX, 300, c["kicker"], 27, AMARILLO, 700, anchor="middle"))
    S.append(txt(CX + 4, 407, c["title"], c["title_size"], c["glow"], 700, cls='', anchor="middle"))
    S.append(txt(CX, 403, c["title"], c["title_size"], BLANCO, 700, anchor="middle"))
    S.append('</g>')
    # cajas
    S.append('<g id="cajas_editables">')
    for (yy, hh) in [(b1y, b1h), (b2y, b2h)]:
        S.append(f'<rect x="120" y="{yy}" width="1760" height="{hh}" rx="44" fill="{PANEL}" stroke="{LINE}" stroke-width="3"/>')
        S.append(f'<rect x="120" y="{yy}" width="1760" height="{hh}" rx="44" fill="none" stroke="{acc}" stroke-width="2" opacity=".45"/>')
    S.append(f'<rect x="120" y="2230" width="1760" height="380" rx="44" fill="{PANEL}" stroke="{MAGENTA}" stroke-width="3" opacity=".95"/>')
    S.append('</g>')
    # contenido
    S.append('<g id="contenido_texto">')
    y = b1y + 103
    S.append(txt(185, y, c["desc_title"], 48, AMARILLO, 700))
    y += 72
    for para in c["desc_paras"]:
        for ln in textwrap.wrap(para, c["desc_wrap"]):
            S.append(txt(185, y, ln, c["desc_size"]))
            y += c["desc_lead"]
        y += 32
    assert y - 32 <= b1y + b1h - 40, f"{key}: desc desborda caja1 ({y})"
    y = b2y + 103
    S.append(txt(185, y, c["list_title"], 48, AMARILLO, 700))
    y += 64
    for item in c["items"]:
        first = True
        for ln in textwrap.wrap(item, c["item_wrap"]):
            if first:
                S.append(txt(185, y, "•", c["item_size"], acc, 700, cls=""))
                S.append(txt(235, y, ln, c["item_size"]))
                first = False
            else:
                S.append(txt(235, y, ln, c["item_size"]))
            y += c["item_lead"]
        y += c["item_gap"]
    assert y - c["item_gap"] <= b2y + b2h - 40, f"{key}: items desbordan caja2 ({y})"
    S.append('</g>')
    # bloque QR (tarjeta blanca para escaneo)
    S.append('<g id="bloque_qr">')
    qr_block, n = qr_svg(205, 2275, 290)
    S.append(qr_block)
    S.append(txt(590, 2360, "Escanea el código", 46, AMARILLO, 700))
    S.append(txt(590, 2432, "y visita reduciendodano.cl", 40, BLANCO, 400))
    S.append(txt(590, 2510, "Síguenos en nuestras redes sociales · @reduciendodano.cl", 28, MUTED, 400))
    S.append('</g>')
    # footer
    S.append('<g id="footer">')
    S.append(f'<line x1="120" y1="2640" x2="1880" y2="2640" stroke="{MAGENTA}" stroke-width="5" opacity=".7"/>')
    S.append(txt(120, 2716, "@ REDUCIENDODANO.CL", 46, AMARILLO, 700))
    S.append(txt(1060, 2698, "VISITA NUESTRA WEB Y SÍGUENOS EN NUESTRAS REDES", 22, MUTED, 700))
    S.append(txt(1060, 2726, "SOCIALES", 22, MUTED, 700))
    S.append('</g>')
    S.append('</svg>')
    with open(c["out"], "w", encoding="utf-8") as f:
        f.write("\n".join(S) + "\n")
    print(f"OK {c['out']} (QR {n}x{n})")


for k in CONTENT:
    build(k)
