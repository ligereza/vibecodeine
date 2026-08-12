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
from collections import Counter, defaultdict

# 'corpus' are the artist's perceived works; the rest MAK wrote itself.
_CLASE_POR_DIR = {"corpus": "obra", "codex": "codigo"}

_EXTENSIONES = (".md", ".txt", ".json", ".jpg", ".jpeg", ".png", ".webp")
PORTFOLIO_ENTITY_SCHEMA = "faro-portfolio-entity-v1"
MESA_SCENE_SCHEMA = "faro-portfolio-scene-v1"
PORTFOLIO_PURPOSE = "triage audiovisual records without turning stories into works"
OPPORTUNITY_CARD_SCHEMA = "faro-opportunity-card-v1"
PORTFOLIO_RELATION_KEYS = (
    "artist", "username", "client", "collab", "event", "festival", "venue",
    "date", "audio",
)
IDENTITY_GRAPH_SCHEMA = "faro-identity-graph-v1"
_GENERIC_CANDIDATE_VALUES = frozenset({
    "", "unknown", "candidate", "none", "null", "n/a", "na",
    "no confirmado", "sin confirmar",
})


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


def desde_portfolio_item(item: dict) -> dict:
    """Derive the shared projection envelope from one portfolio inbox item.

    The inbox remains the source of truth. This pure adapter gives the archive,
    organism, gallery and editor the same identity and routing fields without
    copying the media record or creating a second portfolio schema.
    """
    if not isinstance(item, dict):
        raise TypeError("portfolio item must be an object")
    entity_id = str(item.get("id") or "").strip()
    if not entity_id:
        raise ValueError("portfolio item needs an id")
    content_type = str(item.get("tipo_contenido") or "media").strip()
    record_kind = "story_record" if content_type == "story" else "media_candidate"
    selection = str(item.get("selection") or "pendiente").strip()
    next_action = {
        "seleccionar": "triangulate",
        "deseleccionar": "reject",
    }.get(selection, "review")
    source_id = str(item.get("publicacion_id") or entity_id).strip()
    source_kind = str(item.get("source_kind") or (
        "instagram_export" if item.get("publicacion_id") else "portfolio_inbox"
    )).strip()
    consent_status = str(item.get("consent_status") or "unknown").strip()
    public_status = str(item.get("public_status") or "private_candidate").strip()
    return {
        "schema": PORTFOLIO_ENTITY_SCHEMA,
        "entity_id": entity_id,
        "source_id": source_id,
        "lane": "obra",
        "purpose": PORTFOLIO_PURPOSE,
        "record_kind": record_kind,
        "format": str(item.get("format") or (
            "registro" if record_kind == "story_record" else "media"
        )),
        "evidence_kind": str(item.get("evidence_kind") or "media_metadata"),
        "status": selection,
        "next_action": next_action,
        "owner": "human" if next_action == "review" else "MAK",
        "source": {
            "kind": source_kind,
            "date": item.get("fecha"),
            "asset_available": bool(item.get("asset_available")),
        },
        "consent": {
            "status": consent_status,
            "basis": str(item.get("consent_basis") or "").strip(),
            "recorded_at": str(item.get("consent_recorded_at") or "").strip(),
        },
        "publication": {
            "status": public_status,
            "requires_human_gate": public_status != "public",
        },
    }


