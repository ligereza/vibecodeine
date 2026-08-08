#!/usr/bin/env python3
"""Append-only common ledger for MAK decisions and external findings.

This is the circulation layer: model output becomes small typed records that
can be reviewed, rejected, surfaced or reused without reading old reports.
"""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
import os
import time


HOME = os.path.expanduser("~")
LEDGER = os.path.join(HOME, "plataforma/common_ledger.jsonl")
SCHEMA_VERSION = "mak-ledger-v1"
QUARANTINE_SCHEMA = "mak-ledger-quarantine-v1"

ITEM_TYPES = ("evidence", "idea", "task", "decision", "reject", "artifact")
DOMAINS = ("rd", "iskvw", "mak", "svg", "adobe", "repo", "opportunities")
CONFIDENCE = ("high", "medium", "low", "unknown")
LANES = ("obra", "trabajo", "sistema")
DECISIONS = ("hacer", "revisar", "refutar", "archivar", "descartar")
IDENTITY_SCHEMA = "mak-identity-v1"
IDENTITY_KINDS = (
    "task", "report", "work", "record", "seed", "opportunity", "system",
    "legacy_unknown",
)
ENTITY_FIELDS = (
    "artist", "username", "client", "collab", "event", "festival", "venue",
    "location", "source",
)
LANE_BY_DOMAIN = {
    "iskvw": "obra", "svg": "obra",
    "rd": "trabajo", "opportunities": "trabajo",
    "mak": "sistema", "adobe": "sistema", "repo": "sistema",
}

ACTION_BY_DOMAIN = {
    "rd": ("verify_source", "triangulate", "draft_report", "reject"),
    "iskvw": ("curate", "expose", "archive", "reject"),
    "mak": ("archive", "refute", "expose", "repair_queue", "reject",
            "review", "decide"),
    "svg": ("measure", "prototype", "reuse", "reject"),
    "adobe": ("rescue", "bridge", "reuse", "reject"),
    "repo": ("reuse", "merge", "retire", "test", "reject"),
    "opportunities": ("verify_source", "triangulate", "draft_report",
                       "review", "reject"),
}

SECRET_MARKERS = ("api_key", "apikey", "secret", "token", "password",
                  "credential", "authorization", "bearer")


def _stable_id(item):
    basis = "|".join(str(item.get(k, "")) for k in
                     ("domain", "type", "claim", "action"))
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]


def _safe_text(value, limit=2000):
    text = str(value or "")
    folded = text.lower()
    if any(marker in folded for marker in SECRET_MARKERS):
        return "[redacted]"
    return text[:limit]


def _default_decision(item):
    if str(item.get("decision") or "").strip():
        return str(item["decision"]).lower()
    if str(item.get("type") or "").lower() == "reject":
        return "descartar"
    if str(item.get("type") or "").lower() == "task":
        return "hacer"
    return "revisar"


def _normalize_identity(identity, work_id, ts):
    """Normalize provenance without forcing old rows into a false identity."""
    if not isinstance(identity, dict):
        return {
            "schema": IDENTITY_SCHEMA,
            "kind": "legacy_unknown",
            "source_id": "",
            "parent_id": "",
            "entities": {field: [] for field in ENTITY_FIELDS},
            "event_date": "",
            "published_at": "",
            "created_at": ts,
        }
    entities = identity.get("entities")
    if not isinstance(entities, dict):
        entities = {}
    normalized_entities = {}
    for field in ENTITY_FIELDS:
        values = entities.get(field, [])
        if not isinstance(values, list):
            values = [values] if values else []
        normalized_entities[field] = [
            _safe_text(value, 240) for value in values if str(value).strip()
        ][:20]
    kind = _safe_text(identity.get("kind"), 40).lower() or "legacy_unknown"
    return {
        "schema": IDENTITY_SCHEMA,
        "kind": kind,
        "source_id": _safe_text(identity.get("source_id"), 240) or (
            "" if kind == "legacy_unknown" else _safe_text(work_id, 240)),
        "parent_id": _safe_text(identity.get("parent_id"), 240),
        "entities": normalized_entities,
        "event_date": _safe_text(identity.get("event_date"), 40),
        "published_at": _safe_text(identity.get("published_at"), 40),
        "created_at": _safe_text(identity.get("created_at"), 40) or ts,
    }


