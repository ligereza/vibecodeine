# -*- coding: utf-8 -*-
"""The substrate contract: micelio graph -> pieces + relations, ONE shape.

Why this module exists (2026-07-29): the data/contract/skin split existed only
for iskvw, and MAK's micelio had its own nodes and its own drawing -- the same
work done twice, so a new skin served only one of them. The layer in between
is a contract of PIECES and RELATIONS that does not know whether the works are
the artist's or MAK's (iskvw/ESQUEMA_ARCHIVO.md). This module is that
conversion as a PURE function, shared by the two consumers:

- `tools/gen_archivo_iskvw.py` (repo side) delegates its micelio branch here,
  so id formation lives in exactly one place -- the "<hash>-<mediaid>.md" vs
  stem mismatch that once produced 1004 pieces / 0 positions cannot fork again.
- `cultura/mak_plataforma/hub.py` (box side, covered by the MAK-REPO-SYNC
  cron) serves it at GET /api/archivo, so any skin or external agent can ask
  the organism's face for "the pieces and their links" and always get the
  same shape, without knowing the micelio's internal node schema.

The rule it inherits is the doublecup thesis: no element may claim a datum it
does not encode. An artist work keeps an EMPTY titulo (machine perception is
not authorship; it travels as extra.percibido), an absent date stays absent,
and every field a consumer does not know is a field it ignores.

Pure stdlib, no I/O: callers fetch the graph payload themselves.

Retirement: when the contract gains a schema version the micelio itself emits.
"""
from __future__ import annotations

import re
import unicodedata

# 'corpus' are the artist's perceived works; the rest MAK wrote itself.
_CLASE_POR_DIR = {"corpus": "obra", "codex": "codigo"}

_EXTENSIONES = (".md", ".txt", ".json", ".jpg", ".jpeg", ".png", ".webp")


def _id(texto: str) -> str:
    base = unicodedata.normalize("NFKD", str(texto or ""))
    base = base.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:60] or "sin-id"


def _id_pieza(texto: str) -> str:
    """A piece's id, without the file suffix.

    The micelio names its nodes after the whole file
    ("b7fd4e77b4a2-17926032902806396.md") while the campo uses the stem, so
    `_id()` produced "...-md" on one side and not the other and positions
    NEVER joined: 1004 pieces, 0 with position. The extension is where the
    datum is stored, not which piece it is.
    """
    s = str(texto or "")
    for ext in _EXTENSIONES:
        if s.lower().endswith(ext):
            s = s[: -len(ext)]
            break
    return _id(s)


def convertir(grafo: dict) -> dict:
    """Micelio graph payload ({"nodes": [...], "edges": [...]}) -> the
    contract shape {"piezas": [...], "vinculos": [...]}.

    What MAK wrote ABOUT an artist work is PERCEPTION, not a title. It used
    to enter as `titulo`, and the contract ended up asserting that a work is
    called "Una mujer sentada bajo una estructura de madera" -- machine voice
    signing as the artist. For works the title stays EMPTY (silence before
    borrowed voice) and the text travels as `extra.percibido`, which a skin
    may use to search and place without showing it as authorship. For reports
    and code, which MAK wrote, the title IS its own.
    """
    piezas = []
    for n in grafo.get("nodes", []):
        cl = _CLASE_POR_DIR.get(n.get("dir"), "informe")
        texto = str(n.get("titulo") or "").strip()
        es_obra = cl == "obra"
        piezas.append({
            "id": _id_pieza(n.get("id")),
            "titulo": "" if es_obra else (texto or _id_pieza(n.get("id"))),
            "clase": cl,
            "fecha": None,
            "resumen": None,
            "etiquetas": [n["dir"]] if n.get("dir") else [],
            "peso": int(n.get("chunks") or 1),
            "medio": {"tipo": "texto"},
            "estado": "publicada",
            "extra": {k: v for k, v in (
                ("carpeta", n.get("dir")),
                ("percibido", texto if es_obra else None),
            ) if v},
        })

    conocidas = {p["id"] for p in piezas}
    vinculos = [{
        "de": _id_pieza(e["a"]), "a": _id_pieza(e["b"]),
        "peso": round(float(e.get("w") or 0), 3), "clase": "semantico",
    } for e in grafo.get("edges", [])
        if _id_pieza(e.get("a")) in conocidas and _id_pieza(e.get("b")) in conocidas]
    return {"piezas": piezas, "vinculos": vinculos}
