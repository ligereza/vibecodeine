#!/usr/bin/env python3
"""Ideas del usuario como nodos del archivo, no como notas sueltas.

Pedido del usuario (2026-07-26): poder INTERVENIR, no mirar. "Tengo ideas
actualmente que no he empezado y que quizas si se relacionan con alguna obra que
esten analizando, o cambiar el orden de las obras que le quedan por analizar
segun mis necesidades".

La primera version de esto iba a ser un panel para arrastrar filas de la cola.
Se descarto por una razon: obligaba al usuario a mirar 46 preguntas y decidir
cual sube -- trabajo suyo. Aca declara lo que esta pensando y el archivo le dice
con que se relaciona, usando la busqueda semantica del micelio que YA existe
(research/memoria.py buscar()).

Y hay un motivo de fondo: una idea dicha en un chat se pierde cuando la sesion
cierra -- que es el problema que este repo entero intenta resolver. Una idea
escrita aca queda, se relaciona sola con lo que llegue despues, y MAK la puede
atender mientras el usuario duerme.

Archivos:
    ~/plataforma/ideas.jsonl        las ideas, una por linea
    ~/plataforma/material.jsonl     la cola de trabajo (ver material.py)
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
    """Que hay en el archivo cerca de esta idea. Devuelve [] si no se puede.

    No inventa parecidos: si el micelio no esta indexado o el embebedor no
    responde, devuelve lista vacia y quien llama lo dice, en vez de mostrar
    resultados de relleno.
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
            # 'corpus' = una obra del archivo del artista; el resto es
            # investigacion propia de MAK. La distincion importa: el usuario
            # pregunto por SUS obras, no por los ensayos de la caja.
            "es_obra": (r.get("dir") == "corpus"),
        })
    return salida


def anotar(texto, k=6, origen_id=None, origen_dir=None):
    with _IDEAS_LOCK:
        return _note_unlocked(texto, k=k, source_id=origen_id,
                              source_dir=origen_dir)


def _note_unlocked(text, k=6, source_id=None, source_dir=None):
    """Record an idea and attach the relations found at write time."""
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

    User questions take priority over automatic triangulation so the new work
    does not remain behind the existing generated queue.
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
