#!/usr/bin/env python3
"""Local discernment gate for MAK external batches.

Premium models can produce volume; the local model should act as a cheap immune
system. The contract is testable without Ollama, but the module can call an
Ollama-compatible endpoint when MAK has one available.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request


SCHEMA_VERSION = "mak-local-review-v1"
VERDICTS = ("accept", "revise", "reject")
REQUIRED = ("schema", "verdict", "domain", "reason", "risks",
            "missing_evidence", "next_action")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

AREA_DOMAINS = {
    "mak_quality": "mak",
    "rd_evidence": "rd",
    "iskvw_curation": "iskvw",
    "tool_archaeology": "repo",
    "svg_pipeline": "svg",
    "adobe_rescue": "adobe",
}

AREA_CRITERIA = {
    "mak_quality": (
        "Does it separate old MAK output as lead/reject/refute instead of truth?",
        "Does it identify wrong format, weak evidence or queue repair?",
    ),
    "rd_evidence": (
        "Does it privilege primary/official sources over plausible summaries?",
        "Does it avoid mixing harm-reduction work with iskvw curation?",
    ),
    "iskvw_curation": (
        "Does it read artwork/archive without turning it into RD or academia?",
        "Does it preserve uncertainty about intention, biography and authorship?",
    ),
    "tool_archaeology": (
        "Does it prove a tool exists before asking to build another one?",
        "Does it name concrete files and tests instead of vibes?",
    ),
    "svg_pipeline": (
        "Does it distinguish SVG generation, animation, laser and measurement?",
        "Does it avoid rebuilding thi.ng-like utilities before locating them?",
    ),
    "adobe_rescue": (
        "Does it rescue Illustrator/Adobe bridge work before proposing rebuilds?",
        "Does it distinguish Adobe bridge from Blender bridge?",
    ),
}


def build_review_prompt(area, payload):
    if area not in AREA_DOMAINS:
        raise ValueError("unknown area: %s" % area)
    return (
        "Eres el juez LOCAL de MAK usando Ollama. Tu rol no es producir mas "
        "investigacion: debes aceptar, pedir revision o rechazar la salida de "
        "otro modelo.\n\n"
        "AREA: %s\n"
        "DOMINIO: %s\n"
        "CRITERIOS:\n%s\n\n"
        "SALIDA A JUZGAR:\n%s\n\n"
        "Devuelve SOLO JSON con esta forma exacta:\n"
        "{\n"
        '  "schema": "%s",\n'
        '  "verdict": "accept|revise|reject",\n'
        '  "domain": "%s",\n'
        '  "reason": "motivo breve",\n'
        '  "risks": ["riesgo concreto"],\n'
        '  "missing_evidence": ["dato o fuente faltante"],\n'
        '  "next_action": "accion minima verificable"\n'
        "}\n\n"
        "Reglas: si la evidencia no sostiene el claim, verdict=reject. Si "
        "sirve pero falta una fuente o archivo, verdict=revise. Si mezcla RD "
        "con iskvw, rechaza. Si pide crear una herramienta sin buscar una "
        "existente, rechaza."
        % (area, AREA_DOMAINS[area],
           "\n".join("- " + c for c in AREA_CRITERIA[area]),
           json.dumps(payload, ensure_ascii=False, indent=2)[:12000],
           SCHEMA_VERSION, AREA_DOMAINS[area])
    )


def validate_review(payload, area=None):
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except ValueError:
            return False, ["not_json"]
    if not isinstance(payload, dict):
        return False, ["not_object"]
    errors = []
    for key in REQUIRED:
        if key not in payload:
            errors.append("missing_%s" % key)
    if payload.get("schema") != SCHEMA_VERSION:
        errors.append("bad_schema")
    if payload.get("verdict") not in VERDICTS:
        errors.append("bad_verdict")
    expected_domain = AREA_DOMAINS.get(area) if area else None
    if expected_domain and payload.get("domain") != expected_domain:
        errors.append("bad_domain")
    if not isinstance(payload.get("risks"), list):
        errors.append("risks_not_list")
    if not isinstance(payload.get("missing_evidence"), list):
        errors.append("missing_evidence_not_list")
    if payload.get("verdict") in ("revise", "reject") and not payload.get("reason"):
        errors.append("verdict_without_reason")
    return not errors, errors


def extract_json(text):
    """Extract the first JSON object from a noisy local-model response."""
    if isinstance(text, dict):
        return text
    raw = str(text or "").strip()
    try:
        return json.loads(raw)
    except ValueError:
        pass
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError("not_json")
    return json.loads(match.group(0))


def deterministic_review(area, payload):
    """Small local fallback before/around Ollama.

    It cannot judge truth, but it can reject the defect classes that caused the
    current mess: empty evidence, domain mixing and tool creation without
    proof of search/reuse.
    """
    domain = AREA_DOMAINS.get(area)
    risks = []
    missing = []
    items = payload.get("items", []) if isinstance(payload, dict) else []
    if not items:
        return {
            "schema": SCHEMA_VERSION,
            "verdict": "reject",
            "domain": domain,
            "reason": "no items to evaluate",
            "risks": ["empty provider output"],
            "missing_evidence": ["at least one atomic item"],
            "next_action": "rerun batch or mark provider output invalid",
        }
    for item in items:
        evidence = item.get("evidence", []) if isinstance(item, dict) else []
        claim = str(item.get("claim", "") if isinstance(item, dict) else "")
        files = item.get("files", []) if isinstance(item, dict) else []
        action = item.get("action", "") if isinstance(item, dict) else ""
        if not evidence:
            missing.append("evidence for: %s" % claim[:80])
        folded = " ".join([claim, " ".join(map(str, evidence)),
                           " ".join(map(str, files))]).lower()
        if area == "rd_evidence" and "iskvw" in folded:
            risks.append("RD item mentions iskvw; domain mixed")
        if area == "iskvw_curation" and ("reduccion de dano" in folded or "harm reduction" in folded):
            risks.append("iskvw item mentions RD; domain mixed")
        if area == "tool_archaeology" and action not in ("reuse", "merge", "retire", "test", "reject"):
            risks.append("tool archaeology item does not choose a reuse/merge/retire/test action")
    if risks:
        verdict = "reject"
        reason = "; ".join(risks[:2])
    elif missing:
        verdict = "revise"
        reason = "missing evidence in %d item(s)" % len(missing)
    else:
        verdict = "accept"
        reason = "contract has atomic items with evidence and no mechanical domain violation"
    return {
        "schema": SCHEMA_VERSION,
        "verdict": verdict,
        "domain": domain,
        "reason": reason,
        "risks": risks,
        "missing_evidence": missing[:8],
        "next_action": "append accepted items to ledger" if verdict == "accept" else "revise provider output",
    }


def call_ollama(prompt, base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL, timeout=120):
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 700},
    }).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/api/generate",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8", "replace"))
    return data.get("response", "")


def review_payload(area, payload, reviewer=None, use_ollama=True):
    """Return (review, meta) using Ollama when possible, deterministic fallback otherwise."""
    if area not in AREA_DOMAINS:
        raise ValueError("unknown area: %s" % area)
    baseline = deterministic_review(area, payload)
    if not use_ollama:
        return baseline, {"reviewer": "deterministic", "fallback": False}
    prompt = build_review_prompt(area, payload)
    call = reviewer or call_ollama
    try:
        review = extract_json(call(prompt))
        ok, errors = validate_review(review, area=area)
        if ok:
            return review, {"reviewer": "ollama", "fallback": False}
        baseline["risks"] = baseline["risks"] + ["ollama review invalid: %s" % ",".join(errors)]
        return baseline, {"reviewer": "deterministic", "fallback": True,
                          "errors": errors}
    except Exception as exc:  # noqa: BLE001 - local judge must not block ledger forever
        baseline["risks"] = baseline["risks"] + ["ollama unavailable: %s" % str(exc)[:120]]
        return baseline, {"reviewer": "deterministic", "fallback": True,
                          "errors": [str(exc)[:120]]}
