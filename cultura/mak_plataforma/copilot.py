"""Curatorial copilot contracts independent of any model provider."""
from __future__ import annotations

import re
import unicodedata


STOPWORDS = {
    "para", "como", "esta", "este", "desde", "entre", "sobre", "con", "una",
    "los", "las", "del", "por", "que", "obra", "sin", "tambien", "cuando",
    "donde", "hacia", "estas", "estos", "ellos", "ellas", "solo", "menos",
    "fue", "eran", "pero", "para", "tiene", "tener", "este", "esta",
}


def _terms(value):
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]{5,}", normalized) if w not in STOPWORDS}


def feedback_index(rows):
    return {(str(r.get("source_id")), str(r.get("target_id"))): r
            for r in rows if r.get("source_id") and r.get("target_id")}


def _confidence(score, prior):
    if prior and prior.get("action") in ("accept", "correct"):
        return "confirmada"
    if prior and prior.get("action") == "reject":
        return "descartada"
    if score >= 9:
        return "alta"
    if score >= 5:
        return "media"
    return "baja"


def build_suggestions(source, items, selections=None, feedback=None, limit=24):
    selections = selections or {}
    learned = feedback_index(feedback or [])
    source_id = str(source.get("id", ""))
    source_terms = _terms(source.get("descripcion_original"))
    result = []
    for candidate in items:
        candidate_id = str(candidate.get("id", ""))
        if not candidate_id or candidate_id == source_id:
            continue
        candidate_terms = _terms(candidate.get("descripcion_original"))
        shared = sorted(source_terms & candidate_terms)
        prior = learned.get((source_id, candidate_id))
        common = {
            "item_id": candidate_id,
            "selection": selections.get(candidate_id, {}).get("decision", "pendiente"),
            "feedback": prior.get("action") if prior else "pendiente",
        }
        if candidate.get("publicacion_id") == source.get("publicacion_id") and source.get("publicacion_id"):
            result.append(dict(common, relation_type="same_carousel", score=12,
                               reasons=["misma publicación/carrusel"]))
        if candidate.get("fecha") == source.get("fecha") and source.get("fecha"):
            result.append(dict(common, relation_type="same_date_context", score=7,
                               reasons=["misma fecha"]))
        if shared:
            result.append(dict(common, relation_type="shared_concept", score=min(6, len(shared)) + 2,
                               reasons=["conceptos compartidos: " + ", ".join(shared[:5])]))
        if candidate.get("tipo_contenido") == source.get("tipo_contenido"):
            result.append(dict(common, relation_type="same_media_role", score=1,
                               reasons=["mismo tipo de medio"]))
    for row in result:
        prior = learned.get((source_id, row["item_id"]))
        if prior and prior.get("action") in ("accept", "correct"):
            row["score"] += 14
            row["reasons"].append("relación aceptada anteriormente")
        elif prior and prior.get("action") == "reject":
            row["score"] -= 20
            row["reasons"].append("relación rechazada anteriormente")
        row["confidence"] = _confidence(row["score"], prior)
    result = [row for row in result if row["score"] > 0]
    result.sort(key=lambda row: (-row["score"], row["item_id"], row["relation_type"]))
    return result[:limit]


def media_manifest(item):
    path = str(item.get("asset_path", ""))
    extension = path.split("?")[0].rsplit(".", 1)[-1].lower() if "." in path else ""
    modality = "video" if extension in {"mp4", "mov", "webm", "m4v"} else "image" if extension else "metadata"
    return {
        "id": item.get("id"),
        "modality": modality,
        "asset_available": bool(item.get("asset_available")),
        "date": item.get("fecha"),
        "publication_id": item.get("publicacion_id"),
        "content_type": item.get("tipo_contenido"),
        "description_present": bool(str(item.get("descripcion_original") or "").strip()),
    }


def provider_status(environment):
    return {
        "local_deterministic": True,
        "ollama": bool(environment.get("OLLAMA_HOST")),
        "groq": bool(environment.get("GROQ_API_KEY")),
        "cerebras": bool(environment.get("CEREBRAS_API_KEY")),
        "watsonx": bool(environment.get("WATSONX_API_KEY") or environment.get("IBM_CLOUD_APIKEY")),
        "aws": bool(environment.get("AWS_ACCESS_KEY_ID")),
    }


def evaluate_feedback(rows):
    counts = {"accept": 0, "correct": 0, "reject": 0, "ignore": 0}
    for row in rows:
        if row.get("action") in counts:
            counts[row["action"]] += 1
    total = sum(counts.values())
    return {"counts": counts, "total": total,
            "confirmed": counts["accept"] + counts["correct"],
            "rejected": counts["reject"]}
