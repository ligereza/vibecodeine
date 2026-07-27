#!/usr/bin/env python3
"""Frentes DARK/NEON de los 8 flyers de suplementos RD (sistema rave v4.1).

Genera versiones oscuras de los 8 frentes canonicos (01-08) desde el contenido
maestro aprobado (projects/piezas_vectoriales/suplementos_rd/01_contenido/
contenido_suplementos_rd.json), en el mismo sistema visual que los reversos
dark 11/12: negro #0A0A0A, magenta #C800C8, amarillo #FFD21F, acentos neon de
la paleta de apoyo v4.1. Logo RD real embebido (NO regenerado con IA).

Mejoras sobre los reversos:
- Cajas de altura DINAMICA: crecen para llenar la pagina sin aire muerto.
- Texto CENTRADO verticalmente dentro de cada caja.
- Ajuste de linea por presupuesto de PIXELES (medicion real, no conteo fijo):
  ningun texto se desborda del marco.
- Tipografia: titulo con eco neon, subrayado de acento bajo cada encabezado,
  pill de tag, capsulas 'gomita' decorativas (los productos son gomitas).

Salida: svg/suplementos_rd/05_dark_neon/NN_<slug>_dark.svg (2000x2800).
Validar con: PYTHONPATH=src python3 -m flujo suplementos validate <ruta>
"""
import base64
import json
import os
import textwrap

ROOT = os.getcwd()
FONT = "Arial, Helvetica, sans-serif"

# --- Paleta rave v4.1 -----------------------------------------------------
NEGRO = "#0A0A0A"
PANEL = "#161318"
BLANCO = "#F2F2F2"
MUTED = "#A79FA8"
MAGENTA = "#C800C8"
AMARILLO = "#FFD21F"
VIOLETA = "#8B4DFF"
LINE = "#33262E"
WHITE = "#FFFFFF"
INK = "#161513"

# Acentos por producto -> equivalente neon oficial (v4.1 §0 + apoyo funcional).
# 'red' = rojo de marca crema #D95436 aclarado a #F0524B para legibilidad en negro.
ACCENT_MAP = {
    "green": "#2ECC71", "yellow": "#FFD21F", "purple": "#8B4DFF",
    "blue": "#2A8DFF", "orange": "#E67E22", "red": "#F0524B",
    "magenta": "#C800C8",
}
# Override deliberado: Pre Fiesta usa magenta RD (firma de marca) para
# diferenciarse de Hongos Adaptogenos, que tambien viene marcado 'purple'.
PER_ID_ACCENT = {"04_pre_fiesta": "#C800C8"}

# Texto del pill: acentos oscuros aclarados para AA >=4.5:1 sobre panel
# #161318 (QA D2). El borde del pill mantiene el acento original.
PILL_TEXT = {"#C800C8": "#E93FE9", "#8B4DFF": "#B375FF"}

TAG_UP = {  # tag corto en mayusculas para el pill superior derecho
    "Información general": "LÍNEA RD",
    "Foco sostenido": "FOCO SOSTENIDO",
    "Adaptógenos": "ADAPTÓGENOS",
    "Antes de la exigencia": "PRE · EXIGENCIA",
    "Mineral esencial": "MINERAL ESENCIAL",
    "Polvo y gomitas": "POLVO · GOMITAS",
    "Proteína en polvo": "PROTEÍNA",
    "Recuperación post": "RECUPERACIÓN POST",
}

LOGO_PATH = os.path.join(ROOT, "assets/logo/RD_logo_A_transparente.png")
LOGO_B64 = base64.b64encode(open(LOGO_PATH, "rb").read()).decode()
LOGO_W, LOGO_H = 216, 171

def inline_logo_svg(variant, x, y, w):
    """Logo RD vectorial inline (crisp a cualquier zoom). variant: 'negro'|'blanco'|'color'."""
    raw = open(os.path.join(ROOT, f"assets/logo/RD_logo_vector_{variant}.svg"), encoding="utf-8").read()
    inner = raw[raw.index("<svg"):]
    h = round(w * 817.61 / 1060, 1)
    return inner.replace("<svg ", f'<svg x="{x}" y="{y}" width="{w}" height="{h}" ', 1)

