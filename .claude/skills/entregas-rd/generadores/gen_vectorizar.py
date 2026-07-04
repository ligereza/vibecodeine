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


TEXT_RE = re.compile(r'<text([^>]*)>([^<]*)</text>')
ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')
UNESC = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'"}


def unescape(s):
    for k, v in UNESC.items():
        s = s.replace(k, v)
    return s


def vectorize_file(src, dst):
    svg = open(src, encoding="utf-8").read()

    def repl(m):
        attrs = dict(ATTR_RE.findall(m.group(1)))
        content = unescape(m.group(2))
        if not content.strip():
            return ""
        d = text_to_path(
            content,
            attrs.get("x", "0"), attrs.get("y", "0"),
            float(attrs.get("font-size", "16")),
            attrs.get("font-weight", "400"),
            attrs.get("text-anchor", ""),
        )
        if not d:
            return ""
        return f'<path d="{d}" fill="{attrs.get("fill", "#000")}"/>'

    out = TEXT_RE.sub(repl, svg)
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
