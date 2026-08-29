"""Tests for the portfolio production chain.

These tests are deliberately the inverse of the earlier operator-frontier suite.
That suite asserted that the system refuses; abstention there was free, so the
system learned to abstain.  Here the assertions are:

- a declared plant that the evidence can fill **must render a document**;
- a document must carry state, refutation and permission on every line;
- and the epistemic guards must hold *while producing*, not instead of it.

An abstention that is not forced by the evidence is a failure here.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from flujo.knowledge.portfolio_claims import (
    PortfolioClaimsError,
    compile_portfolio_claims,
    validate_portfolio_claims,
)
from flujo.knowledge.portfolio_format import (
    CLAIMS,
    CLAIM_STATE_CEILING,
    PortfolioFormatError,
    STATE_RANK,
    load_format_library,
    validate_portfolio_format,
)
from flujo.knowledge.portfolio_render import (
    PortfolioRenderError,
    assess_feasibility,
    render_markdown,
    render_portfolio,
    validate_portfolio_render,
)
from flujo.knowledge.product_view import stable_json
from flujo.knowledge.screen_setup_evidence import (
    derived_variant_groups,
    read_screen_setup,
    scan_screen_setups,
)


ROOT = Path(__file__).resolve().parents[1]
FORMATS = ROOT / "data" / "portfolio_formats"
INDEX = Path("/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite")
SSD = Path("/media/mak/PortableSSD")
DECLARED_INPUTS = Path("/home/mak/.claude/jobs/3428381a/tmp/declared_inputs.json")
BLEND_TARGETS = Path("/home/mak/.claude/jobs/3428381a/tmp/blend_dependency_targets.json")

real_sources = pytest.mark.skipif(
    not INDEX.exists(), reason="the real SSD index is not mounted")


# --- the format contract ----------------------------------------------------


def test_format_library_loads_and_every_slot_is_bounded() -> None:
    library = load_format_library(FORMATS)

    assert library["format_count"] >= 4
    for spec in library["formats"]:
        assert spec["format_hash"].startswith("sha256:")
        assert spec["consumer"]["does_not_support"], spec["format_id"]
        assert any(slot["required"] for slot in spec["slots"])
        for slot in spec["slots"]:
            assert slot["count"]["min"] <= slot["count"]["max"]
            assert slot["claim"] in CLAIMS
            assert slot["caption_fields_used"], slot["slot_id"]
            # Every caption field must be declared: a grammar that can reach an
            # undeclared field could frame the work silently.
            assert set(slot["caption_fields_used"]) <= set(slot["allowed_caption_fields"])


def test_format_cannot_demand_authorship_the_archive_cannot_prove() -> None:
    spec = json.loads((FORMATS / "F3-rol-tecnico.json").read_text(encoding="utf-8"))
    for slot in spec["slots"]:
        if slot["claim"] == "hice_esta_parte":
            slot["min_state"] = "certified"
            break
    with pytest.raises(PortfolioFormatError, match="above_claim_ceiling"):
        validate_portfolio_format(spec)
    assert CLAIM_STATE_CEILING == {"es_mio": "candidate", "hice_esta_parte": "candidate"}


def test_format_rejects_a_caption_that_escapes_its_declared_fields() -> None:
    spec = json.loads((FORMATS / "F1-trayectoria.json").read_text(encoding="utf-8"))
    spec["slots"][0]["caption_grammar"] = "{context_label} — {precio_de_venta}"
    with pytest.raises(PortfolioFormatError, match="uses_undeclared_field"):
        validate_portfolio_format(spec)


def test_a_foreign_vertical_loads_without_touching_code() -> None:
    """The barber format is the generalization test."""
    library = load_format_library(FORMATS)
    verticals = {spec["vertical_grammar"] for spec in library["formats"]}
    barber = next(
        spec for spec in library["formats"]
        if spec["format_id"] == "F2-capacidad-barberia")

    assert "transformacion" in verticals and "experiencia" in verticals
    assert barber["vertical_grammar"] == "transformacion"
    # Same five slot fields, entirely different evidence vocabulary.
    kinds = {kind for slot in barber["slots"] for kind in slot["evidence_kinds"]}
    assert "before_after_pair" in kinds
    assert not kinds & {"native_project_file", "live_screen_setup"}


# --- screen setup evidence --------------------------------------------------


@pytest.mark.skipif(not SSD.exists(), reason="the SSD is not mounted")
def test_screen_setups_are_identified_by_content_not_by_filename() -> None:
    scan = scan_screen_setups(SSD)

    assert scan["setup_count"] >= 1
    assert scan["tools"] == ["Resolume Arena"]
    for setup in scan["setups"]:
        # Identified by the document's own declared tool, never by extension.
        assert setup["tool"] == "Resolume Arena"
        assert setup["slice_count"] >= 0
        assert setup["canvas"]
        assert setup["label_reliability"] in {
            "matches_filename", "stale_label_from_save_as", "no_declared_name"}
        assert any("save-as" in limit for limit in setup["limits"])


@pytest.mark.skipif(not SSD.exists(), reason="the SSD is not mounted")
def test_a_stale_label_is_not_read_as_a_relation() -> None:
    """A save-as carries the old name; that is unreliability, not evidence."""
    scan = scan_screen_setups(SSD)
    stale = [
        row for row in scan["setups"]
        if row["label_reliability"] == "stale_label_from_save_as"]

    assert stale, "the real archive contains at least one save-as"
    for row in stale:
        assert row["declared_name"] != row["file_stem"]
        assert row["dating_reliability"] == "single_route_may_predate_this_file"
    for group in derived_variant_groups(scan):
        assert group["status"] == "candidate"
        assert "save-as" in group["most_likely_reading"]
        assert any("artifact of re-saving" in item for item in group["evidence_against"])
        assert "any commission, work or authorship relation" in group["does_not_establish"]


def test_a_non_setup_xml_returns_none_rather_than_raising(tmp_path: Path) -> None:
    other = tmp_path / "something.xml"
    other.write_text("<?xml version='1.0'?><Catalog><Item/></Catalog>", encoding="utf-8")
    broken = tmp_path / "broken.xml"
    broken.write_text("<not xml", encoding="utf-8")

    assert read_screen_setup(other) is None
    assert read_screen_setup(broken) is None
    assert read_screen_setup(tmp_path / "absent.xml") is None


# --- the claim base ---------------------------------------------------------


@pytest.fixture(scope="module")
def claims() -> dict:
    if not INDEX.exists():
        pytest.skip("the real SSD index is not mounted")
    return compile_portfolio_claims(
        index_path=INDEX,
        authority_path=ROOT / "data" / "artist_discographies.json",
        archive_path=ROOT / "iskvw" / "datos" / "archivo.json",
        declared_inputs_path=DECLARED_INPUTS if DECLARED_INPUTS.exists() else None,
        blend_targets_path=BLEND_TARGETS if BLEND_TARGETS.exists() else None,
        practices_path=ROOT / "data" / "portfolio_practices.json",
        attestations_path=ROOT / "data" / "portfolio_attestations.json",
        screen_setup_root=SSD if SSD.exists() else None,
    )


@real_sources
def test_claim_base_is_valid_deterministic_and_writes_nothing(claims: dict) -> None:
    replay = compile_portfolio_claims(
        index_path=INDEX,
        authority_path=ROOT / "data" / "artist_discographies.json",
        archive_path=ROOT / "iskvw" / "datos" / "archivo.json",
        declared_inputs_path=DECLARED_INPUTS if DECLARED_INPUTS.exists() else None,
        blend_targets_path=BLEND_TARGETS if BLEND_TARGETS.exists() else None,
        practices_path=ROOT / "data" / "portfolio_practices.json",
        attestations_path=ROOT / "data" / "portfolio_attestations.json",
        screen_setup_root=SSD if SSD.exists() else None,
    )

    assert validate_portfolio_claims(claims) is True
    assert stable_json(replay) == stable_json(claims)
    assert claims["control"]["database_write"] is False
    assert claims["control"]["training_permitted"] is False
    assert claims["control"]["promotion"] == "none"
    assert claims["claim_count"] > 0, "a claim base that says nothing is a failure"


@real_sources
def test_only_a_practice_carries_claims(claims: dict) -> None:
    claimable = {"production", "delivery"}
    scoped = {
        row["scope"].split(":", 1)[-1]
        for row in claims["claims"] if row["scope"].startswith("container:")
    }
    non_practice = {
        row["container"] for row in claims["practices"]
        if row["kind"] not in claimable
    }

    # A tool install, a frame dump, a camera card and filesystem bookkeeping are
    # evidence about the archive, never about the person.
    assert not scoped & non_practice
    kinds = claims["practice_kind_counts"]
    assert kinds.get("installed_tool", 0) >= 1
    assert kinds.get("system_metadata", 0) >= 1
    assert kinds.get("loose_root_file", 0) >= 1


@real_sources
def test_no_route_promotes_its_own_claim(claims: dict) -> None:
    for row in claims["claims"]:
        assert row["generated_by"] not in row["supported_by"], row["claim_id"]
        if STATE_RANK[row["state"]] >= STATE_RANK["supported_candidate"]:
            assert row["supported_by"], row["claim_id"]
    assert claims["invariants"]["no_route_promotes_its_own_claim"]["enforced"] is True


@real_sources
def test_authorship_ceiling_holds_unless_a_named_authority_attests(claims: dict) -> None:
    for row in claims["claims"]:
        ceiling = CLAIM_STATE_CEILING.get(row["verb"])
        if ceiling is None:
            continue
        if STATE_RANK[row["state"]] > STATE_RANK[ceiling]:
            assert "third_party_receipt" in row["evidence_kinds"], row["claim_id"]
            assert any(
                route.startswith("attestation:") for route in
                [row["generated_by"], *row["supported_by"]]), row["claim_id"]


@real_sources
def test_an_attestation_lifts_a_claim_and_is_traceable(claims: dict) -> None:
    attested = [
        row for row in claims["claims"] if row["state"] == "externally_attested"]

    assert attested, "a named attestation exists and must reach the claim base"
    for row in attested:
        routes = [row["generated_by"], *row["supported_by"]]
        assert any(route.startswith("attestation:") for route in routes)
        assert "third_party_receipt" in row["evidence_kinds"]
        assert "attestation" in row["refuted_by"] or "withdrawn" in row["refuted_by"]


@real_sources
def test_every_claim_states_what_would_refute_it(claims: dict) -> None:
    for row in claims["claims"]:
        assert row["refuted_by"].strip(), row["claim_id"]
        assert row["evidence_refs"] or row["evidence_kinds"], row["claim_id"]
        assert row["scope"], row["claim_id"]


def test_a_prefilled_attestation_state_is_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "att.json"
    bad.write_text(json.dumps({
        "schema": "mak-portfolio-attestation-v1",
        "attestations": [{
            "attestation_id": "att:x", "attested_by": "operator",
            "establishes": {"verb": "es_mio", "layer": "role",
                            "state_granted": "irrefutable", "subjects": ["x"]},
        }],
    }), encoding="utf-8")
    if not INDEX.exists():
        pytest.skip("the real SSD index is not mounted")
    with pytest.raises(PortfolioClaimsError, match="attestation_state_invalid"):
        compile_portfolio_claims(
            index_path=INDEX,
            authority_path=ROOT / "data" / "artist_discographies.json",
            attestations_path=bad,
        )


# --- feasibility and the document ------------------------------------------


@real_sources
def test_feasibility_is_answered_before_producing(claims: dict) -> None:
    library = load_format_library(FORMATS)
    results = {
        spec["format_id"]: assess_feasibility(spec, claims)
        for spec in library["formats"]
    }

    for format_id, result in results.items():
        assert result["schema"] == "mak-portfolio-feasibility-v1"
        for slot in result["slots"]:
            # The gap is always a count and a reason, never a question.
            assert isinstance(slot["eligible"], int)
            assert isinstance(slot["shortfall"], int)
        for row in result["blocking"]:
            assert row["shortfall"] > 0
            assert row["what_would_close_it"].strip()
            assert "?" not in row["reason"], format_id


@real_sources
def test_the_feasible_formats_actually_render(claims: dict) -> None:
    """The core inversion: if the evidence can fill the plant, produce."""
    library = load_format_library(FORMATS)
    rendered = 0
    for spec in library["formats"]:
        feasibility = assess_feasibility(spec, claims)
        payload = render_portfolio(spec, claims)
        if feasibility["feasible"]:
            assert payload["status"] == "rendered", spec["format_id"]
            assert payload["document"] is not None
            assert payload["document"]["item_count"] > 0
            assert payload["render_hash"].startswith("sha256:")
            rendered += 1
        else:
            assert payload["status"] == "infeasible"
            assert payload["document"] is None
    assert rendered >= 2, "at least two formats must produce a real document"


@real_sources
def test_a_rendered_document_carries_evidence_on_every_line(claims: dict) -> None:
    spec = next(
        row for row in load_format_library(FORMATS)["formats"]
        if row["format_id"] == "F2-capacidad-visual-musica-eventos")
    payload = render_portfolio(spec, claims)

    assert payload["status"] == "rendered"
    document = payload["document"]
    seen: set[str] = set()
    for section in document["sections"]:
        for item in section["items"]:
            assert item["caption"].strip()
            assert item["state"] in STATE_RANK
            assert item["refuted_by"].strip()
            assert item["claim_id"] not in seen, "no item may appear twice"
            seen.add(item["claim_id"])
    # The document must say what it is not for.
    assert document["consumer"]["does_not_support"]
    assert document["forbidden_inferences"]
    markdown = render_markdown(payload)
    assert "autoria_reclamada=false" in markdown
    assert "se refuta si:" in markdown


@real_sources
def test_a_document_never_claims_more_than_its_format_declares(claims: dict) -> None:
    for spec in load_format_library(FORMATS)["formats"]:
        payload = render_portfolio(spec, claims)
        if payload["status"] != "rendered":
            continue
        forbidden = set(spec["forbidden_claims"])
        for section in payload["document"]["sections"]:
            assert section["claim"] not in forbidden
            assert section["claim"] in spec["declared_claims"]
        assert payload["control"]["authorship_claimed"] is False
        assert payload["control"]["publication"] is False


@real_sources
def test_a_restricted_permission_never_renders_per_case(claims: dict) -> None:
    restricted = {
        row["container"] for row in claims["practices"]
        if row["permission"] in {"prohibited", "aggregate_only"}
    }
    assert restricted, "the archive contains a permission-restricted practice"

    for spec in load_format_library(FORMATS)["formats"]:
        payload = render_portfolio(spec, claims)
        if payload["status"] != "rendered":
            continue
        for section in payload["document"]["sections"]:
            if section["declared_min_permission"] == "aggregate_only":
                continue
            for item in section["items"]:
                assert item["permission"] not in {"prohibited", "aggregate_only"}


@real_sources
def test_render_validation_rejects_a_tampered_document(claims: dict) -> None:
    spec = next(
        row for row in load_format_library(FORMATS)["formats"]
        if row["format_id"] == "F3-rol-tecnico")
    payload = render_portfolio(spec, claims)
    assert payload["status"] == "rendered"

    stripped = copy.deepcopy(payload)
    stripped["document"]["sections"][0]["items"][0]["refuted_by"] = ""
    with pytest.raises(PortfolioRenderError, match="missing_refutation"):
        validate_portfolio_render(stripped, spec)

    uncaptioned = copy.deepcopy(payload)
    uncaptioned["document"]["sections"][0]["items"][0]["caption"] = "  "
    with pytest.raises(PortfolioRenderError, match="caption_empty"):
        validate_portfolio_render(uncaptioned, spec)

    published = copy.deepcopy(payload)
    published["control"]["publication"] = True
    with pytest.raises(PortfolioRenderError, match="control_publication"):
        validate_portfolio_render(published, spec)

    promoted = copy.deepcopy(payload)
    promoted["document"]["sections"][0]["items"][0]["supported_by"] = [
        promoted["document"]["sections"][0]["items"][0]["generated_by"]]
    with pytest.raises(PortfolioRenderError, match="self_promoted"):
        validate_portfolio_render(promoted, spec)


@real_sources
def test_removing_the_practice_partition_shrinks_what_is_claimed(claims: dict) -> None:
    """Corrections must generalize: the partition is the reversible surface."""
    without = compile_portfolio_claims(
        index_path=INDEX,
        authority_path=ROOT / "data" / "artist_discographies.json",
        screen_setup_root=SSD if SSD.exists() else None,
    )

    # No declared roles means no positive role claim at all.
    declared_roles = [
        row for row in claims["claims"]
        if row["verb"] == "hice_esta_parte" and "declared" in row["generated_by"]]
    undeclared_roles = [
        row for row in without["claims"]
        if row["verb"] == "hice_esta_parte" and "declared" in row["generated_by"]]
    assert declared_roles and not undeclared_roles
    assert validate_portfolio_claims(without) is True


# --- the demand and the decisions that already existed ----------------------


SELECTIONS = Path(
    "/home/mak/plataforma/director_runs/portfolio-editor-20260808/selections.jsonl")
CLASSIFICATIONS = Path(
    "/home/mak/plataforma/director_runs/portfolio-editor-20260808/classifications.jsonl")
OPPORTUNITY = ROOT / "experiments/pilots/ARICA-FONDART-2027/runs/enriched/opportunity.json"

human_logs = pytest.mark.skipif(
    not SELECTIONS.exists(), reason="the editor decision logs are not present")


@pytest.mark.skipif(not OPPORTUNITY.exists(), reason="the captured opportunity is absent")
def test_f4_transcribes_the_real_captured_convocatoria() -> None:
    """F4 must be a transcription of captured bases, not an invention."""
    from flujo.knowledge.portfolio_format import load_portfolio_format

    opportunity = json.loads(OPPORTUNITY.read_text(encoding="utf-8"))
    spec = load_portfolio_format(FORMATS / "F4-fondart-nacional-investigacion-2027.json")
    weights = {row["field"]: row.get("weight") for row in opportunity["criteria"]}
    hard_gates = [
        row["field"] for row in opportunity["constraints"] if row.get("kind") == "hard_gate"]

    assert opportunity["opportunity_id"] == "fondart-nacional-investigacion-2027"
    assert weights == {
        "curriculum": 0.2, "quality": 0.3, "transfer_impact": 0.4, "viability": 0.1}
    # The purpose must carry the real weights, so nobody reads the document as
    # covering the whole application.
    for figure in ("0.40", "0.30", "0.20", "0.10"):
        assert figure in spec["purpose"], figure
    # And it must decline the two criteria the archive cannot speak to.
    declined = " ".join(spec["consumer"]["does_not_support"])
    assert "Calidad" in declined and "transferencia" in declined
    assert len(hard_gates) == 8
    assert "8 compuertas duras" in declined
    # The unknown deadline in the capture must be surfaced, not silently used.
    assert any("plazo" in row for row in spec["forbidden_inferences"])
    assert opportunity["unknowns"][0]["code"] == "constraint_status_unknown"


@human_logs
def test_the_decisions_a_person_already_made_are_read_not_requested() -> None:
    from flujo.knowledge.human_decision_log import (
        attesting_declarations,
        consumer_decision_summary,
        read_human_decisions,
    )

    log = read_human_decisions(
        selections_path=SELECTIONS,
        classifications_path=CLASSIFICATIONS if CLASSIFICATIONS.exists() else None)
    summary = consumer_decision_summary(log)

    # A real outcome exists, so the episode must not claim it is pending.
    assert summary["status"] == "recorded"
    assert summary["decided_by"] == "human"
    assert summary["item_count"] > 0
    assert 0.0 <= summary["selection_rate"] <= 1.0
    assert summary["selected"] + summary["rejected"] == summary["item_count"]
    # Churn resolves to the last event without discarding the history.
    for row in log["consumer_decisions"]["by_item"].values():
        assert row["history"]
        assert row["decision"] == row["history"][-1]["decision"]
    # Declarations by a named person are carried with their draft status intact.
    declarations = log["declarations"]
    assert declarations["declared_by"] == {"human": declarations["event_count"]}
    assert set(declarations["promotion_counts"]) == {"none"}
    assert set(declarations["status_counts"]) == {"human_draft"}
    assert not declarations["unmapped_fields"], "a new declared field must be visible"
    attesting = attesting_declarations(log)
    assert attesting, "the log declares ownership for at least one item"
    for rows in attesting.values():
        for row in rows:
            assert row["declared_by"] == "human"
            assert row["kept_as_draft"] is True
            assert row["promotion"] == "none"


@human_logs
@real_sources
def test_a_prior_outcome_is_a_baseline_not_a_result_for_these_documents(
    claims: dict,
) -> None:
    from flujo.knowledge.human_decision_log import (
        consumer_decision_summary,
        read_human_decisions,
    )
    from flujo.knowledge.portfolio_render import build_portfolio_episode

    log = read_human_decisions(
        selections_path=SELECTIONS,
        classifications_path=CLASSIFICATIONS if CLASSIFICATIONS.exists() else None)
    decision = consumer_decision_summary(log)
    payloads = [
        render_portfolio(spec, claims)
        for spec in load_format_library(FORMATS)["formats"]
    ]
    episode = build_portfolio_episode(
        payloads, claims, project_id="test-project", consumer_decision=decision)

    assert episode["consumer_decision"]["status"] == "recorded"
    outcome = episode["observed_outcome"]
    assert outcome["status"] == "prior_selection_measured"
    # The decisive honesty: a rate measured on an earlier surface is a baseline,
    # and learning is not complete until these documents get their own outcome.
    assert outcome["applies_to_these_documents"] is False
    assert episode["rendered_count"] >= 3


# --- curatorial relations a person drew -------------------------------------


CONNECTIONS = Path(
    "/home/mak/plataforma/director_runs/portfolio-editor-20260808/connections.jsonl")
FEEDBACK = Path(
    "/home/mak/plataforma/director_runs/portfolio-editor-20260808/copilot_feedback.jsonl")
EXTERNAL = Path(
    "/home/mak/plataforma/director_runs/portfolio-editor-20260808/copilot_external.jsonl")

relation_logs = pytest.mark.skipif(
    not CONNECTIONS.exists(), reason="the connections log is not present")


@relation_logs
def test_person_drawn_relations_separate_source_facts_from_readings() -> None:
    from flujo.knowledge.human_decision_log import (
        RELATION_KINDS,
        curatorial_relations,
        read_human_decisions,
    )

    log = read_human_decisions(
        connections_path=CONNECTIONS,
        feedback_path=FEEDBACK if FEEDBACK.exists() else None,
        external_path=EXTERNAL if EXTERNAL.exists() else None)
    relations = log["relations"]

    assert relations["pair_count"] > 0
    assert not relations["unknown_kinds"], "a new relation kind must be visible"
    # The distinction that makes this curatorial rather than structural.
    assert set(relations["asserts_counts"]) <= {
        "source_publication_structure", "source_dating", "source_context",
        "interpretation", "unmapped"}
    assert set(RELATION_KINDS.values()) >= set(relations["asserts_counts"]) - {"unmapped"}
    # Only a source-structure relation, or one the person reconfirmed, is attested.
    for row in curatorial_relations(log):
        if row["state"] == "externally_attested":
            assert row["confirmed"] or row["asserts"].startswith("source_")
        else:
            assert row["state"] == "candidate"
            assert not row["confirmed"]
            assert row["asserts"] == "interpretation"


@relation_logs
def test_a_replay_fixture_never_reaches_a_curatorial_document() -> None:
    from flujo.knowledge.human_decision_log import (
        curatorial_relations,
        read_human_decisions,
    )

    log = read_human_decisions(connections_path=CONNECTIONS)
    relations = log["relations"]
    carried = curatorial_relations(log)

    # The real log contains replay fixtures; they are counted, not dropped silently.
    assert relations["non_published_pair_count"] > 0
    assert relations["non_published_examples"]
    assert (relations["published_pair_count"]
            + relations["non_published_pair_count"] == relations["pair_count"])
    assert len(carried) == relations["published_pair_count"]
    for row in carried:
        for side in (row["left"], row["right"]):
            stem = side.rsplit(".", 1)[0] if "." in side else side
            assert stem.isdigit() and len(stem) >= 12, side


@relation_logs
def test_a_machine_provider_proposes_and_never_attests() -> None:
    from flujo.knowledge.human_decision_log import read_human_decisions

    log = read_human_decisions(
        connections_path=CONNECTIONS,
        feedback_path=FEEDBACK if FEEDBACK.exists() else None,
        external_path=EXTERNAL if EXTERNAL.exists() else None)
    machine = log["machine_proposals"]

    assert machine["event_count"] > 0
    assert machine["providers"], "the providers must be named"
    assert "human" not in machine["providers"]
    assert machine["attesting"] is False
    # Feedback rows are only read when the person is the provider.
    assert log["feedback"]["non_human_rows_ignored"] >= 0
    for row in log["feedback"]["by_pair"].values():
        assert row["confirmed_by"] == "human"


@relation_logs
@real_sources
def test_f7_renders_readings_and_source_support_in_the_right_slots() -> None:
    from flujo.knowledge.human_decision_log import (
        curatorial_relations,
        read_human_decisions,
    )

    log = read_human_decisions(
        connections_path=CONNECTIONS,
        feedback_path=FEEDBACK if FEEDBACK.exists() else None)
    base = compile_portfolio_claims(
        index_path=INDEX,
        authority_path=ROOT / "data" / "artist_discographies.json",
        practices_path=ROOT / "data" / "portfolio_practices.json",
        human_relations=curatorial_relations(log))
    spec = next(
        row for row in load_format_library(FORMATS)["formats"]
        if row["format_id"] == "F7-lectura-curatorial")
    payload = render_portfolio(spec, base)

    assert payload["status"] == "rendered"
    sections = {row["slot_id"]: row for row in payload["document"]["sections"]}
    assert set(sections) == {"lecturas", "soporte_de_fuente"}
    # The slot filter is what keeps a source fact out of the readings section.
    for item in sections["lecturas"]["items"]:
        assert "lectura de la persona" in item["caption"]
    for item in sections["soporte_de_fuente"]["items"]:
        assert "source_" in item["caption"]
    # No fixture id survives into the document.
    for section in payload["document"]["sections"]:
        for item in section["items"]:
            assert "mak-replay" not in item["caption"]
            assert "obra-a" not in item["caption"]


def test_a_slot_can_filter_on_a_declared_field_value() -> None:
    spec = json.loads(
        (FORMATS / "F7-lectura-curatorial.json").read_text(encoding="utf-8"))
    loaded = validate_portfolio_format(spec)
    by_id = {row["slot_id"]: row for row in loaded["slots"]}

    assert by_id["lecturas"]["require_fields"] == {"asserts": ["interpretation"]}
    assert "source_dating" in by_id["soporte_de_fuente"]["require_fields"]["asserts"]
    # A filter on an undeclared caption field is rejected.
    broken = copy.deepcopy(spec)
    broken["slots"][0]["require_fields"] = {"precio": ["alto"]}
    with pytest.raises(PortfolioFormatError, match="require_fields_undeclared"):
        validate_portfolio_format(broken)


def test_the_fund_reports_are_recorded_as_unusable_demands() -> None:
    """A plausible report is not a captured demand, and the record says so."""
    path = ROOT / "data" / "demand_source_assessment.json"
    if not path.is_file():
        pytest.skip("the assessment has not been written")
    assessment = json.loads(path.read_text(encoding="utf-8"))

    assert assessment["verdict"] == "not_usable_as_a_demand"
    assert assessment["attesting"] is False
    assert assessment["state"] == "candidate"
    assert len(assessment["reports"]) >= 5
    # Every report must carry the measurements the verdict rests on.
    for row in assessment["reports"]:
        assert "official_source_count" in row
        assert "run_error_count" in row
        assert row["sha256"]
    # And the contrast case must be named, so the difference is legible.
    contrast = assessment["what_a_real_demand_looks_like"]
    assert contrast["schema"] == "mak-opportunity-constraints-v1"
    assert "localizadores de pagina" in " ".join(contrast["has"])
