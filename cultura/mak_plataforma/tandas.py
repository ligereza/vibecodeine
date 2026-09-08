#!/usr/bin/env python3
"""Provider-agnostic batch contracts for MAK.

Temporary credits are fuel, not architecture. This module defines the durable
shape of delegated work so free/local providers (Cerebras/Groq/Ollama) keep the
same system alive without a premium-provider dependency.
"""
from __future__ import annotations

import json
import os
import time
import argparse
import glob
import sys
from pathlib import Path

try:
    from cultura.mak_conductor.runtime import active_enabled, dispatch_sync
except ImportError:  # pragma: no cover - direct MAK deployment
    sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH", "/home/mak/cultura"))
    try:
        from mak_conductor.runtime import active_enabled, dispatch_sync
    except ImportError:
        active_enabled = lambda: False
        dispatch_sync = None

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
try:
    from . import research_router
except Exception:  # noqa: BLE001 - direct script deployment on MAK
    try:
        import research_router
    except Exception:  # noqa: BLE001 - profile policy is optional
        research_router = None
try:
    from . import providers as external_providers
except Exception:  # noqa: BLE001 - direct script deployment on MAK
    try:
        import providers as external_providers
    except Exception:  # noqa: BLE001 - batch briefs can run without providers
        external_providers = None

HOME = os.path.expanduser("~")
LEDGER = os.path.join(HOME, "plataforma/external_batches.jsonl")
COMMON_LEDGER = os.path.join(HOME, "plataforma/common_ledger.jsonl")

SCHEMA_VERSION = "mak-batch-v1"
WORK_SCHEMA_VERSION = "mak-work-v1"
IDENTITY_SCHEMA = "mak-identity-v1"

RESULT_REQUIRED = (
    "claim",
    "evidence",
    "files",
    "confidence",
    "action",
    "reject_reason",
)

PRODUCT_CONTRACTS = {
    "mak_quality": ("verdict", "defect_class", "queue_action"),
    "rd_evidence": ("primary_source", "triangulation", "uncertainty"),
    "iskvw_curation": ("artwork_reading", "selection", "public_status"),
    "portfolio_record": ("record_kind", "relations", "unknowns"),
    "tool_archaeology": ("existing_path", "reuse_test", "decision"),
    "svg_pipeline": ("representation", "measurement", "next_prototype"),
    "adobe_rescue": ("bridge", "installation_evidence", "rescue_action"),
    "opportunity_radar": ("opportunity", "eligibility", "deadline", "source",
                           "next_action", "risk"),
}


def _identity_for_batch(area, batch_id, provider):
    kinds = {
        "rd_evidence": "report",
        "iskvw_curation": "work",
        "portfolio_record": "record",
        "mak_quality": "report",
        "opportunity_radar": "opportunity",
        "svg_pipeline": "work",
        "tool_archaeology": "system",
        "adobe_rescue": "system",
    }
    return {
        "schema": IDENTITY_SCHEMA,
        "kind": kinds.get(area, "task"),
        "source_id": "%s:%s" % (area, batch_id),
        "parent_id": "batch:%s" % batch_id,
        "entities": {
            "artist": [], "username": [], "client": [], "collab": [],
            "event": [], "festival": [], "venue": [], "location": [],
            "source": [provider] if provider else [],
        },
        "event_date": "",
        "published_at": "",
    }


def _print_json(payload, indent=None):
    """Print machine JSON safely on Windows cp1252 consoles."""
    print(json.dumps(payload, ensure_ascii=True, indent=indent))


def _safe_text(value):
    """Replace lone Unicode surrogates before persisting model output."""
    return "".join("\ufffd" if 0xD800 <= ord(char) <= 0xDFFF else char
                   for char in str(value or ""))


def _safe_tree(value):
    """Sanitize decoded JSON too; escaped surrogates appear after json.loads."""
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, list):
        return [_safe_tree(item) for item in value]
    if isinstance(value, dict):
        return {_safe_tree(key): _safe_tree(item) for key, item in value.items()}
    return value


def _path_roots():
    roots = []
    repo_root = str(Path(__file__).resolve().parents[2])
    for value in (
            os.environ.get("MAK_REPO_ROOT", ""),
            os.path.join(repo_root, "flujo"),
            repo_root,
            "/home/mak/flujo",
            os.getcwd(),
            os.path.join(os.path.expanduser("~"), "plataforma")):
        if value and value not in roots:
            roots.append(value)
    return roots


def _resolve_existing_path(path):
    value = os.path.expandvars(os.path.expanduser(str(path or "")))
    if os.path.isabs(value) and os.path.exists(value):
        return value
    for root in _path_roots():
        candidate = os.path.join(root, value)
        if os.path.exists(candidate):
            return candidate
    return ""