def normalize_item(item, source="manual", ts=None):
    if not isinstance(item, dict):
        raise ValueError("item_not_object")
    row = {
        "schema": SCHEMA_VERSION,
        "ts": ts or time.strftime("%F %T"),
        "source": _safe_text(source, 120),
        "domain": str(item.get("domain") or "").lower(),
        "type": str(item.get("type") or "").lower(),
        "claim": _safe_text(item.get("claim"), 1000),
        "evidence": [_safe_text(x, 800) for x in item.get("evidence", [])],
        "files": [_safe_text(x, 400) for x in item.get("files", [])],
        "confidence": str(item.get("confidence") or "unknown").lower(),
        "action": str(item.get("action") or "").lower(),
        "reject_reason": _safe_text(item.get("reject_reason"), 800),
        "lane": str(item.get("lane") or
                    LANE_BY_DOMAIN.get(str(item.get("domain") or "").lower(),
                                       "sistema")).lower(),
        "decision": _default_decision(item),
        "purpose": _safe_text(item.get("purpose"), 500),
        "next_action": _safe_text(item.get("next_action"), 500),
        "owner": _safe_text(item.get("owner"), 120) or "MAK",
    }
    work = item.get("work")
    if not isinstance(work, dict):
        work = {
            "schema": "mak-work-v1",
            "work_id": "legacy:%s" % (row["domain"] or "unknown"),
            "parent_task": "legacy_unknown",
            "lane": row["lane"],
            "purpose": "legacy ledger item without declared work metadata",
            "format": "legacy_unknown",
            "created_at": row["ts"],
            "provider": "unknown",
            "sources": [],
            "status": "legacy_unknown",
        }
    work_id = _safe_text(work.get("work_id"), 240) or "legacy:unknown"
    identity = work.get("identity")
    if not isinstance(identity, dict):
        identity = item.get("identity")
    work_identity = _normalize_identity(identity, work_id, row["ts"])
    row["work"] = {
        "schema": _safe_text(work.get("schema"), 40) or "mak-work-v1",
        "work_id": work_id,
        "parent_task": _safe_text(work.get("parent_task"), 240) or "legacy_unknown",
        "lane": _safe_text(work.get("lane"), 40) or row["lane"],
        "purpose": _safe_text(work.get("purpose"), 500),
        "format": _safe_text(work.get("format"), 120) or "legacy_unknown",
        "created_at": _safe_text(work.get("created_at"), 40) or row["ts"],
        "provider": _safe_text(work.get("provider"), 120) or "unknown",
        "sources": [_safe_text(value, 400) for value in work.get("sources", [])]
        if isinstance(work.get("sources", []), list) else [],
        "status": _safe_text(work.get("status"), 40) or "legacy_unknown",
        "identity": work_identity,
    }
    row["trace_status"] = (
        "declared" if work_identity["kind"] != "legacy_unknown"
        else "legacy_unknown"
    )
    metadata = item.get("metadata")
    if isinstance(metadata, dict):
        row["metadata"] = {
            str(key): _safe_text(value, 800)
            for key, value in metadata.items()
            if str(key).lower() not in SECRET_MARKERS
        }
    row["id"] = item.get("id") or _stable_id(row)
    return row


def validate_item(item, source="manual"):
    try:
        row = normalize_item(item, source=source)
    except ValueError as exc:
        return False, [str(exc)], None
    errors = []
    if row["schema"] != SCHEMA_VERSION:
        errors.append("bad_schema")
    if row["domain"] not in DOMAINS:
        errors.append("bad_domain")
    if row["type"] not in ITEM_TYPES:
        errors.append("bad_type")
    if row["confidence"] not in CONFIDENCE:
        errors.append("bad_confidence")
    if row["lane"] not in LANES:
        errors.append("bad_lane")
    if row["decision"] not in DECISIONS:
        errors.append("bad_decision")
    identity = row["work"].get("identity", {})
    if identity.get("schema") != IDENTITY_SCHEMA:
        errors.append("bad_identity_schema")
    if identity.get("kind") not in IDENTITY_KINDS:
        errors.append("bad_identity_kind")
    if identity.get("kind") != "legacy_unknown" and not identity.get("source_id"):
        errors.append("missing_identity_source_id")
    if not isinstance(identity.get("entities"), dict):
        errors.append("identity_entities_not_object")
    if not row["claim"] and row["type"] != "reject":
        errors.append("missing_claim")
    if not isinstance(row["evidence"], list):
        errors.append("evidence_not_list")
    if not isinstance(row["files"], list):
        errors.append("files_not_list")
    allowed = ACTION_BY_DOMAIN.get(row["domain"], ())
    if row["action"] not in allowed:
        errors.append("bad_action_for_domain")
    if row["type"] == "reject" and not row["reject_reason"]:
        errors.append("reject_without_reason")
    return not errors, errors, row


