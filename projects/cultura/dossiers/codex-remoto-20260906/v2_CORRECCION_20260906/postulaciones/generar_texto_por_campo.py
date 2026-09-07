#!/usr/bin/env python3
"""Genera TEXTO_POR_CAMPO.md con conteos automaticos de palabras y caracteres.

Los conteos NO se escriben a mano: se calculan al generar. Reejecutar tras
cualquier edicion de los textos de este archivo.
"""
import json, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent

def cuenta(t):
    t = t.strip()
    return len(re.findall(r"\S+", t)), len(t)

def render(destino, titulo, cabecera, campos, nota_final=""):
    L = [f"# {titulo}", ""]
    L.append(cabecera.strip())
    L.append("")
    L.append("> **Conteos calculados automaticamente** por `generar_texto_por_campo.py`.")
    L.append("> No estan escritos a mano. Si edita un texto, vuelva a ejecutar el script.")
    L.append("")
    L.append("## Indice de campos")
    L.append("")
    L.append("| Campo | Palabras | Caracteres | Version |")
    L.append("|---|---:|---:|---|")
    for c in campos:
        p, ch = cuenta(c["texto"])
        L.append(f"| {c['campo']} | {p} | {ch} | {c.get('version','unica')} |")
    tp = sum(cuenta(c["texto"])[0] for c in campos)
    tc = sum(cuenta(c["texto"])[1] for c in campos)
    L.append(f"| **TOTAL** | **{tp}** | **{tc}** | |")
    L.append("")
    L.append("---")
    L.append("")
    for c in campos:
        p, ch = cuenta(c["texto"])
        L.append(f"## {c['campo']}")
        L.append("")
        L.append(f"*{c.get('nota','')}*  " if c.get("nota") else "")
        L.append(f"`{p} palabras · {ch} caracteres`"
                 + (f" · version: {c['version']}" if c.get("version") else ""))
        L.append("")
        L.append(c["texto"].strip())
        L.append("")
    if nota_final:
        L.append("---")
        L.append("")
        L.append(nota_final.strip())
        L.append("")
    Path(destino).write_text("\n".join(L), encoding="utf-8")
    return {"archivo": str(destino), "campos": len(campos), "palabras": tp, "caracteres": tc}

if __name__ == "__main__":
    import campos_ama, campos_difusion, campos_formativas, campos_creacion
    out = []
    for m in (campos_ama, campos_difusion, campos_formativas, campos_creacion):
        out.append(render(AQUI / m.DESTINO, m.TITULO, m.CABECERA, m.CAMPOS,
                          getattr(m, "NOTA_FINAL", "")))
    for o in out:
        print(f"{o['campos']:>3} campos  {o['palabras']:>5} palabras  "
              f"{o['caracteres']:>6} caracteres  {o['archivo']}")
