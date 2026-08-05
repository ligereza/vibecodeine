#!/usr/bin/env python3
"""Provider-agnostic batch contracts for MAK.

Temporary credits are fuel, not architecture. This module defines the durable
shape of delegated work so premium providers (Watsonx/AWS) can be burned now
and free/local providers (Cerebras/Groq/Ollama) can keep the same system alive
later.
"""
from __future__ import annotations

import json
import os
import time
import argparse
import sys

try:
    from . import ledger as common_ledger
except Exception:  # noqa: BLE001 - direct script deployment on MAK
    try:
        import ledger as common_ledger
    except Exception:  # noqa: BLE001 - batch validation can run without ledger
        common_ledger = None
try:
    from . import discernment
except Exception:  # noqa: BLE001 - direct script deployment on MAK
    try:
        import discernment
    except Exception:  # noqa: BLE001 - discernment prompt is optional
        discernment = None

HOME = os.path.expanduser("~")
LEDGER = os.path.join(HOME, "plataforma/external_batches.jsonl")
COMMON_LEDGER = os.path.join(HOME, "plataforma/common_ledger.jsonl")

SCHEMA_VERSION = "mak-batch-v1"

RESULT_REQUIRED = (
    "claim",
    "evidence",
    "files",
    "confidence",
    "action",
    "reject_reason",
)

AREAS = {
    "mak_quality": {
        "purpose": "audit MAK output quality and detect wrong formats or weak evidence",
        "default_paths": ["~/research/informes", "~/research/paneles",
                          "~/research/refutaciones", "~/plataforma/logs"],
        "actions": ["archive", "refute", "expose", "repair_queue", "reject"],
    },
    "rd_evidence": {
        "purpose": "surface primary-source leads for RD without mixing with curation",
        "default_paths": ["data", "docs/rd", "jobs", "svg/suplementos_rd"],
        "actions": ["verify_source", "triangulate", "reject", "draft_report"],
    },
    "iskvw_curation": {
        "purpose": "separate public archive, curation, and artwork interpretation",
        "default_paths": ["cultura/mak_curatoria", "projects", "docs/cultura"],
        "actions": ["curate", "expose", "archive", "reject"],
    },
    "tool_archaeology": {
        "purpose": "find duplicated or unused tools before creating new code",
        "default_paths": ["tools", "src/flujo", "cultura"],
        "actions": ["reuse", "merge", "retire", "test", "reject"],
    },
    "svg_pipeline": {
        "purpose": "map SVG generation paths for RD, laser, animation, and thi.ng measurement",
        "default_paths": ["svg", "projects", "tools", "web/src"],
        "actions": ["measure", "prototype", "reuse", "reject"],
    },
    "adobe_rescue": {
        "purpose": "rescue Illustrator/Adobe bridge work without confusing it with Blender",
        "default_paths": ["docs", "tools", "src/flujo", "exports"],
        "actions": ["rescue", "bridge", "reuse", "reject"],
    },
}

PROVIDER_LANES = {
    "premium_burst": ["watsonx", "aws"],
    "free_cloud": ["cerebras", "groq"],
    "local_floor": ["ollama"],
}


def provider_plan(available, allow_premium=True):
    """Return a stable provider order from transient to permanent lanes."""
    have = {str(p).lower() for p in (available or [])}
    order = []
    lanes = ("premium_burst", "free_cloud", "local_floor")
    for lane in lanes:
        if lane == "premium_burst" and not allow_premium:
            continue
        for provider in PROVIDER_LANES[lane]:
            if provider in have and provider not in order:
                order.append(provider)
    return order


def build_brief(area, batch_id, paths=None, providers=None, allow_premium=True):
    """Build the model-facing brief without binding it to one provider."""
    if area not in AREAS:
        raise ValueError("unknown area: %s" % area)
    cfg = AREAS[area]
    selected_paths = list(paths or cfg["default_paths"])
    plan = provider_plan(providers or [], allow_premium=allow_premium)
    brief = {
        "schema": SCHEMA_VERSION,
        "area": area,
        "batch_id": batch_id,
        "purpose": cfg["purpose"],
        "paths": selected_paths,
        "provider_plan": plan,
        "allowed_actions": cfg["actions"],
        "prompt": _prompt(area, batch_id, cfg, selected_paths, plan),
        "result_required": list(RESULT_REQUIRED),
    }
    if discernment is not None:
        brief["local_review"] = {
            "provider": "ollama",
            "schema": discernment.SCHEMA_VERSION,
            "prompt": discernment.build_review_prompt(area, {
                "area": area,
                "batch_id": batch_id,
                "result_required": list(RESULT_REQUIRED),
                "allowed_actions": cfg["actions"],
            }),
        }
    return brief


