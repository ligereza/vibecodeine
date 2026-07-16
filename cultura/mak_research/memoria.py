#!/usr/bin/env python3
"""memoria.py -- memoria del departamento de research (RAG local, MAK).

El departamento deja de ser una carpeta de informes sueltos: indexa TODO lo
que ya produjo (embeddings locales con ollama nomic-embed-text, gratis) y
puede CONSULTAR lo que ya sabe antes de investigar de nuevo. Escala mejor
que el modo Corpus (que relee el archivo entero y choca con el tope de
tokens): aca solo recupera los fragmentos relevantes.

Dos usos:
  - index:     python3 memoria.py index [--rebuild]
  - consultar: python3 memoria.py "tema" [--densidad ..] [--k N] [--ntfy]
               (que sabe el departamento de X + vacios + que investigar)
  - buscar:    python3 memoria.py buscar "tema" [--k N]   (solo recupera)

Tambien exporta contexto(tema) para INYECTAR memoria en otros modos
(grafo.py --memoria). Stdlib-only (via research_lib), Python 3.11.
"""
import argparse
import json
import math
import os
import sys
import time

from research_lib import (LLM, MODELO_CAPAZ, _http_json, escala_tok, load_env,
                          marco, ntfy_publish, slug, stamp)

RESEARCH = os.path.expanduser("~/research")
MEM_DIR = os.path.join(RESEARCH, "memoria")
INDEX_FILE = os.path.join(MEM_DIR, "index.jsonl")
# carpetas de productos a indexar (los .md legibles)
FUENTES = ("informes", "paneles", "cadenas", "refutaciones",
           "correlaciones", "grafos")
EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

CHUNK = 900      # chars por fragmento
SOLAPE = 150     # overlap entre fragmentos


def _embed(texto):
    """Vector de un texto via ollama (local, gratis). [] si falla."""
    try:
        r = _http_json(OLLAMA.rstrip("/") + "/api/embeddings",
                       {"model": EMBED_MODEL, "prompt": texto[:8000]},
                       timeout=60)
        return r.get("embedding") or []
    except Exception:  # noqa: BLE001 - un embed fallido no mata el index
        return []


def _titulo(texto, path):
    for line in texto.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()[:120]
    return os.path.basename(path)


def _fragmentar(texto):
    """Parte por parrafos y arma fragmentos de ~CHUNK chars con solape."""
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    chunks, buf = [], ""
    for p in parrafos:
        if len(buf) + len(p) + 2 <= CHUNK:
            buf = (buf + "\n\n" + p) if buf else p
        else:
            if buf:
                chunks.append(buf)
            if len(p) <= CHUNK:
                buf = p
            else:
                for i in range(0, len(p), CHUNK - SOLAPE):
                    chunks.append(p[i:i + CHUNK])
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks or ([texto[:CHUNK]] if texto.strip() else [])


