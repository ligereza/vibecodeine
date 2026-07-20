#!/usr/bin/env python3
"""research.py -- runner standalone de investigacion cultural (MAK, sin n8n).

Puerto fiel del loop probado end-to-end 2026-07-15 (Code node n8n +
harness): SEARCH (Tavily) -> FETCH -> ANALYZE (LLM fallback) -> DECIDE
-> INFORME. Salida: ~/research/informes/STAMP-slug.{md,json}.

Pausa-en-error (ver pausa.py): si el LLM se queda sin proveedores (o
Tavily falla duro), en vez de morir o degradar el informe se guarda un
checkpoint recuperable en ~/research/checkpoints/<job_id>.json, se
imprime "PAUSADO: <path> | <motivo>" y se sale con codigo 3. Un humano
decide con pausa.aplicar_accion() (reintentar/editar/saltar) y se
reanuda con --resume <path>.

Uso:
    python3 research.py "tema" [--iteraciones 3] [--depth basic|advanced]
                        [--providers groq,cerebras,azure,ollama]
                        [--sin-marco] [--ntfy]
    python3 research.py --resume ~/research/checkpoints/<job_id>.json
"""
import argparse
import json
import os
import sys
import time

import pausa
from research_lib import (LLM, escala_tok, fetch_url, load_env, marco,
                         ntfy_publish, slug, stamp, tavily_search, web_search)

OUT_DIR = os.path.expanduser("~/research/informes")


def _pausar(topic, iteraciones, depth, providers, densidad, sin_marco,
           i, current, query_history, seen_urls, findings, fase, motivo):
    """Arma el checkpoint, lo guarda, imprime la marca PAUSADO y sale con
    codigo 3. job_id se calcula recien aca (lazy): MAK_JOB_ID si worker.py
    lo seteo en el entorno del subproceso, o slug(topic)+stamp() en modo
    standalone."""
    job_id = os.environ.get("MAK_JOB_ID") or (slug(topic) + "-" + stamp())
    checkpoint = {
        "job_id": job_id,
        "modo": "research",
        "tema": topic,
        "params": {
            "iteraciones": iteraciones,
            "depth": depth,
            "providers": providers,
            "densidad": densidad,
            "sin_marco": sin_marco,
        },
        "i": i,
        "current": current,
        "query_history": query_history,
        "seen_urls": list(seen_urls),
        "findings": findings,
        "fase_fallida": fase,
        "motivo": str(motivo),
        "saltar": False,
        "ts": int(time.time()),
    }
    path = pausa.guardar_checkpoint(checkpoint)
    print(pausa.formatear_marca(path, motivo), flush=True)
    sys.exit(3)


def _armar_resultado(topic, report, t0, findings, query_history, sources, llm):
    _primer_parrafo = next((ln.strip() for ln in report.splitlines()
                           if ln.strip() and not ln.strip().startswith("#")), "")
    print("HALLAZGO: " + _primer_parrafo[:140], flush=True)
    return {
        "topic": topic,
        "report": report,
        "meta": {
            "iterations": len(query_history),
            "queries": query_history,
            "findingsCount": len(findings),
            "sources": sources,
            "llmCalls": llm.stats,
            "providerOrder": llm.order,
            "errors": llm.errors[:20],
            "ms": int((time.time() - t0) * 1000),
        },
        "findings": findings,
    }


