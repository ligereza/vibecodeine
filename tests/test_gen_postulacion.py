#!/usr/bin/env python3
"""Contracts for `tools/gen_postulacion.py`.

The tool exists to catch, before a deadline, the failures that put a public
application out of the competition without anyone reading it: a budget over
the ceiling, a percentage cap exceeded, a mandatory document missing. Those
checks are only worth having if they actually fire, so each one is asserted
against a project that breaks it on purpose.

The other half of the contract is what the tool must *not* do: it must never
write the applicant's prose. A section left empty comes out marked, not
filled.
"""
from __future__ import annotations

import copy
from datetime import date, timedelta
import json

import pytest

from tools.gen_postulacion import (
    BLOCKING,
    WARNING,
    load_calls,
    render,
    review,
    template,
)

CALL = "fondart-regional-creacion-artistica-2027"


@pytest.fixture(scope="module")
def bases() -> dict:
    calls = load_calls()
    assert CALL in calls, f"{CALL} is not in data/: without bases there is nothing to check"
    return calls[CALL]


@pytest.fixture
def valid_project(bases: dict) -> dict:
    """A project that satisfies every rule, so a finding means what it says."""
    project = template(bases)
    project["title"] = "Obra de prueba"
    project["duration_months"] = 10
    project["budget"].update(
        requested_from_fund=5_000_000,
        contingency=50_000,
        lead_fee=1_500_000,
    )
    project["declared_documents"] = ["descripcion_propuesta"]
    for section in project["sections"]:
        project["sections"][section] = f"contenido de {section}"
    return project


def _fields(findings: list[dict], level: str | None = None) -> set[str]:
    return {f["field"] for f in findings if level is None or f["level"] == level}


class TestDeclaredBases:
    def test_criteria_weights_sum_to_one_hundred(self, bases: dict) -> None:
        total = sum(int(c["weight"]) for c in bases["criteria"])
        assert total == 100, f"the weights add up to {total}"

    def test_every_criterion_names_sections_that_exist(self, bases: dict) -> None:
        declared = {s["id"] for s in bases["form_sections"]}
        for criterion in bases["criteria"]:
            for section in criterion["fed_by_sections"]:
                assert section in declared, (
                    f"{criterion['name']} claims to be fed by {section!r}, "
                    "which is not a form section"
                )

    def test_the_bases_cite_their_source(self, bases: dict) -> None:
        source = bases.get("source", {})
        assert source.get("bases_pdf", "").startswith("http")
        assert source.get("read_on")

    def test_every_conditional_document_has_a_trigger(self, bases: dict) -> None:
        # A conditional document with no way to fire is a check that can never
        # run: it would read as covered while never demanding anything.
        from tools.gen_postulacion import DOCUMENT_TRIGGERS

        known = set(DOCUMENT_TRIGGERS) | {"individualizacion_socios"}
        catalogue = bases["mandatory_documents"] + bases["evaluation_documents"]
        for document in catalogue:
            if document.get("conditional", True):
                assert document["id"] in known, (
                    f"{document['id']} is conditional but nothing can trigger it"
                )


class TestValidProject:
    def test_a_complete_project_does_not_block(self, bases, valid_project) -> None:
        assert [f for f in review(bases, valid_project) if f["level"] == BLOCKING] == []

    def test_the_empty_template_blocks_on_everything(self, bases) -> None:
        # A freshly requested template is not an application. If it passed the
        # review, the tool would be calling a blank sheet ready to submit.
        findings = review(bases, template(bases))
        assert any(f["level"] == BLOCKING for f in findings)
        assert "title" in _fields(findings)


