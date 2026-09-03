"""IRIS ordering engine, independent of any model provider.

The ``portfolio`` names in schemas and API-compatible callers are historical
domain labels for downstream portfolio material. This module is not a
portfolio publisher: it proposes defensible orders/relations for the internal
MAK system IRIS (Atlas Campo del Orden) and preserves the human decision gate.
"""
from __future__ import annotations

import json
import hashlib
import math
import random
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
ATLAS_SCHEMA = "faro-portfolio-atlas-v1"
ORDER_FIELD_SCHEMA = "faro-ordering-field-v2"
GTM_DIMENSIONS = 32
GTM_FIT_LIMIT = 1024
_GTM_CACHE = {}
_GTM_VECTOR_CACHE = {}
_ORDER_FIELD_CACHE = {}


def _terms(value):
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]{5,}", normalized) if w not in STOPWORDS}


def dedupe_feedback(rows):
    """Collapse repeated human actions for learning without deleting history."""
    latest = {}
    passthrough = []
    undo_barriers = {}
    indexed = []
    for row in rows or []:
        source = str(row.get("source_id") or "").strip()
        target = str(row.get("target_id") or "").strip()
        if not source or not target:
            passthrough.append(row)
            continue
        signal_key = (source, target, str(row.get("facet") or "unknown").lower(),
                      str(row.get("relation") or "related"))
        indexed.append((signal_key, row))
        if str(row.get("action") or "").lower() == "undo":
            undo_barriers[signal_key] = len(indexed) - 1
            continue
        key = (source, target, str(row.get("action") or "").lower(),
               str(row.get("facet") or "unknown").lower(),
               str(row.get("relation") or "related"))
        latest[key] = len(indexed) - 1
    return [
        *passthrough,
        *[row for index, (signal_key, row) in enumerate(indexed)
          if str(row.get("action") or "").lower() != "undo"
          and index > undo_barriers.get(signal_key, -1)
          and latest.get((signal_key[0], signal_key[1],
                         str(row.get("action") or "").lower(),
                         signal_key[2], signal_key[3])) == index],
    ]


def feedback_index(rows):
    return {(str(r.get("source_id")), str(r.get("target_id"))): r
            for r in dedupe_feedback(rows)
            if r.get("source_id") and r.get("target_id")}


def feedback_facet_index(rows):
    """Index human feedback by relation channel, not only by item pair."""
    return {
        (str(row.get("source_id")), str(row.get("target_id")),
         str(row.get("facet") or "unknown").lower()): row
        for row in dedupe_feedback(rows)
        if row.get("source_id") and row.get("target_id")
    }


def _facet_value(item, facet):
    """Read a declared facet without treating free text as structured data."""
    for field in FACET_FIELDS.get(str(facet).lower(), ()):
        value = item.get(field)
        if isinstance(value, (list, tuple, set)):
            return " ".join(str(part) for part in value)
        if value is not None and str(value).strip():
            return str(value)
    return ""


def _facet_values(item, facet):
    """Return exact declared values for one facet, never values guessed from prose."""
    values = []
    for field in FACET_FIELDS.get(str(facet).lower(), ()):
        raw = item.get(field)
        if isinstance(raw, (list, tuple, set)):
            values.extend(raw)
        elif raw is not None:
            values.append(raw)
    entities = item.get("entities")
    if isinstance(entities, dict):
        raw = entities.get(str(facet).lower())
        if isinstance(raw, (list, tuple, set)):
            values.extend(raw)
        elif raw is not None:
            values.append(raw)
    result = []
    seen = set()
    for value in values:
        value = str(value or "").strip()
        folded = _fold(value)
        if not folded or folded in seen:
            continue
        seen.add(folded)
        result.append(value)
    return result


def _explicit_overlap(source, candidate, facet):
    target = {_fold(value): value for value in _facet_values(candidate, facet)}
    return [value for value in _facet_values(source, facet)
            if _fold(value) in target]


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
    rows = dedupe_feedback(rows)
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


def review_profile(rows):
    """Summarize human candidate decisions without turning them into facts."""
    decisions = {"accept": 0, "revise": 0, "reject": 0}
    by_facet = {}
    signals = {}
    reviewed_sources = []
    for row in rows or []:
        decision = str(row.get("decision") or "").lower()
        if decision not in decisions:
            continue
        decisions[decision] += 1
        source_id = str(row.get("source_id") or "").strip()
        if source_id and source_id not in reviewed_sources:
            reviewed_sources.append(source_id)
        fields = row.get("context_fields") or {}
        facets = [str(field).lower() for field in fields if str(field).strip()]
        if not facets:
            facets = ["candidate"]
        for facet in facets:
            bucket = by_facet.setdefault(facet, {"accept": 0, "revise": 0,
                                                   "reject": 0})
            bucket[decision] += 1
        if isinstance(fields, dict):
            for field, values in fields.items():
                field = str(field).lower().strip()
                if not field:
                    continue
                if not isinstance(values, (list, tuple, set)):
                    values = [values]
                field_signals = signals.setdefault(field, {})
                seen_values = set()
                for value in values:
                    value = str(value or "").strip()[:240]
                    if not value or value in seen_values:
                        continue
                    seen_values.add(value)
                    value_counts = field_signals.setdefault(
                        value, {"accept": 0, "revise": 0, "reject": 0})
                    value_counts[decision] += 1
    return {
        "schema": "faro-portfolio-candidate-learning-v1",
        "decision_counts": decisions,
        "decision_total": sum(decisions.values()),
        "by_facet": by_facet,
        "context_signals": signals,
        "reviewed_sources": reviewed_sources,
        "promotion": "none",
        "next": "usar estas señales para proponer contexto; no convertirlas en hechos",
    }


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


def _vector_distance(left, right, weights=None):
    if weights is None:
        # The GTM fit calls this millions of times on 32-dimensional vectors.
        # Keep the weighted path explicit, but use the C-level implementation
        # for the common unweighted distance instead of allocating a weights
        # list and walking the generator in Python.
        return math.dist(left, right)
    weights = weights[:min(len(left), len(right))]
    return math.sqrt(sum(weight * (a - b) ** 2
                         for a, b, weight in zip(left, right, weights)))


def _grid(width, height):
    return [(x, y) for y in range(height) for x in range(width)]