def append_item(item, path=LEDGER, source="manual"):
    ok, errors, row = validate_item(item, source=source)
    if not ok:
        return False, errors, None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return True, [], row


def append_unique(item, path=LEDGER, source="manual"):
    """Append a valid item unless its stable id is already in the ledger."""
    ok, errors, row = validate_item(item, source=source)
    if not ok:
        return False, errors, None
    if any(existing.get("id") == row["id"] for existing in read_items(path)):
        return True, [], None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return True, [], row


def read_items(path=LEDGER, limit=None):
    rows = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("schema") == SCHEMA_VERSION:
                    rows.append(row)
    except OSError:
        rows = []
    if limit is not None:
        rows = rows[-max(0, int(limit)):]
    return rows


def _enrich_legacy(row):
    """Project old valid rows into the current decision view without rewriting them."""
    view = dict(row)
    domain = str(view.get("domain") or "").lower()
    view["lane"] = str(view.get("lane") or LANE_BY_DOMAIN.get(domain, "sistema")).lower()
    view["decision"] = str(view.get("decision") or _default_decision(view)).lower()
    view["purpose"] = _safe_text(view.get("purpose"), 500) or (
        "legacy %s record projected into the decision queue" % domain)
    action = str(view.get("action") or "").lower()
    fallback_actions = {
        "verify_source": "verify source and date",
        "triangulate": "triangulate with a second source",
        "draft_report": "draft the contracted report",
        "curate": "write a curation decision before exposure",
        "expose": "human review before public exposure",
        "archive": "archive without promoting as current truth",
        "measure": "measure the existing pipeline before changing it",
        "prototype": "build one bounded prototype",
        "reuse": "reuse only after local verification",
        "review": "human review of the queued item",
        "refute": "record the contradiction and keep it out of truth",
        "repair_queue": "repair the queue entry before new production",
        "reject": "retain as rejected evidence; do not promote",
    }
    view["next_action"] = _safe_text(view.get("next_action"), 500) or \
        fallback_actions.get(action, "human review of the decision")
    view["owner"] = _safe_text(view.get("owner"), 120) or "MAK"
    identity = (view.get("work") or {}).get("identity")
    if not isinstance(identity, dict):
        identity = _normalize_identity(None, (view.get("work") or {}).get(
            "work_id", "legacy:unknown"), view.get("ts", ""))
    view["trace_status"] = view.get("trace_status") or (
        "declared" if identity.get("kind") != "legacy_unknown"
        else "legacy_unknown")
    view["identity_kind"] = identity.get("kind", "legacy_unknown")
    return view


def summarize(path=LEDGER, limit=50):
    rows = [_enrich_legacy(row) for row in read_items(path, limit=limit)]
    pending = [r for r in rows if r.get("metadata", {}).get("queue_status") == "pending_human"]
    return {
        "total": len(rows),
        "by_domain": dict(Counter(r.get("domain", "") for r in rows)),
        "by_lane": dict(Counter(r.get("lane", "") for r in rows)),
        "by_decision": dict(Counter(r.get("decision", "") for r in rows)),
        "by_type": dict(Counter(r.get("type", "") for r in rows)),
        "by_action": dict(Counter(r.get("action", "") for r in rows)),
        "by_trace_status": dict(Counter(r.get("trace_status", "") for r in rows)),
        "by_identity_kind": dict(Counter(r.get("identity_kind", "") for r in rows)),
        "pending_human": len(pending),
        "last": rows[-5:],
    }


def opportunity_from_vigia(item, source="vigia", path=LEDGER):
    """Queue one watched listing for human review without contacting anyone."""
    title = str(item.get("titulo") or "").strip()
    url = str(item.get("url") or "").strip()
    if not title:
        return False, ["missing_title"], None
    return append_unique({
        "id": "vigia:%s" % item.get("h", ""),
        "domain": "opportunities",
        "type": "task",
        "claim": "New watched opportunity: %s" % title,
        "evidence": [url] if url else [],
        "files": [],
        "confidence": "unknown",
        "action": "review",
        "lane": "trabajo",
        "decision": "revisar",
        "purpose": "verificar una oportunidad oficial sin contacto automatico",
        "next_action": "verify eligibility, deadline and artistic fit",
        "owner": "human",
        "metadata": {
            "queue_status": "pending_human",
            "source_id": item.get("fuente", ""),
            "title": title,
            "url": url,
            "priority_score": item.get("priority_score", 0),
            "priority_reasons": item.get("priority_reasons", ["needs_manual_fit"]),
            "priority_lane": item.get("priority_lane", "general"),
            "next_action": "verify eligibility, deadline and artistic fit",
            "safety": "no contact or submission",
        },
    }, path=path, source=source)


