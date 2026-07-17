#!/usr/bin/env python3
"""debug.py -- CODEX: diagnostica UN bug de un modulo y PROPONE el arreglo.

NO sobrescribe el modulo vivo: produce una PROPUESTA (.py corregido o el bloque
parchado + .md con el diagnostico) para revision humana. Rol por tarea:
planner (gpt-5-mini) DIAGNOSTICA (razonar); coder (DeepSeek) REESCRIBE. Se
valida que el arreglo compile y que no toque red/procesos.

    python3 debug.py /ruta/al/archivo.py [--error "traceback"] [--densidad] [--ntfy]
"""
import argparse
import os
import sys
import time

from codex_lib import (REVISIONES, coder_llm, coder_tok, escanear,
                       extraer_codigo, guardia_espera, planner_llm, tiempo_ms)

sys.path.insert(0, "/home/mak/research")
from research_lib import escala_tok, ntfy_publish, slug, stamp  # noqa: E402

# umbral: sobre esto no reescribimos el archivo entero (se trunca) -> solo el bloque
FULL_MAX = 7000


def reparar(path, error="", densidad="medio"):
    t0 = time.time()
    with open(path, encoding="utf-8", errors="replace") as f:
        codigo = f.read()[:24000]
    nombre = os.path.basename(path)
    entero = len(codigo) <= FULL_MAX
    planner = planner_llm()
    coder = coder_llm()

    print("STATUS: Diagnostico (gpt-5-mini)...", flush=True)
    ctx = "ARCHIVO %s:\n```python\n%s\n```" % (nombre, codigo)
    if error.strip():
        ctx += "\n\nSINTOMA/ERROR observado:\n%s" % error.strip()[:2000]
    try:
        dx, _ = planner.call(
            "Eres el jefe del departamento Codex. Identifica el UNICO bug mas "
            "real y concreto de este modulo (logica, borde, tipo, recurso sin "
            "cerrar, excepcion tragada). Di: que falla, por que, y COMO "
            "arreglarlo con precision. Si no hay bug real, responde exactamente "
            "'SIN BUG'. Espanol con tildes.",
            ctx, escala_tok(700, densidad))
    except RuntimeError as e:
        dx = "[diagnostico fallo: %s]" % e
    _primer = next((ln.strip() for ln in dx.splitlines() if ln.strip()), dx)
    print("HALLAZGO: diagnostico -- " + _primer[:140], flush=True)

    aplicado, valida = "", ""
    if "SIN BUG" not in dx.upper():
        print("STATUS: Escribiendo el arreglo (DeepSeek)...", flush=True)
        if entero:
            sys_p = ("Eres un coder DeepSeek. Reescribe el ARCHIVO COMPLETO "
                     "aplicando SOLO el arreglo indicado, sin cambiar nada mas. "
                     "Devuelve el archivo entero en un bloque ```python. No expliques.")
        else:
            sys_p = ("Eres un coder DeepSeek. El archivo es grande: devuelve SOLO "
                     "la funcion o el bloque CORREGIDO (no el archivo entero) en "
                     "un bloque ```python, listo para reemplazar. No expliques.")
        try:
            salida, _ = coder.call(sys_p, "%s\n\nARREGLO A APLICAR:\n%s" % (ctx, dx),
                                   coder_tok(densidad))
            aplicado = extraer_codigo(salida)
        except RuntimeError as e:
            valida = "coder fallo: %s" % e
        if aplicado:
            try:
                compile(aplicado, nombre, "exec")
                comp = "compila OK"
            except SyntaxError as e:
                comp = "NO compila: %s" % str(e)[:120]
            motivos = escanear(aplicado)
            valida = comp + ("; escaneo: " + ", ".join(motivos)
                             if motivos else "; escaneo limpio")
        print("HALLAZGO: arreglo -- " + valida[:140], flush=True)

    os.makedirs(REVISIONES, exist_ok=True)
    base = os.path.join(REVISIONES, "%s-debug-%s" % (stamp(), slug(nombre)))
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Codex debug: %s\n\n" % path)
        f.write("> PROPUESTA — NO aplicada al modulo vivo. Revision humana.\n\n")
        f.write("## Diagnostico\n\n%s\n\n" % dx)
        if aplicado:
            tipo = "archivo completo" if entero else "bloque parchado (archivo grande)"
            f.write("## Arreglo propuesto (%s)\n\n%s\n\n```python\n%s\n```\n\n"
                    % (tipo, valida, aplicado.strip()))
        f.write("---\nmeta: planner=%s coder=%s ms=%d\n"
                % (planner.stats, coder.stats, tiempo_ms(t0)))
    if aplicado and entero:
        with open(base + ".py", "w", encoding="utf-8") as f:
            f.write(aplicado if aplicado.endswith("\n") else aplicado + "\n")
    return base + ".md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo")
    ap.add_argument("--error", default="")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio")
    ap.add_argument("--ntfy", action="store_true")
    a = ap.parse_args()
    real = os.path.realpath(a.archivo)
    if not real.startswith("/home/mak/") or not os.path.isfile(real):
        print("archivo invalido (debe existir bajo /home/mak): %s" % a.archivo)
        print("INFORME: (ninguno)")
        return 2
    if not guardia_espera():
        print("INFORME: (ninguno)")
        return 1
    path_md = reparar(real, a.error, a.densidad)
    print("INFORME: %s" % path_md)
    if a.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     "codex debug: " + path_md,
                     title="codex debug: " + os.path.basename(real))
    return 0


if __name__ == "__main__":
    sys.exit(main())
