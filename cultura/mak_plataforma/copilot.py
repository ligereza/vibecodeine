"""Curatorial copilot contracts independent of any model provider."""
from __future__ import annotations

import json
import hashlib
import math
import re
import unicodedata


STOPWORDS = {
    "para", "como", "esta", "este", "desde", "entre", "sobre", "con", "una",
    "los", "las", "del", "por", "que", "obra", "sin", "tambien", "cuando",
    "donde", "hacia", "estas", "estos", "ellos", "ellas", "solo", "menos",
    "fue", "eran", "pero", "para", "tiene", "tener", "este", "esta",
}

INFERENCE_SCHEMA = "faro-curatorial-inference-v1"
VISION_SCHEMA = "faro-portfolio-vision-v1"
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

GTM_SCHEMA = "faro-gtm-map-v1"
GTM_DIMENSIONS = 32
_GTM_CACHE = {}


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


def _map_terms(item):
    values = [item.get("descripcion_original", ""), item.get("publicacion_id", ""),
              item.get("fecha", ""), item.get("tipo_contenido", "")]
    classification = item.get("classification") or {}
    if isinstance(classification, dict):
        values.extend(classification.values())
    vision = item.get("vision_features") or {}
    if isinstance(vision, dict):
        for field in ("visual_terms", "dominant_colors", "composition",
                      "motion_or_media"):
            values.extend(vision.get(field) or [])
    for facet in FACET_FIELDS:
        values.append(_facet_value(item, facet))
    return sorted(_terms(" ".join(str(value) for value in values)))


def _hash_feature(token):
    digest = hashlib.blake2b(str(token).encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % GTM_DIMENSIONS


def portfolio_vector(item):
    """Build a dependency-free feature vector for the latent map.

    The vector preserves declared metadata, time, media role and description
    as separate evidence channels. It is not an embedding and does not turn
    free text into fact; a future provider can replace this extractor without
    changing the map contract.
    """
    vector = [0.0] * GTM_DIMENSIONS
    terms = _map_terms(item)
    for term in terms:
        vector[_hash_feature("term:" + term)] += 1.0
    structured = [
        "content:" + str(item.get("tipo_contenido", "")),
        "publication:" + str(item.get("publicacion_id", "")),
        "date:" + str(item.get("fecha", "")),
        "media:" + ("available" if item.get("asset_available") else "missing"),
    ]
    for value in structured:
        vector[_hash_feature(value)] += 2.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 8) for value in vector]


def _vector_distance(left, right):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def _grid(width, height):
    return [(x, y) for y in range(height) for x in range(width)]


