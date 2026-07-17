#!/usr/bin/env python3
"""cadena.py -- flujo ENCADENADO entre modelos (MAK, sin n8n).

A diferencia de panel.py (4 modelos en paralelo, sin depender uno del
otro), aqui la salida de cada modelo alimenta al siguiente: relay
secuencial que termina en una sintesis. El orden lo define el canvas
(prioridad de nodos) via --orden, o el default groq->cerebras->azure->
ollama si no se especifica.
Salida: ~/research/cadenas/STAMP-slug.{md,json}.

Uso:
    python3 cadena.py "tema" [--orden groq,cerebras,azure,ollama]
                      [--densidad corto|medio|largo] [--sin-marco] [--ntfy]
"""
import argparse
import json
import os
import sys
import time

from research_lib import (LLM, correlacionar, escala_tok, load_env, marco,
                          ntfy_publish, slug, stamp)

OUT_DIR = os.path.expanduser("~/research/cadenas")

# Un rol por paso; se recorta/repite si --orden trae menos/mas de 4.
ROLES = [
    "Eres historiador cultural. En %d palabras: origen y contexto "
    "historico del tema.",
    "Eres analista tecnico-cientifico. En %d palabras, TOMA el texto "
    "previo y AGREGA la dimension tecnica/cientifica que falte, sin "
    "repetir lo ya dicho.",
    "Eres analista juridico. En %d palabras, TOMA el texto previo y "
    "AGREGA la dimension legal/regulatoria, sin repetir lo ya dicho.",
    "Eres critico de arte. TOMA todo el texto previo y escribe una "
    "SINTESIS final de %d palabras que integre las dimensiones previas "
    "mas una lectura estetica/simbolica.",
]


def encadenar(tema, orden, densidad="medio"):
    t0 = time.time()
    llm = LLM()
    pasos = list(zip(orden, ROLES + ROLES))  # ROLES*2 cubre orden largo
    texto = ""
    detalle = []

    for i, (proveedor, rol_tpl) in enumerate(pasos):
        palabras = 150 if i < len(pasos) - 1 else 200
        rol = rol_tpl % palabras
        print("STATUS: Paso %d/%d (%s)..." % (i + 1, len(pasos), proveedor),
             flush=True)
        prompt = ('TEMA: "%s"\n\nTEXTO ACUMULADO HASTA AHORA:\n%s\n\n%s'
                  % (tema, texto or "(nada aun, eres el primero)", rol))
        out, real = llm.call(rol, prompt, escala_tok(500, densidad),
                             order=[proveedor])
        detalle.append({"paso": i + 1, "proveedor_pedido": proveedor,
                        "proveedor_real": real, "texto": out})
        texto += "\n\n[%s]: %s" % (proveedor, out)

    # Correlacion semantica sobre los pasos de la cadena.
    print("STATUS: Correlacionando (departamento research)...", flush=True)
    piezas = [{"modelo": "%s (paso %d)" % (d["proveedor_real"], d["paso"]),
               "texto": d["texto"]} for d in detalle]
    correlacion, _ = correlacionar(llm, tema, piezas, densidad)

    return {
        "tema": tema,
        "sintesis": detalle[-1]["texto"] if detalle else "",
        "correlacion": correlacion,
        "pasos": detalle,
        "meta": {
            "orden": orden,
            "llmCalls": llm.stats,
            "errors": llm.errors[:20],
            "ms": int((time.time() - t0) * 1000),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Cadena encadenada multi-modelo (MAK)")
    ap.add_argument("tema")
    ap.add_argument("--orden", default="groq,cerebras,azure,ollama",
                    help="CSV de proveedores, orden de la posta")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio")
    ap.add_argument("--sin-marco", action="store_true")
    ap.add_argument("--ntfy", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    load_env()
    orden = [p.strip() for p in args.orden.split(",")
            if p.strip() in ("groq", "cerebras", "azure", "ollama")]
    if not orden:
        orden = ["groq", "cerebras", "azure", "ollama"]
    tema = marco(args.tema, activo=not args.sin_marco)
    result = encadenar(tema, orden, args.densidad)

    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, "%s-%s" % (stamp(), slug(args.tema)))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Cadena: %s\n\n%s\n\n" % (args.tema, result["sintesis"]))
        if result.get("correlacion"):
            f.write("---\n\n## Correlacion semantica (departamento research)\n\n%s\n\n"
                    % result["correlacion"])
        f.write("---\n\n## Pasos\n\n")
        for p in result["pasos"]:
            f.write("### Paso %d -- %s (real: %s)\n\n%s\n\n"
                    % (p["paso"], p["proveedor_pedido"], p["proveedor_real"],
                       p["texto"]))
        f.write("---\nmeta: %s\n" % json.dumps(result["meta"], ensure_ascii=False))

    m = result["meta"]
    print("cadena: %d pasos, llm=%s, %d ms" % (len(orden), m["llmCalls"], m["ms"]))
    if m["errors"]:
        print("errores no fatales: %d" % len(m["errors"]))
    if args.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     result["sintesis"][:900] + "\n\n" + base + ".md",
                     title="cadena lista: " + args.tema[:80])
    print("INFORME: " + base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