def portfolio_identity_graph(items, connections=None, context_links=None):
    """Project explicit metadata into a graph without resolving free text."""
    nodes = {}
    edges = []
    edge_keys = set()
    relation_fields = {
        "artist": ("artist", "artista"), "username": ("username",),
        "client": ("client", "cliente"), "collab": ("collab", "colaboracion", "colaboradores"),
        "event": ("event", "evento"), "festival": ("festival",),
        "venue": ("venue",), "producer": ("producer", "productora"),
        "location": ("location", "ubicacion", "ciudad"),
    }

    def source_layer(item):
        explicit = str(item.get("semantic_layer") or item.get("layer") or "").strip().lower()
        classification = item.get("classification")
        if isinstance(classification, dict):
            explicit = str(explicit or classification.get("semantic_layer") or
                           classification.get("layer") or "").strip().lower()
        if explicit in {"obra", "registro", "entidad"}:
            return explicit
        role = str(item.get("record_kind") or (
            classification.get("record_kind") if isinstance(classification, dict) else ""
        ) or "").strip().lower()
        if role in {"obra", "work", "artwork"}:
            return "obra"
        if role in {"story_record", "registro", "record"} or item.get("tipo_contenido") == "story":
            return "registro"
        return "candidate"

    def values(value):
        if isinstance(value, (list, tuple, set)):
            source = value
        else:
            source = [value]
        clean = []
        for entry in source:
            if isinstance(entry, dict):
                entry = entry.get("name") or entry.get("value") or ""
            text = str(entry or "").strip()
            if not text or text.lower() in _GENERIC_CANDIDATE_VALUES:
                continue
            clean.append(text)
        return clean

    def add_node(node_id, kind, label, **extra):
        nodes.setdefault(node_id, {"id": node_id, "kind": kind,
                                   "label": label, **extra})

    def add_edge(source, target, relation, evidence_kind, confidence="medium"):
        key = (source, target, relation)
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append({"source": source, "target": target, "relation": relation,
                      "source_layer": nodes.get(source, {}).get("layer", ""),
                      "target_layer": nodes.get(target, {}).get("layer", ""),
                      "evidence_kind": evidence_kind, "confidence": confidence,
                      "status": "candidate"})

    for item in items or []:
        if not isinstance(item, dict) or not str(item.get("id") or "").strip():
            continue
        item_id = str(item["id"])
        node_id = "item:" + _id(item_id)
        classification = item.get("classification")
        declared_record_kind = item.get("record_kind") or (
            classification.get("record_kind") if isinstance(classification, dict) else "")
        add_node(node_id, "item", item_id,
                 record_kind=declared_record_kind or (
                     "story_record" if item.get("tipo_contenido") == "story" else "media_candidate"),
                 layer=source_layer(item), content_type=item.get("tipo_contenido"), date=item.get("fecha"),
                 selection=item.get("selection", "pendiente"))
        if item.get("fecha"):
            date_id = "date:" + _id(item["fecha"])
            add_node(date_id, "date", str(item["fecha"]), layer="context")
            add_edge(node_id, date_id, "date", "instagram_metadata", "high")
        if item.get("publicacion_id"):
            publication_id = "publication:" + _id(item["publicacion_id"])
            add_node(publication_id, "publication", str(item["publicacion_id"]), layer="context")
            add_edge(node_id, publication_id, "publication", "instagram_metadata", "high")
        declared = {}
        for field in ("entities", "classification", "human_context"):
            values_by_relation = item.get(field)
            if not isinstance(values_by_relation, dict):
                continue
            for relation, values_for_relation in values_by_relation.items():
                if relation not in declared:
                    declared[relation] = values_for_relation
                elif isinstance(declared[relation], list):
                    prior = declared[relation]
                    incoming = values_for_relation if isinstance(values_for_relation, list) else [values_for_relation]
                    declared[relation] = prior + incoming
                else:
                    declared[relation] = [declared[relation], values_for_relation]
        for relation, fields in relation_fields.items():
            raw = []
            for field in fields:
                raw.extend(values(item.get(field)))
                raw.extend(values(declared.get(field)))
            for value in sorted(set(raw)):
                entity_id = "%s:%s" % (relation, _id(value))
                add_node(entity_id, relation, value, layer="entidad")
                add_edge(node_id, entity_id, relation, "declared_metadata")

    for connection in connections or []:
        if not isinstance(connection, dict):
            continue
        source = "item:" + _id(connection.get("source_id"))
        target = "item:" + _id(connection.get("target_id"))
        if source in nodes and target in nodes:
            add_edge(source, target, str(connection.get("relation") or "related"),
                     "human_feedback", "high")
    for link in context_links or []:
        if not isinstance(link, dict):
            continue
        source = "item:" + _id(link.get("source_id"))
        group = str(link.get("group_key") or "").strip()
        if source not in nodes or not group:
            continue
        group_id = "group:" + _id(group)
        add_node(group_id, "group", group, layer="context")
        add_edge(source, group_id, "context_link", "human_context", "high")
    layer_counts = Counter(node.get("layer", "") for node in nodes.values())
    return {
        "schema": IDENTITY_GRAPH_SCHEMA,
        "resolution_policy": "explicit_metadata_only",
        "nodes": list(nodes.values()), "edges": edges,
        "counts": {"nodes": len(nodes), "edges": len(edges)},
        "layer_counts": dict(layer_counts),
    }


def _candidate_values(value):
    if isinstance(value, list):
        values = value
    else:
        values = [value]
    flattened = []
    for entry in values:
        if isinstance(entry, dict):
            entry = entry.get("name") or entry.get("value") or ""
        text = str(entry or "").strip()
        if text:
            flattened.append(text)
    return flattened


def _portfolio_source_item(item: dict) -> dict:
    source = dict(item or {})
    source.setdefault("id", source.get("item_id"))
    source.setdefault("tipo_contenido", source.get("content_type"))
    source.setdefault("fecha", source.get("date"))
    source.setdefault("descripcion_original", source.get("description_original"))
    return source


def _candidate_matches_source(value, source_item: dict, relation: str) -> bool:
    source_item = _portfolio_source_item(source_item)
    text = " ".join(str(source_item.get(key) or "") for key in (
        "descripcion_original", "description_original", "caption", "title",
    )).casefold()
    normalized = str(value or "").strip().casefold()
    if relation == "date":
        return normalized == str(source_item.get("fecha") or "").strip().casefold()
    return bool(normalized and normalized in text)


def _source_mentions_username(value, source_item: dict) -> bool:
    source_item = _portfolio_source_item(source_item)
    username = str(value or "").strip().lstrip("@").casefold()
    text = " ".join(str(source_item.get(key) or "") for key in (
        "descripcion_original", "description_original", "caption", "title",
    )).casefold()
    return bool(username and ("@" + username) in text)


def _normalized_candidate_relations(relations: dict, source_item: dict) -> dict:
    normalized = {}
    for relation in PORTFOLIO_RELATION_KEYS:
        values = [value for value in _candidate_values(relations.get(relation))
                  if value.casefold() not in _GENERIC_CANDIDATE_VALUES]
        if not values:
            continue
        target = relation
        if relation == "artist":
            handles = [value for value in values
                       if _source_mentions_username(value, source_item)]
            if handles:
                target = "username"
        normalized.setdefault(target, []).extend(values)
    return {key: sorted(set(values)) for key, values in normalized.items()}


