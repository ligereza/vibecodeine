#!/usr/bin/env python3
"""refutar.py -- flujo ADVERSARIAL: un modelo propone, el resto refuta (MAK).

Un proponente escribe una tesis sobre el tema; los demas modelos
disponibles intentan REFUTARLA independientemente (en paralelo); un
juez final sintetiza el veredicto. Util para poner a prueba afirmaciones
culturales dudosas antes de darlas por buenas.
El orden lo define el canvas (prioridad de nodos) via --orden: el
primero propone, el ultimo juzga, los del medio refutan.
Salida: ~/research/refutaciones/STAMP-slug.{md,json}.

Uso:
    python3 refutar.py "tema" [--orden groq,cerebras,azure,ollama]
                       [--densidad corto|medio|largo] [--sin-marco] [--ntfy]
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from research_lib import (LLM, escala_tok, load_env, marco, ntfy_publish,
                          slug, stamp, tavily_search)

OUT_DIR = os.path.expanduser("~/research/refutaciones")

SISTEMA_PROPONENTE = (
    "Eres un investigador que defiende una TESIS concreta y verificable "
    "sobre el tema, en espanol correcto con tildes. Capa DESCRIPTIVA y "
    "cultural unicamente: nada operativo, nada de sintesis ni cultivo, "
    "jamas perfilar personas reales. Cita fuentes si las tienes."
)
SISTEMA_REFUTADOR = (
    "Eres un revisor academico critico. Tu trabajo es intentar REFUTAR "
    "la tesis dada: buscar fallas logicas, huecos de evidencia, "
    "generalizaciones injustificadas o sesgos. Si la tesis resiste tu "
    "critica, dilo honestamente -- no inventes objeciones debiles. "
    "Espanol correcto con tildes."
)
SISTEMA_JUEZ = (
    "Eres el juez final de un proceso adversarial academico. Lees la "
    "tesis y las refutaciones y emites un VEREDICTO honesto: la tesis "
    "sostiene, sostiene parcialmente, o queda refutada -- con razones. "
    "Espanol correcto con tildes, formato Markdown."
)


def refutar(tema, orden, densidad="medio"):
    t0 = time.time()
    llm = LLM()
    if len(orden) < 3:
        orden = (orden + ["groq", "cerebras", "azure", "ollama"])[:4]
    proponente, jueza = orden[0], orden[-1]
    refutadores = orden[1:-1] or [p for p in orden if p != proponente][:1]

    print("STATUS: Buscando contexto...", flush=True)
    errores = llm.errors
    search = tavily_search(tema, errors=errores)
    contexto = (search.get("answer") or "") + "\n" + "\n".join(
        "- %s | %s" % (r.get("title", ""), r.get("url", ""))
        for r in (search.get("results") or [])[:5])
    fuentes = [r["url"] for r in (search.get("results") or []) if r.get("url")]

    print("STATUS: Proponente (%s) escribe la tesis..." % proponente, flush=True)
    tesis, real_prop = llm.call(
        SISTEMA_PROPONENTE,
        'TEMA: "%s"\n\nCONTEXTO DE BUSQUEDA:\n%s\n\nEscribe tu TESIS '
        "(200-250 palabras): afirmacion concreta + 3 argumentos con fuente."
        % (tema, contexto),
        escala_tok(700, densidad), order=[proponente])

    def refutacion(prov):
        out, real = llm.call(
            SISTEMA_REFUTADOR,
            'TEMA: "%s"\n\nTESIS A REFUTAR:\n%s\n\nEscribe tu REFUTACION '
            "(150-200 palabras): fallas concretas, o admite que resiste "
            "si es honesto."
            % (tema, tesis),
            escala_tok(500, densidad), order=[prov])
        return prov, real, out

    print("STATUS: %d refutadores en paralelo..." % len(refutadores), flush=True)
    with ThreadPoolExecutor(max_workers=max(1, len(refutadores))) as ex:
        refutaciones = list(ex.map(refutacion, refutadores))

    print("STATUS: Juez (%s) emite veredicto..." % jueza, flush=True)
    texto_refutaciones = "\n\n".join(
        "[%s]: %s" % (prov, out) for prov, _, out in refutaciones)
    veredicto, real_juez = llm.call(
        SISTEMA_JUEZ,
        'TEMA: "%s"\n\nTESIS:\n%s\n\nREFUTACIONES:\n%s\n\nEmite tu '
        "VEREDICTO con secciones: 1. TESIS EVALUADA, 2. REFUTACIONES "
        "CONSIDERADAS, 3. VEREDICTO (sostiene/parcial/refutada), 4. RAZONES."
        % (tema, tesis, texto_refutaciones),
        escala_tok(900, densidad), order=[jueza])

    return {
        "tema": tema,
        "veredicto": veredicto,
        "tesis": {"proveedor": real_prop, "texto": tesis},
        "refutaciones": [{"proveedor": r, "real": real, "texto": t}
                         for r, real, t in refutaciones],
        "meta": {
            "proponente": proponente, "refutadores": refutadores,
            "juez": jueza, "fuentes": fuentes,
            "llmCalls": llm.stats, "errors": llm.errors[:20],
            "ms": int((time.time() - t0) * 1000),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Flujo adversarial proponer/refutar (MAK)")
    ap.add_argument("tema")
    ap.add_argument("--orden", default="groq,cerebras,azure,ollama",
                    help="CSV: primero propone, ultimo juzga, resto refuta")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio")
    ap.add_argument("--sin-marco", action="store_true")
    ap.add_argument("--ntfy", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    load_env()
    orden = [p.strip() for p in args.orden.split(",")
            if p.strip() in ("groq", "cerebras", "azure", "ollama")]
    tema = marco(args.tema, activo=not args.sin_marco)
    result = refutar(tema, orden or ["groq", "cerebras", "azure", "ollama"],
                     args.densidad)

    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, "%s-%s" % (stamp(), slug(args.tema)))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Adversarial: %s\n\n%s\n\n---\n\n## Tesis (%s)\n\n%s\n\n"
                "## Refutaciones\n\n"
                % (args.tema, result["veredicto"], result["tesis"]["proveedor"],
                   result["tesis"]["texto"]))
        for r in result["refutaciones"]:
            f.write("### %s (real: %s)\n\n%s\n\n" % (r["proveedor"], r["real"], r["texto"]))
        f.write("---\nmeta: %s\n" % json.dumps(result["meta"], ensure_ascii=False))

    m = result["meta"]
    print("refutar: proponente=%s juez=%s, llm=%s, %d ms"
          % (m["proponente"], m["juez"], m["llmCalls"], m["ms"]))
    if m["errors"]:
        print("errores no fatales: %d" % len(m["errors"]))
    if args.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     result["veredicto"][:900] + "\n\n" + base + ".md",
                     title="veredicto listo: " + args.tema[:80])
    print("INFORME: " + base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
