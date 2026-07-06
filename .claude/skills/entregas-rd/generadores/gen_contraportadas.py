#!/usr/bin/env python3
"""Contraportadas de los 8 suplementos con la PLANTILLA nueva (capa "CAMBIOS"
exportada a SVG) + contenido del JSON maestro.

La plantilla trae el diseño aprobado (fondo, marco, logo, cajas, QR, footer) y NO tiene
texto viejo que quitar (STRIP=[]). Este generador solo SUPERPONE el texto editable de cada
producto: titulo alineado a la izquierda dentro del ovalo de cabecera (sin kicker), y los
bloques Descripcion / Nutrientes alineados a la izquierda ocupando sus cajas, con el cuerpo
justificado a lo ancho (Descripcion) y centrado verticalmente. Reproducible via repo (no
toca el .ai del usuario).

Plantilla: svg/suplementos_rd/_plantilla/contraportada_cambios.svg
Contenido: projects/piezas_vectoriales/suplementos_rd/01_contenido/contenido_suplementos_rd.json
Salida:    svg/suplementos_rd/09_contraportadas_dark/<id>.svg
Ejecutar desde la raiz del repo.
"""
import json, textwrap, os, pathlib

TEMPLATE = "svg/suplementos_rd/_plantilla/contraportada_cambios.svg"
JSON_SRC = "projects/piezas_vectoriales/suplementos_rd/01_contenido/contenido_suplementos_rd.json"
OUTDIR   = "svg/suplementos_rd/09_contraportadas_dark"
# La plantilla CAMBIOS solo trae el diseno aprobado (marco, logo, cajas vacias, QR); su
# unico texto es el (R) del logo. NO hay contenido viejo que quitar: las cajas
# (cajas_editables8, dentro de Capa_28) y el logo (Layer_18) son parte del diseno y se
# CONSERVAN. Solo superponemos el texto editable dentro de cada caja real.
STRIP    = []

FONT="Arial, Helvetica, sans-serif"; BLANCO="#F2F2F2"; AMARILLO="#FFD21F"; MUTED="#A79FA8"
ACCENT={"green":"#2ECC71","yellow":"#FFD21F","purple":"#8B4DFF","blue":"#2A8DFF",
        "orange":"#E67E22","red":"#F0524B","magenta":"#C800C8"}
PID_ACCENT={"04_pre_fiesta":"#C800C8"}

# --- Geometria REAL de la plantilla CAMBIOS (viewBox 2000x2800) ---
# Cajas medidas del SVG (grupo cajas_editables8): x, y, ancho, alto.
BOX_DESC  = (120.8823,  618.583, 1760, 800)   # caja "Descripcion"
BOX_ITEMS = (120.8823, 1478.583, 1760, 700)   # caja "Nutrientes"/items
BOX_FOOT  = (120.8823, 2228.583, 1760, 380)   # caja footer/QR (no se toca: la ocupa bloque_qr)
PAD_X, PAD_TOP, PAD_BOT = 70, 44, 48          # margenes internos de cada caja
# Ovalo (pill) detras del titulo, medido del render: x 70..735, y 248..465.
# Region interior util para el titulo alineado a la izquierda:
PILL_X0, PILL_X1, PILL_YC, PILL_H = 168, 700, 356, 200

# --- Metricas tipograficas aproximadas (Arial), para wrap y justificado ---
CW_REG, CW_BOLD = 0.512, 0.552   # ancho medio de caracter (fraccion del font-size)
LEAD = 1.30                      # interlineado (fraccion del font-size)

esc = lambda s: str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def rm_group(s, gid):
    """Quita un grupo <g id=gid>...</g> (maneja anidamiento)."""
    i = s.find('<g id="'+gid+'"')
    if i < 0: return s
    j = i+2; depth = 1
    while depth > 0:
        ng = s.find('<g', j); nc = s.find('</g>', j)
        if nc < 0: return s
        if ng != -1 and ng < nc: depth += 1; j = ng+2
        else: depth -= 1; j = nc+4
    return s[:i] + s[j:]

def T(x, y, s, size, fill, w=400, anchor=None, tlen=None):
    """Un <text>. Si tlen se da, estira la linea a ese ancho (justificado)."""
    a = f' text-anchor="{anchor}"' if anchor else ""
    j = f' textLength="{tlen:.1f}" lengthAdjust="spacing"' if tlen else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}"{a}{j} fill="{fill}" font-family="{FONT}"'
            f' font-size="{size:.1f}" font-weight="{w}">{esc(s)}</text>')

def wrap_w(text, width_px, size, cw):
    """Envuelve 'text' para que cada linea quepa en width_px a font-size 'size'."""
    maxc = max(1, int(width_px / (cw * size)))
    return textwrap.wrap(text, maxc) or [""]

