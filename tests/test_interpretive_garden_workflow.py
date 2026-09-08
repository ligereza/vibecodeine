#!/usr/bin/env python3
"""Contracts for `tools/interpretive_garden_workflow.py`, 641 lines untested.

The module makes two claims in its first paragraph, and both are the kind a
reader has to take on trust unless something checks them:

    The tool is intentionally offline-first. [...] a URL is not treated as
    verified merely because it appears in the document.

The first is asserted by running the whole seed with `socket.socket` replaced
by a landmine: if anything reaches the network, the test fails instead of
quietly succeeding on a machine that happens to be connected.

The second is asserted by reading back what it stored. A source extracted from
prose may be recorded as *referenced*; it may never be recorded as *fetched*,
*reachable*, or *current*, because nothing here fetched anything.
"""
from __future__ import annotations

import socket
import sqlite3
from pathlib import Path

import pytest

from tools.interpretive_garden_workflow import (
    URL_RE,
    create_schema,
    export_csv,
    family_for_url,
    render_report,
    seed,
    validate,
)

DOCUMENT = """# Jardines interpretativos

Un laboratorio de traduccion entre conocimiento y experiencia.

Referencias consultadas:

- http://algorithmicbotany.org/papers/ sobre modelado de plantas.
- https://openalea.readthedocs.io/ para arquitectura vegetal.
- https://www.wikidata.org/wiki/Q42 como conocimiento estructurado.
- https://gephi.org/users/ para visualizacion de redes.
- https://ejemplo-desconocido.test/algo que nadie ha revisado.
"""


@pytest.fixture
def document(tmp_path: Path) -> Path:
    path = tmp_path / "JARDINES_INTERPRETATIVOS.md"
    path.write_text(DOCUMENT, encoding="utf-8")
    return path


@pytest.fixture
def seeded(tmp_path: Path, document: Path):
    connection = sqlite3.connect(tmp_path / "modelo.sqlite")
    create_schema(connection)
    url_count = seed(connection, document)
    yield connection, url_count
    connection.close()


class TestItReallyIsOffline:
    """The claim is 'intentionally offline-first'. This is what checks it."""

    @pytest.fixture
    def no_network(self, monkeypatch):
        def landmine(*args, **kwargs):
            raise AssertionError("the workflow opened a socket")

        monkeypatch.setattr(socket, "socket", landmine)
        monkeypatch.setattr(socket, "create_connection", landmine)
        monkeypatch.setattr(socket, "getaddrinfo", landmine)

    def test_seeding_never_opens_a_socket(
        self, no_network, tmp_path: Path, document: Path
    ) -> None:
        connection = sqlite3.connect(tmp_path / "modelo.sqlite")
        try:
            create_schema(connection)
            assert seed(connection, document) > 0
        finally:
            connection.close()

    def test_rendering_never_opens_a_socket(
        self, no_network, tmp_path: Path, document: Path
    ) -> None:
        connection = sqlite3.connect(tmp_path / "modelo.sqlite")
        try:
            create_schema(connection)
            count = seed(connection, document)
            render_report(connection, tmp_path / "informe.md", document, count)
        finally:
            connection.close()
        assert (tmp_path / "informe.md").is_file()

    def test_the_landmine_is_armed(self, no_network) -> None:
        # Without this, the two tests above would pass on a build where the
        # patch never took effect.
        with pytest.raises(AssertionError, match="opened a socket"):
            socket.socket()


class TestAUrlIsNotEvidenceOfItself:
    def test_no_source_is_recorded_as_fetched(self, seeded) -> None:
        connection, _count = seeded
        states = {
            row[0] for row in connection.execute("SELECT verification_state FROM sources")
        }
        assert states, "no source was recorded"
        for state in states:
            for forbidden in ("fetched", "reachable", "online", "current", "confirmed",
                              "verified_live", "checked_live"):
                assert forbidden not in state.lower(), (
                    f"a source claims {state!r} when nothing here made a request"
                )

    def test_every_source_carries_the_disclaimer(self, seeded) -> None:
        connection, _count = seeded
        for (notes,) in connection.execute("SELECT notes FROM sources"):
            assert "not proof" in notes.lower(), (
                f"a source was stored without saying what its presence proves: {notes!r}"
            )

    def test_a_referenced_state_says_referenced(self, seeded) -> None:
        connection, _count = seeded
        states = {
            row[0] for row in connection.execute("SELECT verification_state FROM sources")
        }
        assert all("referenced" in state for state in states), states

    def test_an_unknown_host_gets_no_invented_authority(self, seeded) -> None:
        connection, _count = seeded
        row = connection.execute(
            "SELECT family, name FROM sources WHERE url LIKE '%ejemplo-desconocido%'"
        ).fetchone()
        assert row is not None, "the unknown URL was dropped instead of kept"
        family, name = row
        assert family == "reference"
        assert name == "ejemplo-desconocido.test", (
            "an unknown host was given a project name it never claimed"
        )

    def test_every_url_in_the_document_is_kept(self, seeded) -> None:
        # Silently dropping one would make the model unverifiable against its
        # own source.
        connection, count = seeded
        expected = {u.rstrip(".,;:") for u in URL_RE.findall(DOCUMENT)}
        stored = {row[0] for row in connection.execute("SELECT url FROM sources")}
        assert stored == expected
        assert count == len(expected)


