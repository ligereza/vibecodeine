"""Extractor de contexto de transcripciones de subagentes muertos (o sesiones).

Uso:
  py extraer_contexto.py --buscar "keyword"            # localizar candidatos por descripcion
  py extraer_contexto.py <ruta agent-XXX.jsonl>        # briefing comprimido para relanzar
  py extraer_contexto.py <ruta> --volcar rescate.md    # rescate COMPLETO (texto + thinking)
  py extraer_contexto.py <ruta sessionId.jsonl>        # tambien sirve para sesiones enteras

La inversion de tokens del agente muerto NO esta toda en la basura: su producto
VISIBLE (analisis, hallazgos, planes, borradores) persiste en el jsonl con usage
(output_tokens) por mensaje, y los archivos que escribio siguen en disco. El thinking
interno crudo suele persistir solo como firma (no rescatable). El briefing muestra la
inversion; --volcar rescata el producto completo a un .md para heredarselo al reemplazo.

Regla dura: NUNCA hacer Read del jsonl entero en el hilo del agente (blobs base64 de
screenshots revientan el contexto). Este script lee linea por linea y solo emite
texto truncado.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

MAX_CHARS = 400
MAX_CHARS_VOLCADO = 2000
ULTIMAS = 8


def _bloques_texto(contenido):
    """Rinde (tipo, texto) por bloque text/thinking de un content str o lista."""
    if isinstance(contenido, str):
        yield ("text", contenido)
        return
    if isinstance(contenido, list):
        for b in contenido:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text":
                yield ("text", b.get("text", ""))
            elif b.get("type") == "thinking":
                yield ("thinking", b.get("thinking", ""))


def _texto(contenido) -> str:
    return "\n".join(t for tipo, t in _bloques_texto(contenido) if tipo == "text")


def _trunc(s: str, n: int = MAX_CHARS) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n] + " [...corte...]"


def buscar(keyword: str) -> int:
    base = os.path.expanduser("~/.claude/projects")
    patron = os.path.join(base, "*", "*", "subagents", "*.meta.json")
    hallados = []
    for meta_path in glob.glob(patron):
        try:
            with open(meta_path, encoding="utf-8") as fh:
                meta = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        desc = meta.get("description", "")
        if keyword.lower() in desc.lower():
            jsonl = meta_path.replace(".meta.json", ".jsonl")
            hallados.append((os.path.getmtime(meta_path), jsonl, meta))
    if not hallados:
        print(f"Sin coincidencias para '{keyword}' en {patron}")
        return 1
    hallados.sort(reverse=True)
    for mtime, jsonl, meta in hallados[:10]:
        flag = "stoppedByUser" if meta.get("stoppedByUser") else "no-detenido"
        print(f"[{flag}] {meta.get('model','?')} | {meta.get('description','')}")
        print(f"  {jsonl}")
    return 0


def extraer(ruta: str, ultimas: int, max_chars: int, volcar: str | None) -> int:
    if not os.path.isfile(ruta):
        print(f"No existe: {ruta}")
        return 1

    meta_path = ruta.replace(".jsonl", ".meta.json")
    if os.path.isfile(meta_path):
        with open(meta_path, encoding="utf-8") as fh:
            meta = json.load(fh)
        print("== META ==")
        print(f"tipo={meta.get('agentType')} modelo={meta.get('model')} "
              f"stoppedByUser={meta.get('stoppedByUser', False)}")
        print(f"descripcion: {meta.get('description','')}")

    primer_prompt = None
    pedidos_humanos = []
    cola_asistente = []
    herramientas = []
    archivos = set()
    ultimo_ts = None
    tokens_out = 0
    n_thinking = 0
    n_thinking_texto = 0
    volcado = []  # lista de (etiqueta, texto) en orden cronologico

    with open(ruta, encoding="utf-8") as fh:
        for linea in fh:
            try:
                d = json.loads(linea)
            except json.JSONDecodeError:
                continue
            ultimo_ts = d.get("timestamp", ultimo_ts)
            msg = d.get("message") or {}
            contenido = msg.get("content")
            tipo = d.get("type")

            if tipo == "user":
                # content str = pedido humano directo (no tool_result)
                if isinstance(contenido, str):
                    if primer_prompt is None:
                        primer_prompt = contenido
                    else:
                        pedidos_humanos.append(contenido)
                    volcado.append(("HUMANO", contenido))
            elif tipo == "assistant":
                usage = msg.get("usage") or {}
                tokens_out += usage.get("output_tokens", 0)
                if isinstance(contenido, list):
                    n_thinking += sum(
                        1 for b in contenido
                        if isinstance(b, dict) and b.get("type") == "thinking")
                for btipo, btxt in _bloques_texto(contenido):
                    if not btxt.strip():
                        continue
                    if btipo == "thinking":
                        n_thinking_texto += 1
                        volcado.append(("THINKING", btxt))
                    else:
                        volcado.append(("AGENTE", btxt))
                txt = _texto(contenido)
                if txt.strip():
                    cola_asistente.append(txt)
                    cola_asistente = cola_asistente[-ultimas:]
                if isinstance(contenido, list):
                    for b in contenido:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            herramientas.append(b.get("name", "?"))
                            entrada = b.get("input") or {}
                            fp = entrada.get("file_path")
                            if fp:
                                archivos.add(fp)
                                volcado.append(
                                    ("TOOL", f"{b.get('name','?')} -> {fp}"))

    print("\n== INVERSION DEL AGENTE ==")
    print(f"output_tokens: {tokens_out} | bloques thinking: {n_thinking} "
          f"(con texto rescatable: {n_thinking_texto})")
    if n_thinking and not n_thinking_texto:
        print("NOTA: thinking solo persiste como firma (contenido no rescatable);")
        print("el producto VISIBLE (analisis, planes, archivos) si se rescata abajo.")

    print("\n== PRIMER PROMPT (la tarea original) ==")
    print(_trunc(primer_prompt or "(no encontrado)", max_chars * 3))

    if pedidos_humanos:
        print("\n== PEDIDOS HUMANOS POSTERIORES (fuente #1 de trabajo perdido) ==")
        for p in pedidos_humanos:
            print(f"- {_trunc(p, max_chars)}")

    if archivos:
        print("\n== ARCHIVOS TOCADOS (Write/Edit; persisten en disco, revisar git diff) ==")
        for a in sorted(archivos):
            print(f"- {a}")

    if herramientas:
        print(f"\n== HERRAMIENTAS (ultimas 15 de {len(herramientas)}) ==")
        print(", ".join(herramientas[-15:]))

    print(f"\n== ULTIMOS {len(cola_asistente)} MENSAJES DEL AGENTE (punto de corte) ==")
    for t in cola_asistente:
        print(f"- {_trunc(t, max_chars)}")
    print(f"\ncorte: {ultimo_ts}")

    if volcar:
        with open(volcar, "w", encoding="utf-8") as out:
            out.write(f"# Rescate completo de {os.path.basename(ruta)}\n")
            out.write(f"# output_tokens invertidos: {tokens_out} | "
                      f"thinking: {n_thinking} bloques | corte: {ultimo_ts}\n\n")
            for etiqueta, texto in volcado:
                out.write(f"## [{etiqueta}]\n{_trunc(texto, MAX_CHARS_VOLCADO)}\n\n")
        print(f"\nrescate completo ({len(volcado)} bloques) -> {volcar}")
    return 0


def main() -> int:
    # Windows/Git Bash usa cp1252 en stdout por default y revienta con
    # UnicodeEncodeError al imprimir flechas/emoji del transcript. Forzar utf-8
    # (con reemplazo) para que el rescate corra sin PYTHONIOENCODING manual.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ruta", nargs="?", help="ruta al agent-XXX.jsonl o sessionId.jsonl")
    ap.add_argument("--buscar", help="buscar subagentes por keyword en la descripcion")
    ap.add_argument("--volcar", help="escribir rescate completo (texto+thinking) a este .md")
    ap.add_argument("--ultimas", type=int, default=ULTIMAS)
    ap.add_argument("--max-chars", type=int, default=MAX_CHARS)
    args = ap.parse_args()
    if args.buscar:
        return buscar(args.buscar)
    if not args.ruta:
        ap.print_help()
        return 2
    return extraer(args.ruta, args.ultimas, args.max_chars, args.volcar)


if __name__ == "__main__":
    sys.exit(main())