def _manifest_asset_paths(extra_paths):
    assets = []
    for path in extra_paths or []:
        resolved = _resolve_existing_path(path)
        if not resolved or not resolved.lower().endswith(".json"):
            continue
        try:
            with open(resolved, encoding="utf-8") as fh:
                manifest = json.load(fh)
        except (OSError, ValueError, TypeError):
            continue
        root = str(manifest.get("asset_root") or "").strip()
        if not root:
            continue
        rows = (manifest.get("rows") or manifest.get("items") or
                manifest.get("candidate_rows") or [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            for field in ("asset_path", "uri_export"):
                value = str(row.get(field) or "").strip()
                for prefix in ("/portfolio-media/", "portfolio-media/"):
                    if value.startswith(prefix):
                        value = value[len(prefix):]
                        break
                candidate = os.path.realpath(os.path.join(root, value))
                if os.path.isfile(candidate) and candidate not in assets:
                    assets.append(candidate)
    return assets

AREAS = {
    "mak_quality": {
        "purpose": "audit MAK output quality and detect wrong formats or weak evidence",
        "default_paths": ["~/research/informes", "~/research/paneles",
                          "~/research/refutaciones", "~/plataforma/logs"],
        "evidence_paths": ["cultura/mak_plataforma/trabajo.py",
                           "cultura/mak_plataforma/research_router.py",
                           "cultura/mak_research/research_lib.py"],
        "actions": ["archive", "refute", "expose", "repair_queue", "reject"],
    },
    "rd_evidence": {
        "purpose": "surface primary-source leads for RD without mixing with curation",
        "default_paths": ["data", "docs/rd", "jobs", "svg/suplementos_rd"],
        "evidence_paths": ["src/flujo/rd/database.py",
                           "src/flujo/rd/panel.py",
                           "cultura/mak_research/fuentes.py",
                           "tests/test_rd_database.py",
                           "tests/test_fuentes.py"],
        "actions": ["verify_source", "triangulate", "reject", "draft_report"],
    },
    "iskvw_curation": {
        "purpose": "separate public archive, curation, and artwork interpretation",
        "default_paths": ["cultura/mak_curatoria", "projects", "docs/cultura"],
        "evidence_paths": ["tools/gen_archivo_iskvw.py",
                           "tools/validar_curaduria.py",
                           "tools/consolidar_fichas.py",
                           "docs/cultura/FORMATO_ENSAYO.md",
                           "cultura/mak_plataforma/trabajo.py"],
        "actions": ["curate", "expose", "archive", "reject"],
    },
    "portfolio_record": {
        "purpose": "triage audiovisual records without turning stories into works",
        "default_paths": ["~/plataforma/director_runs/faro-story-review-queue-20260809.json"],
        "evidence_paths": [],
        "actions": ["triangulate", "archive", "review", "reject"],
    },
    "tool_archaeology": {
        "purpose": "find duplicated or unused tools before creating new code",
        "default_paths": ["tools", "src/flujo", "cultura"],
        # context_pack.py and token_budget.py were retired on 2026-08-29 with no
        # measured consumer. An allowlist that still names them authorises a
        # citation that can never resolve, which reads as a valid path until a
        # tanda tries it.
        "evidence_paths": ["tools/system_map.py",
                           "tools/arqueologia.py",
                           "tools/esfuerzo.py"],
        "actions": ["reuse", "merge", "retire", "test", "reject"],
    },
    "svg_pipeline": {
        "purpose": "map SVG generation paths for RD, laser, animation, and thi.ng measurement",
        "default_paths": ["svg", "projects", "tools", "web/src"],
        "evidence_paths": ["cultura/mak_codex/iconos.py",
                           "docs/cultura/MOTOR_SEMANTICO.md",
                           "docs/cultura/lib/compilador.js",
                           "src/flujo/laser.py",
                           "tests/test_thing_registro.py",
                           "tests/test_iskvw_librerias.py"],
        "actions": ["measure", "prototype", "reuse", "reject"],
    },
    "adobe_rescue": {
        "purpose": "rescue Illustrator/Adobe bridge work without confusing it with Blender",
        "default_paths": ["docs", "tools", "src/flujo", "exports"],
        "evidence_paths": ["tools/illustrator/README.md",
                           "tools/adobe_panel/README.md",
                           "tools/adobe_panel/js/main.js",
                           "tools/adobe_panel/check_install.ps1",
                           "tools/illustrator/scripts/logo_clean_master.jsx",
                           "tools/illustrator/scripts/logo_revector_batch.jsx",
                           "src/flujo/export/illustrator.py",
                           "src/flujo/export/illustrator_bridge.py"],
        "actions": ["rescue", "bridge", "reuse", "reject"],
    },
    "opportunity_radar": {
        "purpose": "find artist-compatible opportunities without auto-contact or submission",
        "default_paths": ["context/artist_context.example.json",
                           "cultura/mak_vigia/fuentes.json",
                           "docs/becas"],
        "evidence_paths": ["context/artist_context.example.json",
                           "cultura/mak_vigia/fuentes.json",
                           "docs/becas/CALENDARIO_POSTULACIONES.md",
                           "cultura/mak_research/fuentes.py"],
        "actions": ["verify_source", "triangulate", "draft_report", "reject"],
    },
}

PROVIDER_LANES = {
    "free_cloud": ["groq", "gemini", "cerebras"],
    "local_floor": ["ollama"],
}


def provider_plan(available, allow_premium=True):
    """Return a stable provider order from transient to permanent lanes."""
    if external_providers is not None and hasattr(external_providers, "provider_plan"):
        return external_providers.provider_plan(available,
                                                allow_premium=allow_premium)
    have = {str(p).lower() for p in (available or [])}
    order = []
    lanes = ("free_cloud", "local_floor")
    for lane in lanes:
        for provider in PROVIDER_LANES[lane]:
            if provider in have and provider not in order:
                order.append(provider)
    return order


def build_brief(area, batch_id, paths=None, providers=None, allow_premium=True,
                include_evidence=False, max_evidence_chars=60000,
                instruction=""):
    """Build the model-facing brief without binding it to one provider."""
    if area not in AREAS:
        raise ValueError("unknown area: %s" % area)
    cfg = AREAS[area]
    profile = (research_router.profile_for_area(area)
               if research_router is not None else None)
    selected_paths = list(paths or cfg["default_paths"])
    plan = provider_plan(providers or [], allow_premium=allow_premium)
    lane = {"rd_evidence": "trabajo", "opportunity_radar": "trabajo",
            "iskvw_curation": "obra", "portfolio_record": "obra",
            "svg_pipeline": "obra"}.get(area, "sistema")
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    identity = _identity_for_batch(area, batch_id,
                                   plan[0] if plan else "unknown")
    if common_ledger is not None and hasattr(common_ledger, "build_work_envelope"):
        work = common_ledger.build_work_envelope(
            "%s:%s" % (area, batch_id), "batch:%s" % batch_id, lane,
            cfg["purpose"], "external_batch", plan[0] if plan else "unknown",
            sources=selected_paths, status="in_progress", identity=identity,
            owner="MAK", next_action="await_external_result",
            evidence_required=["source_manifest", "provider_output", "local_review"],
            allowed_decisions=(common_ledger.DECISIONS
                               if common_ledger is not None else ()),
            fallback_chain=plan[1:], created_at=created_at)
    else:
        work = {
            "schema": WORK_SCHEMA_VERSION,
            "work_id": "%s:%s" % (area, batch_id),
            "parent_task": "batch:%s" % batch_id,
            "lane": lane, "purpose": cfg["purpose"],
            "format": "external_batch", "created_at": created_at,
            "provider": plan[0] if plan else "unknown", "sources": selected_paths,
            "status": "in_progress", "owner": "MAK",
            "next_action": "await_external_result",
            "evidence_required": ["source_manifest", "provider_output", "local_review"],
            "allowed_decisions": ["hacer", "revisar", "refutar", "archivar", "descartar"],
            "fallback_chain": plan[1:], "identity": identity,
        }
    brief = {
        "schema": SCHEMA_VERSION,
        "area": area,
        "batch_id": batch_id,
        "work": work,
        "purpose": cfg["purpose"],
        "paths": selected_paths,
        "provider_plan": plan,
        "allowed_actions": cfg["actions"],
        "product_contract": list(PRODUCT_CONTRACTS[area]),
        "prompt": _prompt(
            area, batch_id, cfg, selected_paths, plan,
            evidence=evidence_package(area, paths=paths,
                                      max_chars=max_evidence_chars)
            if include_evidence else "",
            instruction=instruction, profile=profile),
        "result_required": list(RESULT_REQUIRED) + ["product"],
    }
    if profile:
        brief["promotion_policy"] = {
            "allowed_formats": list(profile["allowed_formats"]),
            "required_evidence": profile["required_evidence"],
            "promotion_actions": list(profile["promotion_actions"]),
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


def _prompt(area, batch_id, cfg, paths, plan, evidence="", instruction="",
            profile=None):
    evidence_block = (
        "\nPAQUETE DE EVIDENCIA LOCAL:\n%s\n" % evidence
        if evidence else
        "\nPAQUETE DE EVIDENCIA LOCAL: no incluido en este brief.\n"
    )
    instruction_block = (
        "\nINSTRUCCION DE ESTA RONDA:\n%s\n" % instruction.strip()
        if instruction else ""
    )
    curation_guard = (
        "- En iskvw, public_status describe una propuesta local: nunca uses "
        "publicada, public o published sin firma humana.\n"
        if area == "iskvw_curation" else ""
    )
    quality_hint = (
        "- En mak_quality no dejes campos product vacios: si no detectas un "
        "defecto usa defect_class=sin_defecto y explica la decision en verdict. "
        "Usa exactamente format=revision y evidence_kind=local_corpus.\n"
        if area == "mak_quality" else ""
    )
    opportunity_hint = (
        "- En opportunity_radar product debe incluir una elegibilidad concreta, "
        "una fecha verificable, source como URL oficial y next_action humana; "
        "si falta cualquiera, no inventes el dato: usa revise/reject.\n"
        if area == "opportunity_radar" else ""
    )
    record_hint = (
        "- En portfolio_record una historia es un registro audiovisual: usa "
        "record_kind=story_record, separa relations de unknowns y no la llames "
        "obra salvo que exista una decision humana independiente.\n"
        if area == "portfolio_record" else ""
    )
    profile_block = ""
    item_profile_fields = ""
    claim_example = ("lectura curatorial de la obra"
                     if area == "iskvw_curation" else
                     "registro audiovisual candidato"
                     if area == "portfolio_record" else "hallazgo atomico")
    if profile:
        profile_block = (
            "\nPOLITICA DE PROMOCION:\n"
            "- formatos permitidos: %s\n"
            "- evidence_kind DEBE ser exactamente: %s\n"
            "- acciones permitidas: %s\n"
            "- VALORES LITERALES ASCII: format=%r; evidence_kind=%r\n"
            % (", ".join(profile["allowed_formats"]),
               profile["required_evidence"],
               ", ".join(profile["promotion_actions"]),
               profile["allowed_formats"][0], profile["required_evidence"])
        )
        item_profile_fields = (
            '    "format": "%s",\n'
            '    "evidence_kind": "%s",\n'
            % (profile["allowed_formats"][0], profile["required_evidence"])
        )
    return (
        "Eres un agente externo de MAK. Tu proveedor puede ser temporal; el "
        "contrato NO lo es. Trabaja solo con el material de esta tanda.\n\n"
        "AREA: %s\n"
        "BATCH: %s\n"
        "PROPOSITO: %s\n"
        "RUTAS:\n%s\n\n"
        "PLAN DE PROVEEDORES: %s\n"
        "CONTRATO DE PRODUCTO: %s\n"
        "%s"
        "%s\n"
        "%s"
        "DEVUELVE SOLO JSON con esta forma:\n"
        "{\n"
        '  "items": [{\n'
        '    "claim": %r,\n'
        '    "evidence": ["ruta o fuente concreta"],\n'
        '    "files": ["archivo relacionado"],\n'
        '    "confidence": "high|medium|low",\n'
        '    "action": "%s",\n'
        '    "reject_reason": "",\n'
        '%s'
         '    "product": %s\n'
        "  }]\n"
        "}\n\n"
        "REGLAS:\n"
        "- Si no puedes sostener un claim, usa action=reject y explica reject_reason.\n"
        "- Cada item DEBE incluir product con todos los campos del contrato de producto.\n"
        "- Usa exactamente los valores de formato y evidence_kind indicados en la politica; no inventes sinonimos.\n"
        "- No escribas informes largos; entrega hallazgos verificables.\n"
        "- No mezcles RD con iskvw; no conviertas curatoria en research.\n"
        "%s"
        "%s"
        "%s"
        "%s"
        "- No pidas crear una herramienta si ya existe una ruta probable.\n"
        "- Cada item debe poder sobrevivir con Cerebras, Groq u Ollama.\n"
        "- Cada entrada files debe existir en el material entregado; nunca inventes nombres.\n"
        % (area, batch_id, cfg["purpose"],
           "\n".join("- " + p for p in paths),
           ", ".join(plan) if plan else "(sin proveedor preferido)",
           ", ".join(PRODUCT_CONTRACTS[area]),
           profile_block,
           evidence_block,
           instruction_block,
           claim_example,
           "|".join(cfg["actions"]),
           item_profile_fields,
           curation_guard,
           quality_hint,
           opportunity_hint,
           record_hint,
           json.dumps({field: "" for field in PRODUCT_CONTRACTS[area]},
                      ensure_ascii=False))
    )


def evidence_package(area, paths=None, max_chars=60000):
    """Return a bounded local evidence pack for external models."""
    if area not in AREAS:
        raise ValueError("unknown area: %s" % area)
    chunks = []
    remaining = int(max_chars)
    candidates = []
    source_paths = (list(paths) if paths is not None
                    else AREAS[area].get("evidence_paths", []))
    for path in source_paths:
        if path not in candidates:
            candidates.append(path)
    expanded = []
    for candidate in candidates:
        value = os.path.expandvars(os.path.expanduser(str(candidate)))
        matches = glob.glob(value, recursive=True) if glob.has_magic(value) else []
        if matches:
            expanded.extend(matches)
            continue
        if os.path.isdir(value):
            expanded.extend(sorted(glob.glob(
                os.path.join(value, "**", "*"), recursive=True)))
            continue
        expanded.append(candidate)
    for path in expanded:
        if remaining <= 0:
            break
        resolved = _resolve_existing_path(path)
        if not os.path.isfile(resolved):
            continue
        try:
            with open(resolved, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        budget = max(500, min(remaining, max_chars // 3))
        if len(text) > budget:
            text = text[:budget] + "\n... [truncated]\n"
        block = "\n### %s\n%s\n" % (resolved, text)
        chunks.append(block)
        remaining -= len(block)
    return "".join(chunks).strip()


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


def validate_work_identity(work):
    """Validate the trace envelope before a batch can enter the ledger."""
    if not isinstance(work, dict):
        return ["work_not_object"]
    identity = work.get("identity")
    if not isinstance(identity, dict):
        return ["work_identity_missing"]
    errors = []
    if identity.get("schema") != IDENTITY_SCHEMA:
        errors.append("work_identity_bad_schema")
    kind = str(identity.get("kind") or "")
    if not kind:
        errors.append("work_identity_missing_kind")
    if kind != "legacy_unknown" and not str(identity.get("source_id") or "").strip():
        errors.append("work_identity_missing_source_id")
    if not isinstance(identity.get("entities"), dict):
        errors.append("work_identity_entities_not_object")
    return errors


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
    if row.get("failure_class"):
        safe["failure_class"] = str(row["failure_class"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(safe, ensure_ascii=False, sort_keys=True) + "\n")
    return safe


def _provider_failure_class(exc):
    """Classify provider failure without treating it as evidence."""
    text = str(exc or "").lower()
    if "timeout" in text or "timed out" in text:
        return "timeout"
    if any(marker in text for marker in ("unavailable", "not installed", "connection refused")):
        return "unavailable"
    return "error"


def validate_product_contract(payload, area):
    """Require the area-specific deliverable block for new external runs."""
    if area not in PRODUCT_CONTRACTS:
        return False, ["unknown_product_area"]
    errors = []
    items = payload.get("items", []) if isinstance(payload, dict) else []
    for idx, item in enumerate(items):
        product = item.get("product") if isinstance(item, dict) else None
        if not isinstance(product, dict):
            errors.append("item_%d_missing_product" % idx)
            continue
        for field in PRODUCT_CONTRACTS[area]:
            if not str(product.get(field, "")).strip():
                errors.append("item_%d_missing_product_%s" % (idx, field))
    return not errors, errors


def validate_evidence_paths(payload, area=None, extra_paths=None):
    """Reject unknown files, resolving evidence-pack basenames safely."""
    errors = []
    items = payload.get("items", []) if isinstance(payload, dict) else []
    manifest_assets = _manifest_asset_paths(extra_paths)
    for idx, item in enumerate(items):
        for file_idx, path in enumerate(item.get("files", []) or []):
            if (area == "rd_evidence" and isinstance(path, str)
                    and path.startswith(("https://", "http://"))):
                continue
            if extra_paths is not None:
                allowed = [candidate for candidate in extra_paths
                           if os.path.basename(candidate) == os.path.basename(path)
                           or os.path.normcase(str(candidate)) == os.path.normcase(str(path))]
                if not allowed and isinstance(path, str):
                    normalized = path.replace("\\", "/").lstrip("/")
                    variants = [normalized]
                    if normalized.startswith("portfolio-media/"):
                        variants.append(normalized[len("portfolio-media/"):])
                    allowed = [candidate for candidate in manifest_assets
                               if any(candidate.replace("\\", "/").endswith(
                                   "/" + variant) for variant in variants)]
                if not allowed:
                    errors.append("item_%d_missing_evidence_path_%d" % (idx, file_idx))
                    continue
                resolved = _resolve_existing_path(allowed[0])
                if not resolved:
                    errors.append("item_%d_missing_evidence_path_%d" % (idx, file_idx))
                    continue
                continue
            resolved = _resolve_existing_path(path) if isinstance(path, str) else ""
            if not resolved and area in AREAS and isinstance(path, str):
                allowed_paths = (list(extra_paths)
                                 if extra_paths is not None else
                                 AREAS[area].get("evidence_paths", []))
                candidates = [candidate for candidate in allowed_paths
                    if os.path.basename(candidate) == os.path.basename(path)]
                if len(candidates) == 1:
                    resolved = _resolve_existing_path(candidates[0])
            if not resolved:
                errors.append("item_%d_missing_evidence_path_%d" % (idx, file_idx))
    return not errors, errors


def normalize_remote_evidence(payload, area=None):
    """Treat official URLs as evidence paths for factual products."""
    if area != "rd_evidence" or not isinstance(payload, dict):
        return payload
    for item in payload.get("items", []) or []:
        if not isinstance(item, dict):
            continue
        files = item.get("files") or []
        urls = [value for value in (item.get("evidence") or [])
                if isinstance(value, str)
                and value.startswith(("https://", "http://"))]
        if not files and urls:
            item["files"] = urls
    return payload


def append_common_ledger(payload, area, path=COMMON_LEDGER, source="external"):
    """Write validated external items into the shared MAK ledger."""
    if common_ledger is None:
        return [], ["common_ledger_unavailable"]
    return common_ledger.append_external_result(payload, area, path=path,
                                                source=source)


def ingest_result(payload, area, common_path=COMMON_LEDGER, source="external",
                  reviewer=None, use_ollama=True, strict_product=False,
                  extra_paths=None):
    """Validate, locally judge, then append only accepted facts to common ledger."""
    if isinstance(payload, str):
        payload = json.loads(payload)
    payload = normalize_remote_evidence(payload, area=area)
    ok, errors = validate_result(payload)
    if not ok:
        return {"ok": False, "status": "invalid", "errors": errors,
                "review": None, "items": 0}
    if strict_product:
        product_ok, product_errors = validate_product_contract(payload, area)
        if not product_ok:
            return {"ok": False, "status": "revise", "errors": product_errors,
                    "review": None, "items": 0}
        evidence_ok, evidence_errors = validate_evidence_paths(
            payload, area=area, extra_paths=extra_paths)
        if not evidence_ok:
            return {"ok": False, "status": "revise", "errors": evidence_errors,
                    "review": None, "items": 0}
    payload.setdefault("work", {
        "schema": WORK_SCHEMA_VERSION,
        "work_id": "legacy:%s" % area,
        "parent_task": "legacy_unknown",
        "lane": "trabajo" if area in {"rd_evidence", "opportunity_radar"} else "sistema",
        "purpose": "legacy payload without declared purpose",
        "format": "legacy_unknown",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provider": source,
        "sources": [],
        "status": "legacy_unknown",
        "identity": {
            "schema": IDENTITY_SCHEMA,
            "kind": "legacy_unknown",
            "source_id": "",
            "parent_id": "",
            "entities": {},
            "event_date": "",
            "published_at": "",
        },
    })
    identity_errors = validate_work_identity(payload.get("work"))
    if identity_errors:
        return {"ok": False, "status": "invalid", "errors": identity_errors,
                "review": None, "items": 0}
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
    profile_verdict = "accept"
    if research_router is not None:
        profile_verdict = research_router.validate_profile_result(
            research_router.profile_for_area(area), payload)
        if profile_verdict != "accept":
            review = dict(review)
            review["verdict"] = profile_verdict
            review["reason"] = "profile policy: %s" % profile_verdict
            review["risks"] = list(review.get("risks", [])) + [
                "profile promotion policy failed"]
    _review_ok, review_append_errors, _review_row = common_ledger.append_review(
        review, area, path=common_path, source="local_review:%s" % source,
        metadata={
            "provider": source,
            "reviewer": meta.get("reviewer", ""),
            "fallback": bool(meta.get("fallback", False)),
            "profile_verdict": profile_verdict,
            "work": payload.get("work", {}),
        })
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


def _parse_provider_json(text):
    if isinstance(text, dict):
        return text
    clean = str(text or "").strip()
    if clean.startswith("```"):
        lines = clean.splitlines()
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        try:
            return json.loads("\n".join(lines))
        except ValueError:
            pass
    if discernment is not None:
        extracted = discernment.extract_json(text)
        if extracted is not None:
            return extracted
    return json.loads(text)


def _product_repair_prompt(area, payload):
    fields = ", ".join(PRODUCT_CONTRACTS[area])
    template = json.dumps({field: "" for field in PRODUCT_CONTRACTS[area]},
                          ensure_ascii=False)
    return (
        "Repara SOLO el formato del JSON de MAK. No cambies claim, evidence, "
        "files, confidence, action ni reject_reason. Agrega o completa el "
        "objeto product en cada item con exactamente estos campos: %s. "
        "Usa este molde exacto para product: %s. No inventes rutas ni hechos. "
        "Devuelve solo JSON con items.\n\n%s"
        % (fields, template, json.dumps(payload, ensure_ascii=False, indent=2)))


def _product_response_schema(area):
    product = {field: {"type": "string"} for field in PRODUCT_CONTRACTS[area]}
    item = {
        "type": "object",
        "properties": {
            "claim": {"type": "string"},
            "evidence": {"type": "array", "items": {"type": "string"}},
            "files": {"type": "array", "items": {"type": "string"}},
            "confidence": {"type": "string"},
            "action": {"type": "string"},
            "reject_reason": {"type": "string"},
            "product": {"type": "object", "properties": product,
                        "required": list(PRODUCT_CONTRACTS[area])},
        },
        "required": ["claim", "evidence", "files", "confidence", "action",
                      "reject_reason", "product"],
    }
    return {"type": "object", "properties": {
        "items": {"type": "array", "items": item}}, "required": ["items"]}


def _repair_product_payload(area, payload, provider, model, max_tokens):
    kwargs = {}
    if provider == "ollama":
        kwargs["response_format"] = _product_response_schema(area)
    raw = external_providers.call(
        provider, _product_repair_prompt(area, payload), model=model,
        max_tokens=min(max_tokens, 1400), temperature=0.0, **kwargs)
    return _parse_provider_json(raw), raw


def _conservative_portfolio_repair(payload, area):
    if area != "portfolio_record" or not isinstance(payload, dict):
        return None
    repaired = _safe_tree(payload)
    for item in repaired.get("items", []):
        if not isinstance(item, dict) or not isinstance(item.get("product"), dict):
            return None
        product = item["product"]
        if not str(product.get("record_kind") or "").strip():
            file_text = " ".join(str(value).lower()
                                  for value in item.get("files", []) or [])
            if "/stories/" in file_text or "media/stories/" in file_text:
                product["record_kind"] = "story_record"
            elif any(marker in file_text for marker in
                     ("/posts/", "media/posts/", "/igtv/", "media/igtv/",
                      "/reels/", "media/reels/")):
                product["record_kind"] = "published_media_record"
            else:
                return None
        product["relations"] = (str(product.get("relations") or "").strip()
                                 or "sin_relaciones_observables")
        product["unknowns"] = (str(product.get("unknowns") or "").strip()
                                or "identidad_evento_venue_artista_cliente_no_confirmada")
    return repaired


def _human_portfolio_review_for_files(common_path, files):
    targets = set()
    for value in files or []:
        text = str(value or "").strip()
        if text:
            targets.add(text.replace("\\", "/"))
            targets.add(os.path.basename(text))
    if not targets:
        return {}
    latest = {}
    try:
        with open(common_path, encoding="utf-8") as handle:
            rows = handle.readlines()
    except OSError:
        return {}
    for line in rows:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        review = (row.get("metadata") or {}).get("external_candidate_review")
        if not isinstance(review, dict):
            continue
        source_id = str(review.get("source_id") or "").strip()
        normalized = source_id.replace("\\", "/")
        if normalized not in targets and os.path.basename(normalized) not in targets:
            continue
        latest[os.path.basename(normalized)] = review
    return latest


def _apply_human_portfolio_classification(payload, common_path):
    if not isinstance(payload, dict):
        return payload
    for item in payload.get("items", []):
        if not isinstance(item, dict):
            continue
        product = item.get("product")
        if not isinstance(product, dict):
            continue
        files = item.get("files") or item.get("evidence") or []
        reviews = _human_portfolio_review_for_files(common_path, files)
        review = next((reviews.get(os.path.basename(str(path)))
                       for path in files
                       if reviews.get(os.path.basename(str(path)))), None)
        if not review or str(review.get("decision") or "").lower() != "accept":
            continue
        context = review.get("context_fields")
        if not isinstance(context, dict):
            context = {}
        relation = str(review.get("relation") or "").strip()
        note = str(review.get("note") or "").strip()
        relations = product.get("relations")
        relation_payload = {}
        if isinstance(relations, str) and relations.strip():
            try:
                parsed_relations = json.loads(relations)
                if isinstance(parsed_relations, dict):
                    relation_payload.update(parsed_relations)
            except ValueError:
                relation_payload["provider_relations"] = relations.strip()
        relation_payload.update({
            "classification": "obra",
            "classification_source": "human",
            "human_context": context,
            "human_decision": "accept",
        })
        if relation:
            relation_payload["human_relation"] = relation
        if note:
            relation_payload["human_note"] = note
        product["record_kind"] = "obra"
        product["relations"] = json.dumps(
            relation_payload, ensure_ascii=False, sort_keys=True)
        product["unknowns"] = (str(product.get("unknowns") or "").strip()
                                or "identidad_artista_cliente_evento_venue_no_confirmada")
    return payload


def _conservative_opportunity_repair(payload, area):
    """Repair only a missing human next action, never opportunity facts."""
    if area != "opportunity_radar" or not isinstance(payload, dict):
        return None
    repaired = _safe_tree(payload)
    for item in repaired.get("items", []):
        if not isinstance(item, dict) or not isinstance(item.get("product"), dict):
            return None
        product = item["product"]
        required_facts = ("opportunity", "eligibility", "deadline", "source",
                          "risk")
        if any(not str(product.get(field) or "").strip()
               for field in required_facts):
            return None
        product["next_action"] = (
            str(product.get("next_action") or "").strip()
            or "verificar fuente oficial, elegibilidad y fecha de cierre exacta")
    return repaired


def _run_external_batch_unlocked(area, batch_id, provider, paths=None, model=None,
                       out_dir=None, common_path=COMMON_LEDGER,
                       batch_path=LEDGER, use_ollama=True, max_tokens=2500,
                       instruction="", max_items=5, image_paths=None):
    """Run one external provider, persist raw output, then ingest through the gate."""
    if external_providers is None:
        raise RuntimeError("external_providers_unavailable")
    brief = build_brief(area, batch_id, paths=paths,
                        providers=[provider, "ollama"],
                        include_evidence=True, instruction=instruction)
    budget = max(1, int(max_items))
    prompt = brief["prompt"] + (
        "\nPRESUPUESTO DURO DE ESTA TANDA: devuelve como maximo %d items. "
        "Si hay mas hallazgos, conserva solo los mas verificables y deja "
        "constancia en reject_reason de lo omitido.\n" % budget)
    if image_paths:
        allowed_images = [os.path.abspath(str(path)) for path in image_paths]
        prompt += (
            "\nEVIDENCIA VISUAL CERRADA:\n"
            "Solo puedes usar estas imagenes como files; copia la ruta exacta "
            "y no uses rutas del manifiesto ni nombres inventados:\n%s\n"
            "Para esta ronda devuelve como maximo un item por imagen y "
            "separa obra, registro, pantalla/flyer y desconocido.\n"
            % "\n".join("- " + path for path in allowed_images))
        image_paths = allowed_images
    try:
        kwargs = {}
        if provider == "ollama":
            kwargs["response_format"] = _product_response_schema(area)
        call_kwargs = dict(kwargs)
        if image_paths:
            call_kwargs["image_paths"] = image_paths
        raw = external_providers.call(
            provider, prompt, model=model, max_tokens=max_tokens,
            temperature=0.1, **call_kwargs)
    except Exception as exc:  # noqa: BLE001 - one provider must not kill a round
        error = _safe_text(str(exc).strip() or exc.__class__.__name__)
        failure_class = _provider_failure_class(exc)
        row = append_ledger({
            "area": area,
            "batch_id": batch_id,
            "provider": provider,
            "status": "provider_error",
            "items": 0,
            "errors": [error[:200]],
            "failure_class": failure_class,
        }, path=batch_path)
        return {
            "ok": False,
            "status": row["status"],
            "raw_path": "",
            "errors": row["errors"],
            "failure_class": failure_class,
        }
    out_dir = out_dir or os.path.join(HOME, "plataforma/tandas")
    os.makedirs(out_dir, exist_ok=True)
    raw_path = os.path.join(out_dir, "%s-%s-%s.raw.txt" % (area, batch_id, provider))
    raw = _safe_text(raw)
    with open(raw_path, "w", encoding="utf-8") as fh:
        fh.write(raw)
    try:
        payload = _safe_tree(_parse_provider_json(raw))
    except ValueError:
        append_ledger({
            "area": area,
            "batch_id": batch_id,
            "provider": provider,
            "status": "invalid",
            "items": 0,
            "errors": ["provider_output_not_json"],
        }, path=batch_path)
        return {"ok": False, "status": "invalid", "raw_path": raw_path,
                "errors": ["provider_output_not_json"]}
    payload = _apply_human_portfolio_classification(payload, common_path)
    payload["work"] = dict(brief["work"], status="awaiting_review", provider=provider)
    if len(payload.get("items", [])) > budget:
        error = "items_over_budget:%d>%d" % (len(payload["items"]), budget)
        append_ledger({
            "area": area,
            "batch_id": batch_id,
            "provider": provider,
            "status": "revise",
            "items": 0,
            "errors": [error],
        }, path=batch_path)
        return {"ok": False, "status": "revise", "raw_path": raw_path,
                "errors": [error]}
    repair_raw_path = ""
    product_ok, product_errors = validate_product_contract(payload, area)
    if not product_ok:
        try:
            repaired, repair_raw = _repair_product_payload(
                area, payload, provider, model, max_tokens)
            repaired = _safe_tree(repaired)
            repair_raw_path = os.path.join(
                out_dir, "%s-%s-%s.repair.raw.txt" % (area, batch_id, provider))
            with open(repair_raw_path, "w", encoding="utf-8") as fh:
                fh.write(_safe_text(repair_raw))
            repaired_ok, repaired_errors = validate_product_contract(repaired, area)
        except Exception as exc:  # noqa: BLE001 - bounded repair must degrade safely
            repaired = None
            repaired_ok = False
            repaired_errors = ["product_repair_error:%s" % str(exc)[:160]]
        if repaired_ok:
            repaired["work"] = payload.get("work", {})
            payload = repaired
        else:
            conservative = _conservative_portfolio_repair(payload, area)
            if conservative is None:
                conservative = _conservative_opportunity_repair(payload, area)
            if conservative is not None:
                conservative_ok, _conservative_errors = validate_product_contract(
                    conservative, area)
                if conservative_ok:
                    conservative["work"] = payload.get("work", {})
                    payload = conservative
                    repaired_ok = True
            if not repaired_ok:
                errors = product_errors + repaired_errors
                append_ledger({
                    "area": area,
                    "batch_id": batch_id,
                    "provider": provider,
                    "status": "revise",
                    "items": 0,
                    "errors": errors,
                }, path=batch_path)
                return {"ok": False, "status": "revise", "raw_path": raw_path,
                        "repair_raw_path": repair_raw_path, "errors": errors}
    result = ingest_result(
        payload, area, common_path=common_path, source=provider,
        use_ollama=use_ollama, strict_product=True,
        extra_paths=(list(paths or []) + list(image_paths or [])
                     if paths or image_paths else None))
    append_ledger({
        "area": area,
        "batch_id": batch_id,
        "provider": provider,
        "status": result.get("status", ""),
        "items": result.get("items", 0),
        "errors": result.get("errors", []),
    }, path=batch_path)
    result["raw_path"] = raw_path
    if repair_raw_path:
        result["repair_raw_path"] = repair_raw_path
    return result


def run_external_batch(area, batch_id, provider, paths=None, model=None,
                       out_dir=None, common_path=COMMON_LEDGER,
                       batch_path=LEDGER, use_ollama=True, max_tokens=2500,
                       instruction="", max_items=5, image_paths=None):
    """Run one bounded batch through the shared queue when active."""
    if active_enabled() and dispatch_sync is not None:
        payload = {
            "area": area, "batch_id": batch_id, "provider": provider,
            "paths": list(paths or []), "model": model or "",
            "max_tokens": int(max_tokens), "max_items": int(max_items),
            "use_ollama": bool(use_ollama),
        }

        def handle(_job):
            result = _run_external_batch_unlocked(
                area, batch_id, provider, paths=paths, model=model,
                out_dir=out_dir, common_path=common_path, batch_path=batch_path,
                use_ollama=use_ollama, max_tokens=max_tokens,
                instruction=instruction, max_items=max_items,
                image_paths=image_paths,
            )
            artifacts = []
            for key, kind in (("raw_path", "provider_raw_output"),
                              ("repair_raw_path", "provider_repair_output")):
                path = result.get(key) if isinstance(result, dict) else None
                if path:
                    artifacts.append({"kind": kind, "path": path})
            if not isinstance(result, dict):
                return {"validated": False, "error": "batch returned non-mapping"}
            status = str(result.get("status") or "")
            if status == "provider_error":
                return {"validated": False, "retriable": True,
                        "error": ";".join(result.get("errors") or
                                           ["provider_error"]),
                        "result": result, "artifacts": artifacts}
            return {"validated": status in {
                "accepted", "awaiting_review", "revise", "invalid",
            }, "result": result, "artifacts": artifacts}

        queued = dispatch_sync(
            "external_batch", payload,
            producer="platform.tandas.run_external_batch", handler=handle,
            template_version="external-batch-v1",
        )
        if queued and isinstance(queued.get("result"), dict):
            result = dict(queued["result"])
            result["queue_status"] = queued.get("queue_status")
            return result
        return queued or {"ok": False, "status": "queue_unavailable",
                          "errors": ["queue_unavailable"]}
    return _run_external_batch_unlocked(
        area, batch_id, provider, paths=paths, model=model,
        out_dir=out_dir, common_path=common_path, batch_path=batch_path,
        use_ollama=use_ollama, max_tokens=max_tokens, instruction=instruction,
        max_items=max_items, image_paths=image_paths,
    )


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
    by_failure = {}
    for row in rows:
        by_area[row.get("area", "")] = by_area.get(row.get("area", ""), 0) + 1
        by_provider[row.get("provider", "")] = (
            by_provider.get(row.get("provider", ""), 0) + 1)
        by_status[row.get("status", "")] = (
            by_status.get(row.get("status", ""), 0) + 1)
        failure = row.get("failure_class", "")
        if failure:
            by_failure[failure] = by_failure.get(failure, 0) + 1
    return {
        "total": len(rows),
        "by_area": by_area,
        "by_provider": by_provider,
        "by_status": by_status,
        "by_failure": by_failure,
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
                         help="CSV: groq,gemini,cerebras,ollama")
    p_brief.add_argument("--no-premium", action="store_true",
                         help="exclude temporary premium providers")
    p_brief.add_argument("--path", action="append", dest="paths",
                         help="override/add path; repeatable")
    p_brief.add_argument("--with-evidence", action="store_true",
                         help="include bounded local evidence snippets")
    p_brief.add_argument("--max-evidence-chars", type=int, default=60000)
    p_brief.add_argument("--instruction", default="",
                         help="extra round-specific instruction")

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
    p_run = sub.add_parser("run",
                           help="call one external provider and ingest through local review")
    p_run.add_argument("area", choices=sorted(AREAS))
    p_run.add_argument("batch_id")
    p_run.add_argument("--provider", choices=["cerebras", "groq", "ollama"], required=True)
    p_run.add_argument("--model", default="")
    p_run.add_argument("--path", action="append", dest="paths")
    p_run.add_argument("--out-dir", default="")
    p_run.add_argument("--ledger", default=LEDGER,
                       help="external batch run ledger path")
    p_run.add_argument("--common-ledger", default=COMMON_LEDGER)
    p_run.add_argument("--max-tokens", type=int, default=2500)
    p_run.add_argument("--no-ollama", action="store_true")
    p_run.add_argument("--instruction", default="",
                       help="extra round-specific instruction")
    p_run.add_argument("--image", action="append", dest="image_paths",
                       help="image evidence for vision-capable providers")

    args = parser.parse_args(argv)
    if args.cmd == "areas":
        _print_json({"schema": SCHEMA_VERSION, "areas": sorted(AREAS)}, indent=2)
        return 0
    if args.cmd == "brief":
        providers = [p.strip() for p in args.providers.split(",") if p.strip()]
        brief = build_brief(args.area, args.batch_id, paths=args.paths,
                            providers=providers,
                            allow_premium=not args.no_premium,
                            include_evidence=args.with_evidence,
                            max_evidence_chars=args.max_evidence_chars,
                            instruction=args.instruction)
        _print_json(brief, indent=2)
        return 0
    if args.cmd == "summary":
        _print_json(summarize_ledger(args.ledger, args.limit), indent=2)
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
        _print_json({"ok": ok, "errors": errors})
        return 0 if ok else 2
    if args.cmd == "review-prompt":
        if discernment is None:
            _print_json({"ok": False, "errors": ["discernment_unavailable"]})
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
            source=args.provider, use_ollama=not args.no_ollama,
            strict_product=True)
        _print_json(result)
        return 0 if result["ok"] else 2
    if args.cmd == "run":
        try:
            result = run_external_batch(
                args.area, args.batch_id, args.provider, paths=args.paths,
                model=args.model or None, out_dir=args.out_dir or None,
                common_path=args.common_ledger, batch_path=args.ledger,
                use_ollama=not args.no_ollama, max_tokens=args.max_tokens,
                instruction=args.instruction, image_paths=args.image_paths)
        except Exception as exc:  # noqa: BLE001 - operator-facing CLI
            result = {"ok": False, "status": "provider_error",
                      "errors": [str(exc)[:200]]}
        _print_json(result)
        return 0 if result["ok"] else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
