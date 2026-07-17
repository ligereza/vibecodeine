#!/usr/bin/env python3
"""panel.py -- debate academico multi-modelo sobre un tema X (MAK, sin n8n).

4 busquedas Tavily en paralelo (angulos historico / estetico / legal /
tecnico), 4 panelistas = 4 modelos distintos (uno por API disponible),
N rondas de replica cruzada, sintesis final con gpt-5-mini.
Salida: ~/research/paneles/STAMP-slug.{md,json}.

Uso:
    python3 panel.py "tema" [--replicas 2] [--sin-marco] [--ntfy]
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from research_lib import (LLM, correlacionar, escala_tok, load_env, marco,
                          ntfy_publish, slug, stamp, tavily_search)

OUT_DIR = os.path.expanduser("~/research/paneles")

# Un panelista por API: si su proveedor cae, el fallback general responde
# igual y meta registra quien hablo de verdad.
PANEL = [
    {"angulo": "historico", "proveedor": "groq",
     "query": "{tema} historia origen contexto cultural",
     "lente": "historiador cultural: origenes, genealogia, transmision, "
              "rupturas y continuidades"},
    {"angulo": "estetico", "proveedor": "ollama",
     "query": "{tema} estetica arte representacion simbolica",
     "lente": "critico de arte: forma, simbolo, iconografia, como se "
              "representa y que estetica genera"},
    {"angulo": "legal", "proveedor": "azure",
     "query": "{tema} regulacion legal derecho politica publica",
     "lente": "analista juridico: marcos regulatorios, jurisprudencia, "
              "tensiones entre norma y practica cultural"},
    {"angulo": "tecnico", "proveedor": "cerebras",
     "query": "{tema} funcionamiento tecnico investigacion cientifica",
     "lente": "investigador tecnico-cientifico: mecanismos, evidencia, "
              "estado del arte academico"},
]

SISTEMA_PANELISTA = (
    "Eres panelista academico ({lente}). Escribes en espanol correcto con "
    "tildes. Capa DESCRIPTIVA y cultural unicamente: nada operativo, nada "
    "de instrucciones de sintesis ni cultivo, jamas perfilar personas "
    "reales. Cita las URLs de tus fuentes. Se concreto y con postura."
)


def _contexto(res):
    lines = []
    if res.get("answer"):
        lines.append("RESPUESTA AGREGADA: " + res["answer"])
    for r in (res.get("results") or [])[:5]:
        lines.append("- %s | %s\n  %s"
                     % (r.get("title", ""), r.get("url", ""),
                        (r.get("content") or "")[:500]))
    return "\n".join(lines) or "(sin resultados de busqueda)"


def debatir(tema, replicas=2, densidad="medio"):
    t0 = time.time()
    llm = LLM()
    habla = {}  # angulo -> lista de (proveedor_real, texto)

    # 1. Busquedas en paralelo, un angulo cada una (4 creditos Tavily).
    print("STATUS: Buscando contextos en paralelo (4 angulos)...", flush=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        busq = list(ex.map(
            lambda p: tavily_search(p["query"].format(tema=tema),
                                    errors=llm.errors), PANEL))
    contextos = {p["angulo"]: _contexto(b) for p, b in zip(PANEL, busq)}
    fuentes = list(dict.fromkeys(
        r["url"] for b in busq for r in (b.get("results") or [])
        if r.get("url")))

    def posicion(p):
        orden = [p["proveedor"]] + [x for x in llm.order
                                    if x != p["proveedor"]]
        texto, real = llm.call(
            SISTEMA_PANELISTA.format(lente=p["lente"]),
            'TEMA DEL PANEL: "%s"\n\nTu angulo: %s.\n\nFUENTES DE TU '
            "BUSQUEDA:\n%s\n\nEscribe tu POSICION inicial (350-450 "
            "palabras): tesis clara, 3-4 argumentos con fuente, y una "
            "pregunta abierta para los otros panelistas."
            % (tema, p["angulo"], contextos[p["angulo"]]),
            escala_tok(900, densidad), order=orden)
        return p["angulo"], real, texto

    # 2. Posiciones iniciales en paralelo (ollama local va lento; los
    #    otros 3 son API remota, el pool los solapa).
    print("STATUS: Redactando posiciones iniciales...", flush=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        for angulo, real, texto in ex.map(posicion, PANEL):
            habla[angulo] = [(real, texto)]

    # 3. Rondas de replica: cada panelista lee la ultima intervencion de
    #    los otros tres y replica.
    for ronda in range(1, replicas + 1):
        print(f"STATUS: Ronda de replica {ronda}/{replicas}...", flush=True)
        def replica(p, _ronda=ronda):
            otros = "\n\n".join(
                "[%s dijo]:\n%s" % (a, habla[a][-1][1][:1800])
                for a in habla if a != p["angulo"])
            orden = [p["proveedor"]] + [x for x in llm.order
                                        if x != p["proveedor"]]
            texto, real = llm.call(
                SISTEMA_PANELISTA.format(lente=p["lente"]),
                'TEMA: "%s". Ronda de replica %d. Tu posicion previa:\n%s\n\n'
                "LO QUE DIJERON LOS OTROS PANELISTAS:\n%s\n\nEscribe tu "
                "REPLICA (200-300 palabras): en que coincides, en que "
                "discrepas y que matiz aporta tu angulo %s."
                % (tema, _ronda, habla[p["angulo"]][-1][1][:1500], otros,
                   p["angulo"]),
                escala_tok(600, densidad), order=orden)
            return p["angulo"], real, texto

        with ThreadPoolExecutor(max_workers=4) as ex:
            for angulo, real, texto in ex.map(replica, PANEL):
                habla[angulo].append((real, texto))

    # 4. Sintesis final: gpt-5-mini primero en la cadena.
    print("STATUS: Sintetizando panel...", flush=True)
    transcripcion = "\n\n".join(
        "### Angulo %s (%s)\n\n%s" % (
            a, ", ".join(r for r, _ in habla[a]),
            "\n\n".join("**Intervencion %d:**\n%s" % (i + 1, t)
                        for i, (_, t) in enumerate(habla[a])))
        for a in habla)
    sintesis, sintetizador = llm.call(
        "Eres el moderador senior de un panel academico. Redactas en "
        "espanol correcto con tildes, formato Markdown.",
        'Sintetiza este debate sobre "%s" en un informe con secciones: '
        "1. RESUMEN, 2. POSICIONES POR ANGULO (historico/estetico/legal/"
        "tecnico), 3. ACUERDOS, 4. DESACUERDOS Y TENSIONES, 5. PREGUNTAS "
        "ABIERTAS, 6. FUENTES CITADAS.\n\nTRANSCRIPCION:\n%s\n\nFUENTES "
        "DE BUSQUEDA:\n%s"
        % (tema, transcripcion[:24000], "\n".join(fuentes)),
        escala_tok(2200, densidad), order=["azure", "groq", "cerebras", "ollama"])

    # 5. Correlacion semantica: el modelo capaz ordena/relaciona lo que
    #    dijo cada modelo (hilo comun, convergencias, tensiones, vacios).
    print("STATUS: Correlacionando (departamento research)...", flush=True)
    piezas = [{"modelo": "%s/%s" % (a, r), "texto": t}
              for a in habla for r, t in habla[a]]
    correlacion, _ = correlacionar(llm, tema, piezas, densidad)

    return {
        "tema": tema,
        "sintesis": sintesis,
        "correlacion": correlacion,
        "transcripcion": {a: [{"modelo": r, "texto": t} for r, t in habla[a]]
                          for a in habla},
        "meta": {
            "replicas": replicas,
            "sintetizador": sintetizador,
            "fuentes": fuentes,
            "llmCalls": llm.stats,
            "errors": llm.errors[:20],
            "ms": int((time.time() - t0) * 1000),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Panel academico 4 modelos (MAK)")
    ap.add_argument("tema")
    ap.add_argument("--replicas", type=int, default=1)  # frugal: mas es opt-in
    ap.add_argument("--sin-marco", action="store_true")
    ap.add_argument("--ntfy", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    load_env()
    tema = marco(args.tema, activo=not args.sin_marco)
    result = debatir(tema, replicas=max(0, min(args.replicas, 4)))

    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, "%s-%s" % (stamp(), slug(args.tema)))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Panel: %s\n\n%s\n\n" % (args.tema, result["sintesis"]))
        if result.get("correlacion"):
            f.write("---\n\n## Correlacion semantica (departamento research)\n\n%s\n\n"
                    % result["correlacion"])
        f.write("---\n\n## Transcripcion\n\n")
        for a, turnos in result["transcripcion"].items():
            f.write("### %s\n\n" % a)
            for i, t in enumerate(turnos):
                f.write("**%d (%s):** %s\n\n" % (i + 1, t["modelo"], t["texto"]))
        f.write("---\nmeta: %s\n"
                % json.dumps(result["meta"], ensure_ascii=False))

    m = result["meta"]
    print("panel: %d fuentes, llm=%s, %d ms, sintesis=%s"
          % (len(m["fuentes"]), m["llmCalls"], m["ms"], m["sintetizador"]))
    if m["errors"]:
        print("errores no fatales: %d" % len(m["errors"]))
    if args.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     result["sintesis"][:900] + "\n\n" + base + ".md",
                     title="panel listo: " + args.tema[:80])
    print("INFORME: " + base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
