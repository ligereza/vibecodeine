#!/usr/bin/env python3
"""Contracts for `tools/build_application_intake.py`, 808 lines with no witness.

The tool turns an indexed SSD or one project folder into a traceable
application package. Two promises make it usable at all, and neither was
checked by anything in the suite:

* **The source is never copied, moved, renamed, or rewritten.** It is the first
  sentence of the module docstring, and it is what makes it safe to point at an
  archive. Asserted here by hashing the whole source tree before and after.
* **It does not write the application.** Every prose section comes out
  `PENDIENTE`, the fund is `candidate_unverified` and the official call is
  `required_and_unverified`, because a package that reads as if a person wrote
  it would be inventing evidence for a public application.

The rest is arithmetic that decides which project gets proposed, so it is
asserted against inputs that make each rule fire.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from tools.build_application_intake import (
    SCHEMA,
    build_intake,
    fund_spec,
    is_system_project,
    main,
    project_score,
    scan_project_folder,
    slug,
    stable_json,
)


def _tree_fingerprint(root: Path) -> dict[str, str]:
    """Path -> content hash for every file under root, plus its mtime."""
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            out[str(path.relative_to(root))] = f"{digest}:{path.stat().st_mtime_ns}"
    return out


@pytest.fixture
def project(tmp_path: Path) -> Path:
    source = tmp_path / "archivo" / "obra_de_prueba"
    source.mkdir(parents=True)
    (source / "toma01.mp4").write_bytes(b"video de prueba")
    (source / "still.jpg").write_bytes(b"imagen de prueba")
    (source / "escena.blend").write_bytes(b"{}")
    (source / "notas.txt").write_text("apunte", encoding="utf-8")
    return source


@pytest.fixture
def intake(tmp_path: Path, project: Path) -> dict:
    out = tmp_path / "salida"
    index, _root, _summary = scan_project_folder(project, out / "source_index.sqlite")
    return build_intake(
        index, out, project.name, ["Fondart"], 10,
        mak_db=tmp_path / "no_existe.db", source_kind="project_folder",
    )


class TestTheSourceIsNeverTouched:
    """The promise that makes it safe to point this at a real archive."""

    def test_scanning_leaves_every_source_file_byte_identical(
        self, tmp_path: Path, project: Path
    ) -> None:
        before = _tree_fingerprint(project)
        scan_project_folder(project, tmp_path / "out" / "index.sqlite")
        assert _tree_fingerprint(project) == before

    def test_a_full_intake_leaves_every_source_file_byte_identical(
        self, tmp_path: Path, project: Path
    ) -> None:
        before = _tree_fingerprint(project)
        out = tmp_path / "salida"
        index, _root, _summary = scan_project_folder(project, out / "source_index.sqlite")
        build_intake(index, out, project.name, ["Fondart"], 10,
                     mak_db=tmp_path / "no_existe.db", source_kind="project_folder")
        assert _tree_fingerprint(project) == before, "the intake modified the source"

    def test_nothing_new_appears_inside_the_source(
        self, tmp_path: Path, project: Path
    ) -> None:
        # A stray index or lock file written next to the originals would be a
        # copy of the archive nobody asked for.
        before = set(_tree_fingerprint(project))
        out = tmp_path / "salida"
        index, _root, _summary = scan_project_folder(project, out / "source_index.sqlite")
        build_intake(index, out, project.name, ["Fondart"], 10,
                     mak_db=tmp_path / "no_existe.db", source_kind="project_folder")
        assert set(_tree_fingerprint(project)) == before

    def test_the_outputs_land_outside_the_source(self, intake: dict, project: Path) -> None:
        output_dir = Path(intake["output_dir"]).resolve()
        assert project.resolve() not in output_dir.parents
        assert output_dir != project.resolve()


class TestItDoesNotWriteTheApplication:
    def test_every_prose_section_is_left_pending(self, intake: dict, tmp_path: Path) -> None:
        package = _one_application(tmp_path)
        sections = package["sections"]
        for key in ("problem_and_context", "artistic_or_technical_method",
                    "outputs", "audience_and_impact"):
            assert sections[key].startswith("PENDIENTE"), (
                f"{key} came out written: {sections[key][:80]!r}"
            )

    def test_the_fund_is_not_claimed_as_verified(self, intake: dict, tmp_path: Path) -> None:
        package = _one_application(tmp_path)
        assert package["fund"]["status"] == "candidate_unverified"
        assert package["fund"]["requirements"]["official_call"] == "required_and_unverified"

    def test_the_package_declares_its_gaps(self, intake: dict, tmp_path: Path) -> None:
        package = _one_application(tmp_path)
        assert package["status"] == "draft_with_evidence_gaps"
        assert package["gaps"], "a draft with no declared gap reads as ready"

    def test_no_fund_claims_a_checked_live_call(self) -> None:
        for name in ("Fondart", "Ama Amoedo", "cualquier otro"):
            _fund_id, _requirements, evidence = fund_spec(name)
            assert json.loads(evidence)["live_call_checked"] is False, (
                f"{name} claims the live call was checked; nothing here checks it"
            )


class TestScoring:
    def _row(self, **overrides):
        row = {"dimensionality": "2d", "asset_count": 1, "project_path": "obra/una"}
        row.update(overrides)
        return row

    def test_a_system_folder_is_pushed_out_of_reach(self) -> None:
        score, _reason = project_score(
            self._row(project_path="$RECYCLE.BIN/algo", dimensionality="mixto"),
            {"video": 1, "image": 1, "structural": 1}, 6,
        )
        assert score == -100.0, "a recycle bin outscored real work"

    @pytest.mark.parametrize(
        "path", ["$Recycle.Bin/x", ".Spotlight-V100/y", ".Trashes/z", ".fseventsd/w"]
    )
    def test_the_system_folders_are_recognised_whatever_the_case(self, path: str) -> None:
        assert is_system_project(path)

    @pytest.mark.parametrize("path", ["obra/una", "proyectos/2026/video", "recycle/obra"])
    def test_a_real_folder_is_not_a_system_folder(self, path: str) -> None:
        assert not is_system_project(path)

    def test_richer_media_scores_higher(self) -> None:
        bare, _ = project_score(self._row(), {}, 0)
        rich, _ = project_score(self._row(), {"video": 1, "image": 1, "structural": 1}, 0)
        assert rich > bare

    def test_a_mak_consumer_link_counts_but_is_capped(self) -> None:
        none, _ = project_score(self._row(), {}, 0)
        some, _ = project_score(self._row(), {}, 3)
        many, _ = project_score(self._row(), {}, 500)
        assert none < some < many
        assert many - none == 12, "the link bonus must stay capped at 12"

    def test_the_reason_names_what_earned_the_score(self) -> None:
        _score, reason = project_score(
            self._row(dimensionality="mixto"), {"video": 1, "structural": 1}, 2
        )
        for expected in ("mixto", "video", "editable_or_structural", "MAK_consumer_link"):
            assert expected in reason

    def test_metadata_only_says_so(self) -> None:
        _score, reason = project_score(self._row(dimensionality=""), {}, 0)
        assert reason == "metadata_only"


class TestSlugAndSerialisation:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("Obra De Prueba", "obra-de-prueba"),
            ("  espacios  ", "espacios"),
            ("acentos: Créación", "acentos-cr-aci-n"),
            ("---", "project"),
            ("", "project"),
            (None, "project"),
        ],
    )
    def test_slug_normalises_or_falls_back(self, value, expected: str) -> None:
        assert slug(value) == expected

    def test_slug_takes_the_caller_fallback(self) -> None:
        assert slug("", "fund") == "fund"

    def test_stable_json_is_key_order_independent(self) -> None:
        assert stable_json({"b": 1, "a": 2}) == stable_json({"a": 2, "b": 1})


class TestFundSpec:
    def test_fondart_declares_the_artistic_method_requirement(self) -> None:
        fund_id, requirements, _evidence = fund_spec("Fondart")
        assert fund_id == "fondart"
        assert "artistic_or_technical_method" in requirements

    def test_an_unknown_fund_falls_back_without_pretending_to_know_it(self) -> None:
        fund_id, requirements, evidence = fund_spec("Ama Amoedo")
        assert fund_id == "ama-amoedo"
        assert "method_and_impact" in requirements
        assert json.loads(evidence)["source"] == "user_declared_target"


class TestEndToEnd:
    def test_it_produces_the_declared_deliverables(self, intake: dict) -> None:
        output_dir = Path(intake["output_dir"])
        for name in ("intake.sqlite", "intake.json", "summary.json",
                     "project_candidates.csv", "source_index_reference.json"):
            assert (output_dir / name).is_file(), f"missing {name}"
        assert (output_dir / "applications").is_dir()

    def test_the_run_is_recorded_under_the_declared_schema(self, intake: dict) -> None:
        con = sqlite3.connect(Path(intake["output_db"]))
        try:
            schemas = {row[0] for row in con.execute("select schema_name from intake_runs")}
        finally:
            con.close()
        assert schemas == {SCHEMA}

    def test_it_selects_the_project_it_was_pointed_at(self, intake: dict) -> None:
        assert intake["selected"], "nothing was selected from a folder with four files"
        assert intake["selected"][0]["title"] == "obra_de_prueba"

    def test_the_same_index_yields_the_same_run(
        self, tmp_path: Path, project: Path
    ) -> None:
        # `source_fingerprint` hashes the index path and its mtime, so the id
        # identifies the index artifact rather than the archive's content. Two
        # runs over the same index must agree; two separate scans need not, and
        # asserting otherwise would be testing a promise nobody made.
        out = tmp_path / "salida"
        index, _root, _summary = scan_project_folder(project, out / "source_index.sqlite")
        first = build_intake(index, out, project.name, ["Fondart"], 10,
                             mak_db=tmp_path / "no.db", source_kind="project_folder")
        second = build_intake(index, out, project.name, ["Fondart"], 10,
                              mak_db=tmp_path / "no.db", source_kind="project_folder")
        assert first["run_id"] == second["run_id"]
        assert first["selected"][0]["score"] == second["selected"][0]["score"]

    def test_the_same_folder_can_be_scanned_again_into_the_same_index(
        self, tmp_path: Path, project: Path
    ) -> None:
        # `create_schema` uses CREATE TABLE IF NOT EXISTS; the inline DDL in
        # `scan_project_folder` did not, so the second scan died on
        # "table projects already exists" before reaching a single insert.
        index = tmp_path / "out" / "source_index.sqlite"
        scan_project_folder(project, index)
        scan_project_folder(project, index)

    def test_a_rescan_does_not_duplicate_index_rows(
        self, tmp_path: Path, project: Path
    ) -> None:
        index = tmp_path / "out" / "source_index.sqlite"
        counts = []
        for _ in range(2):
            scan_project_folder(project, index)
            con = sqlite3.connect(index)
            try:
                counts.append(tuple(
                    con.execute(f"select count(*) from {table}").fetchone()[0]
                    for table in ("projects", "assets", "families", "project_members")
                ))
            finally:
                con.close()
        assert counts[0] == counts[1], f"a rescan changed the row counts: {counts}"

    def test_a_rescan_picks_up_a_new_file(self, tmp_path: Path, project: Path) -> None:
        # Idempotent must not mean inert: the point of scanning again is to see
        # what changed.
        index = tmp_path / "out" / "source_index.sqlite"
        scan_project_folder(project, index)
        (project / "nueva.mp4").write_bytes(b"otro video")
        scan_project_folder(project, index)

        con = sqlite3.connect(index)
        try:
            paths = {row[0] for row in con.execute("select relative_path from assets")}
        finally:
            con.close()
        assert "nueva.mp4" in paths

    def test_it_can_be_run_again_over_the_same_index(
        self, tmp_path: Path, project: Path
    ) -> None:
        # The run row was inserted OR IGNORE and the candidates OR REPLACE, so
        # re-running was clearly meant to work. Three inserts in load_index were
        # plain INSERTs, and the second run died on a UNIQUE constraint -- after
        # an interrupted run, or just to regenerate the outputs.
        out = tmp_path / "salida"
        index, _root, _summary = scan_project_folder(project, out / "source_index.sqlite")
        build_intake(index, out, project.name, ["Fondart"], 10,
                     mak_db=tmp_path / "no.db", source_kind="project_folder")
        again = build_intake(index, out, project.name, ["Fondart"], 10,
                             mak_db=tmp_path / "no.db", source_kind="project_folder")
        assert again["selected"], "the second run produced nothing"

    def test_a_rerun_does_not_duplicate_rows(
        self, tmp_path: Path, project: Path
    ) -> None:
        out = tmp_path / "salida"
        index, _root, _summary = scan_project_folder(project, out / "source_index.sqlite")
        counts = []
        for _ in range(2):
            result = build_intake(index, out, project.name, ["Fondart"], 10,
                                  mak_db=tmp_path / "no.db", source_kind="project_folder")
            con = sqlite3.connect(Path(result["output_db"]))
            try:
                counts.append(tuple(
                    con.execute(f"select count(*) from {table}").fetchone()[0]
                    for table in ("intake_assets", "intake_projects", "intake_families")
                ))
            finally:
                con.close()
        assert counts[0] == counts[1], f"a re-run changed the row counts: {counts}"

    def test_scoring_does_not_depend_on_where_the_output_went(
        self, tmp_path: Path, project: Path
    ) -> None:
        scores = []
        for name in ("uno", "dos"):
            out = tmp_path / name
            index, _root, _summary = scan_project_folder(project, out / "source_index.sqlite")
            result = build_intake(index, out, project.name, ["Fondart"], 10,
                                  mak_db=tmp_path / "no.db", source_kind="project_folder")
            scores.append(result["selected"][0]["score"])
        assert scores[0] == scores[1]

    def test_the_cli_runs_and_reports_json(self, tmp_path: Path, project: Path,
                                           capsys) -> None:
        code = main([
            "--source-root", str(project),
            "--out-dir", str(tmp_path / "cli"),
            "--mak-db", str(tmp_path / "no.db"),
        ])
        assert code == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["run_id"]
        assert payload["applications"]

class TestAnEmptyFolderIsNotEvidence:
    """A measured zero is an error, not a finding.

    An empty folder used to come back classified `2d` with confidence 0.8 --
    a dimensionality asserted from no files at all -- scoring 160, with an
    application package whose declared gaps were all somebody else's work.
    The tool is responsible for the evidence half, and said nothing about it.
    """

    @pytest.fixture
    def empty_run(self, tmp_path: Path) -> tuple[dict, dict]:
        empty = tmp_path / "vacia"
        empty.mkdir()
        out = tmp_path / "salida_vacia"
        index, _root, _summary = scan_project_folder(empty, out / "source_index.sqlite")
        result = build_intake(index, out, empty.name, ["Fondart"], 10,
                              mak_db=tmp_path / "no.db", source_kind="project_folder")
        package = json.loads(
            sorted((out / "applications").glob("*.json"))[0].read_text(encoding="utf-8")
        )
        return result, package

    def test_it_is_not_classified_from_nothing(self, empty_run) -> None:
        result, _package = empty_run
        assert result["selected"][0]["dimensionality"] == "desconocida"

    def test_it_does_not_borrow_the_score_of_real_work(self, empty_run) -> None:
        result, _package = empty_run
        empty_score = result["selected"][0]["score"]
        flat, _reason = project_score(
            {"dimensionality": "2d", "asset_count": 1, "project_path": "obra"}, {}, 0
        )
        assert empty_score - 100 < flat, (
            "an empty folder scored at least as high as a real 2d project "
            "(the 100 is the explicit-project bonus both would get)"
        )

    def test_the_missing_evidence_is_a_declared_blocking_gap(self, empty_run) -> None:
        _result, package = empty_run
        blocking = [
            gap for gap in package["gaps"]
            if gap["field"] == "evidence_and_portfolio" and gap["severity"] == "blocking"
        ]
        assert blocking, (
            "the package listed only gaps a person must fill and never said the "
            "archive side is empty"
        )

    def test_a_folder_with_evidence_gets_no_such_gap(self, intake: dict, tmp_path: Path) -> None:
        package = _one_application(tmp_path)
        blocking = [
            gap for gap in package["gaps"]
            if gap["field"] == "evidence_and_portfolio" and gap["severity"] == "blocking"
        ]
        assert not blocking, "a folder with four files was told it has no evidence"

    def test_assets_that_are_not_portfolio_material_are_flagged_for_review(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "solo_texto"
        source.mkdir()
        (source / "notas.txt").write_text("apunte", encoding="utf-8")
        (source / "lista.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        out = tmp_path / "salida_texto"
        index, _root, _summary = scan_project_folder(source, out / "source_index.sqlite")
        build_intake(index, out, source.name, ["Fondart"], 10,
                     mak_db=tmp_path / "no.db", source_kind="project_folder")
        package = json.loads(
            sorted((out / "applications").glob("*.json"))[0].read_text(encoding="utf-8")
        )
        flagged = [g for g in package["gaps"] if g["field"] == "evidence_and_portfolio"]
        assert flagged, "two text files were accepted as portfolio evidence in silence"


def _one_application(tmp_path: Path) -> dict:
    """The single application package the fixtures produce."""
    packages = sorted((tmp_path / "salida" / "applications").glob("*.json"))
    assert packages, "the intake produced no application package"
    return json.loads(packages[0].read_text(encoding="utf-8"))
