#!/usr/bin/env python3
"""hook_barrido.py -- barrido idempotente: appendea la medicion de senal
cultural a los .md de productos que aun no la tienen. Pensado para cron
(*/10). Automatiza el enfoque lenguaje sin tocar los workers vivos.
"""
import os
import sys

sys.path.insert(0, "/home/mak/lenguaje")
from lenguaje_lib import medir_senal  # noqa: E402

MARCA = "señal cultural:"
CARPETAS = [
    "/home/mak/research/informes", "/home/mak/research/paneles",
    "/home/mak/research/cadenas", "/home/mak/research/refutaciones",
    "/home/mak/research/correlaciones", "/home/mak/research/grafos",
    "/home/mak/research/memoria", "/home/mak/codex/piezas",
    "/home/mak/codex/revisiones",
]


def barrer():
    tocados = 0
    for d in CARPETAS:
        try:
            nombres = os.listdir(d)
        except OSError:
            continue
        for n in nombres:
            if not n.endswith(".md") or n.endswith(".corregido.md"):
                continue
            path = os.path.join(d, n)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    texto = f.read()
            except OSError:
                continue
            if MARCA in texto:
                continue
            m = medir_senal(texto)
            linea = ("\n---\nseñal cultural: %d/100 (tildes %d, eñes %d, "
                     "aperturas %d, sospechosas %d)\n"
                     % (m["puntaje"], m["tildes"], m["enies"],
                        m["aperturas"], m["n_sospechosas"]))
            try:
                with open(path, "a", encoding="utf-8") as f:
                    f.write(linea)
                tocados += 1
            except OSError:
                pass
    return tocados


if __name__ == "__main__":
    print("hook_barrido: %d piezas medidas" % barrer())
