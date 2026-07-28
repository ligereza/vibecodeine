#!/usr/bin/env python3
"""Turn the user's ideas into first-class micelio documents.

Ideas remain canonical in ~/plataforma/ideas.jsonl. This adapter only makes
that matter indexable beside works, research and code. It never invents text
and rewrites a document only when its source changed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

IDEAS = Path(os.path.expanduser("~/plataforma/ideas.jsonl"))
DESTINO = Path(os.path.expanduser("~/research/ideas"))


def documento(idea: dict) -> str:
    texto = str(idea.get("texto") or "").strip()
    relacionadas = idea.get("relacionadas") or []
    lines = ["# Idea del usuario", "", texto, "", "**Estado:** %s" %
             (idea.get("estado") or "anotada")]
    if relacionadas:
        lines += ["", "**Se relacionó al nacer con:**", ""]
        for r in relacionadas:
            lines.append("- %s [%s; %.3f]" % (
                r.get("titulo") or "sin título", r.get("carpeta") or "?",
                float(r.get("score") or 0)))
    lines += ["", "---", "meta: " + json.dumps({
        "id": idea.get("id"), "tipo": "idea", "origen": "usuario",
        "ts": idea.get("ts")}, ensure_ascii=False)]
    return "\n".join(lines) + "\n"


def sincronizar(origen: Path = IDEAS, destino: Path = DESTINO) -> dict:
    destino.mkdir(parents=True, exist_ok=True)
    vigentes = set()
    escritos = sin_cambio = 0
    try:
        lineas = origen.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        lineas = []
    for linea in lineas:
        try:
            idea = json.loads(linea)
        except ValueError:
            continue
        iid = str(idea.get("id") or "").strip()
        if not iid or not str(idea.get("texto") or "").strip():
            continue
        nombre = "idea-%s.md" % iid
        vigentes.add(nombre)
        path = destino / nombre
        nuevo = documento(idea)
        if path.exists() and path.read_text(encoding="utf-8") == nuevo:
            sin_cambio += 1
        else:
            path.write_text(nuevo, encoding="utf-8")
            escritos += 1
    retirados = 0
    for path in destino.glob("idea-*.md"):
        if path.name not in vigentes:
            path.unlink()
            retirados += 1
    return {"ideas": len(vigentes), "escritas": escritos,
            "sin_cambio": sin_cambio, "retiradas": retirados}


if __name__ == "__main__":
    print(json.dumps(sincronizar(), ensure_ascii=False))