def _cargar_index():
    entradas = []
    try:
        with open(INDEX_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entradas.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except OSError:
        pass
    return entradas


def _guardar_index(entradas):
    os.makedirs(MEM_DIR, exist_ok=True)
    tmp = INDEX_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for e in entradas:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    os.replace(tmp, INDEX_FILE)


def indexar(rebuild=False, log=lambda s: None):
    """Indexa los .md de las carpetas de productos. Incremental: salta los
    archivos ya indexados con el mismo mtime; re-indexa los que cambiaron.
    Devuelve {archivos, chunks, nuevos}."""
    load_env()
    previas = [] if rebuild else _cargar_index()
    # (path -> mtime) ya indexado
    indexado = {}
    for e in previas:
        indexado.setdefault(e["path"], e.get("mtime"))

    vigentes = []   # entradas que sobreviven (archivo sin cambios)
    archivos_actuales = set()
    pendientes = []  # (path, dir, mtime, texto) a re-embeddear

    for d in FUENTES:
        carpeta = os.path.join(RESEARCH, d)
        try:
            nombres = os.listdir(carpeta)
        except OSError:
            continue
        for nombre in nombres:
            if not nombre.endswith(".md"):
                continue
            path = os.path.join(carpeta, nombre)
            try:
                mtime = int(os.path.getmtime(path))
            except OSError:
                continue
            archivos_actuales.add(path)
            if not rebuild and indexado.get(path) == mtime:
                continue  # ya indexado y sin cambios -> se reusa
            try:
                with open(path, encoding="utf-8") as f:
                    texto = f.read()
            except OSError:
                continue
            pendientes.append((path, d, mtime, texto))

    # conservar entradas de archivos sin cambios y que aun existen
    cambiados = {p for p, _, _, _ in pendientes}
    for e in previas:
        if e["path"] in archivos_actuales and e["path"] not in cambiados:
            vigentes.append(e)

    nuevas = []
    for path, d, mtime, texto in pendientes:
        titulo = _titulo(texto, path)
        chunks = _fragmentar(texto)
        log("STATUS: Indexando %s (%d frag)..." % (os.path.basename(path), len(chunks)))
        for i, ch in enumerate(chunks):
            vec = _embed(ch)
            if not vec:
                continue
            nuevas.append({"path": path, "dir": d, "titulo": titulo,
                           "mtime": mtime, "i": i, "chunk": ch, "vec": vec})

    todas = vigentes + nuevas
    _guardar_index(todas)
    return {"archivos": len(archivos_actuales), "chunks": len(todas),
            "nuevos": len(nuevas)}


def _cos(a, b):
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return -1.0
    return dot / (na * nb)


def buscar(tema, k=5):
    """Top-k productos previos mas relevantes al tema (mejor chunk por
    archivo). Devuelve [{path, dir, titulo, score, chunk}]."""
    entradas = _cargar_index()
    if not entradas:
        return []
    q = _embed(tema)
    if not q:
        return []
    mejor = {}   # path -> (score, entrada)
    for e in entradas:
        s = _cos(q, e.get("vec"))
        if e["path"] not in mejor or s > mejor[e["path"]][0]:
            mejor[e["path"]] = (s, e)
    rank = sorted(mejor.values(), key=lambda t: t[0], reverse=True)[:k]
    return [{"path": e["path"], "dir": e["dir"], "titulo": e["titulo"],
             "score": round(s, 3), "chunk": e["chunk"]} for s, e in rank]


def contexto(tema, k=5, max_chars=2500):
    """Bloque Markdown con los hallazgos previos relevantes, para INYECTAR
    en otro modo (grafo --memoria). '' si la memoria esta vacia."""
    hits = buscar(tema, k)
    if not hits:
        return ""
    partes, total = [], 0
    for h in hits:
        frag = h["chunk"].strip()
        if total + len(frag) > max_chars:
            frag = frag[:max(0, max_chars - total)]
        partes.append("- [%s | %s]: %s" % (h["titulo"], h["dir"], frag))
        total += len(frag)
        if total >= max_chars:
            break
    return ("MEMORIA DEL DEPARTAMENTO (hallazgos previos relevantes, "
            "usalos como base, no los repitas literalmente):\n"
            + "\n".join(partes))


def consultar(tema, k=6, densidad="medio"):
    """Modo Memoria: recupera lo que el departamento ya sabe del tema y el
    modelo capaz lo sintetiza (que sabemos / consenso / contradicciones /
    vacios / que investigar). NO inventa: se apoya en los productos previos."""
    t0 = time.time()
    load_env()
    llm = LLM()
    hits = buscar(tema, k)
    if not hits:
        return {"tema": tema, "sintesis": "", "fuentes": [],
                "meta": {"vacio": True, "ms": int((time.time() - t0) * 1000)}}
    cuerpo = "\n\n".join(
        "[%s | %s | score %.2f]: %s"
        % (h["titulo"], h["dir"], h["score"], h["chunk"][:1400])
        for h in hits)
    orden = [MODELO_CAPAZ] + [x for x in llm.order if x != MODELO_CAPAZ]
    print("STATUS: Sintetizando memoria (%d fuentes)..." % len(hits), flush=True)
    try:
        sintesis, real = llm.call(
            "Eres el archivista del departamento de investigacion cultural. "
            "NO inventas: sintetizas lo que el departamento YA produjo. "
            "Espanol correcto con tildes, Markdown.",
            'TEMA CONSULTADO: "%s"\n\nHALLAZGOS PREVIOS DEL ARCHIVO:\n%s\n\n'
            "Produce: 1. QUE SABEMOS YA (sintesis de lo previo, cita el "
            "titulo de la fuente), 2. CONSENSO (lo repetido/solido), "
            "3. CONTRADICCIONES entre productos, 4. VACIOS (que no cubre el "
            "archivo todavia), 5. QUE INVESTIGAR PROXIMO (3-5 preguntas "
            "concretas que llenarian los vacios)." % (tema, cuerpo),
            escala_tok(1300, densidad), order=orden)
    except RuntimeError as e:
        sintesis, real = "[sintesis fallo: %s]" % e, None
    return {
        "tema": tema, "sintesis": sintesis,
        "fuentes": [{"titulo": h["titulo"], "dir": h["dir"],
                     "score": h["score"], "path": os.path.basename(h["path"])}
                    for h in hits],
        "meta": {"n_fuentes": len(hits), "proveedor": real,
                 "llmCalls": llm.stats, "errors": llm.errors[:10],
                 "ms": int((time.time() - t0) * 1000)},
    }


def _escribir(tema_raw, result):
    os.makedirs(MEM_DIR, exist_ok=True)
    base = os.path.join(MEM_DIR, "%s-%s" % (stamp(), slug(tema_raw)))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write("# Memoria: %s\n\n" % tema_raw)
        f.write((result.get("sintesis") or "(sin hallazgos previos)") + "\n\n")
        if result.get("fuentes"):
            f.write("---\n## Fuentes consultadas\n\n")
            for s in result["fuentes"]:
                f.write("- %s (%s, score %.2f) -- %s\n"
                        % (s["titulo"], s["dir"], s["score"], s["path"]))
    return base


def main():
    ap = argparse.ArgumentParser(description="Memoria del departamento (RAG local)")
    ap.add_argument("cmd", help="'index', 'buscar', o el TEMA a consultar")
    ap.add_argument("tema", nargs="?", default="")
    ap.add_argument("--rebuild", action="store_true", help="re-indexa todo")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"), default="medio")
    ap.add_argument("--sin-marco", action="store_true")
    ap.add_argument("--ntfy", action="store_true")
    args = ap.parse_args()
    load_env()

    if args.cmd == "index":
        stats = indexar(rebuild=args.rebuild, log=lambda s: print(s, flush=True))
        print("index: %d archivos, %d chunks (%d nuevos)"
              % (stats["archivos"], stats["chunks"], stats["nuevos"]))
        return 0

    if args.cmd == "buscar":
        tema = args.tema or ""
        if not tema:
            print("falta el tema"); return 2
        for h in buscar(tema, args.k):
            print("%.3f  [%s] %s" % (h["score"], h["dir"], h["titulo"]))
        return 0

    # default: consultar (cmd ES el tema). Auto-indexa incremental antes.
    tema_raw = args.cmd
    print("STATUS: Refrescando memoria...", flush=True)
    indexar(log=lambda s: print(s, flush=True))
    tema = marco(tema_raw, activo=not args.sin_marco)
    result = consultar(tema, args.k, args.densidad)
    if result["meta"].get("vacio"):
        print("La memoria esta vacia (no hay productos indexados aun).")
        print("INFORME: (ninguno)")
        return 0
    base = _escribir(tema_raw, result)
    m = result["meta"]
    print("memoria: %d fuentes, llm=%s, %d ms" % (m["n_fuentes"], m["llmCalls"], m["ms"]))
    if args.ntfy:
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     (result["sintesis"] or "")[:900] + "\n\n" + base + ".md",
                     title="memoria: " + tema_raw[:80])
    print("INFORME: " + base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
