#!/usr/bin/env python3
"""User ideas as archive nodes, not loose notes.

User request (2026-07-26): allow intervention instead of passive viewing. Ideas
may relate to a work already under analysis, or change the order of remaining
work according to the user's needs.

The first version was going to be a panel for dragging queue rows. It was
rejected because it forced the user to inspect 46 questions and decide which
one should move up. Here the user records what they are thinking and the
archive reports related material through the existing semantic mycelium search
(research/memoria.py buscar()).

There is also a deeper reason: an idea stated in chat disappears when the
session closes, which is the problem this repository is meant to solve. An idea
written here persists, relates itself to later material, and MAK can handle it
while the user sleeps.

Files:
    ~/plataforma/ideas.jsonl        one idea per line
    ~/plataforma/material.jsonl     work queue (see material.py)
"""
import json
import os
import sys
import threading
import time
from hashlib import sha1

HOME = os.path.expanduser("~")
IDEAS = os.path.join(HOME, "plataforma", "ideas.jsonl")
_IDEAS_LOCK = threading.RLock()

sys.path.insert(0, os.path.join(HOME, "research"))
sys.path.insert(0, os.path.join(HOME, "plataforma"))


def _id(texto):
    return sha1(texto.strip().lower().encode("utf-8")).hexdigest()[:12]


def cargar():
    if not os.path.exists(IDEAS):
        return []
    filas = []
    with open(IDEAS, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                filas.append(json.loads(linea))
            except ValueError:
                continue
    return filas


def _guardar(filas):
    tmp = IDEAS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in filas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, IDEAS)


def relacionar(texto, k=6):
    """Return archive material near this idea, or [] when unavailable.

    Do not invent similarities: if the mycelium is not indexed or the embedder
    does not respond, return an empty list so the caller can say so instead of
    showing filler results.
    """
    try:
        import memoria
    except Exception:
        return []
    try:
        crudos = memoria.buscar(texto, k=k) or []
    except Exception:
        return []
    salida = []
    for r in crudos:
        if not isinstance(r, dict):
            continue
        ruta = r.get("path") or ""
        salida.append({
            "titulo": r.get("titulo") or os.path.basename(ruta),
            "carpeta": r.get("dir") or "",
            "id": "%s/%s" % (r.get("dir") or "?", os.path.basename(ruta)),
            "score": round(float(r.get("score") or 0), 3),
            # 'corpus' means a work from the artist archive; other directories
            # contain MAK research. The distinction matters because the user
            # asked about THEIR works, not the box's essays.
            "es_obra": (r.get("dir") == "corpus"),
        })
    return salida


def anotar(texto, k=6, origen_id=None, origen_dir=None):
    with _IDEAS_LOCK:
        return _note_unlocked(texto, k=k, source_id=origen_id,
                              source_dir=origen_dir)


def _note_unlocked(text, k=6, source_id=None, source_dir=None):
    """Record an idea and attach relations found at write time."""
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "idea vacia"}
    records = cargar()
    iid = _id(text)
    if any(record.get("id") == iid for record in records):
        return {"ok": False, "error": "esa idea ya estaba anotada", "id": iid}

    related = relacionar(text, k=k)
    record = {
        "id": iid,
        "texto": text,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "relacionadas": related,
        "origen": ({"id": str(source_id), "dir": str(source_dir or "")}
               if source_id else None),
        "estado": "anotada",
    }
    records.append(record)
    _guardar(records)
    return {"ok": True, "idea": record,
            "aviso": "" if related else
                     "No se pudo relacionar: el micelio no respondio. La idea "
                     "quedo guardada igual."}


def encargar(idea_id, depto="research"):
    with _IDEAS_LOCK:
        return _assign_unlocked(idea_id, department=depto)


def _assign_unlocked(idea_id, department="research"):
    """Turn an idea into work and place it at the front of the queue.

    User questions take priority over automatic triangulation so new work does
    not remain behind the existing generated queue.
    """
    try:
        import material
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": "no pude abrir la cola: %s" % e}

    filas = cargar()
    idea = next((f for f in filas if f.get("id") == idea_id), None)
    if not idea:
        return {"ok": False, "error": "no existe esa idea"}
    if department not in ("research", "codex"):
        department = "research"

    tarea = {
        "id": "idea-" + idea_id,
        "origen": "usuario",
        "ficha": None,
        "archivo": None,
        "depto": department,
        "modo": "generar" if department == "codex" else "research",
        "texto": idea["texto"],
        "estado": "pendiente",
    }
    if not material.enqueue_front(tarea):
        return {"ok": False, "error": "esa idea ya estaba encargada"}

    idea["estado"] = "encargada"
    idea["depto"] = department
    _guardar(filas)
    return {"ok": True, "encargada": tarea["texto"][:120], "depto": department}


def priorizar(patron):
    with _IDEAS_LOCK:
        return _prioritize_unlocked(patron)


def _prioritize_unlocked(pattern):
    """Move tasks containing `pattern` to the front of the queue.

    This changes ordering only; it does not delete tasks or change their
    states.
    """
    try:
        import material
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": "no pude abrir la cola: %s" % e}
    pattern = (pattern or "").strip().lower()
    if not pattern:
        return {"ok": False, "error": "sin patron"}
    moved_count = material.reorder_by_pattern(pattern)
    if not moved_count:
        return {"ok": True, "subidas": 0,
                "aviso": "nada en la cola menciona eso"}
    return {"ok": True, "subidas": moved_count}


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "anotar":
        print(json.dumps(anotar(" ".join(sys.argv[2:])), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 2 and sys.argv[1] == "priorizar":
        print(json.dumps(priorizar(" ".join(sys.argv[2:])), ensure_ascii=False))
    elif len(sys.argv) > 2 and sys.argv[1] == "encargar":
        print(json.dumps(encargar(sys.argv[2]), ensure_ascii=False))
    else:
        for f in cargar():
            print("%s  %-10s %s" % (f["id"], f.get("estado", ""), f["texto"][:70]))
