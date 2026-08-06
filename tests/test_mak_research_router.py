import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAK_PLATAFORMA = REPO_ROOT / "cultura" / "mak_plataforma"

sys.path.insert(0, str(MAK_PLATAFORMA))

import research_router as R  # noqa: E402


def test_rd_event_question_routes_to_short_report_even_from_cultural_verb():
    route = R.route_research_task(
        "multiplicar",
        "En CHILE, que productora organizo el evento del 2023-10-28?",
    )
    assert route.domain == "rd"
    assert route.intent == "factual_evidence"
    assert route.formato == "informe"
    assert route.densidad == "corto"


def test_injected_factual_detector_wins_over_verb():
    route = R.route_research_task(
        "definir",
        "Quien firma la autorizacion municipal de este evento?",
        factual_detector=lambda _topic: True,
    )
    assert route.formato == "informe"
    assert route.densidad == "corto"


def test_iskvw_curation_does_not_become_report_or_essay():
    route = R.route_research_task(
        "multiplicar",
        "curatoria de mis obras para el archivo publico iskvw y posible montaje",
    )
    assert route.domain == "iskvw"
    assert route.intent == "curation"
    assert route.formato == "curatoria"
    assert route.densidad == "medio"


def test_quality_review_routes_to_revision():
    route = R.route_research_task(
        "multiplicar",
        "repasar los informes viejos de MAK y decidir que va a cuarentena",
    )
    assert route.domain == "mak"
    assert route.intent == "review"
    assert route.formato == "revision"
    assert route.densidad == "corto"


def test_public_post_routes_to_exposition():
    route = R.route_research_task(
        "multiplicar",
        "explicar este hallazgo como post de Instagram con una bajada clara",
    )
    assert route.intent == "exposition"
    assert route.formato == "exposicion"
    assert route.densidad == "corto"


def test_cultural_topic_keeps_essay_contract():
    route = R.route_research_task(
        "multiplicar",
        "genealogia cultural de la tilde y su poetica en el arte digital",
    )
    assert route.intent == "essay"
    assert route.formato == "ensayo"
    assert route.densidad == "medio"


def test_unknown_topic_uses_verb_default():
    route = R.route_research_task("atender", "un pedido sin marcas claras")
    assert route.formato == "informe"
    assert route.densidad == "corto"


def test_route_exposes_contract_for_selected_product():
    route = R.route_research_task(
        "multiplicar", "curatoria de mis obras para el archivo publico iskvw")
    assert route.required_fields == (
        "reading", "selection", "relationships", "public_status")