def _prompt(area, batch_id, cfg, paths, plan):
    return (
        "Eres un agente externo de MAK. Tu proveedor puede ser temporal; el "
        "contrato NO lo es. Trabaja solo con el material de esta tanda.\n\n"
        "AREA: %s\n"
        "BATCH: %s\n"
        "PROPOSITO: %s\n"
        "RUTAS:\n%s\n\n"
        "PLAN DE PROVEEDORES: %s\n\n"
        "DEVUELVE SOLO JSON con esta forma:\n"
        "{\n"
        '  "items": [{\n'
        '    "claim": "hallazgo atomico",\n'
        '    "evidence": ["ruta o fuente concreta"],\n'
        '    "files": ["archivo relacionado"],\n'
        '    "confidence": "high|medium|low",\n'
        '    "action": "%s",\n'
        '    "reject_reason": ""\n'
        "  }]\n"
        "}\n\n"
        "REGLAS:\n"
        "- Si no puedes sostener un claim, usa action=reject y explica reject_reason.\n"
        "- No escribas informes largos; entrega hallazgos verificables.\n"
        "- No mezcles RD con iskvw; no conviertas curatoria en research.\n"
        "- No pidas crear una herramienta si ya existe una ruta probable.\n"
        "- Cada item debe poder sobrevivir cuando Watsonx/AWS ya no existan.\n"
        % (area, batch_id, cfg["purpose"],
           "\n".join("- " + p for p in paths),
           ", ".join(plan) if plan else "(sin proveedor preferido)",
           "|".join(cfg["actions"]))
    )


