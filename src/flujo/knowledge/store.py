from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ..paths import repo_root

ENTITY_DIRS = {
    "productora": "productoras",
    "productoras": "productoras",
    "venue": "venues",
    "venues": "venues",
    "logo": "logos",
    "logos": "logos",
    "event": "events",
    "events": "events",
}


def knowledge_root() -> Path:
    return repo_root() / "knowledge"


def slugify(value: str) -> str:
    value = (value or "item").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or "item"


def entity_dir(entity: str) -> Path:
    key = ENTITY_DIRS.get(entity, entity)
    return knowledge_root() / key


def list_entities(entity: str) -> list[str]:
    d = entity_dir(entity)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.yaml"))


def load_entity(entity: str, item_id: str) -> dict[str, Any]:
    p = entity_dir(entity) / f"{slugify(item_id)}.yaml"
    if not p.exists():
        raise FileNotFoundError(str(p))
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    data["_path"] = str(p.relative_to(repo_root())).replace("\\", "/")
    return data


def save_entity(entity: str, item_id: str, data: dict[str, Any]) -> Path:
    d = entity_dir(entity)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{slugify(item_id)}.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return p


def classify_event_text(text: str) -> dict[str, Any]:
    low = (text or "").lower()
    producers = []
    for pid in list_entities("productoras"):
        data = load_entity("productoras", pid)
        names = [data.get("name", ""), *(data.get("aliases") or [])]
        if any(str(name).lower() in low for name in names if name):
            producers.append(data)
    venues = []
    for vid in list_entities("venues"):
        data = load_entity("venues", vid)
        names = [data.get("name", ""), *(data.get("aliases") or [])]
        if any(str(name).lower() in low for name in names if name):
            venues.append(data)
    preset = "base"
    reasons = []
    if any(v.get("scale_default") == "mainstream" for v in venues):
        preset = "mainstream"; reasons.append("venue mainstream")
    if any(p.get("scale_default") == "mainstream" for p in producers):
        preset = "mainstream"; reasons.append("productora mainstream")
    if "rave" in low or "aporte minimo" in low or "aporte mínimo" in low:
        preset = "under"; reasons.append("senales rave/under")
    if "espacio riesco" in low or "festival" in low or "creamfields" in low:
        preset = "mainstream"; reasons.append("senales masivas")
    deliverables = []
    if "rider" in low: deliverables.append("rider_completo")
    if "cartelera" in low: deliverables.append("cartelera_digital")
    if "flyer" in low and "cartelera" not in low: deliverables.append("flyer_impreso_10x14_vertical")
    if "instagram.com" in low: deliverables.append("descarga_instagram")
    return {
        "preset": preset,
        "confidence": 0.75 if reasons else 0.45,
        "reasons": reasons or ["fallback base"],
        "producers": [p.get("id") for p in producers],
        "venues": [v.get("id") for v in venues],
        "deliverables": deliverables,
    }


def ingest_example(path: str | Path, example_type: str = "unknown", producer: str = "") -> Path:
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(str(src))
    slug = slugify(src.stem if src.is_file() else src.name)
    out_dir = knowledge_root() / "examples" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    if src.is_file():
        dest = out_dir / src.name
        shutil.copy2(src, dest)
        files.append(dest.name)
    else:
        for f in src.iterdir():
            if f.is_file():
                dest = out_dir / f.name
                shutil.copy2(f, dest)
                files.append(dest.name)
    manifest = {
        "id": slug,
        "type": example_type,
        "producer_id": producer or None,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "files": files,
        "for_ai": {
            "task": "Analiza layout, estilo, logos, formato, campos editables y senales de escala.",
            "important_fields": ["layout", "style", "producer", "venue", "format", "editable_fields", "signals", "logo_candidates"],
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_dir / "manifest.json"


def register_logo_source(producer_id: str, source_path: str | Path) -> Path:
    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(str(src))
    logo_id = f"{slugify(producer_id)}_primary"
    asset_dir = repo_root() / "assets" / "logos" / slugify(producer_id) / "source"
    asset_dir.mkdir(parents=True, exist_ok=True)
    dest = asset_dir / src.name
    shutil.copy2(src, dest)
    data = {
        "id": logo_id,
        "producer_id": slugify(producer_id),
        "status": "source_registered",
        "source_quality": "unknown",
        "sources": [str(dest.relative_to(repo_root())).replace("\\", "/")],
        "workflow": {"suggested_tool": "logo_clean_lab", "next_action": "vectorize_and_clean"},
        "outputs": {},
    }
    return save_entity("logos", producer_id, data)