def _path_roots():
    roots = []
    for value in (
            os.environ.get("MAK_REPO_ROOT", ""),
            "/home/mak/flujo",
            os.getcwd(),
            os.path.join(os.path.expanduser("~"), "plataforma")):
        if value and value not in roots:
            roots.append(value)
    return roots


def _exists_path(path):
    value = os.path.expandvars(os.path.expanduser(str(path or "")))
    if os.path.isabs(value) and os.path.exists(value):
        return True
    return any(os.path.exists(os.path.join(root, value)) for root in _path_roots())


def audit_missing_paths(path=LEDGER):
    rows = []
    for row in read_items(path):
        if row.get("type") != "evidence":
            continue
        missing = [file_path for file_path in row.get("files", [])
                   if not _exists_path(file_path)]
        if missing:
            rows.append({
                "original_id": row.get("id", ""),
                "source": row.get("source", ""),
                "domain": row.get("domain", ""),
                "claim": row.get("claim", ""),
                "missing_files": missing,
                "reason": "evidence_path_not_found",
            })
    return rows


def read_items_quarantine(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("schema") == QUARANTINE_SCHEMA:
                    rows.append(row)
    except OSError:
        pass
    return rows


def classify_quarantine(rows, roots=None):
    """Classify quarantined evidence without restoring or mutating memory."""
    roots = [os.path.expanduser(str(root)) for root in (roots or _path_roots())]
    basename_index = {}
    for root in roots:
        if not os.path.isdir(root):
            continue
        for current, directories, filenames in os.walk(root):
            directories[:] = [name for name in directories if name != ".git"]
            for filename in filenames:
                basename_index.setdefault(filename, []).append(
                    os.path.join(current, filename))
    classified = []
    for row in rows or []:
        missing = [str(path) for path in row.get("missing_files", [])]
        if any("[redacted]" in path.lower() or any(marker in path.lower()
               for marker in SECRET_MARKERS) for path in missing):
            disposition = "reject_secret"
            candidates = []
        else:
            candidates = sorted({candidate for path in missing
                                 for candidate in basename_index.get(
                                     os.path.basename(path), [])})
            disposition = (
                "review_only_unique" if len(candidates) == 1
                else "stale_reject")
        item = dict(row)
        item["disposition"] = disposition
        item["candidate_paths"] = candidates[:8]
        classified.append(item)
    return classified


def write_quarantine(rows, path=None):
    path = path or os.path.join(HOME, "plataforma/common_ledger_quarantine.jsonl")
    existing = {row.get("original_id") for row in read_items_quarantine(path)}
    added = []
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        for row in rows:
            if not row.get("original_id") or row["original_id"] in existing:
                continue
            safe = dict(row)
            safe.update({"schema": QUARANTINE_SCHEMA,
                         "status": "quarantined",
                         "ts": time.strftime("%F %T")})
            fh.write(json.dumps(safe, ensure_ascii=False, sort_keys=True) + "\n")
            existing.add(row["original_id"])
            added.append(safe)
    return added


def external_item_to_ledger(item, area, work=None):
    domain_by_area = {
        "rd_evidence": "rd",
        "iskvw_curation": "iskvw",
        "mak_quality": "mak",
        "svg_pipeline": "svg",
        "tool_archaeology": "repo",
        "adobe_rescue": "adobe",
        "opportunity_radar": "opportunities",
    }
    item_type = "reject" if item.get("action") == "reject" else "evidence"
    domain = domain_by_area.get(area, "mak")
    work = work if isinstance(work, dict) else {}
    return {
        "work": work,
        "domain": domain,
        "type": item_type,
        "claim": item.get("claim", ""),
        "evidence": item.get("evidence", []),
        "files": item.get("files", []),
        "confidence": item.get("confidence", "unknown"),
        "action": item.get("action", ""),
        "reject_reason": item.get("reject_reason", ""),
        "lane": LANE_BY_DOMAIN.get(domain, "sistema"),
        "decision": "descartar" if item.get("action") == "reject" else "revisar",
        "purpose": item.get("product", {}).get("purpose", "")
        if isinstance(item.get("product"), dict) else "",
        "next_action": item.get("reject_reason", "revisar evidencia local"),
        "owner": "MAK",
    }


def append_external_result(payload, area, path=LEDGER, source="external"):
    if isinstance(payload, str):
        payload = json.loads(payload)
    rows = []
    errors = []
    for idx, item in enumerate(payload.get("items", []) if isinstance(payload, dict) else []):
        ok, item_errors, row = append_item(
            external_item_to_ledger(item, area, payload.get("work")), path=path,
            source="%s:%s" % (source, area))
        if ok:
            rows.append(row)
        else:
            errors.extend("item_%d_%s" % (idx, e) for e in item_errors)
    return rows, errors


def review_to_ledger(review, area, metadata=None):
    domain = str(review.get("domain") or "").lower()
    verdict = str(review.get("verdict") or "").lower()
    item_type = "decision" if verdict == "accept" else "reject"
    action = {
        "rd": "reject" if verdict == "reject" else "verify_source",
        "iskvw": "reject" if verdict == "reject" else "curate",
        "mak": "reject" if verdict == "reject" else "decide",
        "svg": "reject" if verdict == "reject" else "measure",
        "adobe": "reject" if verdict == "reject" else "rescue",
        "repo": "reject" if verdict == "reject" else "test",
        "opportunities": "reject" if verdict == "reject" else "review",
    }.get(domain, "reject")
    row = {
        "domain": domain,
        "type": item_type,
        "claim": "%s review for %s: %s" % (verdict, area, review.get("reason", "")),
        "evidence": (review.get("evidence", []) +
                     review.get("missing_evidence", []) +
                     review.get("risks", [])),
        "files": [],
        "confidence": "medium" if verdict == "accept" else "low",
        "action": action,
        "reject_reason": "" if item_type != "reject" else review.get("reason", ""),
        "lane": LANE_BY_DOMAIN.get(domain, "sistema"),
        "decision": ("hacer" if verdict == "accept" else
                     "descartar" if verdict == "reject" else "revisar"),
        "purpose": "juzgar salida de %s" % area,
        "next_action": review.get("next_action", "revisar evidencia"),
        "owner": "human" if verdict != "accept" else "MAK",
    }
    if isinstance(metadata, dict):
        row["metadata"] = metadata
    return row


def append_review(review, area, path=LEDGER, source="local_review", metadata=None):
    return append_item(review_to_ledger(review, area, metadata=metadata),
                       path=path, source=source)


def main(argv=None):
    parser = argparse.ArgumentParser(description="MAK common append-only ledger")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("append", help="append one ledger item from stdin")
    p_add.add_argument("--ledger", default=LEDGER)
    p_add.add_argument("--source", default="manual")
    p_sum = sub.add_parser("summary", help="summarize ledger")
    p_sum.add_argument("--ledger", default=LEDGER)
    p_sum.add_argument("--limit", type=int, default=50)
    p_audit = sub.add_parser("audit", help="quarantine missing evidence paths")
    p_audit.add_argument("--ledger", default=LEDGER)
    p_audit.add_argument("--quarantine", default="")
    p_review = sub.add_parser("review-quarantine",
                              help="classify quarantine without restoring items")
    p_review.add_argument("--quarantine", default="")
    p_review.add_argument("--root", action="append", dest="roots")
    args = parser.parse_args(argv)
    if args.cmd == "append":
        ok, errors, row = append_item(json.loads(input()), path=args.ledger,
                                      source=args.source)
        print(json.dumps({"ok": ok, "errors": errors, "item": row},
                         ensure_ascii=False))
        return 0 if ok else 2
    if args.cmd == "summary":
        print(json.dumps(summarize(args.ledger, args.limit),
                         ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "audit":
        found = audit_missing_paths(args.ledger)
        added = write_quarantine(found, args.quarantine or None)
        print(json.dumps({"found": len(found), "quarantined": len(added),
                          "items": added}, ensure_ascii=False))
        return 0
    if args.cmd == "review-quarantine":
        path = args.quarantine or os.path.join(
            HOME, "plataforma/common_ledger_quarantine.jsonl")
        rows = classify_quarantine(read_items_quarantine(path), roots=args.roots)
        print(json.dumps({"total": len(rows), "items": rows},
                         ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
