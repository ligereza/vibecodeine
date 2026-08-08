"""Curatorial copilot contracts independent of any model provider."""
from __future__ import annotations

import json
import re
import unicodedata


STOPWORDS = {
    "para", "como", "esta", "este", "desde", "entre", "sobre", "con", "una",
    "los", "las", "del", "por", "que", "obra", "sin", "tambien", "cuando",
    "donde", "hacia", "estas", "estos", "ellos", "ellas", "solo", "menos",
    "fue", "eran", "pero", "para", "tiene", "tener", "este", "esta",
}

INFERENCE_SCHEMA = "faro-curatorial-inference-v1"
INFERENCE_FACETS = {
    "date", "event", "venue", "artist", "client", "collab", "publication",
    "text", "visual", "audio", "process", "period",
}

FACET_FIELDS = {
    "date": ("fecha", "date"),
    "artist": ("artista", "artist", "artista_principal"),
    "venue": ("venue", "lugar", "espacio"),
    "event": ("evento", "event", "festival"),
    "client": ("cliente", "client", "productora"),
    "collab": ("colaboracion", "collab", "colaboradores"),
    "period": ("periodo", "period"),
}


def _terms(value):
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]{5,}", normalized) if w not in STOPWORDS}


def feedback_index(rows):
    return {(str(r.get("source_id")), str(r.get("target_id"))): r
            for r in rows if r.get("source_id") and r.get("target_id")}


def _facet_value(item, facet):
    """Read a declared facet without treating free text as structured data."""
    for field in FACET_FIELDS.get(str(facet).lower(), ()):
        value = item.get(field)
        if isinstance(value, (list, tuple, set)):
            return " ".join(str(part) for part in value)
        if value is not None and str(value).strip():
            return str(value)
    return ""


def _fold(value):
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(c for c in normalized if not unicodedata.combining(c)).strip()


def board_scope(context):
    """Return the explicit board constraint, never an inferred one."""
    context = context or {}
    facet = str(context.get("facet") or "").lower()
    value = str(context.get("value") or "").strip()
    item_ids = {str(value) for value in context.get("item_ids", [])}
    if (facet not in FACET_FIELDS or not value) and not item_ids:
        return None
    return {"facet": facet if facet in FACET_FIELDS else "", "value": value,
            "item_ids": item_ids}


def learning_profile(rows):
    """Summarize human feedback as bounded facet weights.

    This is online evidence, not a pretend neural model: providers may propose
    hypotheses, while the artist's decisions change only the ranking of future
    candidates. The bounds prevent a small board from becoming a permanent
    filter.
    """
    counts = {}
    weights = {}
    for row in rows or []:
        facet = str(row.get("facet") or "unknown").lower()
        action = str(row.get("action") or "ignore").lower()
        bucket = counts.setdefault(facet, {"accept": 0, "correct": 0,
                                           "reject": 0, "ignore": 0})
        if action not in bucket:
            action = "ignore"
        bucket[action] += 1
        delta = {"accept": 1.5, "correct": 2.0, "reject": -1.5,
                 "ignore": -0.25}[action]
        weights[facet] = max(-8.0, min(8.0, weights.get(facet, 0.0) + delta))
    return {"schema": "faro-portfolio-learning-v1", "counts": counts,
            "weights": {key: round(value, 2) for key, value in weights.items()},
            "feedback_total": sum(sum(value.values()) for value in counts.values())}


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


