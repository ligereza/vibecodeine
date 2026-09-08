#!/usr/bin/env python3
"""Turn the user's ideas into first-class micelio documents.

Ideas remain canonical in ~/plataforma/ideas.jsonl. This adapter only makes
that matter indexable beside works, research and code. It never invents text
and rewrites a document only when its source changed.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

IDEAS = Path(os.path.expanduser("~/plataforma/ideas.jsonl"))
DESTINO = Path(os.path.expanduser("~/research/ideas"))
_SYNC_LOCK = threading.RLock()


@contextmanager
def _exclusive_sync_lock(destination):
    """Prevent two indexers from deleting or writing crossing adapters."""
    with _SYNC_LOCK:
        lock_path = os.path.abspath(str(destination)) + ".lock"
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


def documento(idea: dict) -> str:
    texto = str(idea.get("texto") or "").strip()
    relacionadas = idea.get("relacionadas") or []
    lines = ["# Idea del usuario", "", texto, "", "**Estado:** %s" %
             (idea.get("estado") or "anotada")]
    if relacionadas:
        lines += ["", "**Se relacionó al nacer con:**", ""]
        for r in relacionadas:
            lines.append("- %s [%s; %.3f; id=%s]" % (
                r.get("titulo") or "sin título", r.get("carpeta") or "?",
                float(r.get("score") or 0), r.get("id") or ""))
    origen = idea.get("origen") if isinstance(idea.get("origen"), dict) else None
    lines += ["", "---", "meta: " + json.dumps({
        "id": idea.get("id"), "tipo": "idea", "origen": "usuario",
        "ts": idea.get("ts"), "origen_materia": origen},
        ensure_ascii=False)]
    return "\n".join(lines) + "\n"


def sincronizar(origen: Path = IDEAS, destino: Path = DESTINO) -> dict:
    origen = Path(origen)
    destino = Path(destino)
    with _exclusive_sync_lock(destino):
        return _sync_unlocked(origen, destino)


def _sync_unlocked(source: Path, destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    active_names = set()
    written = unchanged = 0
    try:
        line_texts = source.read_text(
            encoding="utf-8", errors="replace").splitlines()
    except OSError:
        line_texts = []
    for line_text in line_texts:
        try:
            idea = json.loads(line_text)
        except ValueError:
            continue
        iid = str(idea.get("id") or "").strip()
        if not iid or not str(idea.get("texto") or "").strip():
            continue
        filename = "idea-%s.md" % iid
        active_names.add(filename)
        output_path = destination / filename
        new_text = documento(idea)
        if (output_path.exists()
                and output_path.read_text(encoding="utf-8") == new_text):
            unchanged += 1
        else:
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                        "w", encoding="utf-8", dir=destination,
                        prefix=".idea-", suffix=".tmp", delete=False) as f:
                    temp_path = f.name
                    f.write(new_text)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp_path, output_path)
                temp_path = None
            finally:
                if temp_path:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
            written += 1
    removed = 0
    for output_path in destination.glob("idea-*.md"):
        if output_path.name not in active_names:
            output_path.unlink()
            removed += 1
    return {"ideas": len(active_names), "escritas": written,
            "sin_cambio": unchanged, "retiradas": removed}


if __name__ == "__main__":
    print(json.dumps(sincronizar(), ensure_ascii=False))
