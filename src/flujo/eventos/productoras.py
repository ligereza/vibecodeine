"""Productora identification from event flyer images via Gemini vision.

Flow: read flyer image -> Gemini extracts name/logo/venue -> match against
data/productoras/*.json (JSON per productora, git-tracked) -> if no match,
flag for human confirmation instead of silently auto-creating (avoids
duplicate/misspelled entries piling up unattended).
"""
from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any

_MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]

_EXTRACT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "productora_name": {"type": "STRING", "nullable": True},
        "has_logo": {"type": "BOOLEAN"},
        "logo_description": {"type": "STRING", "nullable": True},
        "venue_name": {"type": "STRING", "nullable": True},
        "venue_location_text": {"type": "STRING", "nullable": True},
        "location_is_private": {"type": "BOOLEAN"},
        "other_text_visible": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["has_logo", "location_is_private", "other_text_visible"],
}

_PROMPT = (
    "Analiza este flyer de evento. Extrae: nombre de la productora/promotora "
    "(si aparece en logo o texto), si hay un logo visible y como es, nombre "
    "del venue/lugar si aparece, cualquier texto de ubicacion (direccion, "
    "ciudad, o si dice que la ubicacion es privada/por DM), y otro texto "
    "identificatorio visible (nombres de artistas, fecha). Si un campo no "
    "esta presente en el flyer, usa null (no inventes)."
)


def _keys() -> list[str]:
    keys = [os.getenv("GEMINI_API_KEY", "")]
    i = 2
    while True:
        k = os.getenv(f"GEMINI_API_KEY_{i}", "")
        if not k:
            break
        keys.append(k)
        i += 1
    return [k for k in keys if k]


def _mime_type(path: Path) -> str:
    ext = path.suffix.lower()
    return {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".webp": "image/webp"}.get(ext, "image/jpeg")


def extract_from_flyer(image_path: Path) -> dict[str, Any]:
    """Call Gemini vision on the flyer image, return structured extraction.
    Raises RuntimeError if no key works (caller decides whether that's fatal
    for the pipeline or just skips productora tagging for this run)."""
    import requests

    keys = _keys()
    if not keys:
        raise RuntimeError("GEMINI_API_KEY no configurada (.env raiz).")

    img_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    payload = {
        "contents": [{"role": "user", "parts": [
            {"text": _PROMPT},
            {"inline_data": {"mime_type": _mime_type(image_path), "data": img_b64}},
        ]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _EXTRACT_SCHEMA,
        },
    }

    last_err = ""
    for key in keys:
        for model in _MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                r = requests.post(url, json=payload, timeout=45)
            except Exception as e:  # noqa: BLE001
                last_err = f"{model}: {e}"
                continue
            if r.status_code == 200:
                data = r.json()
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    last_err = f"{model}: respuesta invalida ({e})"
                    continue
            else:
                last_err = f"{model}: HTTP {r.status_code}"
    raise RuntimeError(f"Gemini vision fallo en todas las keys/modelos: {last_err}")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "sin_nombre"


def load_all(data_dir: Path) -> dict[str, dict]:
    data_dir.mkdir(parents=True, exist_ok=True)
    entries = {}
    for f in data_dir.glob("*.json"):
        try:
            entries[f.stem] = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
    return entries


def match(extracted: dict, known: dict[str, dict]) -> str | None:
    """Case-insensitive match on name or any alias. None if no match."""
    name = (extracted.get("productora_name") or "").strip().lower()
    if not name:
        return None
    for slug, entry in known.items():
        candidates = [entry.get("name", "")] + entry.get("aliases", [])
        if any(name == c.strip().lower() for c in candidates if c):
            return slug
    return None


def save(data_dir: Path, slug: str, entry: dict) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / f"{slug}.json"
    path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def identify(image_path: Path, data_dir: Path) -> dict[str, Any]:
    """Full pipeline step: extract -> match -> report. Never auto-creates a
    new productora entry; returns needs_confirmation=True with the raw
    extraction when nothing matches, so a human confirms before it's saved."""
    extracted = extract_from_flyer(image_path)
    known = load_all(data_dir)
    slug = match(extracted, known)
    if slug:
        return {"matched": True, "slug": slug, "productora": known[slug], "extracted": extracted}
    return {"matched": False, "needs_confirmation": True, "extracted": extracted}