def _map_signature(items, feedback, width, height):
    compact = [
        (item.get("id"), item.get("fecha"), item.get("publicacion_id"),
         item.get("tipo_contenido"), item.get("descripcion_original", ""),
         item.get("classification", {}), item.get("selection", ""),
         item.get("vision_features", {}))
        for item in items
    ]
    feedback_compact = [(row.get("source_id"), row.get("target_id"),
                         row.get("action"), row.get("facet"))
                        for row in feedback or []]
    payload = json.dumps([compact, feedback_compact, width, height],
                         ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stable_topology_items(items):
    """Remove only live triage labels from the geometry input."""
    stable = []
    for item in items or []:
        row = dict(item)
        classification = row.get("classification")
        if isinstance(classification, dict) and "triage" in classification:
            classification = dict(classification)
            classification.pop("triage", None)
            row["classification"] = classification
        row["selection"] = ""
        stable.append(row)
    return stable


def _ordering_revision(items, feedback=None):
    labels = [(str(item.get("id") or ""), _triage_label(item))
              for item in items or [] if item.get("id")]
    feedback_state = [
        (str(row.get("source_id") or ""), str(row.get("target_id") or ""),
         str(row.get("action") or "").lower(),
         str(row.get("facet") or "unknown").lower(),
         str(row.get("relation") or "related"))
        for row in dedupe_feedback(feedback or [])
    ]
    payload = json.dumps([labels, feedback_state], ensure_ascii=False,
                         separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _prediction_uncertainty(probabilities):
    values = sorted((max(0.0, float(value))
                     for value in probabilities.values()), reverse=True)
    entropy = -sum(value * math.log(value) for value in values if value > 0)
    normalized = entropy / math.log(max(2, len(ORDER_LABELS)))
    margin = values[0] - values[1] if len(values) > 1 else values[0]
    return round(normalized, 6), round(margin, 6)


ORDER_LABELS = ("work", "record", "review", "discard")
ORDER_NEIGHBOR_LIMIT = 128
ORDER_MIN_COVERAGE = 0.01
ORDER_ACTIVE_POOL_LIMIT = 512
DISTANCE_SCHEMA = "faro-ordering-distance-v1"
DISTANCE_MIN_WEIGHT = 0.55
DISTANCE_MAX_WEIGHT = 1.8
DISTANCE_PAIR_LIMIT = 512


def _triage_label(item):
    classification = item.get("classification") or {}
    declared = classification.get("triage") if isinstance(classification, dict) else ""
    if declared in ORDER_LABELS:
        return declared
    return {
        "seleccionar": "work",
        "descartar": "discard",
    }.get(str(item.get("selection") or "").lower(), "")


def _triage_label_source(item):
    classification = item.get("classification") or {}
    declared = classification.get("triage") if isinstance(classification, dict) else ""
    if declared in ORDER_LABELS:
        return declared, "triage"
    selection = str(item.get("selection") or "").lower()
    label = {"seleccionar": "work", "descartar": "discard"}.get(selection, "")
    return label, "selection"


def _sample_pair_ids(values, limit=32):
    values = sorted({str(value) for value in values if str(value)})
    if len(values) <= limit:
        return values
    step = max(1, math.ceil(len(values) / limit))
    selected = values[::step][:limit - 1]
    if values[-1] not in selected:
        selected.append(values[-1])
    return selected


def _distance_constraints(items, vectors, feedback=None):
    by_id = {str(item.get("id")): item for item in items or []
             if item.get("id") and str(item.get("id")) in vectors}
    positive = set()
    negative = set()

    def add_pair(left, right, bucket):
        left, right = str(left), str(right)
        if not left or not right or left == right:
            return
        bucket.add(tuple(sorted((left, right))))

    grouped = {}
    for item_id, item in by_id.items():
        label = _triage_label(item)
        if label:
            grouped.setdefault(label, []).append(item_id)
    for group in grouped.values():
        sampled = _sample_pair_ids(group)
        for index, left in enumerate(sampled):
            for right in sampled[index + 1:]:
                add_pair(left, right, positive)
    labels = sorted(grouped)
    for index, left_label in enumerate(labels):
        for right_label in labels[index + 1:]:
            left_ids = _sample_pair_ids(grouped[left_label])
            right_ids = _sample_pair_ids(grouped[right_label])
            for left in left_ids:
                for right in right_ids:
                    add_pair(left, right, negative)
    for row in dedupe_feedback(feedback or []):
        action = str(row.get("action") or "").lower()
        bucket = positive if action in {"accept", "correct"} else negative if action == "reject" else None
        if bucket is not None:
            add_pair(row.get("source_id"), row.get("target_id"), bucket)
    conflicts = positive & negative
    positive = sorted(positive - conflicts)[:DISTANCE_PAIR_LIMIT]
    negative = sorted(negative - conflicts)[:DISTANCE_PAIR_LIMIT]
    return {"positive": positive, "negative": negative,
            "conflicted": sorted(conflicts)}


def ordering_distance_profile(items, vectors=None, feedback=None):
    """Learn a bounded pairwise metric over the existing structural vector."""
    vectors = vectors or {
        str(item.get("id")): portfolio_vector(item)
        for item in items or [] if item.get("id")
    }
    constraints = _distance_constraints(items, vectors, feedback=feedback)
    positive = constraints["positive"]
    negative = constraints["negative"]
    weights = [1.0] * GTM_DIMENSIONS
    positive_mean = [0.0] * GTM_DIMENSIONS
    negative_mean = [0.0] * GTM_DIMENSIONS
    positive_count = 0
    negative_count = 0

    def add_difference(pair, target):
        vector_left, vector_right = vectors.get(pair[0]), vectors.get(pair[1])
        if not vector_left or not vector_right:
            return False
        for index, value in enumerate(abs(a - b)
                                      for a, b in zip(vector_left, vector_right)):
            target[index] += value
        return True

    for pair in positive:
        positive_count += int(add_difference(pair, positive_mean))
    for pair in negative:
        negative_count += int(add_difference(pair, negative_mean))
    observed_labels = len({
        _triage_label(item) for item in items or [] if _triage_label(item)
    })
    metric_ready = positive_count >= 2 and negative_count >= 2
    if metric_ready:
        shrink = min(1.0, min(positive_count, negative_count) / 8.0)
        for index in range(GTM_DIMENSIONS):
            positive_value = positive_mean[index] / positive_count
            negative_value = negative_mean[index] / negative_count
            contrast = ((negative_value - positive_value)
                        / (negative_value + positive_value + 0.25))
            weights[index] = max(
                DISTANCE_MIN_WEIGHT,
                min(DISTANCE_MAX_WEIGHT, 1.0 + 0.8 * contrast * shrink))
    method = "pair_contrast" if metric_ready else "identity"
    confidence = "alta" if min(positive_count, negative_count) >= 12 else (
        "media" if metric_ready else "baja")
    ranked_dimensions = sorted(
        range(GTM_DIMENSIONS), key=lambda index: abs(weights[index] - 1.0),
        reverse=True)
    return {
        "schema": DISTANCE_SCHEMA,
        "method": method,
        "confidence": confidence,
        "metric_ready": metric_ready,
        "observed_labels": observed_labels,
        "pair_support": {"positive": positive_count,
                          "negative": negative_count,
                          "conflicted": len(constraints["conflicted"])},
        "weights": [round(value, 6) for value in weights],
        "top_dimensions": [
            {"index": index, "weight": round(weights[index], 6)}
            for index in ranked_dimensions[:6]
            if abs(weights[index] - 1.0) >= 0.01
        ],
        "promotion": "none",
    }


def ordering_profile(items):
    """Return bounded Bayesian priors from human ordering decisions."""
    counts = {label: 0 for label in ORDER_LABELS}
    for item in items or []:
        label = _triage_label(item)
        if label:
            counts[label] += 1
    total = sum(counts.values())
    denominator = total + len(ORDER_LABELS)
    probabilities = {
        label: round((counts[label] + 1) / denominator, 6)
        for label in ORDER_LABELS
    }
    return {
        "schema": "faro-ordering-learning-v1",
        "counts": counts,
        "labeled": total,
        "unlabeled": max(0, len(items or []) - total),
        "coverage": round(total / len(items), 6) if items else 0.0,
        "learning_ready": bool(items) and total / len(items) >= ORDER_MIN_COVERAGE,
        "missing_labels": [label for label in ORDER_LABELS if not counts[label]],
        "probabilities": probabilities,
        "method": "laplace_prior_plus_nearest_labeled_vectors",
    }


def ordering_seed(items, limit=24):
    """Select a balanced human-review seed without assigning a label."""
    labeled_publications = {
        str(item.get("publicacion_id")) for item in items or []
        if item.get("publicacion_id") and _triage_label(item)
    }
    unlabeled = [item for item in items or []
                 if item.get("id") and not _triage_label(item)
                 and item.get("asset_available")
                 and str(item.get("publicacion_id") or "") not in labeled_publications]
    buckets = {}
    for item in unlabeled:
        content_type = str(item.get("tipo_contenido") or "unknown")
        month = str(item.get("fecha") or "unknown")[:7]
        visual = bool(item.get("vision_features"))
        description = bool(str(item.get("descripcion_original") or "").strip())
        key = (content_type, month, visual, description)
        buckets.setdefault(key, []).append(item)
    for bucket in buckets.values():
        bucket.sort(key=lambda item: str(item.get("id")))
    selected = []
    selected_publications = set()
    target = max(1, int(limit))
    keys = sorted(buckets)
    while keys and len(selected) < target:
        next_keys = []
        for key in keys:
            if len(selected) >= target:
                break
            bucket = buckets[key]
            item = None
            while bucket and item is None:
                candidate = bucket.pop(0)
                publication_id = str(candidate.get("publicacion_id") or "")
                if publication_id and publication_id in selected_publications:
                    continue
                item = candidate
            if item:
                publication_id = str(item.get("publicacion_id") or "")
                if publication_id:
                    selected_publications.add(publication_id)
                selected.append({
                    "item_id": str(item.get("id")),
                    "content_type": item.get("tipo_contenido") or "unknown",
                    "date": item.get("fecha") or "",
                    "publication_id": item.get("publicacion_id") or "",
                    "asset_available": bool(item.get("asset_available")),
                    "has_description": bool(str(item.get("descripcion_original") or "").strip()),
                    "has_vision": bool(item.get("vision_features")),
                    "review_scope": "record_or_review",
                    "status": "human_candidate",
                })
            if bucket:
                next_keys.append(key)
        keys = next_keys
    return selected


def active_ordering_seed(items, map_surface, limit=24):
    """Choose the next human cases by uncertainty, coverage and diversity."""
    positions = {
        str(row.get("item_id")): row for row in map_surface.get("items", [])
        if isinstance(row, dict) and row.get("item_id")
    }
    candidates = []
    labeled_publications = {
        str(item.get("publicacion_id")) for item in items or []
        if item.get("publicacion_id") and _triage_label(item)
    }
    for item in items or []:
        item_id = str(item.get("id") or "")
        if not item_id or _triage_label(item) or not item.get("asset_available"):
            continue
        position = positions.get(item_id)
        if not position:
            continue
        publication_id = str(item.get("publicacion_id") or "")
        if publication_id and publication_id in labeled_publications:
            continue
        unit_id = publication_id or item_id
        prediction = position.get("triage_prediction") or {}
        uncertainty = float(prediction.get("uncertainty", 1.0))
        coverage_gap = float(prediction.get("coverage_gap", 1.0))
        evidence_bonus = 0.04 * bool(item.get("vision_features"))
        evidence_bonus += 0.03 * bool(str(
            item.get("descripcion_original") or "").strip())
        base_priority = min(
            1.0, uncertainty * 0.62 + coverage_gap * 0.31 + evidence_bonus)
        candidates.append({
            "item": item,
            "position": position,
            "base_priority": base_priority,
            "uncertainty": uncertainty,
            "coverage_gap": coverage_gap,
            "probabilities": dict(prediction.get("probabilities") or {}),
            "unit_id": unit_id,
        })
    by_unit = {}
    unit_counts = {}
    for candidate in candidates:
        unit_id = candidate["unit_id"]
        unit_counts[unit_id] = unit_counts.get(unit_id, 0) + 1
        previous = by_unit.get(unit_id)
        if previous is None or candidate["base_priority"] > previous["base_priority"]:
            by_unit[unit_id] = candidate
    candidates = list(by_unit.values())
    for candidate in candidates:
        candidate["publication_media_count"] = unit_counts[candidate["unit_id"]]
    if not candidates:
        return ordering_seed(items, limit=limit)
    candidates.sort(key=lambda row: (
        -row["base_priority"], str(row["item"].get("id"))))
    selected = []
    target = max(1, int(limit))
    pool_size = min(ORDER_ACTIVE_POOL_LIMIT, max(target * 16, 256))
    remaining = candidates[:pool_size]
    while remaining and len(selected) < target:
        best_index = 0
        best_score = -1.0
        for index, candidate in enumerate(remaining):
            if selected:
                nearest = min(math.sqrt(
                    (candidate["position"]["x"] - other["position"]["x"]) ** 2
                    + (candidate["position"]["y"] - other["position"]["y"]) ** 2)
                    for other in selected)
                diversity = min(1.0, nearest / math.sqrt(2.0))
            else:
                diversity = candidate["coverage_gap"]
            score = candidate["base_priority"] * 0.78 + diversity * 0.22
            if score > best_score:
                best_index, best_score = index, score
        chosen = remaining.pop(best_index)
        chosen["priority"] = round(best_score, 6)
        selected.append(chosen)
    result = []
    for row in selected:
        item = row["item"]
        if row["coverage_gap"] >= 0.6:
            reason = "zona_sin_cobertura"
        elif row["uncertainty"] >= 0.75:
            reason = "frontera_ambigua"
        else:
            reason = "muestra_diversa"
        result.append({
            "item_id": str(item.get("id")),
            "content_type": item.get("tipo_contenido") or "unknown",
            "date": item.get("fecha") or "",
            "publication_id": item.get("publicacion_id") or "",
            "publication_media_count": row["publication_media_count"],
            "asset_available": bool(item.get("asset_available")),
            "has_description": bool(str(
                item.get("descripcion_original") or "").strip()),
            "has_vision": bool(item.get("vision_features")),
            "review_scope": "record_or_review",
            "status": "human_candidate",
            "selection_method": "active_information_gain",
            "priority": row["priority"],
            "uncertainty": round(row["uncertainty"], 6),
            "coverage_gap": round(row["coverage_gap"], 6),
            "probabilities": row["probabilities"],
            "reason": reason,
        })
    return result


def _triage_prediction(vector, labeled_vectors, prior_counts,
                       labeled_total=None, item_total=None,
                       distance_weights=None):
    scores = {label: float(prior_counts.get(label, 0)) + 1.0
              for label in ORDER_LABELS}
    neighbors = []
    for index, label, candidate_vector in labeled_vectors:
        distance = _vector_distance(vector, candidate_vector,
                                    weights=distance_weights)
        neighbors.append((distance, index, label))
    neighbors.sort(key=lambda row: (row[0], row[1]))
    for distance, index, label in neighbors[:8]:
        scores[label] += 1.0 / (0.08 + distance)
    neighbor_labels = [label for _, _, label in neighbors[:8]]
    neighbor_counts = {label: neighbor_labels.count(label)
                       for label in ORDER_LABELS}
    observed_labels = sum(1 for count in neighbor_counts.values() if count)
    total = sum(scores.values()) or 1.0
    probabilities = {
        label: round(value / total, 6)
        for label, value in scores.items()
    }
    recommended = max(probabilities, key=probabilities.get)
    confidence = "baja"
    evidence_count = len(neighbors)
    coverage = (labeled_total / item_total
                if labeled_total is not None and item_total else 0.0)
    learning_ready = coverage >= ORDER_MIN_COVERAGE
    if (learning_ready and evidence_count >= 5 and observed_labels >= 2
            and probabilities[recommended] >= 0.68):
        confidence = "alta"
    elif (learning_ready and evidence_count >= 2 and observed_labels >= 2
          and probabilities[recommended] >= 0.52):
        confidence = "media"
    return {
        "recommended": recommended,
        "confidence": confidence,
        "probabilities": probabilities,
        "evidence_count": evidence_count,
        "observed_labels": observed_labels,
        "neighbor_counts": neighbor_counts,
        "coverage": round(coverage, 6),
        "learning_ready": learning_ready,
        "neighbors": [index for _, index, _ in neighbors[:3]],
        "prior_counts": dict(prior_counts),
    }


def _apply_ordering_field(positions, items):
    """Apply a soft human-decision field without replacing GTM coordinates."""
    anchors = {label: [] for label in ORDER_LABELS}
    for item, position in zip(items, positions):
        label = _triage_label(item)
        if label:
            anchors[label].append(position)
    anchor_positions = {}
    for label, rows in anchors.items():
        if len(rows) < 2:
            continue
        anchor_positions[label] = {
            "x": round(sum(row["x"] for row in rows) / len(rows), 6),
            "y": round(sum(row["y"] for row in rows) / len(rows), 6),
            "count": len(rows),
        }
    moved = 0
    displacement_total = 0.0
    for item, position in zip(items, positions):
        if _triage_label(item):
            continue
        prediction = position.get("triage_prediction") or {}
        anchor = anchor_positions.get(prediction.get("recommended"))
        if not anchor or prediction.get("confidence") not in {"media", "alta"}:
            continue
        alpha = 0.08 if prediction["confidence"] == "alta" else 0.04
        old_x, old_y = position["x"], position["y"]
        position["x"] = round(old_x + (anchor["x"] - old_x) * alpha, 6)
        position["y"] = round(old_y + (anchor["y"] - old_y) * alpha, 6)
        displacement_total += math.sqrt(
            (position["x"] - old_x) ** 2 + (position["y"] - old_y) ** 2)
        moved += 1
    return {
        "schema": "faro-ordering-field-v1",
        "method": "soft_anchor_attraction",
        "anchors": anchor_positions,
        "moved_items": moved,
        "mean_displacement": round(displacement_total / moved, 6) if moved else 0.0,
    }


def _ordering_evaluation(items, vector_by_id, distance_weights=None,
                         method="leave_one_out_on_stable_feature_vectors"):
    labeled = []
    for item in items or []:
        item_id = str(item.get("id") or "")
        label = _triage_label(item)
        vector = vector_by_id.get(item_id)
        if label and vector:
            labeled.append((item_id, label, vector))
    support = {label: 0 for label in ORDER_LABELS}
    confusion = {label: {candidate: 0 for candidate in ORDER_LABELS}
                 for label in ORDER_LABELS}
    correct = 0
    for item_id, actual, vector in labeled:
        peers = [row for row in labeled if row[0] != item_id]
        peer_counts = {label: 0 for label in ORDER_LABELS}
        for _, label, _ in peers:
            peer_counts[label] += 1
        prediction = _triage_prediction(
            vector, peers, peer_counts,
            labeled_total=len(peers), item_total=len(items or []),
            distance_weights=distance_weights)
        recommended = prediction["recommended"]
        support[actual] += 1
        confusion[actual][recommended] += 1
        correct += int(recommended == actual)
    evaluated = len(labeled)
    recalls = {
        label: round(confusion[label][label] / support[label], 6)
        for label in ORDER_LABELS if support[label]
    }
    macro_recall = (round(sum(recalls.values()) / len(recalls), 6)
                    if recalls else 0.0)
    coverage = evaluated / len(items) if items else 0.0
    observed_classes = sum(1 for value in support.values() if value)
    active_learning_ready = evaluated >= 8 and observed_classes >= 2
    automation_ready = (
        evaluated >= 100 and coverage >= 0.01
        and all(value >= 5 for value in support.values())
        and macro_recall >= 0.75)
    return {
        "schema": "faro-ordering-evaluation-v1",
        "method": method,
        "evaluated": evaluated,
        "accuracy": round(correct / evaluated, 6) if evaluated else 0.0,
        "macro_recall": macro_recall,
        "support": support,
        "observed_classes": observed_classes,
        "missing_classes": [label for label, value in support.items() if not value],
        "confusion": confusion,
        "active_learning_ready": active_learning_ready,
        "automation_ready": automation_ready,
        "automation_gate": {
            "minimum_labels": 100,
            "minimum_coverage": 0.01,
            "minimum_per_class": 5,
            "minimum_macro_recall": 0.75,
        },
        "promotion": "none",
    }


def _ordering_metric_summary(evaluation):
    return {key: evaluation.get(key, 0.0)
            for key in ("evaluated", "accuracy", "macro_recall")}


def replay_ordering_evaluation(items, vector_by_id=None, distance_weights=None,
                               include_cases=True, label_source="all"):
    """Replay known human triage without letting the answer leak into itself.

    This is a diagnostic surface for bounded samples.  It keeps the existing
    leave-one-out judge, reports abstentions separately from wrong guesses, and
    never promotes a result or mutates an item.
    """
    if label_source not in {"all", "triage", "selection"}:
        raise ValueError("label_source must be all, triage or selection")
    vector_by_id = vector_by_id or {
        str(item.get("id")): portfolio_vector(item)
        for item in items or [] if item.get("id")
    }
    labeled = []
    for item in items or []:
        item_id = str(item.get("id") or "")
        label, source = _triage_label_source(item)
        vector = vector_by_id.get(item_id)
        if (item_id and label and vector
                and (label_source == "all" or source == label_source)):
            labeled.append((item_id, label, vector, source))
    support = {label: 0 for label in ORDER_LABELS}
    confusion = {
        label: {candidate: 0 for candidate in (*ORDER_LABELS, "abstain")}
        for label in ORDER_LABELS
    }
    cases = []
    correct = 0
    committed = 0
    abstained = 0
    source_counts = {source: 0 for source in ("triage", "selection")}
    for item_id, actual, vector, source in labeled:
        source_counts[source] += 1
        peers = [row[:3] for row in labeled if row[0] != item_id]
        peer_counts = {label: 0 for label in ORDER_LABELS}
        for _, label, _ in peers:
            peer_counts[label] += 1
        prediction = _triage_prediction(
            vector, peers, peer_counts,
            labeled_total=len(peers), item_total=len(items or []),
            distance_weights=distance_weights)
        uncertainty, margin = _prediction_uncertainty(
            prediction["probabilities"])
        abstain = prediction["confidence"] == "baja"
        outcome = "abstain" if abstain else prediction["recommended"]
        support[actual] += 1
        confusion[actual][outcome] += 1
        if abstain:
            abstained += 1
        else:
            committed += 1
            correct += int(outcome == actual)
        if include_cases:
            cases.append({
                "item_id": item_id,
                "expected": actual,
                "label_source": source,
                "predicted": outcome,
                "abstained": abstain,
                "confidence": prediction["confidence"],
                "uncertainty": uncertainty,
                "margin": margin,
                "evidence_count": prediction["evidence_count"],
                "neighbors": prediction["neighbors"],
            })
    evaluated = len(labeled)
    coverage = committed / evaluated if evaluated else 0.0
    accuracy = correct / evaluated if evaluated else 0.0
    selective_accuracy = correct / committed if committed else 0.0
    result = {
        "schema": "faro-ordering-replay-v1",
        "method": "leave_one_out_with_confidence_gate",
        "label_source": label_source,
        "evaluated": evaluated,
        "committed": committed,
        "abstained": abstained,
        "coverage": round(coverage, 6),
        "abstention_rate": round(abstained / evaluated, 6) if evaluated else 0.0,
        "accuracy": round(accuracy, 6),
        "selective_accuracy": round(selective_accuracy, 6),
        "support": support,
        "source_counts": source_counts,
        "confusion": confusion,
        "cases": cases if include_cases else [],
        "promotion": "none",
        "next_action": "human_review",
    }
    if label_source == "all":
        result["metrics_by_source"] = {
            source: replay_ordering_evaluation(
                items, vector_by_id=vector_by_id,
                distance_weights=distance_weights, include_cases=False,
                label_source=source)
            for source in ("triage", "selection")
        }
    return result


def _stable_ordering_surface(base_surface, items, feedback=None):
    topology_id = str((base_surface.get("atlas") or {}).get(
        "topology_id") or "unknown")
    feedback = dedupe_feedback(feedback or [])
    revision = _ordering_revision(items, feedback)
    cache_key = "%s:%s" % (topology_id, revision)
    cached = _ORDER_FIELD_CACHE.get(cache_key)
    if cached is not None:
        return cached
    by_id = {str(item.get("id")): item for item in items or []
             if item.get("id")}
    positions = [dict(row) for row in base_surface.get("items", [])]
    ordering = ordering_profile(items)
    vector_by_id = _GTM_VECTOR_CACHE.get(topology_id, {})
    candidate_distance_profile = ordering_distance_profile(
        items, vectors=vector_by_id, feedback=feedback)
    baseline_evaluation = _ordering_evaluation(items, vector_by_id)
    candidate_evaluation = _ordering_evaluation(
        items, vector_by_id,
        distance_weights=candidate_distance_profile["weights"],
        method="leave_one_out_on_stable_feature_vectors_with_pair_metric")
    metric_accepted = candidate_distance_profile["metric_ready"] and (
        candidate_evaluation["accuracy"] > baseline_evaluation["accuracy"] or
        candidate_evaluation["macro_recall"] > baseline_evaluation["macro_recall"])
    distance_profile = dict(candidate_distance_profile)
    distance_profile["active"] = metric_accepted
    if metric_accepted:
        distance_profile["activation"] = "replay_gain"
    else:
        distance_profile.update({
            "candidate_method": candidate_distance_profile["method"],
            "method": "identity",
            "metric_ready": False,
            "weights": [1.0] * GTM_DIMENSIONS,
            "activation": "held_out_no_replay_gain",
            "rejection_reason": "no_replay_gain",
        })
    labeled_positions = []
    labeled_points = []
    for position in positions:
        item = by_id.get(str(position.get("item_id")), {})
        label = _triage_label(item)
        if label:
            labeled_positions.append((
                str(position.get("item_id")), label,
                vector_by_id.get(str(position.get("item_id"))) or [
                    float(position.get("x", 0.0)), float(position.get("y", 0.0))]))
            labeled_points.append((float(position.get("x", 0.0)),
                                  float(position.get("y", 0.0))))
    if len(labeled_positions) > ORDER_NEIGHBOR_LIMIT:
        labeled_positions = labeled_positions[-ORDER_NEIGHBOR_LIMIT:]
    uncertainty_total = 0.0
    unlabeled_total = 0
    confidence_counts = {
        level: 0 for level in ("confirmada", "alta", "media", "baja")}
    for position in positions:
        item_id = str(position.get("item_id"))
        item = by_id.get(item_id, {})
        label = _triage_label(item)
        if label:
            probabilities = {
                candidate: 1.0 if candidate == label else 0.0
                for candidate in ORDER_LABELS
            }
            prediction = {
                "recommended": label,
                "confidence": "confirmada",
                "probabilities": probabilities,
                "evidence_count": 1,
                "observed_labels": 1,
                "neighbor_counts": {
                    candidate: 1 if candidate == label else 0
                    for candidate in ORDER_LABELS
                },
                "coverage": ordering["coverage"],
                "learning_ready": ordering["learning_ready"],
                "neighbors": [item_id],
                "prior_counts": dict(ordering["counts"]),
                "uncertainty": 0.0,
                "margin": 1.0,
                "coverage_gap": 0.0,
                "information_gain": 0.0,
            }
        else:
            point = [float(position.get("x", 0.0)),
                     float(position.get("y", 0.0))]
            prediction_vector = vector_by_id.get(item_id) or point
            prediction = _triage_prediction(
                prediction_vector, labeled_positions, ordering["counts"],
                labeled_total=ordering["labeled"], item_total=len(items or []),
                distance_weights=distance_profile["weights"])
            uncertainty, margin = _prediction_uncertainty(
                prediction["probabilities"])
            if labeled_points:
                nearest = min(math.sqrt(
                    (point[0] - other[0]) ** 2 +
                    (point[1] - other[1]) ** 2)
                    for other in labeled_points)
                coverage_gap = min(1.0, nearest / math.sqrt(2.0))
            else:
                coverage_gap = 1.0
            prediction["uncertainty"] = uncertainty
            prediction["margin"] = margin
            prediction["coverage_gap"] = round(coverage_gap, 6)
            prediction["information_gain"] = round(
                uncertainty * (0.65 + coverage_gap * 0.35), 6)
            uncertainty_total += uncertainty
            unlabeled_total += 1
        position["triage_prediction"] = prediction
        confidence = prediction.get("confidence", "baja")
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
    anchors = {}
    for label in ORDER_LABELS:
        rows = [position for position in positions
                if _triage_label(by_id.get(str(position.get("item_id")), {})) == label]
        if rows:
            anchors[label] = {
                "x": round(sum(row["x"] for row in rows) / len(rows), 6),
                "y": round(sum(row["y"] for row in rows) / len(rows), 6),
                "count": len(rows),
            }
    ordering["mode"] = "stable_topology_live_field"
    ordering["feedback_applied"] = True
    ordering["revision"] = revision
    ordering["prediction_confidence"] = confidence_counts
    active_evaluation = (candidate_evaluation if metric_accepted
                         else baseline_evaluation)
    active_evaluation = dict(active_evaluation)
    active_evaluation["baseline"] = _ordering_metric_summary(baseline_evaluation)
    active_evaluation["candidate"] = _ordering_metric_summary(candidate_evaluation)
    active_evaluation["distance_comparison"] = {
        "accuracy_delta": round(
            candidate_evaluation["accuracy"] - baseline_evaluation["accuracy"], 6),
        "macro_recall_delta": round(
            candidate_evaluation["macro_recall"] - baseline_evaluation["macro_recall"], 6),
        "metric": candidate_distance_profile["method"],
        "active": metric_accepted,
        "promotion": "none",
    }
    ordering["evaluation"] = active_evaluation
    ordering["field"] = {
        "schema": ORDER_FIELD_SCHEMA,
        "method": "adaptive_pair_metric_on_stable_topology",
        "prediction_metric": "declared-hashed32-weighted",
        "coverage_metric": "gtm-2d",
        "anchors": anchors,
        "moves_geometry": False,
        "labeled_items": len(labeled_positions),
        "unlabeled_items": unlabeled_total,
        "mean_uncertainty": round(
            uncertainty_total / unlabeled_total, 6) if unlabeled_total else 0.0,
        "distance_profile": distance_profile,
    }
    result = dict(base_surface)
    result["items"] = positions
    result["ordering"] = ordering
    result["atlas"] = dict(base_surface.get("atlas") or {},
                           learning_revision=revision)
    _ORDER_FIELD_CACHE.clear()
    _ORDER_FIELD_CACHE[cache_key] = result
    return result


def build_gtm_map(items, feedback=None, width=8, height=6,
                  stable_topology=False):
    """Fit a small elastic latent grid and return every item position.

    This is the local, dependency-free map engine: nodes form a rectangular
    latent topology, assignments are soft, and neighboring nodes are smoothed
    during fitting. It is deliberately called GTM in the contract while the
    feature extractor remains replaceable and explicitly non-semantic.
    """
    width = max(3, min(int(width), 16))
    height = max(3, min(int(height), 12))
    original_items = [item for item in items or [] if item.get("id")]
    valid_items = (_stable_topology_items(original_items)
                   if stable_topology else original_items)
    live_feedback = dedupe_feedback(feedback or [])
    feedback = [] if stable_topology else live_feedback
    signature = _map_signature(valid_items, feedback, width, height)
    cached = _GTM_CACHE.get(signature)
    if cached is not None:
        if stable_topology:
            return _stable_ordering_surface(cached, original_items, live_feedback)
        return cached
    vectors = [portfolio_vector(item) for item in valid_items]
    ordering = ordering_profile(valid_items)
    labeled_vectors = [
        (index, _triage_label(item), vector)
        for index, (item, vector) in enumerate(zip(valid_items, vectors))
        if _triage_label(item)
    ]
    if len(labeled_vectors) > ORDER_NEIGHBOR_LIMIT:
        labeled_vectors = labeled_vectors[-ORDER_NEIGHBOR_LIMIT:]
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
    if len(vectors) > GTM_FIT_LIMIT:
        step = max(1, len(vectors) // GTM_FIT_LIMIT)
        fit_indices = list(range(0, len(vectors), step))[:GTM_FIT_LIMIT]
        if fit_indices[-1] != len(vectors) - 1:
            fit_indices[-1] = len(vectors) - 1
    else:
        fit_indices = list(range(len(vectors)))
    fit_vectors = [vectors[index] for index in fit_indices]
    nodes = _grid(width, height)
    codebooks = []
    if fit_vectors:
        chosen = [0]
        while len(chosen) < len(nodes):
            next_index = max(
                (index for index in range(len(fit_vectors)) if index not in chosen),
                key=lambda index: min(_vector_distance(fit_vectors[index], fit_vectors[other])
                                      for other in chosen),
                default=chosen[-1])
            chosen.append(next_index)
        codebooks = [list(fit_vectors[index % len(fit_vectors)]) for index in chosen]
    else:
        codebooks = [[0.0] * GTM_DIMENSIONS for _ in nodes]
    for iteration in range(6):
        sigma = max(0.55, max(width, height) * (0.34 - iteration * 0.045))
        learning_rate = 0.42 - iteration * 0.045
        accumulators = [[0.0] * GTM_DIMENSIONS for _ in nodes]
        weights = [0.0] * len(nodes)
        for vector in fit_vectors:
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
            "triage_prediction": _triage_prediction(
                vector, labeled_vectors, ordering["counts"],
                labeled_total=ordering["labeled"], item_total=len(valid_items)),
        })
    ordering["field"] = _apply_ordering_field(positions, valid_items)
    confidence_counts = {level: 0 for level in ("alta", "media", "baja")}
    for position in positions:
        level = (position.get("triage_prediction") or {}).get("confidence", "baja")
        confidence_counts[level] = confidence_counts.get(level, 0) + 1
    ordering["prediction_confidence"] = confidence_counts
    topology_id = signature[:16]
    result = {"schema": GTM_SCHEMA, "engine": "elastic_latent_grid",
        "feature_extractor": "declared_metadata_plus_hashed_terms_plus_vision",
              "grid": {"width": width, "height": height},
              "fit": {"items": len(fit_vectors), "total": len(vectors),
                      "sampled": len(fit_vectors) < len(vectors)},
              "items": positions, "count": len(positions),
              "ordering": ordering,
              "atlas": {
                  "schema": ATLAS_SCHEMA,
                  "topology_id": topology_id,
                  "stable_during_pass": bool(stable_topology),
                  "feature_version": "declared-hashed32-v1",
                  "refresh_policy": (
                      "structural_change_or_session_boundary"
                      if stable_topology else "feedback_or_structural_change"),
              }}
    _GTM_CACHE.clear()
    _GTM_CACHE[signature] = result
    _GTM_VECTOR_CACHE.clear()
    _GTM_VECTOR_CACHE[topology_id] = {
        str(item.get("id")): vector
        for item, vector in zip(valid_items, vectors)
    }
    if stable_topology:
        return _stable_ordering_surface(result, original_items, live_feedback)
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


def build_suggestions(source, items, selections=None, feedback=None, context=None,
                      limit=24, focus_facet="", shuffle=False, shuffle_seed="",
                      visual_relations=None):
    selections = selections or {}
    feedback = feedback or []
    learned = feedback_index(feedback)
    learned_facets = feedback_facet_index(feedback)
    profile = learning_profile(feedback)
    context = context or {}
    context_facet = str(context.get("facet", "")).lower()
    scope = board_scope(context)
    source_id = str(source.get("id", ""))
    source_terms = _terms(source.get("descripcion_original"))
    result = []
    suppressed_scope = 0
    suppressed_carousel = 0
    for candidate in items:
        candidate_id = str(candidate.get("id", ""))
        if not candidate_id or candidate_id == source_id:
            continue
        selection = selections.get(candidate_id, {}).get("decision", "pendiente")
        if selection == "descartar":
            continue
        source_publication = str(source.get("publicacion_id") or "").strip()
        candidate_publication = str(candidate.get("publicacion_id") or "").strip()
        if source_publication and source_publication == candidate_publication:
            suppressed_carousel += 1
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
        pair_prior = learned.get((source_id, candidate_id))
        common = {
            "item_id": candidate_id,
            "selection": selection,
            "feedback": pair_prior.get("action") if pair_prior else "pendiente",
            "source_role": source.get("record_kind") or source.get("tipo_contenido") or "media_candidate",
            "candidate_role": candidate.get("record_kind") or candidate.get("tipo_contenido") or "media_candidate",
        }
        if candidate.get("publicacion_id") == source.get("publicacion_id") and source.get("publicacion_id"):
            result.append(dict(common, facet="publication", relation_type="same_carousel", score=12,
                               scope="declared", evidence=[{
                                   "kind": "instagram_metadata", "facet": "publication",
                                   "source_value": source.get("publicacion_id"),
                                   "candidate_value": candidate.get("publicacion_id"),
                                   "strength": "high",
                               }], reasons=["misma publicación/carrusel"]))
        if candidate.get("fecha") == source.get("fecha") and source.get("fecha"):
            result.append(dict(common, facet="date", relation_type="same_date_context", score=7,
                               scope="declared", evidence=[{
                                   "kind": "instagram_metadata", "facet": "date",
                                   "source_value": source.get("fecha"),
                                   "candidate_value": candidate.get("fecha"),
                                   "strength": "high",
                               }], reasons=["misma fecha"]))
        for facet, base_score in (("artist", 11), ("venue", 10), ("event", 10),
                                  ("client", 10), ("collab", 9), ("period", 6)):
            overlap = _explicit_overlap(source, candidate, facet)
            if not overlap:
                continue
            result.append(dict(
                common, facet=facet, relation_type="same_%s" % facet,
                score=base_score, scope="declared", evidence=[{
                    "kind": "declared_metadata", "facet": facet,
                    "values": overlap, "strength": "high",
                }], reasons=["mismo %s declarado: %s" % (
                    facet, ", ".join(overlap[:3]))]))
        if shared:
            result.append(dict(common, facet="text", relation_type="shared_concept", score=min(6, len(shared)) + 2,
                               scope="exploratory", evidence=[{
                                   "kind": "description_term", "facet": "text",
                                   "values": shared[:5], "strength": "low",
                               }], reasons=["conceptos compartidos: " + ", ".join(shared[:5])]))
        if candidate.get("tipo_contenido") == source.get("tipo_contenido"):
            result.append(dict(common, facet="format", relation_type="same_media_role", score=1,
                               scope="declared", evidence=[{
                                   "kind": "instagram_metadata", "facet": "format",
                                   "source_value": source.get("tipo_contenido"),
                                   "candidate_value": candidate.get("tipo_contenido"),
                                   "strength": "low",
                               }], reasons=["mismo tipo de medio"]))

    # Visual similarity is a derived, exploratory channel.  It is appended
    # only when the bounded FAISS worker has already supplied an eligible
    # candidate.  A pair with an existing metadata relation keeps that one
    # relation instead of receiving a duplicate card for the same pair.
    metadata_targets = {str(row.get("item_id")) for row in result}
    by_id = {str(item.get("id")): item for item in items or []
             if isinstance(item, dict) and item.get("id")}
    for visual in visual_relations or []:
        candidate_id = str(visual.get("item_id") or "").strip()
        candidate = by_id.get(candidate_id)
        if (not candidate or candidate_id == source_id
                or candidate_id in metadata_targets
                or selections.get(candidate_id, {}).get("decision") == "descartar"):
            continue
        if (source.get("publicacion_id") and candidate.get("publicacion_id")
                and source.get("publicacion_id") == candidate.get("publicacion_id")):
            continue
        score = float(visual.get("score") or 0.0)
        margin = float(visual.get("margin") or 0.0)
        if not math.isfinite(score) or not math.isfinite(margin):
            continue
        visual_score = max(-1.0, min(1.0, score))
        visual_margin = max(0.0, min(1.0, margin))
        visual_model = str(visual.get("model") or "MobileCLIP-S0")[:100]
        visual_version = str(visual.get("model_version") or "")[:120]
        visual_source_kind = str(visual.get("source_kind") or "")[:80]
        visual_source_ref = str(visual.get("source_ref") or "")[:240]
        visual_record_kind = str(visual.get("record_kind") or "")[:80]
        visual_values = [
            "score=%.4f" % visual_score,
            "margen=%.4f" % visual_margin,
            "modelo=%s" % visual_model,
        ]
        if visual_version:
            visual_values.append("versión=%s" % visual_version)
        if visual_source_kind:
            visual_values.append("fuente=%s" % visual_source_kind)
        result.append(dict(
            {
                "item_id": candidate_id,
                "selection": selections.get(candidate_id, {}).get("decision", "pendiente"),
                "feedback": "pendiente",
                "source_role": source.get("record_kind") or source.get(
                    "tipo_contenido") or "media_candidate",
                "candidate_role": candidate.get("record_kind") or candidate.get(
                    "tipo_contenido") or "media_candidate",
            },
            facet="visual_similarity", relation_type="visual_similarity",
            score=round(visual_score * 10.0, 4), visual_score=round(visual_score, 6),
            visual_margin=round(visual_margin, 6), scope="exploratory",
            evidence=[{
                "kind": "visual_similarity", "facet": "visual_similarity",
                "values": visual_values, "strength": "medium",
                "score": round(visual_score, 6),
                "margin": round(visual_margin, 6),
                "model": visual_model, "model_version": visual_version,
                "source_kind": visual_source_kind,
                "source_ref": visual_source_ref,
                "record_kind": visual_record_kind,
            }],
            visual={
                "score": round(visual_score, 6),
                "margin": round(visual_margin, 6),
                "model": visual_model,
                "model_version": visual_version,
                "source_kind": visual_source_kind,
                "source_ref": visual_source_ref,
                "record_kind": visual_record_kind,
                "evidence_kind": "visual_similarity",
            },
            reasons=[
                "similitud visual derivada; no establece identidad ni autoría",
                "vecindad MobileCLIP/FAISS sobre la unidad editorial",
            ]))
    for row in result:
        prior = learned_facets.get((source_id, row["item_id"],
                                    str(row.get("facet") or "unknown").lower()))
        if prior is None:
            prior = learned_facets.get((source_id, row["item_id"], "unknown"))
        if prior and prior.get("action") == "reject":
            row["score"] = -20
            row["reasons"].append("relación rechazada para esta faceta")
        row["space"] = "evidence" if row.get("scope") == "declared" else "resonance"
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
    suppressed = (suppressed_scope + suppressed_carousel
                  + sum(1 for row in result if context_facet
                        and row.get("facet") == context_facet))
    result = [row for row in result if row["score"] > 0 and row.get("facet") != context_facet]
    focus_facet = str(focus_facet or "").lower().strip()
    if focus_facet == "concept":
        focus_facet = "text"
    if focus_facet in INFERENCE_FACETS or focus_facet == "visual_similarity":
        result = [row for row in result if row.get("facet") == focus_facet]
    if shuffle:
        random.Random(str(shuffle_seed or source_id)).shuffle(result)
    else:
        result.sort(key=lambda row: (-row["score"], row["item_id"], row["relation_type"]))
    return result[:limit], suppressed


def group_suggestions(rows):
    """Collapse repeated candidate cards while preserving every relation channel."""
    grouped = {}
    for row in rows or []:
        item_id = str(row.get("item_id") or "").strip()
        if not item_id:
            continue
        group = grouped.setdefault(item_id, {
            "item_id": item_id,
            "selection": row.get("selection", "pendiente"),
            "feedback": row.get("feedback", "pendiente"),
            "source_role": row.get("source_role", ""),
            "candidate_role": row.get("candidate_role", ""),
            "score": row.get("score", 0),
            "confidence": row.get("confidence", "baja"),
            "scope": row.get("scope", "exploratory"),
            "spaces": [],
            "facets": [],
            "relations": [],
            "evidence": [],
            "reasons": [],
            "visual": dict(row.get("visual") or {}),
        })
        relation_key = (row.get("facet", ""), row.get("relation_type", ""))
        if not any((relation.get("facet", ""), relation.get("relation_type", "")) == relation_key
                   for relation in group["relations"]):
            group["relations"].append({
                "facet": row.get("facet", ""),
                "relation_type": row.get("relation_type", ""),
                "score": row.get("score", 0),
                "confidence": row.get("confidence", "baja"),
                "scope": row.get("scope", "exploratory"),
                "space": row.get("space", "resonance"),
                "evidence": row.get("evidence", []),
            })
        space = str(row.get("space") or "resonance").strip()
        if space and space not in group["spaces"]:
            group["spaces"].append(space)
        facet = str(row.get("facet") or "").strip()
        if facet and facet not in group["facets"]:
            group["facets"].append(facet)
        for evidence in row.get("evidence", []) or []:
            if evidence not in group["evidence"]:
                group["evidence"].append(evidence)
        for reason in row.get("reasons", []) or []:
            if reason not in group["reasons"]:
                group["reasons"].append(reason)
        for key, value in (row.get("visual") or {}).items():
            if value not in (None, "", []):
                group.setdefault("visual", {})[key] = value
        if row.get("score", 0) > group["score"]:
            group["score"] = row["score"]
            group["confidence"] = row.get("confidence", group["confidence"])
        if row.get("scope") == "declared":
            group["scope"] = "declared"
    result = list(grouped.values())
    for group in result:
        primary = max(group["relations"], key=lambda relation: relation.get("score", 0),
                      default={})
        group["facet"] = primary.get("facet", "")
        group["relation_type"] = primary.get("relation_type", "related")
        group["space"] = primary.get("space", "resonance")
        group["relation_count"] = len(group["relations"])
        group["relations"].sort(key=lambda relation: (
            -relation.get("score", 0), relation.get("facet", "")))
    result.sort(key=lambda row: (-row["score"], row["item_id"]))
    return result


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


READINESS_SCHEMA = "faro-evidence-readiness-v1"

# What a person needs in front of them before labelling a record work / record
# / review / discard. Measured 2026-09-02: of 7044 records, 116 are labelled
# and 6928 are not, and the ordering model predicts NONE of them with high
# confidence (alta=0, media=4156, baja=2772). So every case is still a human
# look, and the only lever left is making that look cheaper. The seed rows
# already carry `has_description`, `has_vision` and `review_scope`; the
# interface read none of them, so the operator decided without seeing what the
# case even contains -- and `review`, the label that means "not decidable yet",
# was used once in 116 decisions.
#
# Retirement: when the ordering model predicts a usable share of the field and
# the frontier stops being one-by-one.
READINESS_CHANNELS = ("asset", "description", "date", "perception",
                      "classification", "relations", "work_group")

# The minimum a defensible label rests on. Everything else enriches.
READINESS_REQUIRED = ("asset", "description")


def _readiness_row(channel, status, detail="", source_ref=""):
    """One channel, with its status kept separate from its explanation.

    `absent` means measured and not there. `unknown` means NOT MEASURED for
    this record, which is a different claim and must never collapse into
    `absent` -- reading an absence as a finding is how a gap becomes a fact.
    """
    if status not in ("present", "absent", "unknown"):
        status = "unknown"
    return {"channel": channel, "status": status,
            "detail": str(detail or "")[:240],
            "source_ref": str(source_ref or "")[:400]}


def evidence_readiness(record, vision=None, vision_indexed=None,
                       relations=None, work_group=None):
    """Report what one record HAS and LACKS before a human decides on it.

    Pure: it receives what was already measured elsewhere and invents nothing.
    `vision_indexed` is the set of ids the perception index actually covers;
    without it, a missing vision record stays `unknown`, because the index
    covered 100 of 7044 records and "not indexed" is not "has no perception".
    """
    record = record if isinstance(record, dict) else {}
    rows = []

    asset = record.get("asset_available")
    rows.append(_readiness_row(
        "asset",
        "present" if asset is True else "absent" if asset is False else "unknown",
        "archivo local del registro",
        record.get("asset_path", "")))

    description = str(record.get("description") or "").strip()
    rows.append(_readiness_row(
        "description",
        "present" if description else "absent",
        "texto que el autor escribio sobre la pieza",
        record.get("source_id", "")))

    date = str(record.get("date") or "").strip()
    rows.append(_readiness_row(
        "date", "present" if date else "absent", date or "sin fecha declarada",
        record.get("publication_id", "")))

    item_id = str(record.get("source_id") or "")
    if isinstance(vision, dict) and vision.get("features"):
        rows.append(_readiness_row(
            "perception", "present",
            "confianza declarada: %s" % (vision.get("confidence") or "low"),
            item_id))
    elif vision_indexed is not None and item_id in set(vision_indexed):
        rows.append(_readiness_row(
            "perception", "absent",
            "indexado y sin lectura utilizable", item_id))
    else:
        rows.append(_readiness_row(
            "perception", "unknown",
            "fuera del indice de percepcion; no medido, no ausente", item_id))

    classification = record.get("classification")
    rows.append(_readiness_row(
        "classification",
        "present" if isinstance(classification, dict) and classification else "absent",
        "clasificacion humana previa", item_id))

    relation_rows = relations if isinstance(relations, (list, tuple)) else []
    rows.append(_readiness_row(
        "relations",
        "present" if relation_rows else "absent",
        "%d relacion(es) propuestas, todas candidatas" % len(relation_rows),
        item_id))

    group = work_group if work_group is not None else record.get("work_group")
    rows.append(_readiness_row(
        "work_group",
        "present" if isinstance(group, dict) and group else "absent",
        "agrupacion de obra ya establecida", item_id))

    by_channel = {row["channel"]: row for row in rows}
    missing = [row["channel"] for row in rows if row["status"] == "absent"]
    unmeasured = [row["channel"] for row in rows if row["status"] == "unknown"]
    blocking = [name for name in READINESS_REQUIRED
                if by_channel[name]["status"] != "present"]

    if blocking:
        decision = "abstain"
        next_action = ("falta lo minimo para etiquetar (%s): registrar `review` "
                       "con la evidencia que falta" % ", ".join(blocking))
    elif missing or unmeasured:
        decision = "decidable_con_reservas"
        next_action = ("se puede etiquetar; lo no medido queda declarado, "
                       "no resuelto")
    else:
        decision = "decidable"
        next_action = "etiquetar con la evidencia completa a la vista"

    return {
        "schema": READINESS_SCHEMA,
        "item_id": item_id,
        "channels": rows,
        "missing": missing,
        "unmeasured": unmeasured,
        "blocking": blocking,
        "decision": decision,
        "labels": list(ORDER_LABELS),
        "promotion": "none",
        "owner": "human",
        "producer": "local_readiness_report",
        "next_action": next_action,
    }


def provider_status(environment):
    return {
        "local_deterministic": True,
        "ollama": bool(environment.get("OLLAMA_HOST") or environment.get("OLLAMA_BASE_URL")),
        "groq": bool(environment.get("GROQ_API_KEY")),
        "cerebras": bool(environment.get("CEREBRAS_API_KEY")),
        "gemini": bool(environment.get("GEMINI_API_KEY")),
    }


def external_evidence_profile(external_rows=None, vision_rows=None):
    """Summarize provider yield without promoting any provider output."""
    external_rows = [row for row in external_rows or [] if isinstance(row, dict)]
    vision_rows = [row for row in vision_rows or [] if isinstance(row, dict)]
    by_provider = {}
    hypothesis_total = 0
    unknown_total = 0
    external_ids = set()
    for row in external_rows:
        provider = str(row.get("provider") or "unknown")
        summary = by_provider.setdefault(provider, {"rows": 0, "items": set()})
        summary["rows"] += 1
        item_id = str(row.get("item_id") or "").strip()
        if item_id:
            summary["items"].add(item_id)
            external_ids.add(item_id)
        inference = row.get("inference") or {}
        hypothesis_total += len(inference.get("hypotheses") or [])
        unknown_total += len(inference.get("unknowns") or [])
    confidence_counts = {level: 0 for level in ("high", "medium", "low")}
    evidence_kind_counts = {}
    vision_ids = set()
    for row in vision_rows:
        item_id = str(row.get("item_id") or "").strip()
        if item_id:
            vision_ids.add(item_id)
        confidence = str(row.get("confidence") or "low")
        if confidence in confidence_counts:
            confidence_counts[confidence] += 1
        kind = str(row.get("evidence_kind") or "unknown")
        evidence_kind_counts[kind] = evidence_kind_counts.get(kind, 0) + 1
    providers = {
        provider: {"rows": summary["rows"], "unique_items": len(summary["items"])}
        for provider, summary in sorted(by_provider.items())
    }
    return {
        "schema": "faro-external-evidence-profile-v1",
        "external_rows": len(external_rows),
        "external_unique_items": len(external_ids),
        "vision_rows": len(vision_rows),
        "vision_unique_items": len(vision_ids),
        "cross_provider_items": len(external_ids & vision_ids),
        "providers": providers,
        "normalized_hypotheses": hypothesis_total,
        "unknowns": unknown_total,
        "vision_confidence": confidence_counts,
        "evidence_kinds": evidence_kind_counts,
        "promotion": "none",
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

    def visual_observations(item):
        vision = item.get("vision_features")
        if not isinstance(vision, dict):
            return {}
        return {
            field: [str(value)[:120] for value in (vision.get(field) or [])[:16]]
            for field in ("visual_terms", "dominant_colors", "composition",
                          "motion_or_media")
            if isinstance(vision.get(field), list) and vision.get(field)
        }

    compact = []
    for item in candidates:
        compact.append({
            "item_id": item.get("id"),
            "date": item.get("fecha"),
            "publication_id": item.get("publicacion_id"),
            "content_type": item.get("tipo_contenido"),
            "description_original": item.get("descripcion_original", ""),
            "asset_available": bool(item.get("asset_available")),
            "vision_observations": visual_observations(item),
        })
    payload = {
        "task": "Inferir relaciones curatoriales multimodales sin inventar hechos.",
        "rules": [
            "Una hipótesis no es un hecho: expresa evidencia y desconocidos.",
            "No agrupes por una palabra aislada.",
            "Conserva la descripción original como dato, no como verdad.",
            "Usa las observaciones visuales solo como señal de composición o apariencia; nunca como identidad.",
            "Si las señales de texto, fecha y visión no convergen, devuelve unknowns y ninguna hipótesis.",
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
            "vision_observations": visual_observations(source),
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


def inference_quality(inference):
    """Gate provider hypotheses without treating them as facts or deleting them."""
    hypotheses = inference.get("hypotheses", []) if isinstance(inference, dict) else []
    if not isinstance(hypotheses, list) or not hypotheses:
        return {
            "verdict": "revise",
            "reason": "no_evidenced_hypotheses",
            "valid_hypotheses": 0,
            "missing_evidence": [],
            "promotion": "none",
        }
    missing_evidence = [str(row.get("item_id", "")) for row in hypotheses
                        if not isinstance(row.get("evidence"), list)
                        or not [value for value in row.get("evidence", [])
                                if str(value).strip()]]
    valid = len(hypotheses) - len(missing_evidence)
    verdict = "accept" if valid == len(hypotheses) else "revise"
    return {
        "verdict": verdict,
        "reason": ("all_hypotheses_have_evidence" if verdict == "accept"
                   else "some_hypotheses_missing_evidence"),
        "valid_hypotheses": max(0, valid),
        "missing_evidence": missing_evidence[:48],
        "promotion": "none",
    }