# --- Layout ---------------------------------------------------------------
CARD_X, CARD_W = 120, 1760
TEXT_X = 185                # margen interno de texto
BULLET_X, BULLET_TEXT_X = 185, 245
CARD_TOP = 660             # primera caja empieza aqui
FOOTER_TOP = 2588          # las cajas terminan antes de la linea de footer (2640)
GAP = 54                   # separacion entre cajas
PAD_TOP, PAD_BOTTOM = 54, 50


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size, fill=BLANCO, weight=400, anchor=None, cls=' class="txt"'):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text{cls} x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{FONT}" '
            f'font-size="{size}"{a} font-weight="{weight}">{esc(s)}</text>')


def wrap_px(text, size, max_w, bold=False):
    """Ajuste por presupuesto de pixeles (sobreestima ancho -> nunca desborda)."""
    factor = 0.605 if bold else 0.545  # ancho medio de char en DejaVu Sans
    cpl = max(6, int(max_w / (factor * size)))
    return textwrap.wrap(text, cpl) or [""]


def neon_ring(cx, cy, r, color):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="34" opacity=".05"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="18" opacity=".12"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="6" opacity=".5"/>')


def capsule(cx, cy, w, h, rot, color, op):
    """Capsula 'gomita' decorativa: rounded rect con contorno neon."""
    return (f'<rect x="{cx-w/2:.0f}" y="{cy-h/2:.0f}" width="{w}" height="{h}" rx="{h/2}" '
            f'fill="none" stroke="{color}" stroke-width="6" transform="rotate({rot} {cx} {cy})" opacity="{op}"/>')


# --- Modelo de filas (para centrado vertical dinamico) --------------------
# Cada "row" = (step_antes_del_baseline, funcion_dibujo(y)). El primer step es
# el ascenso del encabezado; se centra el bloque completo en la caja.
HEAD_SIZE = 50
DESC_SIZE, DESC_LEAD = 46, 66
ITEM_SIZE, ITEM_LEAD, ITEM_GAP = 38, 54, 24
VTITLE_SIZE, VBODY_SIZE, VBODY_LEAD, V_GAP = 40, 36, 52, 34
PARA_GAP = 30
HEAD_TO_BODY = 86
TEXT_MAX = CARD_W - 2 * (TEXT_X - CARD_X)          # ancho util caja completa
ITEM_MAX = CARD_W - (BULLET_TEXT_X - CARD_X) - (TEXT_X - CARD_X)


def build_card_rows(card, acc):
    """Devuelve (rows, content_h). rows = lista de (step, draw(y)->str)."""
    rows = []

    # Encabezado + subrayado de acento
    def draw_head(y, s=card["heading"]):
        bar = (f'<rect x="{TEXT_X}" y="{y+16:.1f}" width="{min(300, 20+len(s)*20)}" height="6" rx="3" '
               f'fill="{acc}" opacity=".85"/>')
        return txt(TEXT_X, y, s, HEAD_SIZE, AMARILLO, 700) + "\n" + bar
    rows.append((HEAD_SIZE, draw_head))

    kind = card["kind"]
    if kind == "desc":
        for pi, para in enumerate(card["paras"]):
            lines = wrap_px(para, DESC_SIZE, TEXT_MAX)
            for li, ln in enumerate(lines):
                step = HEAD_TO_BODY if (pi == 0 and li == 0) else DESC_LEAD
                rows.append((step, (lambda t: (lambda y: txt(TEXT_X, y, t, DESC_SIZE)))(ln)))
            if pi < len(card["paras"]) - 1:
                rows[-1] = (rows[-1][0], rows[-1][1])
                rows.append((PARA_GAP, lambda y: ""))
    elif kind == "items":
        first = True
        for it in card["items"]:
            lines = wrap_px(it, ITEM_SIZE, ITEM_MAX)
            for li, ln in enumerate(lines):
                step = HEAD_TO_BODY if first else (ITEM_LEAD if li else ITEM_LEAD)
                if li == 0:
                    def draw(y, t=ln):
                        return (txt(BULLET_X, y, "•", ITEM_SIZE, acc, 700, cls="")
                                + "\n" + txt(BULLET_TEXT_X, y, t, ITEM_SIZE))
                else:
                    def draw(y, t=ln):
                        return txt(BULLET_TEXT_X, y, t, ITEM_SIZE)
                rows.append((step if not first else HEAD_TO_BODY, draw))
                first = False
            rows.append((ITEM_GAP, lambda y: ""))
        rows.pop()  # sin gap tras el ultimo item
    elif kind == "versions":
        # step pre-titulo 74 > VBODY_LEAD para que cada titulo se agrupe con
        # SU cuerpo y no con el parrafo anterior (ley de proximidad; QA D1)
        first = True
        for v in card["versions"]:
            rows.append(((HEAD_TO_BODY if first else 74),
                         (lambda t: (lambda y: txt(TEXT_X, y, t, VTITLE_SIZE, acc, 700)))(v["title"])))
            first = False
            for ln in wrap_px(v["body"], VBODY_SIZE, TEXT_MAX):
                rows.append((VBODY_LEAD, (lambda t: (lambda y: txt(TEXT_X, y, t, VBODY_SIZE)))(ln)))
    elif kind == "usage":
        for li, ln in enumerate(wrap_px(card["text"], DESC_SIZE, TEXT_MAX)):
            rows.append(((HEAD_TO_BODY if li == 0 else DESC_LEAD),
                         (lambda t: (lambda y: txt(TEXT_X, y, t, DESC_SIZE)))(ln)))

    content_h = sum(s for s, _ in rows)
    return rows, content_h


