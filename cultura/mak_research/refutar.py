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

from research_lib import (LLM, PROVIDERS, escala_tok, load_env, marco_solo,
                          ntfy_publish, slug, stamp, web_search)

try:
    import fuentes
except ImportError:          # el flujo puede correr sin la compuerta
    fuentes = None

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


def refutar(tema, orden, densidad="medio", marco_activo=True, modelos=None):
    """`tema` es el tema CRUDO. El encuadre se le da al MODELO, nunca al
    buscador.

    Esta funcion recibia el tema con el encuadre ya pegado adelante y se lo
    mandaba entero a `web_search`. Es exactamente el defecto que `marco_solo()`
    fue escrito para cortar en `research.py` el 2026-07-30, y que aca seguia
    vivo: medido el 2026-07-31 contra una afirmacion sobre derecho chileno, las
    fuentes que volvieron fueron estudios culturales de la UNAM, una pagina
    peruana sobre que es la investigacion cultural y un volcado de estadisticas
    de Wikipedia en sueco -- y el veredicto fue que la tesis "sostiene
    parcialmente". Con el tema limpio y la compuerta puesta, la busqueda llega a
    minsal.cl y el veredicto se da vuelta.
    """
    t0 = time.time()
    llm = LLM()
    modelos = modelos or {}
    # Hacen falta tres papeles (propone / refuta / juzga). Si pidieron menos, se
    # repite lo PEDIDO en vez de completar con la cadena entera: pedir un solo
    # proveedor y recibir de juez a otro que no tiene llave es como moria esto
    # antes -- el ultimo puesto se llenaba con `azure` y el juicio no ocurria.
    if len(orden) < 3:
        orden = [orden[i % len(orden)] for i in range(3)] if orden else \
            list(PROVIDERS)[:4]
    proponente, jueza = orden[0], orden[-1]
    refutadores = orden[1:-1] or [p for p in orden if p != proponente][:1]

    # El encuadre va al SYSTEM de cada papel; el buscador recibe el tema solo.
    encuadre = marco_solo(tema, activo=marco_activo)
    sis_prop = encuadre + SISTEMA_PROPONENTE
    sis_ref = encuadre + SISTEMA_REFUTADOR
    sis_juez = encuadre + SISTEMA_JUEZ

    print("STATUS: Buscando contexto...", flush=True)
    errores = llm.errors
    # La compuerta de dominio decide QUE se busca. Para casi todo devuelve None
    # y no estorba: la mayoria de las preguntas culturales no tienen una fuente
    # primaria que exigir.
    dom = fuentes.dominio_de_tema(tema) if fuentes else None
    consultas = (fuentes.sugerir_queries(tema, dom) if (fuentes and dom)
                 else [tema])
    resultados, respuesta = [], ""
    for q in consultas[:3]:
        s = web_search(q, errors=errores)
        respuesta = respuesta or (s.get("answer") or "")
        resultados.extend(s.get("results") or [])
    urls = list(dict.fromkeys(r["url"] for r in resultados if r.get("url")))
    contexto = respuesta + "\n" + "\n".join(
        "- %s | %s" % (r.get("title", ""), r.get("url", ""))
        for r in resultados[:8])

    # Sin fuente primaria la TAREA cambia: de sostener una tesis a reportar que
    # no hay con que sostenerla. No es un aviso al margen, es otra instruccion
    # -- y es la diferencia entre un juez que dice "sostiene parcialmente" y uno
    # que dice que nadie trajo la ley.
    evaluacion = fuentes.evaluar(tema, urls, dom) if (fuentes and dom) else None
    if evaluacion:
        extra = fuentes.instruccion_sintesis(urls, dom)
        sis_prop += extra
        sis_juez += extra
        sis_ref += extra
        print("STATUS: dominio %s -- %d de %d fuentes son primarias"
              % (dom, len(evaluacion["fuentes_primarias"]), len(urls)),
              flush=True)

    print("STATUS: Proponente (%s) escribe la tesis..." % proponente, flush=True)
    tesis, real_prop = llm.call(
        sis_prop,
        'TEMA: "%s"\n\nCONTEXTO DE BUSQUEDA:\n%s\n\nEscribe tu TESIS '
        "(200-250 palabras): afirmacion concreta + 3 argumentos con fuente. "
        "Si el contexto no sostiene la afirmacion, DILO: una tesis sin fuente "
        "no es una tesis debil, es una que no se puede escribir."
        % (tema, contexto),
        escala_tok(700, densidad), order=[proponente],
        model=modelos.get("proponente"))
    print("HALLAZGO: propuesta -- " + tesis.replace("\n", " ")[:140], flush=True)

    def refutacion(prov):
        out, real = llm.call(
            sis_ref,
            'TEMA: "%s"\n\nTESIS A REFUTAR:\n%s\n\nFUENTES DISPONIBLES:\n%s\n\n'
            "Escribe tu REFUTACION (150-200 palabras). Empieza por el HECHO: "
            "cual afirmacion NO esta respaldada por las fuentes de arriba. "
            "Recien despues, fallas de razonamiento. Si la tesis resiste, "
            "dilo honestamente."
            % (tema, tesis, "\n".join("- " + u for u in urls[:8])),
            escala_tok(500, densidad), order=[prov],
            model=modelos.get("refutador"))
        print("HALLAZGO: refutacion -- " + out.replace("\n", " ")[:140], flush=True)
        return prov, real, out

    print("STATUS: %d refutadores en paralelo..." % len(refutadores), flush=True)
    with ThreadPoolExecutor(max_workers=max(1, len(refutadores))) as ex:
        refutaciones = list(ex.map(refutacion, refutadores))

    print("STATUS: Juez (%s) emite veredicto..." % jueza, flush=True)
    texto_refutaciones = "\n\n".join(
        "[%s]: %s" % (prov, out) for prov, _, out in refutaciones)
    veredicto, real_juez = llm.call(
        sis_juez,
        'TEMA: "%s"\n\nTESIS:\n%s\n\nREFUTACIONES:\n%s\n\nFUENTES:\n%s\n\n'
        "Emite tu VEREDICTO con secciones: 1. TESIS EVALUADA, 2. REFUTACIONES "
        "CONSIDERADAS, 3. VEREDICTO (sostiene/parcial/refutada), 4. RAZONES. "
        "Una tesis cuyas afirmaciones no aparecen en las fuentes queda "
        "REFUTADA por falta de respaldo, por bien escrita que este."
        % (tema, tesis, texto_refutaciones,
           "\n".join("- " + u for u in urls[:8])),
        escala_tok(900, densidad), order=[jueza],
        model=modelos.get("juez"))
    print("HALLAZGO: veredicto -- " + veredicto.replace("\n", " ")[:140], flush=True)

    return {
        "tema": tema,
        "veredicto": veredicto,
        "tesis": {"proveedor": real_prop, "texto": tesis},
        "refutaciones": [{"proveedor": r, "real": real, "texto": t}
                         for r, real, t in refutaciones],
        "meta": {
            "proponente": proponente, "refutadores": refutadores,
            "juez": jueza, "fuentes": urls,
            "dominio": dom,
            # La llave se lee de `evaluar()`, no se recalcula: la primera
            # version preguntaba por `primarias`, una llave que ese dict no
            # tiene, asi que marcaba SIN FUENTE PRIMARIA incluso con seis
            # fuentes primarias en la mano. Un instrumento que se contradice con
            # su propia linea de estado no puede acusar a nadie.
            "sin_fuente_primaria": bool(
                evaluacion and evaluacion["sin_fuente_primaria"]),
            "fuentes_primarias": (evaluacion["fuentes_primarias"]
                                  if evaluacion else []),
            "modelos": modelos or None,
            "llmCalls": llm.stats, "errors": llm.errors[:20],
            "ms": int((time.time() - t0) * 1000),
        },
        "encabezado": (fuentes.encabezado(urls, dom)
                       if (fuentes and dom) else ""),
    }