def _candidate_evidence_basis(value, source_item: dict) -> list:
    source_item = _portfolio_source_item(source_item)
    allowed = {
        "description", "description_original", "caption", "instagram_metadata",
        "date_metadata", "asset_metadata", "visual_contact_sheet", "audio",
    }
    source_text = " ".join(str(source_item.get(key) or "") for key in (
        "descripcion_original", "description_original", "caption", "title",
    )).casefold()
    basis = []
    for entry in _candidate_values(value):
        folded = entry.casefold()
        if folded in {"description", "description_original", "caption"}:
            basis.append("description_original")
        elif folded in allowed:
            basis.append(folded)
        elif len(entry) > 20 and folded in source_text:
            basis.append("description_original")
    return sorted(set(basis))


def portfolio_candidate_verdict(row: dict, source_item: dict) -> str:
    """Return only accept, revise or reject for one external portfolio row."""
    if not isinstance(row, dict) or not isinstance(source_item, dict):
        return "reject"
    source_item = _portfolio_source_item(source_item)
    item_id = str(row.get("item_id") or "").strip()
    source_id = str(source_item.get("id") or "").strip()
    if not item_id or item_id != source_id:
        return "reject"
    expected_kind = ("story_record" if source_item.get("tipo_contenido") == "story"
                     else "media_candidate")
    if str(row.get("record_kind") or "").strip() != expected_kind:
        return "reject"
    relations = row.get("candidate_relations")
    if not isinstance(relations, dict):
        return "revise"
    found = False
    for relation in PORTFOLIO_RELATION_KEYS:
        for value in _candidate_values(relations.get(relation)):
            if value.casefold() in _GENERIC_CANDIDATE_VALUES:
                continue
            if relation != "date":
                found = True
            if not _candidate_matches_source(value, source_item, relation):
                return "revise"
    if not _candidate_evidence_basis(relations.get("evidence_basis"), source_item):
        return "revise"
    return "accept" if found else "revise"


def normalize_portfolio_candidate(row: dict, source_item: dict,
                                  provider: str = "") -> dict:
    """Keep a traceable candidate inside the existing portfolio contract."""
    source_item = _portfolio_source_item(source_item)
    contract = desde_portfolio_item(source_item)
    relations = row.get("candidate_relations") if isinstance(row, dict) else {}
    relations = relations if isinstance(relations, dict) else {}
    normalized = _normalized_candidate_relations(relations, source_item)
    contract.update({
        "status": "candidate_external",
        "next_action": "human_review",
        "owner": "human",
        "triage": {
            "provider": str(provider or "unknown").strip(),
            "verdict": portfolio_candidate_verdict(row, source_item),
            "candidate_relations": normalized,
            "evidence_basis": _candidate_evidence_basis(
                relations.get("evidence_basis"), source_item),
            "uncertainty": relations.get("uncertainty") or "unknown",
        },
    })
    return contract


def portfolio_metadata_index(items) -> dict:
    """Build a compact index without loading media or resolving identities."""
    rows = [item for item in items if isinstance(item, dict)]
    by_type = Counter()
    by_date = Counter()
    by_publication = defaultdict(list)
    mentions = defaultdict(list)
    for item in rows:
        content_type = str(item.get("tipo_contenido") or
                           item.get("content_type") or "media").strip()
        item_id = str(item.get("id") or item.get("item_id") or "").strip()
        date = str(item.get("fecha") or item.get("date") or "").strip()
        publication = str(item.get("publicacion_id") or
                          item.get("publication_id") or "").strip()
        by_type[content_type] += 1
        if date:
            by_date[date] += 1
        if publication:
            by_publication[publication].append(item_id)
        description = str(item.get("descripcion_original") or
                          item.get("description_original") or "")
        for username in sorted(set(re.findall(
                r"(?<![A-Za-z0-9_])@([A-Za-z0-9._]{2,80})", description))):
            if item_id and item_id not in mentions[username.lower()]:
                mentions[username.lower()].append(item_id)
    publication_sizes = list(by_publication.values())
    return {
        "schema": "faro-portfolio-metadata-index-v1",
        "total": len(rows),
        "by_content_type": dict(sorted(by_type.items())),
        "grouping": {
            "publication_groups": len(publication_sizes),
            "carousel_groups": sum(1 for group in publication_sizes
                                    if len(group) > 1),
            "date_groups": len(by_date),
            "story_records": by_type.get("story", 0),
        },
        "date_range": {
            "first": min(by_date) if by_date else "",
            "last": max(by_date) if by_date else "",
        },
        "dates": [{"date": date, "count": count}
                  for date, count in sorted(by_date.items(), reverse=True)],
        "user_mentions": [
            {"username": username, "count": len(item_ids),
             "item_ids": item_ids[:24]}
            for username, item_ids in sorted(
                mentions.items(), key=lambda pair: (-len(pair[1]), pair[0]))[:200]
        ],
        "identity_resolution": "mentions_only; no artist, client or venue inferred",
    }


