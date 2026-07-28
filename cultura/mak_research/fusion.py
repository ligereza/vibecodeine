#!/usr/bin/env python3
"""Create an explicit fusion primordium without deleting its sources."""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

DESTINO = Path(os.path.expanduser("~/research/fusiones"))


def crear(tema: str, fuentes: list[str], destino: Path = DESTINO) -> dict:
    tema = str(tema or "").strip()
    fuentes = list(dict.fromkeys(str(x) for x in fuentes if x))
    if not tema or len(fuentes) < 2:
        raise ValueError("una fusión necesita tema y dos fuentes")
    fid = hashlib.sha1((tema + "\n" + "\n".join(fuentes)).encode("utf-8")).hexdigest()[:12]
    destino.mkdir(parents=True, exist_ok=True)
    path = destino / ("fusion-%s.md" % fid)
    lines = ["# Primordio de fusión", "", tema, "", "**Fuentes que conserva:**", ""]
    lines += ["- `%s`" % x for x in fuentes]
    lines += ["", "**Estado:** esperando correlación y decisión humana.", "", "---",
              "meta: " + json.dumps({"id": fid, "tipo": "fusion",
              "origen": "usuario", "fuentes": fuentes,
              "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}, ensure_ascii=False)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"id": "fusiones/" + path.name, "path": str(path), "fuentes": fuentes}