def fit_title(title, cw=CW_BOLD, cap=118, floor=34):
    """Elige (font, lineas) para llenar el ovalo alineado a la izquierda.
    Prueba 1 y 2 lineas y se queda con la variante de MAYOR tamano legible."""
    W = PILL_X1 - PILL_X0
    best = None
    for nlines in (1, 2):
        lines = wrap_w(title, W * nlines, cap, cw) if nlines == 2 else [title]
        lines = lines[:nlines]
        if not lines: continue
        maxc = max(len(ln) for ln in lines)
        f_w = W / (maxc * cw)
        f_h = PILL_H / (nlines * LEAD)
        f = min(cap, f_w, f_h)
        if best is None or f > best[0]:
            best = (f, lines)
    f = max(floor, best[0]); lines = best[1]
    if len(lines) == 1:  # reintenta wrap real con el font elegido
        lines = wrap_w(title, PILL_X1 - PILL_X0, f, cw)[:2]
    return f, lines

FONT_MAX, FONT_MIN, LAB = 46, 22, 48   # cuerpo: mayor tam. legible que quepa; label fijo

def block(box, label, paras, acc, justify=False):
    """Dibuja un bloque (label + cuerpo) alineado a la IZQUIERDA que OCUPA la caja.
    'paras' = lista de (es_vineta, texto_crudo). Elige la mayor fuente legible que
    quepa (baja solo si el contenido es denso) y centra el bloque completo en la caja.
    Descripcion se justifica a lo ancho; los items van a bandera (izquierda)."""
    bx, by, bw, bh = box
    x = bx + PAD_X
    ind = 56 if any(p[0] for p in paras) else 0
    inner_w = bw - 2 * PAD_X
    avail_top = by + PAD_TOP
    avail = bh - PAD_TOP - PAD_BOT

    def layout(font):
        lstep = font * LEAD; pgap = font * 0.55; lab_gap = font * 1.25
        wl = [(b, wrap_w(t, inner_w - ind, font, CW_REG)) for b, t in paras]
        n = sum(len(w) for _, w in wl)
        body_last = (n - 1) * lstep + max(0, len(wl) - 1) * pgap if n else 0
        content_h = lab_gap + body_last + font * 0.23 + LAB * 0.72
        return wl, lstep, pgap, lab_gap, content_h

    font = FONT_MIN
    for f in range(FONT_MAX, FONT_MIN - 1, -1):
        wl, lstep, pgap, lab_gap, content_h = layout(f)
        if content_h <= avail: font = f; break
    else:
        wl, lstep, pgap, lab_gap, content_h = layout(FONT_MIN)

    start_top = avail_top + max(0, (avail - content_h) / 2)
    lab_base = start_top + LAB * 0.72
    y = lab_base + lab_gap
    G = [T(x, lab_base, label, LAB, AMARILLO, 700)]
    for bullet, lines in wl:
        for k, ln in enumerate(lines):
            last = (k == len(lines) - 1)
            if bullet and k == 0: G.append(T(x, y, "•", font, acc, 700))
            tl = (inner_w - ind) if (justify and not last and len(ln) > 2) else None
            G.append(T(x + ind, y, ln, font, BLANCO, tlen=tl))
            y += lstep
        y += pgap
    return G

def desc_block(fl):
    paras = [(False, p) for p in fl.get("description", [])]
    return block(BOX_DESC, "Descripción", paras, AMARILLO, justify=True)

def items_block(fl, acc):
    items = fl.get("items", [])
    if not items: return []
    label = fl.get("section_title") or "Nutrientes"
    body = [(True, it) for it in items]
    return block(BOX_ITEMS, label, body, acc, justify=False)

def content_group(fl):
    gen = fl.get("type") == "general"
    acc = PID_ACCENT.get(fl["id"], ACCENT.get(fl.get("accent","magenta"), "#C800C8"))
    title = fl.get("title","") if gen else fl.get("title","").upper()
    G = ['<g id="contenido_nuevo">']
    # --- Titulo: alineado a la izquierda, dentro del ovalo, centrado vertical ---
    f, tlines = fit_title(title)
    step = f * LEAD
    y0 = PILL_YC - (len(tlines) - 1) * step / 2 + f * 0.34   # centrado vertical del bloque
    for i, ln in enumerate(tlines):
        y = y0 + i * step
        G.append(T(PILL_X0, y, ln, f, BLANCO, 700))
    # --- Cuerpos ---
    G.extend(desc_block(fl))
    G.extend(items_block(fl, acc))
    G.append('</g>')
    return "\n".join(G)

def main():
    tpl = pathlib.Path(TEMPLATE).read_text(encoding="utf-8", errors="replace")
    for gid in STRIP: tpl = rm_group(tpl, gid)
    flyers = json.load(open(JSON_SRC, encoding="utf-8"))["flyers"]
    os.makedirs(OUTDIR, exist_ok=True)
    for fl in flyers:
        out = tpl.replace("</svg>", content_group(fl) + "\n</svg>")
        pathlib.Path(f"{OUTDIR}/{fl['id']}.svg").write_text(out, encoding="utf-8")
        print("OK", f"{OUTDIR}/{fl['id']}.svg")

if __name__ == "__main__":
    main()