def mesa_scene(source: dict, records, relation_groups, limit: int = 10) -> dict:
    """Build the single-scene projection used by the portfolio workbench.

    The inbox and feedback files remain the sources of truth. This projection
    only deduplicates visible records by id and expresses suggestions as edges
    over those records; it never creates a second card for a relation.
    """
    source = dict(source or {})
    source_id = str(source.get("id") or source.get("source_id") or "").strip()
    if not source_id:
        return {
            "schema": MESA_SCENE_SCHEMA, "active_id": "", "records": [],
            "relations": [], "window": {"limit": max(1, int(limit or 10)), "count": 0},
        }
    try:
        limit = max(2, min(20, int(limit or 10)))
    except (TypeError, ValueError):
        limit = 10

    by_id = {source_id: source}
    groups = [row for row in relation_groups or [] if isinstance(row, dict)]
    discarded_ids = {
        str(record.get("id") or record.get("source_id") or "").strip()
        for record in records or []
        if isinstance(record, dict)
        and str(record.get("selection") or "") == "descartar"
    }
    target_order = []
    for group in groups:
        target_id = str(group.get("item_id") or "").strip()
        if (target_id and target_id != source_id
                and target_id not in discarded_ids
                and target_id not in target_order):
            target_order.append(target_id)
    for record in records or []:
        if not isinstance(record, dict):
            continue
        record_id = str(record.get("id") or record.get("source_id") or "").strip()
        if record_id and record_id not in discarded_ids and record_id not in by_id:
            by_id[record_id] = dict(record)

    publication_groups = {}
    publication_records = [source, *[record for record in records or []
                                      if isinstance(record, dict)]]
    seen_publication_members = {}
    for record in publication_records:
        record_id = str(record.get("id") or record.get("source_id") or "").strip()
        current_publication = str(record.get("publicacion_id") or "").strip()
        if (not current_publication or not record_id
                or str(record.get("selection") or "") == "descartar"):
            continue
        seen = seen_publication_members.setdefault(current_publication, set())
        if record_id in seen:
            continue
        seen.add(record_id)
        publication_groups.setdefault(current_publication, []).append({
            "source_id": record_id,
            "asset_path": record.get("asset_path") or "",
            "asset_available": bool(record.get("asset_available")),
            "index": record.get("medio_indice"),
            "total": record.get("medio_total"),
            "selection": record.get("selection") or "pendiente",
        })
    for media in publication_groups.values():
        media.sort(key=lambda row: (
            row.get("index") is None, row.get("index") or 0, row["source_id"]))
    publication_representative = {}
    for record_id, record in by_id.items():
        publication_key = str(record.get("publicacion_id") or "").strip()
        if publication_key and publication_key not in publication_representative:
            publication_representative[publication_key] = record_id

    visible_ids = [source_id]
    source_publication = str(source.get("publicacion_id") or "").strip()
    seen_units = {("publication", source_publication) if source_publication
                  else ("item", source_id)}
    for record_id in target_order:
        record = by_id.get(record_id, {})
        publication_key = str(record.get("publicacion_id") or "").strip()
        unit_key = ("publication", publication_key) if publication_key else ("item", record_id)
        if unit_key in seen_units:
            continue
        seen_units.add(unit_key)
        visible_ids.append(publication_representative.get(publication_key, record_id)
                           if publication_key else record_id)
    visible_ids = visible_ids[:limit]

    def canonical_record_id(record_id):
        record = by_id.get(record_id, {})
        publication_key = str(record.get("publicacion_id") or "").strip()
        return publication_representative.get(publication_key, record_id)

    work_parent = {record_id: record_id for record_id in visible_ids}

    def work_find(record_id):
        parent = work_parent.get(record_id, record_id)
        while parent != work_parent.get(parent, parent):
            parent = work_parent[parent]
        current = record_id
        while current in work_parent and work_parent[current] != parent:
            next_id = work_parent[current]
            work_parent[current] = parent
            current = next_id
        return parent

    def work_union(left, right):
        if left not in work_parent or right not in work_parent:
            return
        left_root, right_root = work_find(left), work_find(right)
        if left_root != right_root:
            work_parent[right_root] = left_root

    def group_feedback(group):
        channels = group.get("feedback_channels")
        if isinstance(channels, list) and channels:
            return [row for row in channels if isinstance(row, dict)]
        feedback = str(group.get("feedback") or "").strip()
        if feedback.lower() not in {"accept", "correct", "reject", "ignore", "undo"}:
            return []
        return [{
            "action": feedback,
            "facet": str(group.get("feedback_facet") or "unknown"),
            "relation": group.get("relation_type") or "related",
            "note": group.get("note") or "",
        }]

    def effective_feedback(channels):
        """Return the latest action per relation facet after undo barriers."""
        current = {}
        order = []
        for row in channels:
            facet = str(row.get("facet") or "unknown").lower()
            relation = str(row.get("relation") or "related")
            key = (facet, relation)
            if str(row.get("action") or "").lower() == "undo":
                current.pop(key, None)
                if key in order:
                    order.remove(key)
                continue
            current[key] = row
            if key not in order:
                order.append(key)
        return [current[key] for key in order if key in current]

    def feedback_status(channels):
        actions = {str(row.get("action") or "").lower()
                   for row in effective_feedback(channels)}
        if actions & {"accept", "correct"}:
            return "accepted"
        if actions and actions <= {"reject"}:
            return "rejected"
        return "candidate"

    for group in groups:
        target_id = canonical_record_id(str(group.get("item_id") or "").strip())
        channels = effective_feedback(group_feedback(group))
        for feedback_row in channels:
            feedback = str(feedback_row.get("action") or "").strip().lower()
            feedback_facet = str(feedback_row.get("facet") or "").strip().lower()
            if (feedback in {"accept", "correct"}
                    and feedback_facet in {"obra", "work", "same_work"}):
                work_union(source_id, target_id)

    work_components = {}
    for record_id in visible_ids:
        work_components.setdefault(work_find(record_id), []).append(record_id)
    work_groups = {}
    for member_ids in work_components.values():
        if len(member_ids) < 2:
            continue
        member_ids = sorted(member_ids)
        group_id = "work:" + ":".join(member_ids)
        members = [{
            "source_id": member_id,
            "asset_path": by_id[member_id].get("asset_path") or "",
            "asset_available": bool(by_id[member_id].get("asset_available")),
            "date": by_id[member_id].get("fecha") or by_id[member_id].get("date"),
        } for member_id in member_ids if member_id in by_id]
        group = {"id": group_id, "label": "misma obra", "count": len(members),
                 "member_ids": member_ids, "members": members, "basis": "human_feedback"}
        for member_id in member_ids:
            work_groups[member_id] = group

    visible = []
    for record_id in visible_ids:
        record = by_id[record_id]
        record_kind = str(record.get("record_kind") or "").strip()
        if record_kind in {"story_record", "registro", "record"}:
            layer = "registro"
        else:
            layer = str(record.get("semantic_layer") or record.get("layer") or
                        "candidate").strip() or "candidate"
        visible.append({
            "source_id": record_id,
            "role": "active" if record_id == source_id else "related",
            "semantic_layer": layer,
            "record_kind": record_kind or ("story_record" if record.get(
                "tipo_contenido") == "story" else "media_candidate"),
            "content_type": record.get("tipo_contenido") or record.get("content_type"),
            "date": record.get("fecha") or record.get("date"),
            "publication_id": record.get("publicacion_id") or record.get("publication_id"),
            "publication_group": ({
                "id": record_publication,
                "count": len(publication_groups.get(record_publication, [])),
                "media": publication_groups.get(record_publication, []),
            } if (record_publication := str(
                record.get("publicacion_id") or record.get("publication_id") or ""))
              else None),
            "publication_index": record.get("medio_indice"),
            "publication_total": record.get("medio_total"),
            "work_group": work_groups.get(record_id),
            "classification": dict(record.get("classification") or {}),
            "decision_draft": dict(record.get("decision_draft") or {}),
            "description": record.get("descripcion_original") or record.get(
                "description_original") or "",
            "asset_path": record.get("asset_path") or "",
            "asset_available": bool(record.get("asset_available")),
            "selection": record.get("selection") or "pendiente",
        })

    visible_set = set(visible_ids)
    relations = []
    for group in groups:
        raw_target_id = str(group.get("item_id") or "").strip()
        target_id = canonical_record_id(raw_target_id)
        if not target_id or target_id not in visible_set or target_id == source_id:
            continue
        feedback_channels = group_feedback(group)
        status = feedback_status(feedback_channels)
        channels = list(group.get("facets") or [])
        feedback_facets = [str(row.get("facet") or "").strip()
                           for row in feedback_channels]
        feedback_facets = [facet for facet in feedback_facets if facet]
        for feedback_facet in feedback_facets:
            if feedback_facet not in channels:
                channels.insert(0, feedback_facet)
        effective_channels = effective_feedback(feedback_channels)
        accepted_facet = next((str(row.get("facet") or "").strip()
                               for row in effective_channels
                               if row.get("action") in {"accept", "correct"}), "")
        feedback_facet = accepted_facet or (feedback_facets[0] if feedback_facets else "")
        decisions = [{
            "action": row.get("action", ""),
            "facet": row.get("facet", "unknown"),
            "relation": row.get("relation", group.get("relation_type") or "related"),
            "note": str(row.get("note") or "")[:1000],
        } for row in feedback_channels]
        relation_id = "%s->%s" % (source_id, target_id)
        existing = next((row for row in relations
                         if row["relation_id"] == relation_id), None)
        if existing:
            for channel in channels:
                if channel not in existing["channels"]:
                    existing["channels"].append(channel)
            for key in ("evidence", "reasons"):
                for value in list(group.get(key) or []):
                    if value not in existing[key]:
                        existing[key].append(value)
            for key, value in (group.get("visual") or {}).items():
                if value not in (None, "", []):
                    existing.setdefault("visual", {})[key] = value
            existing.setdefault("member_ids", []).append(raw_target_id)
            existing.setdefault("decisions", []).extend(decisions)
            existing["status"] = feedback_status(existing.get("decisions", []))
            continue
        relations.append({
            "relation_id": relation_id,
            "source_id": source_id,
            "target_id": target_id,
            "channels": channels,
            "feedback_facet": feedback_facet,
            "relation_type": group.get("relation_type") or "related",
            "confidence": group.get("confidence") or "baja",
            "scope": group.get("scope") or "exploratory",
            "space": group.get("space") or (
                "evidence" if group.get("scope") == "declared" else "resonance"),
            "spaces": list(group.get("spaces") or [group.get("space") or (
                "evidence" if group.get("scope") == "declared" else "resonance")]),
            "evidence": list(group.get("evidence") or []),
            "reasons": list(group.get("reasons") or []),
            "visual": dict(group.get("visual") or {}),
            "note": str(group.get("note") or "")[:1000],
            "status": status,
            "decisions": decisions,
            "decision_actions": ["accept", "reject"],
            "member_ids": [raw_target_id],
        })

    return {
        "schema": MESA_SCENE_SCHEMA,
        "active_id": source_id,
        "records": visible,
        "relations": relations,
        "window": {"limit": limit, "count": len(visible), "source_total": len(by_id)},
        "interaction": {
            "camera_drag": True,
            "node_drag": False,
            "duplicate_targets": False,
            "decision_surface": "map_hud",
            "projection": "gtm",
            "feedback_updates_topology": False,
            "learning_surface": "live_field_over_stable_atlas",
        },
        "promotion": "none",
    }


