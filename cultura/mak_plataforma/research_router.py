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


DEFAULT_BY_VERB = {
    "atender": ResearchRoute("research", "answer", "informe", "corto",
                             "material queue answers concrete requests"),
    "multiplicar": ResearchRoute("research", "essay", "ensayo", "medio",
                                  "generative backlog develops cultural topics"),
    "definir": ResearchRoute("research", "essay", "ensayo", "medio",
                              "definition backlog develops cultural topics"),
}


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
