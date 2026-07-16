#!/usr/bin/env python3
"""grafo.py -- ejecutor de grafo real (MAK, sin n8n).

El canvas define un grafo (nodos + conexiones) que DIRIGE la ejecucion:
orden topologico de los nodos-modelo, cada uno recibe como contexto la
salida concatenada de sus predecesores; los nodos trigger inyectan el
tema y los nodos output recopilan. Valida flujos extremos antes de correr.

Tipos de nodo: trigger (entrada, lleva el tema), groq/cerebras/azure/
ollama (accion = una llamada LLM), output (recopila), nota (ignorado).
Se permiten MULTIPLES triggers y outputs.

Salida: ~/research/grafos/STAMP-slug.{md,json}.

Uso:
    python3 grafo.py "tema" [--workflow ~/research/workflow.json]
                     [--densidad corto|medio|largo] [--sin-marco] [--ntfy]
"""
import argparse
import json
import os
import sys
import time

from research_lib import (LLM, correlacionar, escala_tok, load_env, marco,
                          ntfy_publish, slug, stamp)

OUT_DIR = os.path.expanduser("~/research/grafos")
WORKFLOW_FILE = os.path.expanduser("~/research/workflow.json")
PROVEEDORES = ("groq", "cerebras", "azure", "ollama")

# Limites anti-flujo-extremo (el usuario pidio anticiparse a casos que
# confunden al modelo). Se validan antes de ejecutar.
MAX_NODOS = 12       # nodos-modelo ejecutables
MAX_FANOUT = 6       # aristas saliendo de un mismo nodo
MAX_FANIN = 6        # aristas entrando a un mismo nodo


def _tipo(nd):
    t = nd.get("tipo")
    if t:
        return t
    return "modelo"  # groq/cerebras/azure/ollama sin tipo explicito


def validar_grafo(nodes, conns):
    """Devuelve lista de errores (vacia = grafo sano). Bloquea ciclos,
    huerfanos, sin-camino, y fan-out/in extremos."""
    errores = []
    activos = {k for k, nd in nodes.items()
               if nd.get("active", True) and _tipo(nd) != "nota"}
    triggers = {k for k in activos if _tipo(nodes[k]) == "trigger" or k == "trigger"}
    outputs = {k for k in activos if _tipo(nodes[k]) == "output" or k == "output"}
    modelos = {k for k in activos if k in PROVEEDORES}

    if not triggers:
        errores.append("No hay nodo de entrada (trigger) activo.")
    if not outputs:
        errores.append("No hay nodo de salida (output) activo.")
    if not modelos:
        errores.append("No hay ningun modelo activo en el grafo.")
    if len(modelos) > MAX_NODOS:
        errores.append("Demasiados modelos (%d > %d): flujo extremo."
                       % (len(modelos), MAX_NODOS))

    # aristas solo entre nodos activos
    edges = [(c["from"], c["to"]) for c in conns
             if c.get("from") in activos and c.get("to") in activos]

    # fan-out / fan-in
    from collections import defaultdict
    fout, fin = defaultdict(int), defaultdict(int)
    for a, b in edges:
        fout[a] += 1
        fin[b] += 1
    for k, n in fout.items():
        if n > MAX_FANOUT:
            errores.append("Nodo '%s' con fan-out extremo (%d > %d)." % (k, n, MAX_FANOUT))
    for k, n in fin.items():
        if n > MAX_FANIN:
            errores.append("Nodo '%s' con fan-in extremo (%d > %d)." % (k, n, MAX_FANIN))

    # ciclos (Kahn): si sobran nodos, hay ciclo
    adj = defaultdict(list)
    indeg = defaultdict(int)
    en_grafo = set()
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
        en_grafo.add(a)
        en_grafo.add(b)
    cola = [k for k in en_grafo if indeg[k] == 0]
    visto = 0
    indeg2 = dict(indeg)
    while cola:
        n = cola.pop()
        visto += 1
        for m in adj[n]:
            indeg2[m] -= 1
            if indeg2[m] == 0:
                cola.append(m)
    if visto < len(en_grafo):
        errores.append("El grafo tiene un ciclo (los modelos no pueden "
                       "correr en orden). Quita alguna conexion.")

    # camino trigger -> output (alcanzabilidad)
    if triggers and outputs and not errores:
        alcanzables = set(triggers)
        frontera = list(triggers)
        while frontera:
            n = frontera.pop()
            for m in adj[n]:
                if m not in alcanzables:
                    alcanzables.add(m)
                    frontera.append(m)
        if not (outputs & alcanzables):
            errores.append("Ningun output es alcanzable desde un trigger.")
        huerfanos = modelos - alcanzables
        if huerfanos:
            errores.append("Modelos sin conexion desde la entrada: %s."
                           % ", ".join(sorted(huerfanos)))
    return errores


def orden_topologico(modelos, edges):
    """Orden de ejecucion de los nodos-modelo (Kahn, estable por nombre)."""
    from collections import defaultdict
    adj = defaultdict(list)
    indeg = defaultdict(int)
    for a, b in edges:
        if b in modelos:
            adj[a].append(b)
            if a in modelos:
                indeg[b] += 1
    cola = sorted(m for m in modelos if indeg[m] == 0)
    orden = []
    while cola:
        n = cola.pop(0)
        orden.append(n)
        for m in sorted(adj[n]):
            if m in modelos:
                indeg[m] -= 1
                if indeg[m] == 0:
                    cola.append(m)
    # cualquier resto (no deberia si validado) al final
    for m in modelos:
        if m not in orden:
            orden.append(m)
    return orden


