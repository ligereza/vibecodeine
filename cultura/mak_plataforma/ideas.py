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
import time
from hashlib import sha1

HOME = os.path.expanduser("~")
IDEAS = os.path.join(HOME, "plataforma", "ideas.jsonl")

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
            "score": round(float(r.get("score") or 0), 3),
            # 'corpus' = una obra del archivo del artista; el resto es
            # investigacion propia de MAK. La distincion importa: el usuario
            # pregunto por SUS obras, no por los ensayos de la caja.
            "es_obra": (r.get("dir") == "corpus"),
        })
    return salida


def anotar(texto, k=6):
    """Registra la idea y le adjunta con que se relacionó al momento de escribirla."""
    texto = (texto or "").strip()
    if not texto:
        return {"ok": False, "error": "idea vacia"}
    filas = cargar()
    iid = _id(texto)
    if any(f.get("id") == iid for f in filas):
        return {"ok": False, "error": "esa idea ya estaba anotada", "id": iid}

    relacionadas = relacionar(texto, k=k)
    fila = {
        "id": iid,
        "texto": texto,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "relacionadas": relacionadas,
        "estado": "anotada",
    }
    filas.append(fila)
    _guardar(filas)
    return {"ok": True, "idea": fila,
            "aviso": "" if relacionadas else
                     "No se pudo relacionar: el micelio no respondio. La idea "
                     "quedo guardada igual."}


def encargar(idea_id, depto="research"):
    """Convierte una idea en trabajo, al frente de la cola.

    Va PRIMERO a proposito: una pregunta del usuario le gana a la triangulacion
    automatica. Sin esto, su idea entraria detras de 46 preguntas de flyers.
    """
    try:
        import material
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": "no pude abrir la cola: %s" % e}

    filas = cargar()
    idea = next((f for f in filas if f.get("id") == idea_id), None)
    if not idea:
        return {"ok": False, "error": "no existe esa idea"}
    if depto not in ("research", "codex"):
        depto = "research"

    cola = material.cargar()
    tarea = {
        "id": "idea-" + idea_id,
        "origen": "usuario",
        "ficha": None,
        "archivo": None,
        "depto": depto,
        "modo": "generar" if depto == "codex" else "research",
        "texto": idea["texto"],
        "estado": "pendiente",
    }
    if any(t.get("id") == tarea["id"] for t in cola):
        return {"ok": False, "error": "esa idea ya estaba encargada"}
    material.guardar([tarea] + cola)   # al frente

    idea["estado"] = "encargada"
    idea["depto"] = depto
    _guardar(filas)
    return {"ok": True, "encargada": tarea["texto"][:120], "depto": depto}


def priorizar(patron):
    """Sube al frente de la cola las tareas cuyo texto contiene `patron`.

    Es la otra mitad del pedido: "cambiar el orden de las obras que le quedan
    por analizar segun mis necesidades". No borra nada ni cambia estados: solo
    reordena lo pendiente.
    """
    try:
        import material
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": "no pude abrir la cola: %s" % e}
    patron = (patron or "").strip().lower()
    if not patron:
        return {"ok": False, "error": "sin patron"}
    cola = material.cargar()
    suben = [t for t in cola if patron in (t.get("texto") or "").lower()]
    resto = [t for t in cola if t not in suben]
    if not suben:
        return {"ok": True, "subidas": 0,
                "aviso": "nada en la cola menciona eso"}
    material.guardar(suben + resto)
    return {"ok": True, "subidas": len(suben)}


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
