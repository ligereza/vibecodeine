#!/usr/bin/env python3
"""Genera los reversos con QR de suplementos RD (09 y 10) siguiendo la
estructura canonica de svg/suplementos_rd/02_editables_svg/*.editable.svg.

Paleta y reglas: linea_editorial v4.1 §6.H + CONTRAPORTADAS_SUPLEMENTOS_RD.md
(fondo #F6EFE3, verde #173F2F, amarillo #F5C54D, texto >=24px, margen seguro
>=59px, footer @REDUCIENDODANO.CL). QR vectorial a https://reduciendodano.cl
"""
import textwrap
import qrcode

FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"
INK = "#161513"
MUTED = "#675F55"
GREEN = "#173F2F"
YELLOW = "#F5C54D"
ORANGE = "#EF7B2D"
LINE = "#D9CEC0"
WHITE = "#FFFFFF"
CREAM = "#F6EFE3"

CONTENT = {
    "post_fiesta": {
        "accent": ORANGE,
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
        "deco": [ORANGE, YELLOW],
        "circles": ORANGE,
        "meta": "09_post_fiesta_back_qr",
        "out": "svg/suplementos_rd/02_editables_svg/09_post_fiesta_back_qr_editable.svg",
        # layout
        "box1": (620, 800), "box2": (1480, 700),
        "desc_size": 46, "desc_lead": 66, "desc_wrap": 60,
        "item_size": 36, "item_lead": 52, "item_gap": 26, "item_wrap": 82,
    },
    "linea": {
        "accent": GREEN,
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
        "deco": [GREEN, YELLOW],
        "circles": GREEN,
        "meta": "10_linea_suplementos_back_qr",
        "out": "svg/suplementos_rd/02_editables_svg/10_linea_suplementos_back_qr_editable.svg",
        "box1": (620, 560), "box2": (1240, 940),
        "desc_size": 44, "desc_lead": 62, "desc_wrap": 62,
        "item_size": 33, "item_lead": 46, "item_gap": 14, "item_wrap": 88,
    },
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size, fill=INK, weight=400, cls=' class="txt"'):
    return (f'<text{cls} x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}">{esc(s)}</text>')


def qr_svg(x, y, size_px, url="https://reduciendodano.cl"):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=1, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    m = qr.modules
    n = len(m)
    mod = size_px / n
    parts = [f'<rect x="{x-48}" y="{y-48}" width="{size_px+96}" height="{size_px+96}" fill="{WHITE}"/>']
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            if v:
                px = x + c * mod
                py = y + r * mod
                parts.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{mod:.2f}" height="{mod:.2f}" fill="{INK}"/>')
    return "\n".join(parts), n