def ejecutar_grafo(tema, nodes, conns, densidad="medio"):
    t0 = time.time()
    llm = LLM()
    activos = {k for k, nd in nodes.items()
               if nd.get("active", True) and _tipo(nd) != "nota"}
    triggers = {k for k in activos if _tipo(nodes[k]) == "trigger" or k == "trigger"}
    modelos = {k for k in activos if k in PROVEEDORES}
    edges = [(c["from"], c["to"]) for c in conns
             if c.get("from") in activos and c.get("to") in activos]

    # predecesores de cada nodo
    from collections import defaultdict
    preds = defaultdict(list)
    for a, b in edges:
        preds[b].append(a)

    salidas = {}   # nodo -> texto producido
    detalle = []
    orden = orden_topologico(modelos, edges)

    for i, m in enumerate(orden):
        nd = nodes[m]
        # contexto = salida de predecesores; si predecesor es trigger, el tema
        ctx_parts = []
        for p in preds.get(m, []):
            if p in triggers or p == "trigger":
                ctx_parts.append('TEMA: "%s"' % tema)
            elif p in salidas:
                ctx_parts.append("[%s dijo]: %s" % (p, salidas[p]))
        if not ctx_parts:  # sin predecesor: arranca del tema
            ctx_parts.append('TEMA: "%s"' % tema)
        contexto = "\n\n".join(ctx_parts)

        system = nd.get("system_prompt") or (
            "Eres un investigador cultural (nodo %s). Escribes en espanol "
            "correcto con tildes. Capa DESCRIPTIVA: nada operativo, nada de "
            "sintesis quimica ni cultivo, jamas perfilar personas reales." % m)
        print("STATUS: Nodo %d/%d (%s)..." % (i + 1, len(orden), m), flush=True)
        try:
            texto, real = llm.call(
                system,
                contexto + "\n\nAporta tu analisis (250-350 palabras), "
                "construyendo sobre el contexto previo sin repetirlo.",
                escala_tok(700, densidad),
                order=[m] + [x for x in llm.order if x != m])
        except RuntimeError as e:
            texto, real = "[nodo %s fallo: %s]" % (m, e), None
        salidas[m] = texto
        detalle.append({"nodo": m, "proveedor_real": real,
                        "predecesores": preds.get(m, []), "texto": texto})

    # nodos output: recopilan sus predecesores
    outputs = {k for k in activos if _tipo(nodes[k]) == "output" or k == "output"}
    piezas = [{"modelo": d["proveedor_real"] or d["nodo"], "texto": d["texto"]}
              for d in detalle]
    print("STATUS: Correlacionando salida...", flush=True)
    correlacion, _ = correlacionar(llm, tema, piezas, densidad)

    return {
        "tema": tema,
        "correlacion": correlacion,
        "nodos": detalle,
        "orden": orden,
        "meta": {
            "n_modelos": len(orden),
            "n_outputs": len(outputs),
            "llmCalls": llm.stats,
            "errors": llm.errors[:20],
            "ms": int((time.time() - t0) * 1000),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Ejecutor de grafo custom (MAK)")
    ap.add_argument("tema")
    ap.add_argument("--workflow", default=WORKFLOW_FILE)
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio")
    ap.add_argument("--sin-marco", action="store_true")
    ap.add_argument("--ntfy", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    load_env()
    try:
        with open(args.workflow, encoding="utf-8") as f:
            wf = json.load(f)
    except (OSError, ValueError) as e:
        print("No se pudo leer el workflow: %s" % e)
        print("INFORME: (ninguno)")
        return 1
    nodes = wf.get("nodes", {})
    conns = wf.get("connections", [])

    errores = validar_grafo(nodes, conns)
    if errores:
        print("GRAFO INVALIDO (no se ejecuta):")
        for e in errores:
            print("  - " + e)
        print("INFORME: (ninguno)")
        return 2

    tema = marco(args.tema, activo=not args.sin_marco)
    result = ejecutar_grafo(tema, nodes, conns, args.densidad)

    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, "%s-%s" % (stamp(), slug(args.tema)))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Grafo: %s\n\n" % args.tema)
        if result.get("correlacion"):
            f.write("## Correlacion (salida)\n\n%s\n\n---\n\n" % result["correlacion"])
        f.write("## Nodos (orden de ejecucion)\n\n")
        for d in result["nodos"]:
            pred = ", ".join(d["predecesores"]) or "(entrada)"
            f.write("### %s (real: %s) <- %s\n\n%s\n\n"
                    % (d["nodo"], d["proveedor_real"], pred, d["texto"]))
        f.write("---\nmeta: %s\n" % json.dumps(result["meta"], ensure_ascii=False))

    m = result["meta"]
    print("grafo: %d modelos, %d outputs, llm=%s, %d ms"
          % (m["n_modelos"], m["n_outputs"], m["llmCalls"], m["ms"]))
    if m["errors"]:
        print("errores no fatales: %d" % len(m["errors"]))
    if args.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     (result["correlacion"] or "")[:900] + "\n\n" + base + ".md",
                     title="grafo listo: " + args.tema[:80])
    print("INFORME: " + base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