def build_suggestions(source, items, selections=None, feedback=None, context=None, limit=24):
    selections = selections or {}
    feedback = feedback or []
    learned = feedback_index(feedback)
    profile = learning_profile(feedback)
    context = context or {}
    context_facet = str(context.get("facet", "")).lower()
    scope = board_scope(context)
    source_id = str(source.get("id", ""))
    source_terms = _terms(source.get("descripcion_original"))
    result = []
    suppressed_scope = 0
    for candidate in items:
        candidate_id = str(candidate.get("id", ""))
        if not candidate_id or candidate_id == source_id:
            continue
        if scope and scope["item_ids"] and candidate_id not in scope["item_ids"]:
            suppressed_scope += 1
            continue
        if scope and scope["facet"]:
            candidate_value = _facet_value(candidate, scope["facet"])
            if not candidate_value or _fold(scope["value"]) not in _fold(candidate_value):
                suppressed_scope += 1
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
            result.append(dict(common, facet="publication", relation_type="same_carousel", score=12,
                               reasons=["misma publicación/carrusel"]))
        if candidate.get("fecha") == source.get("fecha") and source.get("fecha"):
            result.append(dict(common, facet="date", relation_type="same_date_context", score=7,
                               reasons=["misma fecha"]))
        if shared:
            result.append(dict(common, facet="text", relation_type="shared_concept", score=min(6, len(shared)) + 2,
                               reasons=["conceptos compartidos: " + ", ".join(shared[:5])]))
        if candidate.get("tipo_contenido") == source.get("tipo_contenido"):
            result.append(dict(common, facet="format", relation_type="same_media_role", score=1,
                               reasons=["mismo tipo de medio"]))
    for row in result:
        prior = learned.get((source_id, row["item_id"]))
        facet_weight = profile.get("weights", {}).get(row["facet"], 0)
        row["score"] += facet_weight
        if facet_weight:
            row["reasons"].append("peso aprendido del tablero: %+.2f" % facet_weight)
        if prior and prior.get("action") in ("accept", "correct"):
            row["score"] += 14
            row["reasons"].append("relación aceptada anteriormente")
        elif prior and prior.get("action") == "reject":
            row["score"] -= 20
            row["reasons"].append("relación rechazada anteriormente")
        row["confidence"] = _confidence(row["score"], prior)
    suppressed = suppressed_scope + sum(1 for row in result if context_facet and row.get("facet") == context_facet)
    result = [row for row in result if row["score"] > 0 and row.get("facet") != context_facet]
    result.sort(key=lambda row: (-row["score"], row["item_id"], row["relation_type"]))
    return result[:limit], suppressed


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
        "ollama": bool(environment.get("OLLAMA_HOST") or environment.get("OLLAMA_BASE_URL")),
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


def inference_prompt(source, candidates, context=None):
    """Build the provider prompt; Python transports evidence, it does not infer."""
    context = context or {}
    compact = []
    for item in candidates:
        compact.append({
            "item_id": item.get("id"),
            "date": item.get("fecha"),
            "publication_id": item.get("publicacion_id"),
            "content_type": item.get("tipo_contenido"),
            "description_original": item.get("descripcion_original", ""),
            "asset_available": bool(item.get("asset_available")),
        })
    payload = {
        "task": "Inferir relaciones curatoriales multimodales sin inventar hechos.",
        "rules": [
            "Una hipótesis no es un hecho: expresa evidencia y desconocidos.",
            "No agrupes por una palabra aislada.",
            "Conserva la descripción original como dato, no como verdad.",
            "Usa solo item_id presentes en candidates.",
        ],
        "context": context,
        "source": {
            "item_id": source.get("id"),
            "date": source.get("fecha"),
            "publication_id": source.get("publicacion_id"),
            "content_type": source.get("tipo_contenido"),
            "description_original": source.get("descripcion_original", ""),
            "asset_available": bool(source.get("asset_available")),
        },
        "candidates": compact,
        "output": {
            "hypotheses": "array de {item_id, facet, relation_type, reason, evidence, confidence}",
            "unknowns": "array de datos que faltan",
        },
    }
    return json.dumps(payload, ensure_ascii=False)


def normalize_inference(raw, source_id, candidate_ids):
    """Validate model hypotheses without turning them into ledger truth."""
    if isinstance(raw, str):
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end < start:
            return {"schema": INFERENCE_SCHEMA, "source_id": source_id,
                    "hypotheses": [], "unknowns": ["provider_output_not_json"]}
        try:
            raw = json.loads(raw[start:end + 1])
        except ValueError:
            return {"schema": INFERENCE_SCHEMA, "source_id": source_id,
                    "hypotheses": [], "unknowns": ["provider_output_not_json"]}
    if not isinstance(raw, dict):
        raw = {}
    allowed = {str(value) for value in candidate_ids}
    hypotheses = []
    seen = set()
    for row in raw.get("hypotheses", raw.get("new_hypotheses", [])) or []:
        if not isinstance(row, dict):
            continue
        item_id = str(row.get("item_id", ""))
        facet = str(row.get("facet", "")).lower()
        reason = str(row.get("reason", "")).strip()
        if item_id not in allowed or facet not in INFERENCE_FACETS or not reason:
            continue
        key = (item_id, facet, str(row.get("relation_type", "related")))
        if key in seen:
            continue
        seen.add(key)
        hypotheses.append({
            "item_id": item_id,
            "facet": facet,
            "relation_type": str(row.get("relation_type", "related"))[:80],
            "reason": reason[:500],
            "evidence": [str(value)[:300] for value in row.get("evidence", [])]
            if isinstance(row.get("evidence", []), list) else [],
            "confidence": str(row.get("confidence", "low")).lower()
            if str(row.get("confidence", "low")).lower() in {"high", "medium", "low"}
            else "low",
            "status": "candidate",
        })
    unknowns = raw.get("unknowns", [])
    return {"schema": INFERENCE_SCHEMA, "source_id": str(source_id),
            "hypotheses": hypotheses[:48],
            "unknowns": [str(value)[:300] for value in unknowns[:24]]
            if isinstance(unknowns, list) else []}