def build(key):
    c = CONTENT[key]
    acc = c["accent"]
    b1y, b1h = c["box1"]
    b2y, b2h = c["box2"]
    S = []
    S.append('<svg xmlns="http://www.w3.org/2000/svg" width="2000px" height="2800px" viewBox="0 0 2000 2800">')
    S.append(f'<metadata>{c["meta"]} / editable / 2000x2800 px</metadata>')
    # fondo
    S.append('<g id="fondo_editable">')
    S.append(f'<rect x="0" y="0" width="2000" height="2800" rx="0" fill="{CREAM}"/>')
    S.append(f'<circle cx="300" cy="300" r="380" fill="{c["circles"]}" opacity=".16"/>')
    S.append(f'<circle cx="1700" cy="200" r="330" fill="#315EE8" opacity=".08"/>')
    S.append(f'<circle cx="1900" cy="2650" r="410" fill="none" stroke="{GREEN}" stroke-width="90" opacity=".14"/>')
    S.append(f'<circle cx="-40" cy="2400" r="230" fill="{c["circles"]}" opacity=".10"/>')
    S.append('</g>')
    # marco y deco
    S.append('<g id="marco_y_decoracion_editable">')
    S.append(f'<rect x="70" y="70" width="1860" height="2660" rx="70" fill="none" stroke="#CFC2B2" stroke-width="4" opacity=".7"/>')
    S.append(f'<rect x="1600" y="210" width="210" height="92" rx="46" fill="{c["deco"][0]}" stroke="{INK}" stroke-width="6" transform="rotate(-14 1705 256)" opacity=".92"/>')
    S.append(f'<rect x="1435" y="315" width="158" height="76" rx="38" fill="{c["deco"][1]}" stroke="{INK}" stroke-width="5" transform="rotate(18 1514 353)" opacity=".86"/>')
    S.append('</g>')
    # header
    tag_x = 1880 - c["tag_w"]
    S.append('<g id="header_marca">')
    S.append(f'<rect x="120" y="105" width="74" height="74" rx="24" fill="{GREEN}"/>')
    S.append(txt(136, 153, "RD", 34, WHITE, 700))
    S.append(txt(215, 161, "Reduciendo Daño", 42, INK, 700))
    S.append(f'<rect x="{tag_x}" y="116" width="{c["tag_w"]}" height="60" rx="30" fill="{WHITE}" stroke="{LINE}" stroke-width="2" opacity=".7"/>')
    S.append(txt(tag_x + 35, 148, c["tag"], 24, acc if acc != GREEN else GREEN, 700))
    S.append('</g>')
    # titulo
    S.append('<g id="titulo">')
    S.append(txt(120, 287, c["kicker"], 27, acc, 700))
    S.append(txt(120, 390, c["title"], c["title_size"], INK, 700))
    S.append('</g>')
    # cajas
    S.append('<g id="cajas_editables">')
    S.append(f'<rect x="120" y="{b1y}" width="1760" height="{b1h}" rx="44" fill="{WHITE}" stroke="{LINE}" stroke-width="3" opacity=".64"/>')
    S.append(f'<rect x="120" y="{b2y}" width="1760" height="{b2h}" rx="44" fill="{WHITE}" stroke="{LINE}" stroke-width="3" opacity=".64"/>')
    S.append(f'<rect x="120" y="2230" width="1760" height="380" rx="44" fill="{WHITE}" stroke="{LINE}" stroke-width="3" opacity=".85"/>')
    S.append('</g>')
    # contenido
    S.append('<g id="contenido_texto">')
    y = b1y + 103
    S.append(txt(185, y, c["desc_title"], 48, acc, 700))
    y += 72
    for para in c["desc_paras"]:
        for ln in textwrap.wrap(para, c["desc_wrap"]):
            S.append(txt(185, y, ln, c["desc_size"]))
            y += c["desc_lead"]
        y += 32
    assert y - 32 <= b1y + b1h - 40, f"{key}: desc desborda caja1 ({y} > {b1y+b1h-40})"
    y = b2y + 103
    S.append(txt(185, y, c["list_title"], 48, acc, 700))
    y += 64
    for item in c["items"]:
        first = True
        for ln in textwrap.wrap(item, c["item_wrap"]):
            if first:
                S.append(txt(185, y, "•", c["item_size"], INK, 700, cls=""))
                S.append(txt(235, y, ln, c["item_size"]))
                first = False
            else:
                S.append(txt(235, y, ln, c["item_size"]))
            y += c["item_lead"]
        y += c["item_gap"]
    assert y - c["item_gap"] <= b2y + b2h - 40, f"{key}: items desbordan caja2 ({y} > {b2y+b2h-40})"
    S.append('</g>')
    # bloque QR
    S.append('<g id="bloque_qr">')
    qr_block, n = qr_svg(205, 2275, 290)
    S.append(qr_block)
    S.append(txt(590, 2360, "Escanea el código", 46, GREEN, 700))
    S.append(txt(590, 2432, "y visita reduciendodano.cl", 40, INK, 400))
    S.append(txt(590, 2510, "Síguenos en nuestras redes sociales · @reduciendodano.cl", 28, MUTED, 400))
    S.append('</g>')
    # footer canonico
    S.append('<g id="footer">')
    S.append(f'<line x1="120" y1="2640" x2="1880" y2="2640" stroke="{LINE}" stroke-width="5"/>')
    S.append(txt(120, 2716, "@ REDUCIENDODANO.CL", 46, GREEN, 700))
    S.append(txt(1060, 2698, "VISITA NUESTRA WEB Y SÍGUENOS EN NUESTRAS REDES", 22, MUTED, 700))
    S.append(txt(1060, 2726, "SOCIALES", 22, MUTED, 700))
    S.append('</g>')
    S.append('</svg>')
    out = c["out"]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(S) + "\n")
    print(f"OK {out} (QR {n}x{n} modulos)")


for k in CONTENT:
    build(k)