def validate_result(payload):
    """Validate the external model output contract, not its truth."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except ValueError:
            return False, ["not_json"]
    if not isinstance(payload, dict):
        return False, ["not_object"]
    items = payload.get("items")
    if not isinstance(items, list):
        return False, ["items_not_list"]
    errors = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append("item_%d_not_object" % idx)
            continue
        for key in RESULT_REQUIRED:
            if key not in item:
                errors.append("item_%d_missing_%s" % (idx, key))
        if item.get("confidence") not in ("high", "medium", "low"):
            errors.append("item_%d_bad_confidence" % idx)
        if not isinstance(item.get("evidence"), list):
            errors.append("item_%d_evidence_not_list" % idx)
        if not isinstance(item.get("files"), list):
            errors.append("item_%d_files_not_list" % idx)
        if item.get("action") == "reject" and not item.get("reject_reason"):
            errors.append("item_%d_reject_without_reason" % idx)
    return not errors, errors


def append_ledger(row, path=LEDGER):
    """Append a durable batch record. Never writes credentials."""
    safe = {
        "ts": row.get("ts", time.strftime("%F %T")),
        "schema": row.get("schema", SCHEMA_VERSION),
        "area": row.get("area", ""),
        "batch_id": row.get("batch_id", ""),
        "provider": row.get("provider", ""),
        "status": row.get("status", ""),
        "items": int(row.get("items", 0) or 0),
        "errors": list(row.get("errors", []) or []),
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(safe, ensure_ascii=False, sort_keys=True) + "\n")
    return safe


def append_common_ledger(payload, area, path=COMMON_LEDGER, source="external"):
    """Write validated external items into the shared MAK ledger."""
    if common_ledger is None:
        return [], ["common_ledger_unavailable"]
    return common_ledger.append_external_result(payload, area, path=path,
                                                source=source)


def ingest_result(payload, area, common_path=COMMON_LEDGER, source="external",
                  reviewer=None, use_ollama=True):
    """Validate, locally judge, then append only accepted facts to common ledger."""
    ok, errors = validate_result(payload)
    if not ok:
        return {"ok": False, "status": "invalid", "errors": errors,
                "review": None, "items": 0}
    if isinstance(payload, str):
        payload = json.loads(payload)
    if discernment is None or common_ledger is None:
        return {"ok": False, "status": "unavailable",
                "errors": ["discernment_or_ledger_unavailable"],
                "review": None, "items": 0}
    review, meta = discernment.review_payload(
        area, payload, reviewer=reviewer, use_ollama=use_ollama)
    review_ok, review_errors = discernment.validate_review(review, area=area)
    if not review_ok:
        return {"ok": False, "status": "bad_review", "errors": review_errors,
                "review": review, "items": 0, "review_meta": meta}
    _review_ok, review_append_errors, _review_row = common_ledger.append_review(
        review, area, path=common_path, source="local_review:%s" % source)
    if review_append_errors:
        return {"ok": False, "status": "review_ledger_error",
                "errors": review_append_errors, "review": review,
                "items": 0, "review_meta": meta}
    if review["verdict"] != "accept":
        return {"ok": False, "status": review["verdict"], "errors": [],
                "review": review, "items": 0, "review_meta": meta}
    rows, ledger_errors = append_common_ledger(
        payload, area, path=common_path, source=source)
    return {"ok": not ledger_errors, "status": "accepted",
            "errors": ledger_errors, "review": review, "items": len(rows),
            "review_meta": meta}


def write_brief(brief, out_dir=None):
    """Persist a generated brief for any external provider/operator."""
    out_dir = out_dir or os.path.join(HOME, "plataforma/tandas")
    os.makedirs(out_dir, exist_ok=True)
    name = "%s-%s.json" % (brief["area"], brief["batch_id"])
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2, sort_keys=True)
    return path


def summarize_ledger(path=LEDGER, limit=20):
    """Small deterministic summary of external batch activity."""
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        rows = []
    rows = rows[-max(0, int(limit)):]
    by_area = {}
    by_provider = {}
    by_status = {}
    for row in rows:
        by_area[row.get("area", "")] = by_area.get(row.get("area", ""), 0) + 1
        by_provider[row.get("provider", "")] = (
            by_provider.get(row.get("provider", ""), 0) + 1)
        by_status[row.get("status", "")] = (
            by_status.get(row.get("status", ""), 0) + 1)
    return {
        "total": len(rows),
        "by_area": by_area,
        "by_provider": by_provider,
        "by_status": by_status,
        "last": rows[-5:],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build durable provider-agnostic MAK batch briefs")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("areas", help="list available batch areas")
    p_summary = sub.add_parser("summary", help="summarize external batch ledger")
    p_summary.add_argument("--ledger", default=LEDGER)
    p_summary.add_argument("--limit", type=int, default=20)

    p_brief = sub.add_parser("brief", help="render one batch brief as JSON")
    p_brief.add_argument("area", choices=sorted(AREAS))
    p_brief.add_argument("batch_id")
    p_brief.add_argument("--providers", default="",
                         help="CSV: watsonx,aws,cerebras,groq,ollama")
    p_brief.add_argument("--no-premium", action="store_true",
                         help="exclude temporary premium providers")
    p_brief.add_argument("--path", action="append", dest="paths",
                         help="override/add path; repeatable")

    p_val = sub.add_parser("validate", help="validate result JSON from stdin")
    p_val.add_argument("--ledger-provider", default="")
    p_val.add_argument("--ledger-area", default="")
    p_val.add_argument("--ledger-batch", default="")
    p_val.add_argument("--ledger", default="")
    p_val.add_argument("--common-ledger", default="")
    p_review = sub.add_parser("review-prompt",
                              help="build local Ollama review prompt for JSON stdin")
    p_review.add_argument("area", choices=sorted(AREAS))
    p_ingest = sub.add_parser("ingest",
                              help="validate, local-review and ingest JSON stdin")
    p_ingest.add_argument("area", choices=sorted(AREAS))
    p_ingest.add_argument("--provider", default="external")
    p_ingest.add_argument("--common-ledger", default=COMMON_LEDGER)
    p_ingest.add_argument("--no-ollama", action="store_true",
                          help="use deterministic local review only")

    args = parser.parse_args(argv)
    if args.cmd == "areas":
        print(json.dumps({"schema": SCHEMA_VERSION, "areas": sorted(AREAS)},
                         ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "brief":
        providers = [p.strip() for p in args.providers.split(",") if p.strip()]
        brief = build_brief(args.area, args.batch_id, paths=args.paths,
                            providers=providers,
                            allow_premium=not args.no_premium)
        print(json.dumps(brief, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "summary":
        print(json.dumps(summarize_ledger(args.ledger, args.limit),
                         ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "validate":
        raw = sys.stdin.read()
        ok, errors = validate_result(raw)
        if args.ledger:
            try:
                payload = json.loads(raw)
                items = len(payload.get("items", [])) if isinstance(payload, dict) else 0
            except ValueError:
                items = 0
            append_ledger({
                "area": args.ledger_area,
                "batch_id": args.ledger_batch,
                "provider": args.ledger_provider,
                "status": "ok" if ok else "invalid",
                "items": items,
                "errors": errors,
            }, path=args.ledger)
        common_errors = []
        if ok and args.common_ledger:
            try:
                payload = json.loads(raw)
                _rows, common_errors = append_common_ledger(
                    payload, args.ledger_area, path=args.common_ledger,
                    source=args.ledger_provider or "external")
            except ValueError:
                common_errors = ["not_json"]
            if common_errors:
                ok = False
                errors = errors + common_errors
        print(json.dumps({"ok": ok, "errors": errors}, ensure_ascii=False))
        return 0 if ok else 2
    if args.cmd == "review-prompt":
        if discernment is None:
            print(json.dumps({"ok": False, "errors": ["discernment_unavailable"]},
                             ensure_ascii=False))
            return 2
        raw = sys.stdin.read()
        try:
            payload = json.loads(raw)
        except ValueError:
            payload = {"raw": raw}
        print(discernment.build_review_prompt(args.area, payload))
        return 0
    if args.cmd == "ingest":
        raw = sys.stdin.read()
        result = ingest_result(
            raw, args.area, common_path=args.common_ledger,
            source=args.provider, use_ollama=not args.no_ollama)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["ok"] else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
