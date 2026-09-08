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
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

REGISTRO = Path(os.path.expanduser("~/plataforma/fructificaciones.json"))
_RECORD_LOCK = threading.RLock()


@contextmanager
def _exclusive_record_lock(path):
    """Serialize human decision records across requests and processes."""
    with _RECORD_LOCK:
        lock_path = os.path.abspath(str(path)) + ".lock"
        parent = os.path.dirname(lock_path)
        os.makedirs(parent, exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


def cargar(path: Path = REGISTRO) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def decidir(node_id: str, accion: str, nota: str = "",
            path: Path = REGISTRO) -> dict:
    path = Path(path)
    with _exclusive_record_lock(path):
        return _decide_unlocked(node_id, accion, nota, path)


def _decide_unlocked(node_id: str, action: str, note: str,
                     path: Path) -> dict:
    node_id = str(node_id or "").strip()
    if not node_id or ".." in node_id:
        return {"ok": False, "error": "id invalido"}
    if action not in ("fructificar", "devolver"):
        return {"ok": False, "error": "accion invalida"}
    data = cargar(path)
    data[node_id] = {
        "estatuto": "fructifero" if action == "fructificar" else "sustrato",
        "nota": str(note or "")[:500],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "por": "usuario",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=path.parent,
                prefix=".fructificaciones-", suffix=".tmp", delete=False) as f:
            temp_path = f.name
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
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