class TestBudgetCaps:
    def test_over_the_ceiling_blocks(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        project["budget"]["requested_from_fund"] = bases["amounts"]["max_per_project"] + 1
        assert "budget.requested_from_fund" in _fields(review(bases, project), BLOCKING)

    def test_under_the_floor_blocks(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        project["budget"]["requested_from_fund"] = bases["amounts"]["min_per_project"] - 1
        assert "budget.requested_from_fund" in _fields(review(bases, project), BLOCKING)

    def test_contingency_over_two_percent_blocks(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        requested = project["budget"]["requested_from_fund"]
        project["budget"]["contingency"] = int(requested * 0.021)
        assert "budget.contingency" in _fields(review(bases, project), BLOCKING)

    def test_contingency_exactly_at_the_cap_does_not_block(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        requested = project["budget"]["requested_from_fund"]
        project["budget"]["contingency"] = int(requested * 0.02)
        assert "budget.contingency" not in _fields(review(bases, project), BLOCKING)

    def test_lead_fee_over_forty_percent_blocks(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        requested = project["budget"]["requested_from_fund"]
        project["budget"]["lead_fee"] = int(requested * 0.41)
        assert "budget.lead_fee" in _fields(review(bases, project), BLOCKING)


class TestDuration:
    def test_over_the_month_limit_blocks(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        project["duration_months"] = bases["deadlines"]["max_duration_months"] + 1
        assert "duration_months" in _fields(review(bases, project), BLOCKING)


class TestRequiredDocuments:
    @pytest.mark.parametrize(
        "condition,document",
        [
            ("uses_third_party_works", "documents.autorizacion_derechos_autor"),
            ("has_team", "documents.cartas_compromiso_equipo"),
            ("activities_in_indigenous_territory", "documents.consentimiento_comunidad_indigena"),
            ("works_with_minors", "documents.certificado_inhabilidades_menores"),
            ("activities_in_public_space", "documents.permiso_espacio_publico"),
            ("ephemeral_architecture", "documents.anteproyecto_arquitectura"),
            ("outreach_in_existing_venues", "documents.compromisos_exhibicion"),
        ],
    )
    def test_a_declared_condition_demands_its_document(
        self, bases, valid_project, condition: str, document: str
    ) -> None:
        project = copy.deepcopy(valid_project)
        project["conditions"][condition] = True
        assert document in _fields(review(bases, project), BLOCKING)

    def test_an_undeclared_condition_invents_no_obligation(self, bases, valid_project) -> None:
        # The valid project declares no condition beyond the proposal itself,
        # so demanding a public-space permit would be inventing a formality its
        # own declared conditions never triggered.
        fields = _fields(review(bases, valid_project), BLOCKING)
        assert "documents.permiso_espacio_publico" not in fields
        assert "documents.autorizacion_derechos_autor" not in fields

    def test_declaring_the_document_lifts_the_block(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        project["conditions"]["uses_third_party_works"] = True
        assert "documents.autorizacion_derechos_autor" in _fields(review(bases, project))

        project["declared_documents"].append("autorizacion_derechos_autor")
        assert "documents.autorizacion_derechos_autor" not in _fields(review(bases, project))

    def test_the_unconditional_document_is_always_demanded(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        project["declared_documents"] = []
        assert "documents.descripcion_propuesta" in _fields(review(bases, project), BLOCKING)

    def test_a_for_profit_legal_entity_must_list_its_partners(
        self, bases, valid_project
    ) -> None:
        project = copy.deepcopy(valid_project)
        project["lead"]["is_legal_entity"] = True
        project["lead"]["is_for_profit"] = True
        fields = _fields(review(bases, project), BLOCKING)
        assert "documents.individualizacion_socios" in fields
        assert "documents.estatutos_persona_juridica" in fields

    def test_a_non_profit_legal_entity_owes_statutes_but_not_the_partner_list(
        self, bases, valid_project
    ) -> None:
        project = copy.deepcopy(valid_project)
        project["lead"]["is_legal_entity"] = True
        project["lead"]["is_for_profit"] = False
        fields = _fields(review(bases, project), BLOCKING)
        assert "documents.estatutos_persona_juridica" in fields
        assert "documents.individualizacion_socios" not in fields


class TestEmptySections:
    def test_an_empty_section_blocks_and_says_what_it_costs(
        self, bases, valid_project
    ) -> None:
        project = copy.deepcopy(valid_project)
        project["sections"]["aporte_ecosistema"] = "   "
        findings = [f for f in review(bases, project) if f["field"].endswith("aporte_ecosistema")]
        assert findings, "a blank section has to show up as a finding"
        assert "40%" in findings[0]["detail"]

    def test_empty_sections_are_ordered_by_the_score_they_cost(
        self, bases, valid_project
    ) -> None:
        project = copy.deepcopy(valid_project)
        project["sections"]["objetivos"] = ""          # 10%
        project["sections"]["aporte_ecosistema"] = ""  # 40%
        empty = [f for f in review(bases, project) if f["field"].startswith("sections.")]
        assert empty[0]["field"] == "sections.aporte_ecosistema", (
            "what costs the most score comes first"
        )


class TestDraft:
    def test_it_does_not_write_the_applicants_text(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        project["sections"]["innovacion"] = ""
        assert "[FALTA]" in render(bases, project)

    def test_it_keeps_the_text_the_applicant_did_write(self, bases, valid_project) -> None:
        project = copy.deepcopy(valid_project)
        project["sections"]["fundamentacion"] = "una frase inconfundible del autor"
        assert "una frase inconfundible del autor" in render(bases, project)

    def test_every_section_states_the_criterion_that_scores_it(
        self, bases, valid_project
    ) -> None:
        text = render(bases, valid_project)
        for section in bases["form_sections"]:
            assert section["title"] in text
        for criterion in bases["criteria"]:
            assert f"{criterion['name']} {criterion['weight']}%" in text

    def test_it_cites_the_source_of_the_bases(self, bases, valid_project) -> None:
        assert bases["source"]["bases_pdf"] in render(bases, valid_project)


class TestDeadline:
    def test_a_closed_call_blocks(self, bases, valid_project) -> None:
        closed = copy.deepcopy(bases)
        closed["deadlines"]["closes"] = "2000-01-01"
        assert "deadline" in _fields(review(closed, valid_project), BLOCKING)

    def test_a_distant_close_says_nothing(self, bases, valid_project) -> None:
        distant = copy.deepcopy(bases)
        distant["deadlines"]["closes"] = "2099-12-31"
        assert "deadline" not in _fields(review(distant, valid_project))

    def test_an_imminent_close_warns_without_blocking(self, bases, valid_project) -> None:
        soon = copy.deepcopy(bases)
        soon["deadlines"]["closes"] = (date.today() + timedelta(days=3)).isoformat()
        findings = review(soon, valid_project)
        assert "deadline" in _fields(findings, WARNING)
        assert "deadline" not in _fields(findings, BLOCKING)


class TestProvenanceIsPerField:
    """A file can be the official bases and still carry a borrowed date.

    The Fondart bases PDF states the amounts and the criteria and contains no
    date at all -- checked by searching the extracted text for any
    `N de MES de 2026|2027`: zero matches. The opening and closing dates came
    from a portal summary and had been attributed to the PDF. Warning on the
    file as a whole would say nothing, because the file *is* the official
    bases; the warning has to be about the field.
    """

    def test_the_fondart_deadline_declares_its_own_weaker_source(self, bases) -> None:
        source = bases["deadlines"].get("source") or {}
        assert source.get("kind") and source["kind"] != "official_bases"
        assert source.get("todo"), "a borrowed date must say it needs confirming"

    def test_the_bases_still_own_the_criteria_and_the_amounts(self, bases) -> None:
        # The correction must not throw away what the PDF does support.
        assert bases["source"]["kind"] == "official_bases"
        assert bases["criteria"] and bases["amounts"]["max_per_project"]
        assert bases["deadlines"]["max_duration_months"] == 12

    def test_a_borrowed_deadline_is_warned_about(self, bases, valid_project) -> None:
        findings = review(bases, valid_project)
        assert "deadline.source" in _fields(findings, WARNING)
        assert "deadline.source" not in _fields(findings, BLOCKING), (
            "an unconfirmed date is a warning: blocking would stop a real application"
        )

    def test_a_deadline_read_from_the_document_is_not_warned_about(
        self, bases, valid_project
    ) -> None:
        confirmed = copy.deepcopy(bases)
        confirmed["deadlines"].pop("source", None)
        assert "deadline.source" not in _fields(review(confirmed, valid_project))


class TestRegionalExtensions:
    """Two of them, covering the country between them.

    The northern regions were extended by resolution to a fixed date; Coquimbo
    to Magallanes by two working days, under Rex 2596. Reporting one would give
    most applicants the wrong date, and collapsing them into a single
    "extended" figure would give all of them the wrong date.
    """

    def _extensions(self, bases) -> list[dict]:
        return bases["deadlines"]["regional_extensions"]

    def test_both_declared_extensions_are_surfaced(self, bases, valid_project) -> None:
        fields = _fields(review(bases, valid_project), WARNING)
        assert "deadline.extension.norte-clima" in fields
        assert "deadline.extension.coquimbo-magallanes" in fields

    def test_the_northern_one_names_a_date_and_its_regions(self, bases) -> None:
        north = next(e for e in self._extensions(bases) if e["id"] == "norte-clima")
        assert north["extended_closes"] == "2026-09-16"
        assert north["applies_to_regions"] == [
            "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama",
        ]
        assert "ARTÍCULO PRIMERO" in north["quote"]

    def test_the_southern_one_declares_a_shift_not_an_invented_date(
        self, bases
    ) -> None:
        # The notice gives "two working days", and `closes` itself is not
        # confirmed. Computing a date from an unconfirmed base and printing it
        # as fact is the failure this whole entry was corrected for.
        south = next(
            e for e in self._extensions(bases) if e["id"] == "coquimbo-magallanes"
        )
        assert south["extended_closes"] is None
        assert south["extension_business_days"] == 2
        assert south["regions_as_quoted"] == "de Coquimbo a Magallanes"

    def test_every_extension_cites_where_it_was_read(self, bases) -> None:
        for extension in self._extensions(bases):
            assert extension["url"].startswith("http")
            assert extension["read_on"]
            assert extension["source_kind"]
            assert extension["quote"]

    def test_no_extension_moves_the_declared_close(self, bases) -> None:
        # They are reported beside the date, never instead of it: applying the
        # wrong region's extension hands the applicant days they do not have.
        assert bases["deadlines"]["closes"] == "2026-09-08"

    def test_a_call_without_extensions_says_nothing_about_one(
        self, bases, valid_project
    ) -> None:
        plain = copy.deepcopy(bases)
        plain["deadlines"].pop("regional_extensions", None)
        fields = _fields(review(plain, valid_project))
        assert not any(field.startswith("deadline.extension.") for field in fields)


class TestClosingTimeAndZone:
    """A deadline in someone else's clock can be missed while feeling met.

    Ama Amoedo closes 23:59 Uruguay time. Chile enters DST on 2026-09-06 per
    IANA tzdata, so on the 9th both are UTC-3 and the two coincide -- but a
    close on the 5th would have been 22:59 in Chile. The entry records the
    zone; the checker says so; neither converts silently.
    """

    CALL = "ama-amoedo-becas-2026"

    @pytest.fixture(scope="class")
    @classmethod
    def timed(cls) -> dict:
        return load_calls()[cls.CALL]

    def test_the_entry_records_the_hour_and_the_zone(self, timed) -> None:
        assert timed["deadlines"]["closes_time"] == "23:59"
        assert timed["deadlines"]["closes_timezone"] == "America/Montevideo"

    def test_a_foreign_zone_is_warned_about(self, timed) -> None:
        findings = review(timed, template(timed))
        assert "deadline.timezone" in _fields(findings, WARNING)

    def test_the_warning_names_the_zone_rather_than_converting(self, timed) -> None:
        # Converting for the applicant means guessing where they are.
        finding = next(
            f for f in review(timed, template(timed))
            if f["field"] == "deadline.timezone"
        )
        assert "America/Montevideo" in finding["detail"]
        assert "23:59" in finding["detail"]

    def test_a_call_without_a_declared_zone_says_nothing(self, bases) -> None:
        # Fondart declares no closing time, so inventing a warning would be
        # noise on the entry that matters most.
        assert "closes_timezone" not in bases["deadlines"]
        assert "deadline.timezone" not in _fields(review(bases, template(bases)))

    def test_the_absence_of_extensions_records_that_it_was_checked(
        self, timed
    ) -> None:
        # An empty list can mean "none exist" or "nobody looked", and four days
        # from a close those are not worth the same.
        checked = timed["deadlines"]["extensions_checked"]
        assert checked["on"] and checked["found"]
        assert timed["deadlines"]["regional_extensions"] == []


class TestPartialBases:
    """A convocatoria whose official document could not be read.

    The Ama Amoedo file carries the deadline and the amount from corroborated
    press coverage, and deliberately leaves `criteria` empty because
    transcribing evaluation criteria from a press summary would be inventing
    them. The tool has to stay useful and stay honest at the same time.
    """

    CALL = "ama-amoedo-becas-2026"

    @pytest.fixture(scope="class")
    @classmethod
    def partial(cls) -> dict:
        calls = load_calls()
        assert cls.CALL in calls
        return calls[cls.CALL]

    def test_it_warns_that_the_bases_are_not_official(self, partial) -> None:
        findings = review(partial, template(partial))
        assert "bases" in _fields(findings, WARNING)
        assert "bases.criteria" in _fields(findings, WARNING)

    def test_it_does_not_claim_a_weight_it_cannot_know(self, partial) -> None:
        findings = review(partial, template(partial))
        empty = [f for f in findings if f["field"].startswith("sections.")]
        assert empty, "the empty sections still have to be reported"
        for finding in empty:
            assert "0%" not in finding["detail"], (
                "reporting 0% would read as measured, not as unknown"
            )

    def test_it_does_not_demand_a_duration_the_bases_never_set(self, partial) -> None:
        # Over-demanding is how a checker teaches the operator to skim past it.
        assert partial["deadlines"]["max_duration_months"] is None
        assert "duration_months" not in _fields(review(partial, template(partial)))

    def test_it_does_not_demand_a_minimum_that_does_not_exist(self, partial) -> None:
        assert partial["amounts"]["min_per_project"] is None
        assert "budget.requested_from_fund" not in _fields(review(partial, template(partial)))

    def test_the_ceiling_it_does_know_still_applies(self, partial) -> None:
        project = template(partial)
        project["budget"]["requested_from_fund"] = partial["amounts"]["max_per_project"] + 1
        assert "budget.requested_from_fund" in _fields(review(partial, project), BLOCKING)

    def test_it_records_which_official_urls_failed(self, partial) -> None:
        # Without this the next reader repeats the same dead links.
        assert partial["source"]["official_bases_unreachable"]
        assert partial["source"]["corroborated_by"]

    def test_the_fondart_bases_are_not_marked_partial(self, bases) -> None:
        findings = review(bases, template(bases))
        assert "bases" not in _fields(findings, WARNING)
        assert "bases.criteria" not in _fields(findings, WARNING)


class TestTemplate:
    def test_the_template_is_serializable_and_carries_every_section(self, bases) -> None:
        empty = template(bases)
        json.dumps(empty)
        assert set(empty["sections"]) == {s["id"] for s in bases["form_sections"]}
