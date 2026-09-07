#!/usr/bin/env python3
"""Post-procesa un SVG generado: fusiona lineas consecutivas de un mismo parrafo
(mismo x, mismo estilo, y creciente con paso constante) en UN solo <text> con
<tspan x dy> por linea. Asi Illustrator lo importa como un bloque editable por
parrafo/item, no como lineas sueltas. El render queda identico (mismas posiciones).

Uso: py merge_paragraphs.py IN.svg [OUT.svg]   (sin OUT edita en sitio)
Solo fusiona <text> consecutivos con solo whitespace entre medio (si hay otro
elemento, corta el bloque). Los <text> del logo (®) quedan intactos.
"""
import re, sys

TEXT_RE = re.compile(r"<text\b[^>]*>.*?</text>", re.S)

def _attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None

def parse(el):
    ot = el[:el.index(">") + 1]
    inner = el[el.index(">") + 1: el.rindex("</text>")]
    x, y = _attr(ot, "x"), _attr(ot, "y")
    if x is None or y is None:
        return None
    try:
        x, y = float(x), float(y)
    except ValueError:
        return None
    key = re.sub(r'\s(x|y)="[^"]*"', "", ot)   # estilo sin x/y
    return {"el": el, "open": ot, "inner": inner, "x": x, "y": y, "key": key}

def merge_run(run):
    if len(run) == 1:
        return run[0]["el"]
    e0 = run[0]
    sp = [f'<tspan x="{e0["x"]:.1f}" dy="0">{e0["inner"]}</tspan>']
    for i in range(1, len(run)):
        dy = run[i]["y"] - run[i - 1]["y"]
        sp.append(f'<tspan x="{run[i]["x"]:.1f}" dy="{dy:.1f}">{run[i]["inner"]}</tspan>')
    return e0["open"] + "".join(sp) + "</text>"

def process(svg):
    parts = TEXT_RE.split(svg)        # len = n_texts + 1
    texts = TEXT_RE.findall(svg)
    out, run = [], []

    def flush():
        if run:
            out.append(merge_run(run)); run.clear()

    for i, t in enumerate(texts):
        sep = parts[i]                # separador ANTES de este <text>
        ws = (sep.strip() == "")
        p = parse(t)
        cont = False
        if run and p and ws and p["key"] == run[-1]["key"] and abs(p["x"] - run[-1]["x"]) < 1.0:
            d = p["y"] - run[-1]["y"]
            pd = (run[-1]["y"] - run[-2]["y"]) if len(run) >= 2 else None
            if d > 0 and (pd is None or 0.5 * pd <= d <= 1.6 * pd):
                cont = True
        if cont:
            run.append(p)             # el whitespace 'sep' se absorbe (se descarta)
        else:
            flush()
            out.append(sep)           # emitir separador antes del nuevo bloque
            if p:
                run.append(p)
            else:
                out.append(t)         # <text> no parseable (® del logo): tal cual
    flush()
    out.append(parts[len(texts)])     # separador final
    return "".join(out)

if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    svg = open(src, encoding="utf-8").read()
    nb = svg.count("<text ") + svg.count("<text>")
    res = process(svg)
    na = res.count("<text ") + res.count("<text>")
    open(dst, "w", encoding="utf-8").write(res)
    print(f"{src.split('/')[-1]}: <text> {nb} -> {na}  (parrafos/items agrupados)")
