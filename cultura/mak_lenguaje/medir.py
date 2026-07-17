#!/usr/bin/env python3
"""medir.py -- mide la senal cultural de un archivo.

    python3 medir.py archivo.md [--json]
"""
import argparse
import json
import sys

from lenguaje_lib import cargar_diccionario, desconocidas, medir_archivo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        m = medir_archivo(a.archivo)
    except OSError as e:
        print("no se pudo leer: %s" % e, file=sys.stderr)
        return 1
    dic = cargar_diccionario()
    if dic:
        with open(a.archivo, encoding="utf-8", errors="replace") as f:
            m["desconocidas"] = desconocidas(f.read(), dic)[:20]
    if a.json:
        print(json.dumps(m, ensure_ascii=False, indent=1))
        return 0
    print("señal cultural: %d/100" % m["puntaje"])
    print("  palabras: %d | tildes: %d (ratio %.3f) | eñes: %d | ¿¡: %d"
          % (m["total_palabras"], m["tildes"], m["ratio_tilde"],
             m["enies"], m["aperturas"]))
    if m["sospechosas"]:
        print("  sospechosas (%d): %s" % (m["n_sospechosas"],
                                          ", ".join(m["sospechosas"][:10])))
    if m.get("desconocidas"):
        print("  fuera del diccionario: %s" % ", ".join(m["desconocidas"][:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
