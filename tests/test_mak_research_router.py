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


def test_route_exposes_reasoning_mode_without_changing_output_contract():
    assert R.route_research_task("multiplicar", "curatoria de una obra").epistemic_mode == "interpretacion"
    assert R.route_research_task("multiplicar", "repasar un informe").epistemic_mode == "critica"
    assert R.route_research_task("atender", "quien organizo el evento").epistemic_mode == "evidencia"


def test_route_exposes_declarative_department_profile():
    route = R.route_research_task("multiplicar", "quien organizo el evento")
    profile = R.profile_for_route(route)
    assert profile["destination"] == "rd"
    assert profile["evidence"] == "primary_source"
    assert "informe" in profile["formats"]


def test_profile_accepts_rd_primary_source_report():
    profile = R.profile_for_area("rd_evidence")
    result = {"items": [{
        "format": "informe",
        "evidence_kind": "primary_source",
        "evidence": ["https://www.gob.cl/fuente"],
        "files": ["src/flujo/rd/database.py"],
        "action": "verify_source",
    }]}
    assert R.validate_profile_result(profile, result) == "accept"


def test_profile_rejects_iskvw_report_format():
    profile = R.profile_for_area("iskvw_curation")
    result = {"items": [{
        "format": "informe",
        "evidence_kind": "artwork_context",
        "evidence": ["obra propia"],
        "files": ["tools/gen_archivo_iskvw.py"],
        "action": "curate",
    }]}
    assert R.validate_profile_result(profile, result) == "reject"


def test_profile_revises_mak_review_without_local_evidence():
    profile = R.profile_for_area("mak_quality")
    result = {"items": [{
        "format": "revision",
        "evidence_kind": "local_corpus",
        "evidence": [],
        "files": [],
        "action": "review",
    }]}
    assert R.validate_profile_result(profile, result) == "revise"


def test_profile_revises_missing_format_instead_of_promoting_implicitly():
    profile = R.profile_for_area("rd_evidence")
    result = {"items": [{
        "evidence_kind": "primary_source",
        "evidence": ["https://www.gob.cl/fuente"],
        "files": ["src/flujo/rd/database.py"],
        "action": "verify_source",
    }]}
    assert R.validate_profile_result(profile, result) == "revise"


def test_research_profile_accepts_essay_without_public_promotion():
    route = R.route_research_task(
        "multiplicar", "genealogia cultural de la tilde")
    profile = R.profile_for_route(route)
    result = {"items": [{
        "format": "ensayo",
        "evidence_kind": "mixed_sources",
        "evidence": ["context/LAST_HANDOFF.md"],
        "files": ["docs/cultura/FORMATO_ENSAYO.md"],
        "action": "draft_report",
    }]}
    assert R.validate_profile_result(profile, result) == "accept"


def test_fondart_routes_to_opportunity_card_not_generic_report():
    route = R.route_research_task(
        "multiplicar", "Fondart convocatoria para artista visual")
    assert route.domain == "opportunities"
    assert route.intent == "opportunity"
    assert route.formato == "oportunidad"
    assert route.required_fields == (
        "opportunity", "eligibility", "deadline", "source", "next_action")


def test_breathing_cycle_keeps_five_ways_of_knowing_separate():
    cases = [
        ("atender", "quien organizo el evento", "evidencia", "informe"),
        ("multiplicar", "curatoria de una obra ambigua", "interpretacion", "curatoria"),
        ("multiplicar", "repasar una obra y sus debilidades", "critica", "revision"),
        ("multiplicar", "presentar una obra como post de Instagram", "interpretacion", "exposicion"),
        ("multiplicar", "genealogia cultural de una practica", "argumento", "ensayo"),
    ]
    for verbo, tema, modo, formato in cases:
        route = R.route_research_task(verbo, tema)
        assert route.epistemic_mode == modo
        assert route.formato == formato


def test_breathing_cycle_promotes_only_the_right_evidence_contract():
    cases = [
        ("rd_evidence", "informe", "primary_source", "verify_source", "accept"),
        ("iskvw_curation", "informe", "artwork_context", "curate", "reject"),
        ("mak_quality", "revision", "local_corpus", "review", "revise"),
        ("research", "ensayo", "mixed_sources", "draft_report", "accept"),
    ]
    for area, formato, evidence_kind, action, verdict in cases:
        profile = R.profile_for_area(area) or R.DEPARTMENT_PROFILES["research"]
        result = {"items": [{
            "format": formato,
            "evidence_kind": evidence_kind,
            "evidence": (["local-or-primary-evidence"]
                          if verdict == "accept" else []),
            "files": (["local/file.md"]
                      if verdict == "accept" else []),
            "action": action,
        }]}
        assert R.validate_profile_result(profile, result) == verdict
