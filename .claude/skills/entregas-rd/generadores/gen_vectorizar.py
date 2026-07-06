#!/usr/bin/env python3
"""Vectoriza SVGs editables de suplementos RD: convierte cada <text> a <path>
con las curvas reales de DejaVu Sans / DejaVu Sans Bold (fontTools), igual que
los archivos de 03_final_vectorizado_svg (texto a curvas, cero <text>).

Uso:
  python3 gen_vectorizar.py ENTRADA.svg SALIDA.svg [ENTRADA2 SALIDA2 ...]

Notas:
- Respeta x/y, font-size, font-weight (400/700), fill y text-anchor="middle".
- Todo lo demas (rects, circles, images/QR, grupos) pasa intacto.
- Sin kerning GPOS (igual que un trazado basico); el ajuste de linea ya viene
  calculado con margen en los editables, no hay riesgo de desborde.
"""
import re
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

import os

def _dejavu(name):
    """Resuelve DejaVu en Linux o Windows (via matplotlib)."""
    cands = [f"/usr/share/fonts/truetype/dejavu/{name}",
             f"/Library/Fonts/{name}"]
    for p in cands:
        if os.path.exists(p):
            return p
    try:
        import matplotlib
        return os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", name)
    except Exception:
        return cands[0]

FONTS = {
    "400": _dejavu("DejaVuSans.ttf"),
    "700": _dejavu("DejaVuSans-Bold.ttf"),
}

_cache = {}


def load_font(weight):
    key = "700" if str(weight) == "700" else "400"
    if key not in _cache:
        f = TTFont(FONTS[key])
        _cache[key] = {
            "font": f,
            "cmap": f.getBestCmap(),
            "glyphs": f.getGlyphSet(),
            "hmtx": f["hmtx"],
            "upm": f["head"].unitsPerEm,
        }
    return _cache[key]


def text_width(s, size, weight):
    ft = load_font(weight)
    scale = size / ft["upm"]
    total = 0
    for ch in s:
        gname = ft["cmap"].get(ord(ch))
        if gname is None:
            gname = ".notdef"
        total += ft["hmtx"][gname][0]
    return total * scale


def text_to_path(s, x, y, size, weight, anchor):
    ft = load_font(weight)
    scale = size / ft["upm"]
    cx = float(x)
    if anchor == "middle":
        cx -= text_width(s, size, weight) / 2
    elif anchor == "end":
        cx -= text_width(s, size, weight)
    pen = SVGPathPen(ft["glyphs"])
    for ch in s:
        gname = ft["cmap"].get(ord(ch))
        if gname is None:
            gname = ".notdef"
        t = Transform(scale, 0, 0, -scale, cx, float(y))
        ft["glyphs"][gname].draw(TransformPen(pen, t))
        cx += ft["hmtx"][gname][0] * scale
    return pen.getCommands()


# <text>...</text> con hijos permitidos (.*? no-greedy: text no anida text).
BLOCK_RE = re.compile(r'<text\b([^>]*)>(.*?)</text>', re.S)
ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')
UNESC = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'"}


def unescape(s):
    for k, v in UNESC.items():
        s = s.replace(k, v)
    return s


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _path(s, x, y, size, weight, fill, anchor=""):
    """text_to_path envuelto: devuelve el <path> (o '' si el texto es vacio)."""
    s = s.replace("\n", " ")
    if not s.strip():
        return ""
    d = text_to_path(s, x, y, size, weight, anchor)
    return f'<path d="{d}" fill="{fill}"/>' if d else ""


def _tokenize(s):
    """Tokeniza el contenido de un <text>/<tspan> en nodos de PRIMER nivel, en orden:
    ('text', str) o ('tspan', attrs_str, body_str). Respeta anidamiento (regex no
    puede: el </tspan> mas cercano cierra el hijo, no el padre)."""
    toks = []; i = 0; n = len(s)
    while i < n:
        j = s.find("<tspan", i)
        if j < 0:
            toks.append(("text", s[i:])); break
        if j > i:
            toks.append(("text", s[i:j]))
        gt = s.find(">", j)
        attrs = s[j + 6:gt]
        depth = 1; k = gt + 1; close = n
        while k < n:
            no = s.find("<tspan", k); nc = s.find("</tspan>", k)
            if nc < 0:
                break
            if no != -1 and no < nc:
                depth += 1; k = no + 6
            else:
                depth -= 1; k = nc + 8
                if depth == 0:
                    close = nc; break
        toks.append(("tspan", attrs, s[gt + 1:close]))
        i = close + 8
    return toks