def desde_convocatoria_seed(item: dict, captured_at: str = "") -> dict:
    """Normalize a watched opportunity without treating it as verified."""
    if not isinstance(item, dict):
        raise TypeError("opportunity seed must be an object")
    title = str(item.get("titulo") or item.get("title") or "").strip()
    source_url = str(item.get("url") or item.get("source_url") or "").strip()
    if not title:
        raise ValueError("opportunity seed needs a title")
    if not source_url.startswith(("http://", "https://")):
        raise ValueError("opportunity seed needs an http source_url")
    areas = item.get("areas") or ""
    if isinstance(areas, str):
        areas = [part.strip() for part in areas.split(",") if part.strip()]
    elif isinstance(areas, (list, tuple)):
        areas = [str(part).strip() for part in areas if str(part).strip()]
    else:
        areas = []
    natural_person = item.get("personas_naturales")
    eligibility = "persona natural" if natural_person is True else "no confirmado"
    return {
        "schema": OPPORTUNITY_CARD_SCHEMA,
        "opportunity_id": "opportunity:%s" % _id(source_url or title),
        "title": title,
        "source_url": source_url,
        "source_name": str(item.get("fuente") or "").strip(),
        "source_kind": "candidate_source",
        "deadline_raw": str(item.get("cierre") or item.get("deadline") or "").strip(),
        "deadline_verified": False,
        "eligibility": eligibility,
        "eligibility_verified": False,
        "amount_raw": str(item.get("monto") or "").strip(),
        "areas": areas,
        "captured_at": str(captured_at or item.get("detectada") or "").strip(),
        "last_verified": "",
        "status": "unverified",
        "next_action": "verify official bases, eligibility and exact deadline",
        "evidence": [source_url],
        "raw_score": item.get("score"),
    }


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


