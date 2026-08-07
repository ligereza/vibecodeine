#!/usr/bin/env python3
"""Deterministic routing for MAK research work.

The cron verb is not enough to choose the product. A factual RD question, an
iskvw curation note and a cultural essay can all arrive through the same
rotation slot; the request intent decides the output contract.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class ResearchRoute:
    domain: str
    intent: str
    formato: str
    densidad: str
    reason: str

    @property
    def required_fields(self) -> tuple[str, ...]:
        return OUTPUT_CONTRACTS[self.formato]


OUTPUT_CONTRACTS = {
    "informe": ("claim", "sources", "uncertainty", "next_action"),
    "curatoria": ("reading", "selection", "relationships", "public_status"),
    "revision": ("verdict", "defects", "decision", "next_action"),
    "exposicion": ("thesis", "audience", "copy", "visual_proposal"),
    "ensayo": ("thesis", "counterreading", "chronology", "argument"),
    "ledger": ("verdict", "evidence", "next_action"),
    "oportunidad": ("opportunity", "eligibility", "deadline", "source",
                     "next_action"),
}


DEFAULT_BY_VERB = {
    "atender": ResearchRoute("research", "answer", "informe", "corto",
                             "material queue answers concrete requests"),
    "multiplicar": ResearchRoute("research", "essay", "ensayo", "medio",
                                  "generative backlog develops cultural topics"),
    "definir": ResearchRoute("research", "essay", "ensayo", "medio",
                              "definition backlog develops cultural topics"),
}


DEPARTMENT_PROFILES = {
    "rd": {
        "destination": "rd",
        "evidence": "primary_source",
        "judge": "source_gate",
        "formats": ("informe",),
        "allowed_formats": ("informe",),
        "required_evidence": "primary_source",
        "promotion_actions": ("verify_source", "triangulate", "draft_report"),
    },
    "iskvw": {
        "destination": "iskvw",
        "evidence": "artwork_context",
        "judge": "curation_gate",
        "formats": ("curatoria",),
        "allowed_formats": ("curatoria",),
        "required_evidence": "artwork_context",
        "promotion_actions": ("curate", "expose", "archive"),
    },
    "mak": {
        "destination": "mak",
        "evidence": "local_corpus",
        "judge": "quality_gate",
        "formats": ("revision", "exposicion"),
        "allowed_formats": ("revision", "exposicion"),
        "required_evidence": "local_corpus",
        "promotion_actions": ("archive", "refute", "expose", "repair_queue",
                               "review", "decide"),
    },
    "research": {
        "destination": "research",
        "evidence": "mixed_sources",
        "judge": "format_gate",
        "formats": ("ensayo", "informe"),
        "allowed_formats": ("ensayo", "informe"),
        "required_evidence": "mixed_sources",
        "promotion_actions": ("draft_report",),
    },
    "opportunities": {
        "destination": "mak",
        "evidence": "official_source",
        "judge": "source_gate",
        "formats": ("oportunidad",),
        "allowed_formats": ("oportunidad",),
        "required_evidence": "official_source",
        "promotion_actions": ("verify_source", "triangulate", "draft_report"),
    },
}


AREA_PROFILES = {
    "rd_evidence": "rd",
    "iskvw_curation": "iskvw",
    "mak_quality": "mak",
    "opportunity_radar": "opportunities",
}


def profile_for_route(route: ResearchRoute) -> dict:
    """Return a copy of the declarative profile for a route."""
    profile = DEPARTMENT_PROFILES.get(route.domain,
                                      DEPARTMENT_PROFILES["research"])
    return dict(profile)


def profile_for_area(area: str) -> dict | None:
    """Return the promotion profile for a batch area when one is defined."""
    name = AREA_PROFILES.get(str(area or ""))
    return dict(DEPARTMENT_PROFILES[name]) if name else None


def validate_profile_result(profile: dict | None, result: dict) -> str:
    """Return only the promotion verdict for a profile/result pair."""
    if profile is None:
        return "accept"
    if not isinstance(result, dict):
        return "reject"
    items = result.get("items")
    if not isinstance(items, list) or not items:
        return "reject"
    allowed_formats = tuple(profile.get("allowed_formats", ()))
    required_evidence = profile.get("required_evidence")
    allowed_actions = tuple(profile.get("promotion_actions", ()))
    needs_revision = False
    for item in items:
        if not isinstance(item, dict):
            return "reject"
        declared_format = item.get("format")
        if declared_format not in allowed_formats:
            if declared_format:
                return "reject"
            needs_revision = True
        if item.get("action") not in allowed_actions:
            return "reject"
        evidence = item.get("evidence") or []
        files = item.get("files") or []
        if not evidence and not files:
            needs_revision = True
        evidence_kind = item.get("evidence_kind")
        if evidence_kind and evidence_kind != required_evidence:
            return "reject"
        if evidence_kind != required_evidence:
            needs_revision = True
    return "revise" if needs_revision else "accept"


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFD", str(text or "").lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


RD_TERMS = (
    "reduccion de dano", "reduccion de danos", "rd ", " chile ", "santiago",
    "productora", "evento", "cartel", "headliner", "ticket", "entrada",
    "fuente verificable", "no se encontro", "sustancia", "reactivo",
    "drogas", "droga", "fiscalizacion", "ley", "ministerio", "bcn",
)

CURATION_TERMS = (
    "iskvw", "curatoria", "curaduria", "archivo publico", "archivo de obra",
    "obra propia", "mis obras", "mi obra", "pieza", "montaje", "portfolio",
    "portafolio", "familia visual", "serie visual", "exhibicion",
)

REVIEW_TERMS = (
    "revisar", "revision", "repasar", "auditar", "calidad", "formato",
    "basura", "archivar", "cuarentena", "deuda", "cabos sueltos",
    "trabajo viejo", "informe viejo",
)

EXPOSITION_TERMS = (
    "exponer", "explicar", "post", "instagram", " ig ", "bajada", "caption",
    "texto publico", "lectura humana", "ficha", "presentar",
)

ESSAY_TERMS = (
    "ensayo", "tesis", "genealogia", "historia cultural", "estetica",
    "poetica", "paradigma", "mito", "retorica", "subcultura",
)

OPPORTUNITY_TERMS = (
    "fondart", "fondos de cultura", "fondos concursables", "fondos del estado",
    "postulacion", "postulaciones", "convocatoria", "convocatorias", "beca",
    "becas", "residencia artistica", "residencias", "premio artistico",
    "open call", "oportunidad", "financiamiento", "grant", "cliente",
    "buscar trabajo", "oferta de trabajo", "nicho", "colaboracion",
)


def route_research_task(verbo: str, tema: str, factual_detector=None) -> ResearchRoute:
    """Return the stable research product route for a work item.

    `factual_detector` is injected by `trabajo.py` from `research_lib` when
    available. This module stays standalone so low-tier agents can test the
    contract without booting the whole research organ.
    """
    folded = " %s " % _fold(tema)
    is_factual = False
    if factual_detector is not None:
        try:
            is_factual = bool(factual_detector(tema))
        except Exception:  # noqa: BLE001 - routing must degrade to local rules
            is_factual = False

    if _has_any(folded, OPPORTUNITY_TERMS):
        return ResearchRoute("opportunities", "opportunity", "oportunidad", "corto",
                             "opportunities need eligibility, deadline and official source")
    if is_factual or _has_any(folded, RD_TERMS):
        return ResearchRoute("rd", "factual_evidence", "informe", "corto",
                             "factual/RD work needs sources before prose")
    if _has_any(folded, REVIEW_TERMS):
        return ResearchRoute("mak", "review", "revision", "corto",
                             "quality work must produce verdicts, not essays")
    if _has_any(folded, CURATION_TERMS):
        return ResearchRoute("iskvw", "curation", "curatoria", "medio",
                             "art archive work needs curation, not reports")
    if _has_any(folded, EXPOSITION_TERMS):
        return ResearchRoute("mak", "exposition", "exposicion", "corto",
                             "human-facing work needs usable exposition")
    if _has_any(folded, ESSAY_TERMS):
        return ResearchRoute("research", "essay", "ensayo", "medio",
                             "cultural interpretation can sustain an essay")
    return DEFAULT_BY_VERB.get(
        verbo,
        ResearchRoute("research", "answer", "informe", "corto",
                      "unknown verbs fall back to conservative report"),
    )