def _vectorize_tspan_block(base, inner):
    """Un <text> con hijos <tspan> (bloque envuelto: descripcion/nutrientes).
    Cada tspan de primer nivel es una LINEA (x reinicia el margen, dy avanza la y).
    Dentro de una linea puede haber tspans anidados (p.ej. el bullet de color) mas
    texto suelto: se colocan en secuencia avanzando un cursor horizontal."""
    bx = _num(base.get("x", "0")); by = _num(base.get("y", "0"))
    bsize = _num(base.get("font-size", "16")); bweight = base.get("font-weight", "400")
    bfill = base.get("fill", "#000")
    cx, cy = bx, by
    out = []
    for tok in _tokenize(inner):
        if tok[0] != "tspan":
            continue  # texto suelto de primer nivel (whitespace de indentacion): ignorar
        la = dict(ATTR_RE.findall(tok[1]))
        if "x" in la:
            cx = _num(la["x"])
        cy += _num(la.get("dy", "0"))
        lfill = la.get("fill", bfill)
        lweight = la.get("font-weight", bweight)
        lsize = _num(la.get("font-size", bsize)) if la.get("font-size") else bsize
        cursor = cx
        for seg in _tokenize(tok[2]):  # inline: texto suelto y tspans anidados (bullet)
            if seg[0] == "text":
                txt = unescape(seg[1])
                if txt.strip() or txt == "  ":  # conservar separacion tras el bullet
                    out.append(_path(txt, cursor, cy, lsize, lweight, lfill))
                    cursor += text_width(txt.replace("\n", " "), lsize, lweight)
            else:
                na = dict(ATTR_RE.findall(seg[1]))
                ntext = unescape(seg[2])
                nfill = na.get("fill", lfill)
                nweight = na.get("font-weight", lweight)
                nsize = _num(na.get("font-size", lsize)) if na.get("font-size") else lsize
                out.append(_path(ntext, cursor, cy, nsize, nweight, nfill))
                cursor += text_width(ntext.replace("\n", " "), nsize, nweight)
    return "".join(p for p in out if p)


def vectorize_file(src, dst):
    svg = open(src, encoding="utf-8").read()

    def repl(m):
        attrs = dict(ATTR_RE.findall(m.group(1)))
        inner = m.group(2)
        # El logo trae ® como <text class=... transform=...> sin font-size: dejarlo.
        if "font-size" not in attrs:
            return m.group(0)
        if "<tspan" in inner:
            return _vectorize_tspan_block(attrs, inner)
        content = unescape(inner)
        return _path(content, attrs.get("x", "0"), attrs.get("y", "0"),
                     _num(attrs.get("font-size", "16")), attrs.get("font-weight", "400"),
                     attrs.get("fill", "#000"), attrs.get("text-anchor", ""))

    out = BLOCK_RE.sub(repl, svg)
    out = out.replace("/ editable dark-neon /", "/ vector dark-neon /")
    out = out.replace("/ editable /", "/ vector /")
    _left = out.count("<text")
    if _left:
        # el logo vectorial trae el simbolo ® como <text> (fuente Helvetica, presente
        # en toda fuente): es seguro dejarlo. Solo avisamos.
        print(f"  aviso {src}: {_left} <text> restante(s) (simbolo ® del logo)")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"OK {dst}")


if __name__ == "__main__":
    args = sys.argv[1:]
    assert args and len(args) % 2 == 0, "uso: gen_vectorizar.py IN.svg OUT.svg [...]"
    for i in range(0, len(args), 2):
        vectorize_file(args[i], args[i + 1])