def investigar(topic, iteraciones=3, depth="basic",
               providers="groq,cerebras,azure,ollama", densidad="medio",
               sin_marco=False, reanudar=None):
    t0 = time.time()
    llm = LLM(providers)
    iteraciones = min(max(iteraciones, 1), 10)

    saltar_informe = False
    if reanudar:
        findings = list(reanudar.get("findings") or [])
        query_history = list(reanudar.get("query_history") or [])
        seen_urls = set(reanudar.get("seen_urls") or [])
        current = reanudar.get("current", topic)
        fase_previa = reanudar.get("fase_fallida")
        i_inicio = int(reanudar.get("i", 0))
        if fase_previa == "informe":
            # el loop de iteraciones ya habia terminado; solo falta el informe
            i_inicio = iteraciones
            if reanudar.get("saltar"):
                saltar_informe = True
        elif reanudar.get("saltar"):
            # "fuentes"/"decidir": saltar esta iteracion, seguir con la que sigue
            i_inicio += 1
    else:
        findings = []
        query_history = []
        seen_urls = set()
        current = topic
        i_inicio = 0

    def pausar(i_actual, fase, motivo):
        _pausar(topic, iteraciones, depth, providers, densidad, sin_marco,
               i_actual, current, query_history, seen_urls, findings,
               fase, motivo)

    for i in range(i_inicio, iteraciones):
        print(f"STATUS: Buscando iteracion {i + 1}/{iteraciones}: {current[:50]}...", flush=True)
        # al reanudar AT i (reintentar/editar), current ya quedo en
        # query_history por el intento que fallo -- no duplicarlo.
        if not (reanudar and i == i_inicio and query_history
               and query_history[-1] == current):
            query_history.append(current)

        try:
            search = web_search(current, depth, errors=llm.errors)
        except Exception as e:  # noqa: BLE001 - blindaje si tavily llega a raise
            pausar(i, "fuentes", "tavily_search: %s" % e)

        if search.get("answer"):
            findings.append({"type": "tavily_answer", "iteration": i + 1,
                             "query": current, "content": search["answer"]})

        fresh = [r for r in (search.get("results") or [])
                 if r.get("url") and r["url"] not in seen_urls][:3]
        for idx, r in enumerate(fresh):
            print(f"STATUS: Analizando fuente {idx + 1}/{len(fresh)} (iteracion {i + 1})", flush=True)
            seen_urls.add(r["url"])
            raw = fetch_url(r["url"])
            content = raw if len(raw) > 200 else (r.get("content") or raw)
            if not content:
                continue
            try:
                analysis, _ = llm.call(
                    "Eres un asistente de investigacion. Analizas contenido web "
                    "y devuelves SOLO JSON valido, sin markdown ni texto extra.",
                    'Tema: "%s"\nTITULO: %s\nURL: %s\n\nCONTENIDO:\n%s\n\n'
                    'Devuelve JSON: {"key_facts":["..."],"relevance":'
                    '"alta|media|baja","summary":"2-3 frases","new_angles":["..."]}'
                    % (topic, r.get("title", ""), r["url"], content),
                    escala_tok(900, densidad),
                )
            except RuntimeError as e:
                pausar(i, "fuentes", str(e))
            try:
                parsed = json.loads(
                    analysis.replace("```json", "").replace("```", "").strip())
            except ValueError:
                parsed = {"raw_analysis": analysis[:1500]}
            findings.append({"type": "web_analysis", "iteration": i + 1,
                             "query": current, "title": r.get("title"),
                             "url": r["url"], "analysis": parsed})
            print(f"HALLAZGO: {r.get('title') or r['url']}", flush=True)

        if i == iteraciones - 1:
            break  # ultima vuelta: no gastar la llamada DECIDIR

        try:
            decision, _ = llm.call(
                None,
                'Eres agente de investigacion. Tema: "%s". Iteracion %d/%d.\n'
                "Hallazgos recientes:\n%s\n\n"
                'Si la informacion ya cubre el tema responde EXACTAMENTE '
                '"FINALIZAR: <razon breve>". Si falta, responde EXACTAMENTE '
                '"CONTINUAR: <nueva consulta concreta>". '
                "No repitas estas consultas ya hechas: %s"
                % (topic, i + 1, iteraciones,
                   json.dumps(findings[-5:], ensure_ascii=False)[:6000],
                   " | ".join(query_history)),
                escala_tok(300, densidad),
            )
        except RuntimeError as e:
            pausar(i, "decidir", str(e))
        if decision.strip().upper().startswith("FINALIZAR"):
            break
        nxt = ""
        low = decision.lower()
        if "continuar" in low:
            nxt = decision[low.index("continuar") + len("continuar"):]
            nxt = nxt.lstrip(": ").strip().strip('"\'')
        if not nxt or any(q.lower() == nxt.lower() for q in query_history):
            nxt = "%s (angulo %d)" % (topic, i + 2)
        current = nxt[:300]

    sources = list(dict.fromkeys(f["url"] for f in findings if f.get("url")))

    if saltar_informe:
        report = ("[Informe omitido por accion humana: saltar] La fase de "
                  "generacion de informe fue saltada tras una pausa; ver "
                  "findings crudos para el detalle recolectado.")
        return _armar_resultado(topic, report, t0, findings, query_history,
                                sources, llm)

    print("STATUS: Generando informe final...", flush=True)
    try:
        report, _ = llm.call(
            "Eres un investigador senior. Redactas informes claros en "
            "espanol correcto (con tildes), en formato Markdown.",
            "Genera un informe con secciones: 1. RESUMEN EJECUTIVO, "
            "2. HALLAZGOS PRINCIPALES (cita fuente URL), 3. ANALISIS "
            "CRITICO, 4. LAGUNAS DE INFORMACION, 5. PROXIMOS PASOS.\n\n"
            'TEMA: "%s"\n\nHALLAZGOS:\n%s\n\nFUENTES:\n%s'
            % (topic, json.dumps(findings, ensure_ascii=False, indent=1)[:14000],
               "\n".join(sources)),
            escala_tok(2000, densidad),
        )
    except RuntimeError as e:
        pausar(iteraciones, "informe", str(e))

    return _armar_resultado(topic, report, t0, findings, query_history,
                            sources, llm)