def build(flyer):
    acc = PER_ID_ACCENT.get(flyer["id"]) or ACCENT_MAP[flyer["accent"]]
    slug = flyer["id"].split("_", 1)[1]
    num = flyer["id"][:2]
    title = flyer["title"]
    subtitle = flyer.get("subtitle", "")
    tag = TAG_UP.get(flyer.get("tag", ""), flyer.get("tag", "").upper())

    # --- construir cards segun el modelo de contenido ---
    cards = [{"kind": "desc", "heading": flyer.get("description_title") or "Descripción",
              "paras": flyer["description"]}]
    if flyer.get("items"):
        cards.append({"kind": "items", "heading": flyer.get("section_title") or "Nutrientes",
                      "items": flyer["items"]})
    if flyer.get("versions"):
        cards.append({"kind": "versions", "heading": flyer.get("versions_title") or "Versiones",
                      "versions": flyer["versions"]})
    if flyer.get("usage"):
        cards.append({"kind": "usage", "heading": flyer.get("usage_title") or "Modo de uso",
                      "text": flyer["usage"]})

    # medir contenido y repartir altura disponible con tope de crecimiento.
    # Las cajas crecen hasta 1.5x su tamano natural (para no quedar vacias);
    # el remanente se reparte como aire simetrico arriba/abajo del bloque, de
    # modo que productos con poco texto quedan centrados y no inflados.
    measured = [(c,) + build_card_rows(c, acc) for c in cards]
    naturals = [PAD_TOP + ch + PAD_BOTTOM for (_, _, ch) in measured]
    n = len(cards)
    available = FOOTER_TOP - CARD_TOP - GAP * (n - 1)
    slack = available - sum(naturals)
    assert slack > -1, f"{flyer['id']}: contenido no cabe (slack={slack:.0f})"
    caps = [nat * 1.5 for nat in naturals]
    heights = list(naturals)
    remaining = slack
    for _ in range(8):
        openi = [i for i in range(n) if caps[i] - heights[i] > 1]
        if remaining <= 1 or not openi:
            break
        share = remaining / len(openi)
        for i in openi:
            add = min(share, caps[i] - heights[i])
            heights[i] += add
            remaining -= add
    top_offset = max(0.0, remaining) / 2      # centra el bloque de cajas

    S = []
    S.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             'width="2000px" height="2800px" viewBox="0 0 2000 2800">')
    S.append(f'<metadata>{num}_{slug}_dark / front editable dark-neon / 2000x2800 px</metadata>')

    # fondo + glow
    S.append('<g id="fondo_editable">')
    S.append(f'<rect x="0" y="0" width="2000" height="2800" fill="{NEGRO}"/>')
    S.append(neon_ring(255, 330, 340, acc))
    S.append(neon_ring(1800, 210, 250, VIOLETA))
    S.append(neon_ring(1930, 2600, 380, MAGENTA))
    S.append(f'<circle cx="-30" cy="2380" r="220" fill="{acc}" opacity=".06"/>')
    S.append('</g>')

    # marco + capsulas gomita decorativas
    S.append('<g id="marco_y_decoracion_editable">')
    S.append(f'<rect x="70" y="70" width="1860" height="2660" rx="70" fill="none" stroke="{MAGENTA}" stroke-width="10" opacity=".14"/>')
    S.append(f'<rect x="70" y="70" width="1860" height="2660" rx="70" fill="none" stroke="{MAGENTA}" stroke-width="4" opacity=".5"/>')
    S.append(capsule(1690, 300, 190, 84, -14, acc, ".7"))
    S.append(capsule(1520, 402, 140, 66, 18, AMARILLO, ".55"))
    S.append('</g>')

    # header: logo real + nombre + tag pill
    tag_w = max(300, 150 + len(tag) * 17)
    tag_x = 1880 - tag_w
    lw = 176
    lh = round(lw * LOGO_H / LOGO_W)
    S.append('<g id="header_marca">')
    S.append(inline_logo_svg("blanco", 112, 86, lw))
    S.append(txt(310, 172, "Reduciendo Daño", 42, BLANCO, 700))
    S.append(f'<rect x="{tag_x}" y="116" width="{tag_w}" height="60" rx="30" fill="{PANEL}" stroke="{acc}" stroke-width="3"/>')
    S.append(txt(tag_x + tag_w / 2, 154, tag, 24, PILL_TEXT.get(acc, acc), 700, anchor="middle"))
    S.append('</g>')

    # titulo con eco neon + subtitulo
    tlen = len(title)
    tsize = 92 if tlen <= 9 else (80 if tlen <= 15 else 62)
    ty = 452
    kicker = "LÍNEA" if flyer.get("type") == "general" else "PRODUCTO"
    CX = 1000  # centro del canvas 2000
    S.append('<g id="titulo">')
    S.append(txt(CX, 348, kicker, 27, AMARILLO, 700, anchor="middle"))
    S.append(txt(CX + 4, ty + 5, title, tsize, acc, 700, anchor="middle", cls=""))   # eco
    S.append(txt(CX, ty, title, tsize, BLANCO, 700, anchor="middle"))
    if subtitle:
        S.append(txt(CX, ty + 62, subtitle, 40, MUTED, 400, anchor="middle"))
    S.append('</g>')

    # cajas dinamicas con texto centrado verticalmente
    S.append('<g id="cajas_editables">')
    y = CARD_TOP + top_offset
    card_frames = []
    for h in heights:
        S.append(f'<rect x="{CARD_X}" y="{y:.0f}" width="{CARD_W}" height="{h:.0f}" rx="44" fill="{PANEL}" stroke="{LINE}" stroke-width="3"/>')
        S.append(f'<rect x="{CARD_X}" y="{y:.0f}" width="{CARD_W}" height="{h:.0f}" rx="44" fill="none" stroke="{acc}" stroke-width="2" opacity=".42"/>')
        card_frames.append((y, h))
        y += h + GAP
    S.append('</g>')

    S.append('<g id="contenido_texto">')
    for (cy, ch), (_, rows, content_h) in zip(card_frames, measured):
        start = cy + (ch - content_h) / 2
        yy = start
        for step, draw in rows:
            yy += step
            out = draw(yy)
            if out:
                S.append(out)
    S.append('</g>')

    # footer
    S.append('<g id="footer">')
    S.append(f'<line x1="120" y1="2640" x2="1880" y2="2640" stroke="{MAGENTA}" stroke-width="5" opacity=".7"/>')
    S.append(txt(120, 2716, "@ REDUCIENDODANO.CL", 46, AMARILLO, 700))
    S.append(txt(1060, 2698, "VISITA NUESTRA WEB Y SÍGUENOS EN NUESTRAS REDES", 22, MUTED, 700))
    S.append(txt(1060, 2726, "SOCIALES", 22, MUTED, 700))
    S.append('</g>')
    S.append('</svg>')

    out = f"svg/suplementos_rd/05_dark_neon/{num}_{slug}_dark.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(S) + "\n")
    return out


def main():
    data = json.load(open("projects/piezas_vectoriales/suplementos_rd/01_contenido/contenido_suplementos_rd.json", encoding="utf-8"))
    os.makedirs("svg/suplementos_rd/05_dark_neon", exist_ok=True)
    for flyer in data["flyers"]:
        out = build(flyer)
        print("OK", out)


if __name__ == "__main__":
    main()
