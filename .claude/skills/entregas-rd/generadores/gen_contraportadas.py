#!/usr/bin/env python3
"""Contraportadas de los 8 suplementos con la PLANTILLA nueva (capa "CAMBIOS"
exportada a SVG) + contenido del JSON maestro.

La plantilla trae el diseño aprobado (fondo, marco, logo, cajas, QR, footer). Este
generador le quita el contenido viejo (grupos outlined) y le superpone el texto EDITABLE
de cada producto, en las posiciones calibradas al diseño. Reproducible via repo (no toca
el .ai del usuario).

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
PAD_X, PAD_TOP, PAD_BOT = 70, 40, 44          # margenes internos de cada caja
CENTER_X = 1000                               # eje del titulo centrado
KICK_Y, TITLE_Y = 330, 470                    # banda de cabecera (68..618), bajo el logo esquina
DESC_WRAP, ITEM_WRAP = 60, 72
FIT_FLOOR = 0.50                              # escala minima al auto-ajustar contenido denso

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

def T(x, y, s, size, fill, w=400, anchor=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}"{a} fill="{fill}" font-family="{FONT}"'
            f' font-size="{size:.1f}" font-weight="{w}">{esc(s)}</text>')

def fit(needed, usable):
    """Factor de escala para que 'needed' px de contenido quepan en 'usable' px."""
    if needed <= usable or needed <= 0: return 1.0
    return max(FIT_FLOOR, usable / needed)

def desc_block(fl):
    """Bloque 'Descripcion' calibrado dentro de BOX_DESC."""
    bx, by, bw, bh = BOX_DESC
    x = bx + PAD_X
    tsize, tgap, lsize, step, pgap = 48, 66, 44, 60, 26
    paras = [textwrap.wrap(p, DESC_WRAP) or [""] for p in fl.get("description", [])]
    body_lines = sum(len(p) for p in paras)
    title_base = by + PAD_TOP + tsize
    bottom = by + bh - PAD_BOT
    needed = tgap + body_lines * step + max(0, len(paras) - 1) * pgap
    s = fit(needed, bottom - title_base)
    G = [T(x, title_base, "Descripción", tsize, AMARILLO, 700)]
    y = title_base + tgap * s
    for p in paras:
        for ln in p: G.append(T(x, y, ln, lsize * s, BLANCO)); y += step * s
        y += pgap * s
    return G

def items_block(fl, acc):
    """Bloque de nutrientes/items calibrado dentro de BOX_ITEMS."""
    items = fl.get("items", [])
    if not items: return []
    bx, by, bw, bh = BOX_ITEMS
    x = bx + PAD_X
    tsize, tgap, isize, step, igap = 48, 60, 34, 46, 16
    wrapped = [textwrap.wrap(it, ITEM_WRAP) or [""] for it in items]
    body_lines = sum(len(w) for w in wrapped)
    title_base = by + PAD_TOP + tsize
    bottom = by + bh - PAD_BOT
    needed = tgap + body_lines * step + max(0, len(items) - 1) * igap
    s = fit(needed, bottom - title_base)
    G = [T(x, title_base, fl.get("section_title") or "Nutrientes", tsize, AMARILLO, 700)]
    y = title_base + tgap * s
    for w in wrapped:
        first = True
        for ln in w:
            if first: G.append(T(x, y, "•", isize * s, acc, 700)); first = False
            G.append(T(x + 50 * s, y, ln, isize * s, BLANCO)); y += step * s
        y += igap * s
    return G

def content_group(fl):
    gen = fl.get("type") == "general"
    acc = PID_ACCENT.get(fl["id"], ACCENT.get(fl.get("accent","magenta"), "#C800C8"))
    title = fl.get("title","") if gen else fl.get("title","").upper()
    ts = 92 if len(title) <= 9 else (80 if len(title) <= 15 else 62)
    G = ['<g id="contenido_nuevo">']
    # cabecera centrada en la banda superior (bajo el logo de esquina)
    G.append(T(CENTER_X, KICK_Y, "LÍNEA" if gen else "PRODUCTO", 27, AMARILLO, 700, "middle"))
    G.append(T(CENTER_X + 4, TITLE_Y, title, ts, acc, 700, "middle"))
    G.append(T(CENTER_X, TITLE_Y, title, ts, BLANCO, 700, "middle"))
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