def sustrato_publico(datos: dict) -> dict:
    """Return the public projection without historical research products.

    Research reports and visual annexes remain in the source corpus and can be
    requested explicitly. The public projection avoids loading them as signed
    artwork and keeps every surviving relation connected to real pieces.
    """
    excluded = {"informe", "concepto", "pieza_grafica"}
    piezas = [pieza for pieza in datos.get("piezas", [])
              if pieza.get("clase") not in excluded]
    ids = {pieza.get("id") for pieza in piezas}
    vinculos = [vinculo for vinculo in datos.get("vinculos", [])
                if vinculo.get("de") in ids and vinculo.get("a") in ids]
    return {"piezas": piezas, "vinculos": vinculos}


def desde_ensayo(ensayo: dict) -> dict:
    """An ENSAYO with its iconographic annex -> the same contract shape.

    Why here and not in the generator: an essay exists on BOTH sides. The repo
    keeps the curated ones under `docs/cultura/ensayos/<tema>/`, and the box
    writes them to `~/research/informes/` (`research.py --formato ensayo`). One
    pure function, two consumers -- the same reason `convertir()` lives here.
    This is what makes MAK's output reach the portfolio instead of stopping at
    a folder nobody reads.

    `ensayo` is what the caller already has on disk, nothing invented:
        {"slug", "titulo", "fecha"?, "resumen"?, "ruta"?,
         "conceptos": [{"n", "slug", "titulo", "descripcion", "ancla"?,
                        "archivo"?, "estilo"?}]}

    Three classes of piece and two of link, and every one of them encodes
    something the manifest really says (the doublecup rule -- no element claims
    a datum it does not encode):

    - the essay              -> clase `informe`, its own title (MAK wrote it)
    - each nameable concept  -> clase `concepto`, linked to the essay
    - each icon that EXISTS  -> clase `pieza_grafica`, medio svg, linked to its
      concept. An icon declared in the manifest but missing from disk produces
      NO piece: a piece that claims a file that is not there is exactly the
      lie this contract forbids.

    Links are `clase: "manual"`, never `semantico`: nobody measured a distance
    here, the relation is declared by the manifest. Calling it measured would
    be the same defect as the tag-derived links pretending to be semantic.
    """
    slug_ensayo = _id(ensayo.get("slug") or ensayo.get("titulo") or "ensayo")
    id_ensayo = "ensayo-%s" % slug_ensayo
    piezas = [{
        "id": id_ensayo,
        "titulo": str(ensayo.get("titulo") or slug_ensayo),
        "clase": "informe",
        "fecha": ensayo.get("fecha"),
        "resumen": ensayo.get("resumen"),
        "etiquetas": ["ensayo", "cultura"],
        "peso": max(1, len(ensayo.get("conceptos") or [])),
        "medio": ({"tipo": "texto", "src": ensayo["ruta"]}
                  if ensayo.get("ruta") else {"tipo": "texto"}),
        "estado": "publicada",
        "extra": {"formato": "ensayo"},
    }]
    vinculos = []
    for c in ensayo.get("conceptos") or []:
        titulo = str(c.get("titulo") or "").strip()
        if not titulo:
            continue                      # sin nombre no es un concepto nombrable
        id_concepto = "concepto-%s-%s" % (slug_ensayo, _id(c.get("slug") or titulo))
        piezas.append({
            "id": id_concepto,
            "titulo": titulo,
            "clase": "concepto",
            "fecha": None,
            "resumen": str(c.get("descripcion") or "").strip() or None,
            "etiquetas": ["ensayo", slug_ensayo],
            "peso": 1,
            "medio": {"tipo": "texto"},
            "estado": "publicada",
            "extra": {k: v for k, v in (("ancla", c.get("ancla")),
                                        ("n", c.get("n"))) if v},
        })
        vinculos.append({"de": id_concepto, "a": id_ensayo, "peso": 1.0,
                         "clase": "manual"})
        src = c.get("archivo_src")
        if not src:
            continue                      # el icono no existe en disco: no entra
        id_icono = "icono-%s-%s" % (slug_ensayo, _id(c.get("slug") or titulo))
        piezas.append({
            "id": id_icono,
            "titulo": titulo,
            "clase": "pieza_grafica",
            "fecha": None,
            "resumen": str(c.get("descripcion") or "").strip() or None,
            "etiquetas": [e for e in ["icono", "animado", slug_ensayo,
                                      (c.get("estilo") or "").strip()] if e],
            "peso": 1,
            "medio": {"tipo": "imagen", "src": src},
            "estado": "publicada",
            # `declara_animacion` y no `anima`: lo que el archivo codifica es
            # que TIENE keyframes, y eso lo puede ver quien lo lee sin
            # rasterizar. Que se MUEVA de forma perceptible es otra cosa y se
            # mide aparte contando cuadros distintos (`iconos_conjunto animar`,
            # y `tests/test_iconos_conjunto.py` exige que todo icono que declara
            # keyframes se mueva dentro de su propio ciclo). Son dos hechos
            # distintos y el contrato solo puede afirmar el que el archivo
            # codifica -- la regla que existe para hacer cumplir.
            "extra": ({"declara_animacion": True}
                      if c.get("declara_animacion") else {}),
        })
        vinculos.append({"de": id_icono, "a": id_concepto, "peso": 1.0,
                         "clase": "manual"})
    return {"piezas": piezas, "vinculos": vinculos}