def main():
    ap = argparse.ArgumentParser(description="Flujo adversarial proponer/refutar (MAK)")
    ap.add_argument("tema")
    ap.add_argument("--orden", default="groq,cerebras,azure,ollama",
                    help="CSV: primero propone, ultimo juzga, resto refuta")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio")
    ap.add_argument("--sin-marco", action="store_true")
    ap.add_argument("--modelos", default="",
                    help="CSV de hasta 3: modelo del proponente, del refutador "
                         "y del juez. Solo lo respetan los proveedores que "
                         "eligen modelo (hoy watsonx). Un mismo modelo en dos "
                         "papeles no es un adversario.")
    ap.add_argument("--ntfy", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    load_env()
    # El filtro sale de `research_lib.PROVIDERS`, no de una lista escrita aca:
    # la copia a mano se quedo sin `watsonx` ni `win` y los descartaba en
    # silencio. Un nombre que no existe SI se descarta -- pero avisando, porque
    # un dedazo que deja la lista vacia terminaba en "Ultimo: None", un error
    # que no nombra a nadie porque nunca se intento nada.
    pedidos = [p.strip() for p in args.orden.split(",") if p.strip()]
    orden = [p for p in pedidos if p in PROVIDERS]
    desconocidos = [p for p in pedidos if p not in PROVIDERS]
    if desconocidos:
        print("AVISO: proveedor desconocido, lo salteo: %s (validos: %s)"
              % (", ".join(desconocidos), ", ".join(PROVIDERS)), flush=True)
    if not orden:
        print("AVISO: --orden quedo vacio, uso la cadena por defecto",
              flush=True)
    ms = [m.strip() for m in args.modelos.split(",") if m.strip()]
    modelos = {}
    for papel, i in (("proponente", 0), ("refutador", 1), ("juez", 2)):
        if len(ms) > i:
            modelos[papel] = ms[i]
    # El tema viaja CRUDO: el encuadre se le da al modelo dentro de refutar().
    result = refutar(args.tema, orden or list(PROVIDERS), args.densidad,
                     marco_activo=not args.sin_marco, modelos=modelos)

    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, "%s-%s" % (stamp(), slug(args.tema)))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Adversarial: %s\n\n%s%s\n\n---\n\n## Tesis (%s)\n\n%s\n\n"
                "## Refutaciones\n\n"
                % (args.tema, result["encabezado"], result["veredicto"],
                   result["tesis"]["proveedor"], result["tesis"]["texto"]))
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
