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
STRIP    = ["Capa_28", "Layer_18"]   # grupos con el contenido viejo (texto outlined) a reemplazar

FONT="Arial, Helvetica, sans-serif"; BLANCO="#F2F2F2"; AMARILLO="#FFD21F"; MUTED="#A79FA8"
ACCENT={"green":"#2ECC71","yellow":"#FFD21F","purple":"#8B4DFF","blue":"#2A8DFF",
        "orange":"#E67E22","red":"#F0524B","magenta":"#C800C8"}
PID_ACCENT={"04_pre_fiesta":"#C800C8"}
# posiciones de texto calibradas al diseño CAMBIOS (canvas 2000x2800)
KICK_Y, TITLE_Y = 300, 403
DESC_TITLE_Y, ITEMS_TITLE_Y = 603, 1205
DESC_WRAP, ITEM_WRAP = 60, 72

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
    return f'<text x="{x}" y="{y}"{a} fill="{fill}" font-family="{FONT}" font-size="{size}" font-weight="{w}">{esc(s)}</text>'

def content_group(fl):
    gen = fl.get("type") == "general"
    acc = PID_ACCENT.get(fl["id"], ACCENT.get(fl.get("accent","magenta"), "#C800C8"))
    title = fl.get("title","") if gen else fl.get("title","").upper()
    ts = 92 if len(title) <= 9 else (80 if len(title) <= 15 else 62)
    G = ['<g id="contenido_nuevo">']
    G.append(T(1000, KICK_Y, "LÍNEA" if gen else "PRODUCTO", 27, AMARILLO, 700, "middle"))
    G.append(T(1004, TITLE_Y, title, ts, acc, 700, "middle"))
    G.append(T(1000, TITLE_Y, title, ts, BLANCO, 700, "middle"))
    # Descripcion = UN solo bloque editable (todos los parrafos)
    y = DESC_TITLE_Y; G.append(T(185, y, "Descripción", 48, AMARILLO, 700)); y += 72
    dts = []; first = True
    for p in fl.get("description", []):
        for i, ln in enumerate(textwrap.wrap(p, DESC_WRAP) or [""]):
            dy = 0 if first else (86 if i == 0 else 60)   # 60 lead + 26 gap entre parrafos
            dts.append(f'<tspan x="185" dy="{dy}">{esc(ln)}</tspan>'); first = False
    G.append(f'<text x="185" y="{y}" fill="{BLANCO}" font-family="{FONT}" font-size="44" font-weight="400">{"".join(dts)}</text>')
    # Nutrientes = UN solo bloque editable (todos los items)
    y = ITEMS_TITLE_Y; G.append(T(185, y, fl.get("section_title") or "Nutrientes", 48, AMARILLO, 700)); y += 60
    its = []; first = True
    for it in fl.get("items", []):
        for i, ln in enumerate(textwrap.wrap(it, ITEM_WRAP) or [""]):
            if i == 0:
                dy = 0 if first else 62   # 46 lead + 16 gap entre items
                its.append(f'<tspan x="185" dy="{dy}"><tspan fill="{acc}" font-weight="700">•</tspan>  {esc(ln)}</tspan>')
            else:
                its.append(f'<tspan x="235" dy="46">{esc(ln)}</tspan>')
            first = False
    G.append(f'<text x="185" y="{y}" fill="{BLANCO}" font-family="{FONT}" font-size="34" font-weight="400">{"".join(its)}</text>')
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