def desde_campo(campo: dict, existe=None) -> dict:
    """Las obras CURADAS del campo medido, al contrato.

    campo.json es la proyeccion de lo que MAK percibio de las obras reales del
    artista (la carpeta de material que se mando a curar), ya pasada por el
    filtro que el usuario configuro. Hasta ahora solo daba POSICIONES: si el
    micelio no estaba alcanzable (CI, maquina apagada), el archivo salia sin
    las obras -- un portafolio sin las obras del artista. Esta conversion las
    hace piezas de primera clase con lo que el campo si midio.

    `existe` se inyecta para que una piel pueda distinguir una fuente real de
    una ruta historica declarada pero no disponible en el despliegue actual.
    La pieza no desaparece: conserva su referencia y queda marcada para
    revision, evitando presentar una ausencia como si fuera una obra cargable.

    `titulo` va None a proposito: el artista no titulo estas piezas y el
    percibido es texto de maquina -- va a `extra.percibido`, nunca como
    titulo (regla de la VOZ). `unir()` deduplica contra el micelio por id y
    la fuente mas rica completa los campos.
    """
    if existe is None:
        from pathlib import Path as _P
        raiz = _P(__file__).resolve().parents[2]
        existe = lambda src: (raiz / src).is_file()  # noqa: E731
    piezas = []
    for c in campo.get("piezas") or []:
        cid = c.get("id")
        if not cid:
            continue
        extra = {}
        for k in ("colores", "tipo", "estilo", "tilde", "trazo", "percibido"):
            if c.get(k):
                extra[k] = c[k]
        archivo = c.get("archivo")
        fuente_estado = ("presente" if archivo and existe(archivo)
                         else "ausente" if archivo else "no_declarada")
        extra["fuente_original"] = {
            "ruta": archivo,
            "estado": fuente_estado,
            "rol": "obra_original",
        }
        piezas.append({
            "id": cid,
            "titulo": None,
            "clase": "obra",
            "fecha": None,
            "resumen": None,
            "etiquetas": [t for t in ("curada", c.get("tipo")) if t],
            "peso": 1,
            "medio": ({"tipo": "imagen", "src": archivo,
                       "estado_fuente": fuente_estado}
                      if archivo else {"tipo": "imagen",
                                       "estado_fuente": fuente_estado}),
            "estado": "publicada",
            "extra": extra,
        })
    return {"piezas": piezas, "vinculos": []}


def aplicar_curaduria(datos: dict, curaduria: dict, existe=None) -> dict:
    """La mano del artista SOBRE lo percibido, nunca debajo.

    `iskvw/datos/curaduria.json` es el archivo humano de la edicion -- simple
    a proposito, editable a mano sin panel. Por id de pieza:

      titulo       la voz del artista donde la maquina dejo silencio
      mostrar      false = la pieza no entra al archivo publicado
      abstraccion  0..1: cuanto se abstrae en la piel (1 = pura textura de
                   glifos, 0 = pieza completa; para obras sin contexto o
                   con trazo debil la falla se transmuta, no se esconde)
      svg          ruta a una version editada A MANO que desplaza a la
                   generada -- el tier FIRMADO: la maquina propone, el
                   humano firma (si el archivo no existe, se ignora y se
                   conserva el generado: nunca un src que 404ea)
      regimen      por pieza; el global va en curaduria["regimen"]

    Y tres campos OPCIONALES, inertes mientras no se escriban (2026-07-31):
    la curaduria crece por campos que NO cambian nada hasta que el artista
    los usa, porque un default nuevo seria una decision estetica ajena.

      peso         numero > 0: cuanta materia tiene la pieza (el campo `peso`
                   del contrato, ESQUEMA_ARCHIVO.md: sirve para el tamano);
                   desplaza al peso que la fuente haya medido
      serie        etiqueta de agrupacion (va a extra["serie"]): la mano que
                   dice "estas van juntas" sin inventar un vinculo medido
      nota         la nota del artista (va a extra["nota"]), valor que lee un
                   humano: espanol correcto con tildes, nunca se degrada

    Se aplica AL FINAL, sobre el resultado de unir(): gana sobre cualquier
    fuente. Ids desconocidos se ignoran sin ruido -- la curaduria puede
    nombrar obras que el filtro de hoy dejo fuera.
    """
    if existe is None:
        from pathlib import Path as _P
        raiz = _P(__file__).resolve().parents[2]
        existe = lambda src: (raiz / src).is_file()  # noqa: E731
    por_id = curaduria.get("piezas") or {}
    piezas, fuera = [], set()
    for p in datos["piezas"]:
        c = por_id.get(p["id"])
        if not c:
            piezas.append(p)
            continue
        if c.get("mostrar") is False:
            fuera.add(p["id"])
            continue
        q = dict(p)
        q["extra"] = dict(q.get("extra") or {})
        if c.get("titulo"):
            q["titulo"] = str(c["titulo"])
            q["extra"]["titulo_firmado"] = True
        if c.get("abstraccion") is not None:
            q["extra"]["abstraccion"] = max(0.0, min(1.0, float(c["abstraccion"])))
        if c.get("regimen"):
            q["extra"]["regimen"] = str(c["regimen"])
        if c.get("peso") is not None:
            peso = float(c["peso"])
            if peso > 0:
                q["peso"] = peso
        if c.get("serie"):
            q["extra"]["serie"] = str(c["serie"])
        if c.get("nota"):
            q["extra"]["nota"] = str(c["nota"])
        if c.get("svg") and existe(c["svg"]):
            q["medio"] = {"tipo": "imagen", "src": c["svg"]}
            q["extra"]["firmada"] = True
        piezas.append(q)
    vinculos = [v for v in datos["vinculos"]
                if v["de"] not in fuera and v["a"] not in fuera]
    return {"piezas": piezas, "vinculos": vinculos}