class TestFamilyForUrl:
    @pytest.mark.parametrize(
        "url,family,name",
        [
            ("http://algorithmicbotany.org/x", "botanical_modeling", "Algorithmic Botany"),
            ("https://openalea.readthedocs.io/y", "botanical_modeling", "OpenAlea"),
            ("https://www.wikidata.org/wiki/Q1", "structured_knowledge", "Wikidata"),
            ("https://gephi.org/users/", "graph_visualization", "Gephi"),
            ("https://gama-platform.org/", "simulation", "GAMA"),
            ("https://p5js.org/", "creative_coding", "p5.js"),
        ],
    )
    def test_a_known_host_is_named(self, url: str, family: str, name: str) -> None:
        assert family_for_url(url)[:2] == (family, name)

    def test_an_unknown_host_falls_back_to_its_own_hostname(self) -> None:
        family, name, role = family_for_url("https://algo.desconocido.test/ruta")
        assert (family, name, role) == (
            "reference", "algo.desconocido.test", "reference source",
        )

    def test_the_host_is_matched_case_insensitively(self) -> None:
        assert family_for_url("https://WWW.WIKIDATA.ORG/wiki/Q1")[1] == "Wikidata"

    def test_a_lookalike_path_does_not_win_the_host(self) -> None:
        # The family comes from the host, not from anywhere in the URL: a path
        # segment must not promote an unrelated site to a known project.
        family, name, _role = family_for_url("https://otro.test/wikidata/gephi")
        assert (family, name) == ("reference", "otro.test")


class TestValidateCatchesAnEmptyModel:
    def test_a_bare_schema_is_reported_as_empty(self, tmp_path: Path) -> None:
        connection = sqlite3.connect(tmp_path / "vacio.sqlite")
        try:
            create_schema(connection)
            errors = validate(connection)
        finally:
            connection.close()
        assert errors, "an unseeded model passed validation"
        assert any("empty table" in error for error in errors)

    def test_a_missing_table_is_reported(self, tmp_path: Path) -> None:
        connection = sqlite3.connect(tmp_path / "incompleto.sqlite")
        try:
            connection.execute("CREATE TABLE metadata(k TEXT)")
            errors = validate(connection)
        finally:
            connection.close()
        assert any("missing table" in error for error in errors)

    def test_a_seeded_model_validates(self, seeded) -> None:
        connection, _count = seeded
        assert validate(connection) == []


class TestDeliverables:
    def test_the_report_names_its_source_document(
        self, seeded, tmp_path: Path, document: Path
    ) -> None:
        connection, count = seeded
        report = tmp_path / "informe.md"
        render_report(connection, report, document, count)
        assert document.name in report.read_text(encoding="utf-8")

    def test_the_csv_export_writes_its_two_declared_files(
        self, seeded, tmp_path: Path
    ) -> None:
        # It exports two named views, not one file per table.
        connection, _count = seeded
        out = tmp_path / "csv"
        export_csv(connection, out)
        assert sorted(path.name for path in out.glob("*.csv")) == [
            "jardines_interpretativos_correlations.csv",
            "jardines_interpretativos_process_semantics.csv",
        ]

    def test_the_export_creates_the_directory_it_was_handed(
        self, seeded, tmp_path: Path
    ) -> None:
        connection, _count = seeded
        out = tmp_path / "no" / "existe" / "todavia"
        export_csv(connection, out)
        assert out.is_dir()

    def test_the_exported_rows_match_the_database(
        self, seeded, tmp_path: Path
    ) -> None:
        connection, _count = seeded
        out = tmp_path / "csv"
        export_csv(connection, out)
        rows = out.joinpath(
            "jardines_interpretativos_correlations.csv"
        ).read_text(encoding="utf-8").splitlines()
        stored = connection.execute("SELECT COUNT(*) FROM correlations").fetchone()[0]
        assert stored > 0, "nothing to compare against"
        assert len(rows) - 1 == stored, "the export lost or duplicated a row"


class TestRerun:
    def test_seeding_twice_does_not_duplicate_sources(
        self, tmp_path: Path, document: Path
    ) -> None:
        connection = sqlite3.connect(tmp_path / "modelo.sqlite")
        try:
            create_schema(connection)
            seed(connection, document)
            first = connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
            create_schema(connection)
            seed(connection, document)
            second = connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        finally:
            connection.close()
        assert first == second, "a second seed duplicated the sources"
