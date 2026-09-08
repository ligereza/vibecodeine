#!/usr/bin/env python3
"""corregir.py -- restaura la senal cultural de un .md con el modelo capaz.

    python3 corregir.py pieza.md [--densidad]

Nunca sobreescribe el original: escribe pieza.corregido.md al lado y
reporta la mejora medida (antes/despues).
"""
import argparse
import difflib
import os
import sys

sys.path.insert(0, "/home/mak/research")
sys.path.insert(0, "/home/mak/lenguaje")
from lenguaje_lib import medir_senal  # noqa: E402
from research_lib import LLM, MODELO_CAPAZ, escala_tok, load_env  # noqa: E402


def corregir(path, densidad="medio"):
    with open(path, encoding="utf-8", errors="replace") as f:
        original = f.read()
    antes = medir_senal(original)
    load_env()
    llm = LLM()
    orden = [MODELO_CAPAZ] + [x for x in llm.order if x != MODELO_CAPAZ]
    print("STATUS: Restaurando senal cultural...", flush=True)
    corregido, real = llm.call(
        "Eres corrector ortotipográfico de español. Restauras tildes, eñes y "
        "signos de apertura (¿¡) SIN cambiar contenido, términos técnicos, "
        "código, URLs ni palabras en inglés. Devuelves el texto completo "
        "corregido, nada más.",
        original[:24000], escala_tok(len(original) // 3 + 500, densidad),
        order=orden)
    despues = medir_senal(corregido)
    destino = os.path.splitext(path)[0] + ".corregido.md"
    with open(destino, "w", encoding="utf-8") as f:
        f.write(corregido)
    diff = list(difflib.unified_diff(original.splitlines(),
                                     corregido.splitlines(), lineterm=""))[:40]
    return destino, antes, despues, diff, real


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"),
                    default="medio")
    a = ap.parse_args()
    if not os.path.isfile(a.archivo):
        print("no existe: %s" % a.archivo, file=sys.stderr)
        return 1
    destino, antes, despues, diff, real = corregir(a.archivo, a.densidad)
    print("señal: %d/100 -> %d/100 (corrigió %s)"
          % (antes["puntaje"], despues["puntaje"], real))
    print("tildes: %d -> %d | eñes: %d -> %d | ¿¡: %d -> %d"
          % (antes["tildes"], despues["tildes"], antes["enies"],
             despues["enies"], antes["aperturas"], despues["aperturas"]))
    if diff:
        print("\n".join(diff[:25]))
    print("INFORME: " + destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
