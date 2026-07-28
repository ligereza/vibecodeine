#!/usr/bin/env python3
"""Measure readiness and record human fructification decisions.

Pressure is a diagnostic, never an artistic verdict. Only an explicit human
record can assign `fructifero`. Everything else is substrate or a suggested
primordium. The registry lives in plataforma because it is a director decision,
not an inference owned by Research.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

REGISTRO = Path(os.path.expanduser("~/plataforma/fructificaciones.json"))


def cargar(path: Path = REGISTRO) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def decidir(node_id: str, accion: str, nota: str = "",
            path: Path = REGISTRO) -> dict:
    node_id = str(node_id or "").strip()
    if not node_id or ".." in node_id:
        return {"ok": False, "error": "id invalido"}
    if accion not in ("fructificar", "devolver"):
        return {"ok": False, "error": "accion invalida"}
    data = cargar(path)
    data[node_id] = {
        "estatuto": "fructifero" if accion == "fructificar" else "sustrato",
        "nota": str(nota or "")[:500],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "por": "usuario",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    os.replace(tmp, path)
    return {"ok": True, "id": node_id, **data[node_id]}


def evaluar(nodes: list[dict], edges: list[dict],
            registro: dict | None = None) -> list[dict]:
    """Attach pressure/components and human status to graph nodes."""
    registro = cargar() if registro is None else registro
    by_id = {n["id"]: n for n in nodes}
    neighbors = {nid: set() for nid in by_id}
    provenance = {nid: 0 for nid in by_id}
    for edge in edges:
        a, b = edge.get("a"), edge.get("b")
        if a not in by_id or b not in by_id:
            continue
        neighbors[a].add(b)
        neighbors[b].add(a)
        if edge.get("clase") == "procedencia":
            provenance[a] += 1
            provenance[b] += 1

    out = []
    for original in nodes:
        node = dict(original)
        nid, directory = node["id"], node.get("dir")
        neighbor_dirs = {by_id[x].get("dir") for x in neighbors[nid]}
        human = 1.0 if directory == "ideas" else (0.7 if directory == "corpus" else 0.0)
        evidence = min(1.0, float(node.get("chunks") or 0) / 4.0)
        relations = min(1.0, len(neighbor_dirs) / 3.0)
        technical = 1.0 if (directory == "codex" or "codex" in neighbor_dirs) else 0.0
        lineage = min(1.0, provenance[nid] / 2.0)
        pressure = round(0.30 * human + 0.20 * evidence + 0.25 * relations
                         + 0.15 * technical + 0.10 * lineage, 3)
        decision = registro.get(nid) if isinstance(registro.get(nid), dict) else {}
        explicit = decision.get("estatuto")
        node["presion"] = pressure
        node["senales"] = {
            "intervencion_humana": human,
            "evidencia": evidence,
            "diversidad_relaciones": relations,
            "experimento_tecnico": technical,
            "procedencia": lineage,
        }
        node["estatuto"] = explicit or ("primordio" if pressure >= 0.60 else "sustrato")
        node["decision_humana"] = bool(explicit)
        if decision.get("nota"):
            node["nota_estatuto"] = decision["nota"]
        out.append(node)
    return out