def _map_signature(items, feedback, width, height):
    compact = [
        (item.get("id"), item.get("fecha"), item.get("publicacion_id"),
         item.get("tipo_contenido"), item.get("descripcion_original", ""),
         item.get("classification", {}), item.get("vision_features", {}))
        for item in items
    ]
    feedback_compact = [(row.get("source_id"), row.get("target_id"),
                         row.get("action"), row.get("facet"))
                        for row in feedback or []]
    payload = json.dumps([compact, feedback_compact, width, height],
                         ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_gtm_map(items, feedback=None, width=8, height=6):
    """Fit a small elastic latent grid and return every item position.

    This is the local, dependency-free map engine: nodes form a rectangular
    latent topology, assignments are soft, and neighboring nodes are smoothed
    during fitting. It is deliberately called GTM in the contract while the
    feature extractor remains replaceable and explicitly non-semantic.
    """
    width = max(3, min(int(width), 16))
    height = max(3, min(int(height), 12))
    valid_items = [item for item in items or [] if item.get("id")]
    feedback = feedback or []
    signature = _map_signature(valid_items, feedback, width, height)
    cached = _GTM_CACHE.get(signature)
    if cached is not None:
        return cached
    vectors = [portfolio_vector(item) for item in valid_items]
    vector_index = {str(item.get("id")): index
                    for index, item in enumerate(valid_items)}
    for row in feedback:
        source_index = vector_index.get(str(row.get("source_id", "")))
        target_index = vector_index.get(str(row.get("target_id", "")))
        if source_index is None or target_index is None:
            continue
        action = str(row.get("action", "")).lower()
        if action in {"accept", "correct"}:
            strength = 0.18 if action == "accept" else 0.24
        elif action == "reject":
            strength = -0.12
        else:
            continue
        source_vector = vectors[source_index]
        target_vector = vectors[target_index]
        delta = [target - source for source, target in zip(source_vector, target_vector)]
        vectors[source_index] = [source + strength * change
                                  for source, change in zip(source_vector, delta)]
        vectors[target_index] = [target - strength * change
                                 for target, change in zip(target_vector, delta)]
    nodes = _grid(width, height)
    codebooks = []
    if vectors:
        chosen = [0]
        while len(chosen) < len(nodes):
            next_index = max(
                (index for index in range(len(vectors)) if index not in chosen),
                key=lambda index: min(_vector_distance(vectors[index], vectors[other])
                                      for other in chosen),
                default=chosen[-1])
            chosen.append(next_index)
        codebooks = [list(vectors[index % len(vectors)]) for index in chosen]
    else:
        codebooks = [[0.0] * GTM_DIMENSIONS for _ in nodes]
    for iteration in range(6):
        sigma = max(0.55, max(width, height) * (0.34 - iteration * 0.045))
        learning_rate = 0.42 - iteration * 0.045
        accumulators = [[0.0] * GTM_DIMENSIONS for _ in nodes]
        weights = [0.0] * len(nodes)
        for vector in vectors:
            bmu = min(range(len(codebooks)),
                      key=lambda index: _vector_distance(vector, codebooks[index]))
            bx, by = nodes[bmu]
            for node_index, (x, y) in enumerate(nodes):
                distance = math.sqrt((x - bx) ** 2 + (y - by) ** 2)
                influence = math.exp(-(distance ** 2) / (2 * sigma ** 2))
                weights[node_index] += influence
                for dimension, value in enumerate(vector):
                    accumulators[node_index][dimension] += influence * value
        for node_index, codebook in enumerate(codebooks):
            if not weights[node_index]:
                continue
            average = [value / weights[node_index]
                       for value in accumulators[node_index]]
            codebooks[node_index] = [value * (1 - learning_rate)
                                     + average[dimension] * learning_rate
                                     for dimension, value in enumerate(codebook)]
    positions = []
    for item, vector in zip(valid_items, vectors):
        raw = [math.exp(-_vector_distance(vector, codebook) / 0.07)
               for codebook in codebooks]
        total = sum(raw) or 1.0
        x = sum(weight * nodes[index][0] for index, weight in enumerate(raw)) / total
        y = sum(weight * nodes[index][1] for index, weight in enumerate(raw)) / total
        bmu = min(range(len(codebooks)), key=lambda index: _vector_distance(vector, codebooks[index]))
        distance = _vector_distance(vector, codebooks[bmu])
        positions.append({
            "item_id": str(item.get("id")), "x": round(x / max(1, width - 1), 6),
            "y": round(y / max(1, height - 1), 6), "bmu": list(nodes[bmu]),
            "distance": round(distance, 6),
            "confidence": "high" if distance < 0.28 else "medium" if distance < 0.5 else "low",
            "features": _map_terms(item)[:12],
        })
    result = {"schema": GTM_SCHEMA, "engine": "elastic_latent_grid",
        "feature_extractor": "declared_metadata_plus_hashed_terms_plus_vision",
              "grid": {"width": width, "height": height},
              "items": positions, "count": len(positions)}
    _GTM_CACHE.clear()
    _GTM_CACHE[signature] = result
    return result


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
        "vision_features_present": bool(item.get("vision_features")),
    }


def normalize_vision(raw, item_id, provider, evidence=None):
    """Keep only visual observations; entity claims never enter the map."""
    if isinstance(raw, str):
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end < start:
            raw = {}
        else:
            try:
                raw = json.loads(raw[start:end + 1])
            except ValueError:
                raw = {}
    if not isinstance(raw, dict):
        raw = {}
    features = raw.get("features") if isinstance(raw.get("features"), dict) else raw

    def values(field, limit, size=100):
        value = features.get(field, [])
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            return []
        result = []
        for entry in value:
            text = str(entry).strip()
            if text and text not in result:
                result.append(text[:size])
        return result[:limit]

    confidence = str(raw.get("confidence", features.get("confidence", "low"))).lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    unknowns = raw.get("unknowns", [])
    if isinstance(unknowns, str):
        unknowns = [unknowns]
    if not isinstance(unknowns, list):
        unknowns = []
    unknowns = [str(value).strip()[:180] for value in unknowns if str(value).strip()][:16]
    if not unknowns:
        unknowns = values("unknowns", 16, 180) or values("limitations", 16, 180)
    return {
        "schema": VISION_SCHEMA,
        "item_id": str(item_id),
        "provider": str(provider),
        "features": {
            "visual_terms": values("visual_terms", 16),
            "dominant_colors": values("dominant_colors", 8, 80),
            "composition": values("composition", 12),
            "motion_or_media": values("motion_or_media", 12),
        },
        "unknowns": unknowns,
        "confidence": confidence,
        "status": "candidate",
        "promotion": "none",
        "evidence": [str(path)[:300] for path in (evidence or []) if path][:8],
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