def main():
    ap = argparse.ArgumentParser(description="Research cultural standalone (MAK)")
    ap.add_argument("tema", nargs="?", help="tema a investigar (opcional con --resume)")
    ap.add_argument("--iteraciones", type=int, default=2)  # frugal: mas es opt-in
    ap.add_argument("--depth", choices=("basic", "advanced"), default="basic")
    ap.add_argument("--providers", default="groq,cerebras,azure,ollama")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio",
                    help="escala tokens por llamada; techo duro anti-timeout")
    ap.add_argument("--sin-marco", action="store_true",
                    help="sin el marco cultural descriptivo")
    ap.add_argument("--ntfy", action="store_true",
                    help="notificar a NTFY_TOPIC_OUT al terminar")
    ap.add_argument("--out", default=OUT_DIR)
    ap.add_argument("--resume", default=None,
                    help="reanudar desde un checkpoint pausado (ver pausa.py)")
    args = ap.parse_args()

    load_env()

    if args.resume:
        ck = pausa.cargar_checkpoint(args.resume)
        os.environ["MAK_JOB_ID"] = ck["job_id"]
        params = ck.get("params") or {}
        topic = ck["tema"]
        tema_para_slug = topic
        result = investigar(
            topic,
            params.get("iteraciones", args.iteraciones),
            params.get("depth", args.depth),
            params.get("providers", args.providers),
            params.get("densidad", args.densidad),
            sin_marco=params.get("sin_marco", args.sin_marco),
            reanudar=ck,
        )
    elif args.tema:
        topic = marco(args.tema, activo=not args.sin_marco)
        tema_para_slug = args.tema
        result = investigar(topic, args.iteraciones, args.depth, args.providers,
                            args.densidad, sin_marco=args.sin_marco)
    else:
        ap.error("tema requerido (o usar --resume <checkpoint>)")
        return 2

    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, "%s-%s" % (stamp(), slug(tema_para_slug)))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# %s\n\n%s\n\n---\nmeta: %s\n"
                % (tema_para_slug, result["report"],
                   json.dumps(result["meta"], ensure_ascii=False)))

    m = result["meta"]
    print("informe: %d iteraciones, %d findings, %d fuentes, %d ms, llm=%s"
          % (m["iterations"], m["findingsCount"], len(m["sources"]), m["ms"],
             m["llmCalls"]))
    if m["errors"]:
        print("errores no fatales: %d (ver meta en el .json)" % len(m["errors"]))
    if args.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     result["report"][:900] + "\n\n" + base + ".md",
                     title="informe listo: " + tema_para_slug[:80])
    print("INFORME: " + base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
