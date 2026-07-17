#!/usr/bin/env python3
"""correlacionar_archivos.py -- correlacion semantica SOBRE los productos.

El reframe: el repo/sistema es pagina (server) + acciones (modelos) +
productos (archivos) + CORRELACION sobre esos archivos. Este script es
esa ultima capa: lee los informes/paneles/cadenas/refutaciones ya
generados y produce un mapa de correlacion entre ellos (que temas se
tocan, que se repite, que hilos culturales emergen del cuerpo de trabajo
acumulado). Es el "departamento de research" mirando su propio archivo.

Salida: ~/research/correlaciones/STAMP-corpus.{md,json}.

Uso:
    python3 correlacionar_archivos.py [--dirs informes,paneles,cadenas]
                                      [--limite 20] [--densidad medio] [--ntfy]
"""
import argparse
import json
import os
import sys
import time

from research_lib import (LLM, MODELO_CAPAZ, escala_tok, load_env,
                          ntfy_publish, stamp)

BASE = os.path.expanduser("~/research")
OUT_DIR = os.path.join(BASE, "correlaciones")
DIRS = {"informes": "informes", "paneles": "paneles",
        "cadenas": "cadenas", "refutaciones": "refutaciones"}


def _resumen_de(path):
    """Extrae tema + primer bloque de texto util de un .json producto."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    tema = d.get("tema") or d.get("topic") or os.path.basename(path)
    cuerpo = (d.get("report") or d.get("sintesis") or d.get("veredicto")
              or d.get("correlacion") or "")
    if not cuerpo and d.get("pasos"):
        cuerpo = d["pasos"][-1].get("texto", "")
    return {"tema": tema, "extracto": cuerpo[:1200],
            "archivo": os.path.basename(path)}


def recopilar(dirs, limite):
    productos = []
    for d in dirs:
        carpeta = os.path.join(BASE, DIRS.get(d, d))
        try:
            jsons = sorted((f for f in os.listdir(carpeta)
                           if f.endswith(".json")), reverse=True)
        except OSError:
            continue
        for fn in jsons[:limite]:
            r = _resumen_de(os.path.join(carpeta, fn))
            if r:
                r["categoria"] = d
                productos.append(r)
    return productos


def correlacionar_corpus(productos, densidad="medio"):
    t0 = time.time()
    llm = LLM()
    cuerpo = "\n\n".join(
        "[%s | %s] %s\n%s"
        % (p["categoria"], p["archivo"], p["tema"], p["extracto"])
        for p in productos)
    orden = [MODELO_CAPAZ] + [x for x in llm.order if x != MODELO_CAPAZ]
    mapa, real = llm.call(
        "Eres el coordinador de un departamento de investigacion cultural "
        "revisando TODO el archivo acumulado de investigaciones. Espanol "
        "correcto con tildes, formato Markdown. NO inventas: correlacionas "
        "lo que ya existe en los productos.",
        "PRODUCTOS DE INVESTIGACION ACUMULADOS (%d):\n\n%s\n\n"
        "Produce un MAPA DE CORRELACION DEL CORPUS con: 1. TEMAS "
        "RECURRENTES (que vuelve una y otra vez), 2. CLUSTERES (agrupa los "
        "productos por afinidad tematica, nombra cada cluster), 3. HILOS "
        "CULTURALES EMERGENTES (que narrativa mayor conecta piezas "
        "distintas), 4. HUECOS DEL CORPUS (que falta investigar), "
        "5. LINEAS SUGERIDAS (proximos temas que el archivo pide)."
        % (len(productos), cuerpo[:22000]),
        escala_tok(2000, densidad), order=orden)
    return {
        "productos": [{"categoria": p["categoria"], "archivo": p["archivo"],
                       "tema": p["tema"]} for p in productos],
        "mapa": mapa,
        "meta": {"n_productos": len(productos), "correlacionador": real,
                 "llmCalls": llm.stats, "errors": llm.errors[:20],
                 "ms": int((time.time() - t0) * 1000)},
    }


def main():
    ap = argparse.ArgumentParser(description="Correlacion semantica del corpus (MAK)")
    ap.add_argument("--dirs", default="informes,paneles,cadenas,refutaciones")
    ap.add_argument("--limite", type=int, default=15,
                    help="max productos por categoria")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio")
    ap.add_argument("--ntfy", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    load_env()
    dirs = [d.strip() for d in args.dirs.split(",") if d.strip() in DIRS]
    print("STATUS: Recopilando productos del archivo...", flush=True)
    productos = recopilar(dirs or list(DIRS), args.limite)
    if not productos:
        print("Sin productos que correlacionar.")
        print("INFORME: (ninguno)")
        return 0

    print("STATUS: Correlacionando corpus (%d productos)..." % len(productos),
          flush=True)
    result = correlacionar_corpus(productos, args.densidad)

    os.makedirs(args.out, exist_ok=True)
    base = os.path.join(args.out, "%s-corpus" % stamp())
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Correlacion del corpus (%d productos)\n\n%s\n\n---\n\n"
                "## Productos incluidos\n\n"
                % (result["meta"]["n_productos"], result["mapa"]))
        for p in result["productos"]:
            f.write("- [%s] %s (`%s`)\n"
                    % (p["categoria"], p["tema"], p["archivo"]))
        f.write("\n---\nmeta: %s\n"
                % json.dumps(result["meta"], ensure_ascii=False))

    m = result["meta"]
    print("corpus: %d productos, llm=%s, %d ms"
          % (m["n_productos"], m["llmCalls"], m["ms"]))
    if args.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     result["mapa"][:900] + "\n\n" + base + ".md",
                     title="correlacion corpus lista")
    print("INFORME: " + base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