def desde_laser(manifiesto: dict, campo: dict, existe=None) -> dict:
    """Las piezas laser/plotter derivadas del material, al contrato.

    `flujo laser lote` camina la carpeta de material y deriva un svg por
    imagen (rayado o campo de flujo, semilla del nombre). La clave de union
    con el campo curado es el MEDIA ID: campo.json trae
    `archivo: posts/<media_id>.mp4` y el material se llama `<media_id>.jpg`
    -- mismos digitos, misma obra. Una pieza cuyo stem no calza con ninguna
    obra curada entra igual (es material del artista) pero sin vinculo.
    Mismas reglas duras: svg ausente = pieza que no entra.
    """
    if existe is None:
        from pathlib import Path as _P
        raiz = _P(__file__).resolve().parents[2]
        existe = lambda src: (raiz / src).is_file()  # noqa: E731
    por_stem = {}
    for c in campo.get("piezas") or []:
        archivo = c.get("archivo") or ""
        stem = archivo.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if stem:
            por_stem[stem] = c["id"]
    piezas, vinculos = [], []
    for fila in manifiesto.get("piezas") or []:
        stem = fila.get("stem")
        src = fila.get("src")
        if not stem or not src or not existe(src):
            continue
        id_pieza = "laser-%s" % stem
        obra = por_stem.get(stem)
        piezas.append({
            "id": id_pieza,
            "titulo": stem,
            "clase": "pieza_grafica",
            "fecha": None,
            "resumen": None,
            "etiquetas": ["laser", fila.get("modo") or "flow", "plotter"],
            "peso": 1,
            "medio": {"tipo": "imagen", "src": src},
            "estado": "publicada",
            "extra": ({"derivada_de": obra, "semilla": fila.get("semilla")}
                      if obra else {"semilla": fila.get("semilla")}),
        })
        if obra:
            vinculos.append({"de": id_pieza, "a": obra, "peso": 1.0,
                             "clase": "manual"})
    return {"piezas": piezas, "vinculos": vinculos}


def desde_animadas(manifiesto: dict, existe=None) -> dict:
    """Las piezas animadas derivadas de las obras curadas, al contrato.

    El generador (`tools/gen_animadas_obras.py`) deriva UNA pieza por obra con
    el motor semantico, determinista desde el id. Aca vive la conversion por
    la misma razon que `desde_ensayo`: la pieza existe en ambos lados (el repo
    la versiona, la caja puede regenerarla) y dos conversiones divergen.

    Mismas reglas del esquema: el vinculo es `manual` (lo declara el
    manifiesto, nadie midio una distancia) y una pieza cuyo svg NO esta en
    disco no entra -- el contrato no afirma lo que no puede mostrarse.
    `existe` se inyecta en tests; por defecto pregunta al disco real.
    """
    if existe is None:
        from pathlib import Path as _P
        raiz = _P(__file__).resolve().parents[2]
        existe = lambda src: (raiz / src).is_file()  # noqa: E731
    piezas, vinculos = [], []
    for fila in manifiesto.get("piezas") or []:
        oid = fila.get("obra_id")
        src = fila.get("src")
        if not oid or not src or not existe(src):
            continue
        id_pieza = "animada-%s" % oid
        piezas.append({
            "id": id_pieza,
            "titulo": str(fila.get("titulo") or oid),
            "clase": "pieza_grafica",
            "fecha": None,
            "resumen": None,
            "etiquetas": ["animada", "generativa", "motor-semantico"],
            "peso": 1,
            "medio": {"tipo": "imagen", "src": src},
            "estado": "publicada",
            "extra": ({"declara_animacion": True, "derivada_de": oid}
                      if fila.get("declara_animacion")
                      else {"derivada_de": oid}),
        })
        vinculos.append({"de": id_pieza, "a": oid, "peso": 1.0,
                         "clase": "manual"})
    return {"piezas": piezas, "vinculos": vinculos}
