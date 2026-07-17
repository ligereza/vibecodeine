#!/usr/bin/env python3
"""revisar.py -- CODEX: revision adversarial de un archivo de codigo.

Lentes (correccion/seguridad/simplificacion) con el coder DeepSeek; veredicto
con el modelo capaz. Producto .md en ~/codex/revisiones/.

    python3 revisar.py /ruta/al/archivo.py [--densidad] [--ntfy]
"""
import argparse
import os
import sys
import time

from codex_lib import REVISIONES, coder_llm, guardia_espera, planner_llm, tiempo_ms

sys.path.insert(0, "/home/mak/research")
from research_lib import escala_tok, ntfy_publish, slug, stamp  # noqa: E402

LENTES = [
    ("correccion", "Busca BUGS reales: logica, bordes, tipos, recursos sin "
                   "cerrar, excepciones tragadas. Se concreto: linea y fallo."),
    ("seguridad", "Busca fallas de seguridad: inyeccion, rutas sin validar, "
                  "secretos hardcodeados, shell=True, deserializacion insegura."),
    ("simplificacion", "Busca complejidad evitable: codigo muerto, duplicacion, "
                       "abstracciones innecesarias, formas mas simples."),
]


def revisar(path, densidad="medio"):
    t0 = time.time()
    with open(path, encoding="utf-8", errors="replace") as f:
        codigo = f.read()[:24000]
    coder = coder_llm()
    planner = planner_llm()
    hallazgos = []
    for nombre, foco in LENTES:
        print("STATUS: Lente %s (DeepSeek)..." % nombre, flush=True)
        try:
            texto, real = coder.call(
                "Eres un revisor de codigo adversarial, en espanol con tildes. "
                + foco + " Si no hay nada real, di 'sin hallazgos'.",
                "ARCHIVO %s:\n```python\n%s\n```" % (os.path.basename(path), codigo),
                escala_tok(700, densidad))
        except RuntimeError as e:
            texto, real = "[lente fallo: %s]" % e, None
        hallazgos.append((nombre, real, texto))

    print("STATUS: Veredicto (gpt-5-mini)...", flush=True)
    cuerpo = "\n\n".join("[%s]:\n%s" % (n, t) for n, _, t in hallazgos)
    try:
        veredicto, _ = planner.call(
            "Eres el jefe del departamento Codex. Sintetiza los hallazgos en "
            "espanol: cuales son REALES y urgentes, cuales dudosos, y un plan "
            "de arreglo en orden. Markdown.",
            cuerpo, escala_tok(800, densidad))
    except RuntimeError as e:
        veredicto = "[veredicto fallo: %s]" % e

    os.makedirs(REVISIONES, exist_ok=True)
    base = os.path.join(REVISIONES, "%s-rev-%s" % (stamp(), slug(os.path.basename(path))))
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Revisión codex: %s\n\n## Veredicto\n\n%s\n\n---\n\n"
                % (path, veredicto))
        for nombre, real, texto in hallazgos:
            f.write("## Lente %s (%s)\n\n%s\n\n" % (nombre, real, texto))
        f.write("---\nmeta: coder=%s planner=%s ms=%d\n"
                % (coder.stats, planner.stats, tiempo_ms(t0)))
    return base + ".md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"),
                    default="medio")
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
    path_md = revisar(real, a.densidad)
    if a.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     "revision codex: " + path_md,
                     title="codex revisa: " + os.path.basename(real))
    print("INFORME: " + path_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
