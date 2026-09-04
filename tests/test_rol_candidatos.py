#!/usr/bin/env python3
"""Contracts for `tools/rol_candidatos.py`.

The F5 Fondart format needs a `rol_y_exclusiones` slot and the archive cannot
supply it: `owner_status` is `unknown` for all 917 projects. A role is a claim
a person makes about their own work, and the format refuses to render without
the negative half because declaring what you did without declaring what you did
not overclaims in a signed document.

So the tool ranks where the effort is best spent and hands back a blank sheet.
The contract that matters is what it must never do: fill either field, infer a
role from a folder name, or let a ranking read as a finding. Everything else
here is arithmetic.
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3

import pytest

from tools.rol_candidatos import (
    DIMENSION_BONUS,
    WEIGHTS,
    candidates,
    connect,
    main,
    score,
    third_party,
    worksheet,
)


def _flat(text: str) -> str:
    """Collapse wrapping so an assertion is about words, not line breaks.

    The worksheet is prose meant to be read, so it wraps. A phrase that
    spans a break is still present in the sheet; asserting on the raw
    string tests the line width instead of the wording.
    """
    return " ".join(text.split())


def _index(path: Path, projects: list[dict], assets: list[dict],
           members: list[tuple[str, str]]) -> Path:
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE projects (project_id TEXT, project_path TEXT, "
        "container_root TEXT, dimensionality TEXT, owner_status TEXT, "
        "owner_evidence_json TEXT, storage_role TEXT, asset_count INTEGER, "
        "bytes INTEGER, anchor_count INTEGER, strategy TEXT, confidence REAL)"
    )
    con.execute(
        "CREATE TABLE assets (asset_id TEXT, media_kind TEXT)"
    )
    con.execute(
        "CREATE TABLE project_members (asset_id TEXT, project_id TEXT)"
    )
    for row in projects:
        con.execute(
            "INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (row["project_id"], row["project_path"], row["container_root"],
             row.get("dimensionality", "2d"), row.get("owner_status", "unknown"),
             "[]", "", row.get("asset_count", 0), row.get("bytes", 0), 0, "", 0.0),
        )
    for row in assets:
        con.execute("INSERT INTO assets VALUES (?,?)",
                    (row["asset_id"], row["media_kind"]))
    for asset_id, project_id in members:
        con.execute("INSERT INTO project_members VALUES (?,?)",
                    (asset_id, project_id))
    con.commit()
    con.close()
    return path


@pytest.fixture
def index(tmp_path: Path) -> Path:
    return _index(
        tmp_path / "archivo.sqlite",
        projects=[
            {"project_id": "p1", "project_path": "LYON/uno",
             "container_root": "LYON", "dimensionality": "mixto",
             "asset_count": 3},
            {"project_id": "p2", "project_path": "LYON/dos",
             "container_root": "LYON", "dimensionality": "2d",
             "asset_count": 1},
            {"project_id": "p3", "project_path": "SOLO/tres",
             "container_root": "SOLO", "dimensionality": "2d",
             "asset_count": 1},
        ],
        assets=[
            {"asset_id": "a1", "media_kind": "structural"},
            {"asset_id": "a2", "media_kind": "video"},
            {"asset_id": "a3", "media_kind": "image"},
            {"asset_id": "a4", "media_kind": "image"},
            {"asset_id": "a5", "media_kind": "image"},
        ],
        members=[("a1", "p1"), ("a2", "p1"), ("a3", "p1"),
                 ("a4", "p2"), ("a5", "p3")],
    )


class TestItNeverDeclaresARole:
    def test_both_role_fields_come_back_empty(self, index: Path) -> None:
        con = connect(index)
        try:
            rows = candidates(con, context=None, limit=10)
        finally:
            con.close()
        assert rows
        for row in rows:
            assert row["part_done"] == ""
            assert row["part_not_done"] == ""

    def test_the_worksheet_leaves_both_columns_blank(self, index: Path) -> None:
        con = connect(index)
        try:
            sheet = worksheet(candidates(con, context=None, limit=10))
        finally:
            con.close()
        for line in sheet.splitlines():
            if line.startswith("| ") and "`" in line:
                assert line.rstrip().endswith("|  |  |"), (
                    f"a worksheet row arrived pre-filled: {line}"
                )

    def test_it_carries_the_undeclared_status_rather_than_hiding_it(
        self, index: Path
    ) -> None:
        # A ranking must not read as a finding about authorship.
        con = connect(index)
        try:
            rows = candidates(con, context=None, limit=10)
        finally:
            con.close()
        assert all(row["owner_status"] == "unknown" for row in rows)

    def test_the_worksheet_says_why_the_columns_are_empty(self, index: Path) -> None:
        con = connect(index)
        try:
            sheet = worksheet(candidates(con, context=None, limit=3))
        finally:
            con.close()
        flat = _flat(sheet)
        assert "no una medición" in flat
        assert "invalid_if" in flat


class TestAToolIsNotAWork:
    """Flagged, sunk, never dropped -- and never decided beyond the obvious.

    A folder holding 4193 assets of a VJ application ranks high on evidence and
    is not something to declare a role over. It is also not something to hide:
    what is not yours is the material of the exclusions half.

    What the tool refuses to decide is the general case. A script or a system
    you wrote can be a work depending on how you present it, and that is a
    decision, not a property of the file.
    """

    @pytest.fixture
    def mixed(self, tmp_path: Path) -> Path:
        return _index(
            tmp_path / "mixto.sqlite",
            projects=[
                {"project_id": "w1", "project_path": "LYON/obra",
                 "container_root": "LYON", "dimensionality": "mixto",
                 "asset_count": 2},
                {"project_id": "t1", "project_path": "NestDropV23",
                 "container_root": "NestDropV23", "dimensionality": "3d",
                 "asset_count": 3},
                {"project_id": "s1", "project_path": ".Spotlight-V100",
                 "container_root": ".Spotlight-V100", "asset_count": 1},
            ],
            assets=[
                {"asset_id": "b1", "media_kind": "structural"},
                {"asset_id": "b2", "media_kind": "video"},
                {"asset_id": "b3", "media_kind": "structural"},
                {"asset_id": "b4", "media_kind": "structural"},
                {"asset_id": "b5", "media_kind": "structural"},
                {"asset_id": "b6", "media_kind": "other"},
                # Five structural assets against the work's one. With
                # three the scores tied at 17.3, because the mixto/3d
                # bonus gap cancelled the evidence gap exactly and the
                # test proved nothing.
                {"asset_id": "b7", "media_kind": "structural"},
                {"asset_id": "b8", "media_kind": "structural"},
            ],
            members=[("b1", "w1"), ("b2", "w1"),
                     ("b3", "t1"), ("b4", "t1"), ("b5", "t1"),
                     ("b7", "t1"), ("b8", "t1"),
                     ("b6", "s1")],
        )

    def test_third_party_software_sinks_below_the_work(self, mixed: Path) -> None:
        con = connect(mixed)
        try:
            rows = candidates(con, context=None, limit=10)
        finally:
            con.close()
        assert rows[0]["path"] == "LYON/obra"
        assert rows[-1]["kind"] == "software_de_terceros"

    def test_it_is_flagged_rather_than_dropped(self, mixed: Path) -> None:
        # Dropping would remove the material the exclusions column is made of.
        con = connect(mixed)
        try:
            paths = {row["path"] for row in candidates(con, context=None, limit=10)}
        finally:
            con.close()
        assert "NestDropV23" in paths

    def test_the_flag_names_what_triggered_it(self, mixed: Path) -> None:
        con = connect(mixed)
        try:
            rows = {r["path"]: r for r in candidates(con, context=None, limit=10)}
        finally:
            con.close()
        assert rows["NestDropV23"]["third_party_marker"] == "nestdrop"
        assert rows["LYON/obra"]["third_party_marker"] == ""

    def test_more_evidence_does_not_promote_a_third_party_product(
        self, mixed: Path
    ) -> None:
        # NestDrop carries five structural assets against the work's one, so
        # on evidence alone it would outrank it.
        con = connect(mixed)
        try:
            rows = candidates(con, context=None, limit=10)
        finally:
            con.close()
        nest = next(r for r in rows if r["path"] == "NestDropV23")
        work = next(r for r in rows if r["path"] == "LYON/obra")
        assert nest["score"] > work["score"], "the premise of this test is gone"
        assert rows.index(work) < rows.index(nest)

    def test_anything_unlisted_is_unexamined_not_approved(self, mixed: Path) -> None:
        con = connect(mixed)
        try:
            rows = candidates(con, context=None, limit=10)
        finally:
            con.close()
        work = next(r for r in rows if r["path"] == "LYON/obra")
        assert work["kind"] == "sin_clasificar"

    def test_the_worksheet_marks_them_and_says_what_it_does_not_decide(
        self, mixed: Path
    ) -> None:
        con = connect(mixed)
        try:
            sheet = worksheet(candidates(con, context=None, limit=10))
        finally:
            con.close()
        flat = _flat(sheet)
        assert "software de terceros" in flat
        assert "según cómo lo presentes" in flat
        assert "sin examinar, no aprobado" in flat

    @pytest.mark.parametrize(
        "name", ["NestDropV23", "nestdropv23", "algo/NESTDROP/x", ".Spotlight-V100"]
    )
    def test_the_marker_match_ignores_case_and_position(self, name: str) -> None:
        assert third_party(name, name) is not None

    @pytest.mark.parametrize("name", ["LYON/obra", "codigo/tools/mi_script.py", "SCD"])
    def test_a_normal_project_is_not_marked(self, name: str) -> None:
        # Notably a script of your own: whether that is a work is a decision
        # about presentation, and this tool does not take it.
        assert third_party(name, name) is None


class TestTheRankingIsExplainable:
    def test_native_project_files_outrank_loose_images(self, index: Path) -> None:
        # The strongest "I made this" evidence should surface first, and the
        # weights say so out loud rather than being tuned into place.
        assert WEIGHTS["structural"] > WEIGHTS["video"] > WEIGHTS["image"]
        con = connect(index)
        try:
            rows = candidates(con, context=None, limit=10)
        finally:
            con.close()
        assert rows[0]["path"] == "LYON/uno"

    def test_every_row_prints_the_score_it_was_ranked_by(self, index: Path) -> None:
        con = connect(index)
        try:
            rows = candidates(con, context=None, limit=10)
        finally:
            con.close()
        for row in rows:
            assert isinstance(row["score"], float)
            assert row["media"] or row["assets"] == 0

    def test_a_crowded_context_is_worth_more_than_a_lone_one(self) -> None:
        # One declaration in a context of many carries across its neighbours.
        project = {"dimensionality": "2d"}
        alone = score(project, {"image": 1}, siblings=1)
        crowded = score(project, {"image": 1}, siblings=40)
        assert crowded > alone

    def test_the_context_bonus_is_capped(self) -> None:
        project = {"dimensionality": "2d"}
        big = score(project, {"image": 1}, siblings=100)
        huge = score(project, {"image": 1}, siblings=10_000)
        assert big == huge, "an enormous context would drown the media evidence"

    def test_the_dimension_bonus_is_declared_not_invented(self) -> None:
        assert set(DIMENSION_BONUS) <= {"mixto", "3d", "motion", "2d"}
        project = {"dimensionality": "desconocida"}
        assert score(project, {}, siblings=0) == 0.0


class TestSelection:
    def test_a_context_filter_returns_only_that_context(self, index: Path) -> None:
        con = connect(index)
        try:
            rows = candidates(con, context="SOLO", limit=10)
        finally:
            con.close()
        assert rows and all(row["context"] == "SOLO" for row in rows)

    def test_the_limit_is_respected(self, index: Path) -> None:
        con = connect(index)
        try:
            assert len(candidates(con, context=None, limit=2)) == 2
        finally:
            con.close()

    def test_the_order_is_stable_across_runs(self, index: Path) -> None:
        con = connect(index)
        try:
            first = [r["path"] for r in candidates(con, context=None, limit=10)]
            second = [r["path"] for r in candidates(con, context=None, limit=10)]
        finally:
            con.close()
        assert first == second


class TestItReadsWithoutWriting:
    def test_the_index_is_opened_read_only(self, index: Path) -> None:
        con = connect(index)
        try:
            with pytest.raises(sqlite3.OperationalError):
                con.execute("CREATE TABLE intruso (x TEXT)")
        finally:
            con.close()

    def test_a_missing_index_names_what_to_do(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit) as caught:
            connect(tmp_path / "no_existe.sqlite")
        assert "SSD" in str(caught.value) or "--index" in str(caught.value)


class TestCli:
    def test_json_output_declares_the_undeclared_count(
        self, index: Path, capsys
    ) -> None:
        assert main(["--index", str(index), "--json", "--limit", "3"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["projects_total"] == 3
        assert payload["owner_undeclared"] == 3
        assert len(payload["candidates"]) == 3

    def test_the_worksheet_is_written_where_asked(
        self, index: Path, tmp_path: Path, capsys
    ) -> None:
        target = tmp_path / "sub" / "hoja.md"
        assert main(["--index", str(index), "--hoja", str(target)]) == 0
        capsys.readouterr()
        assert target.is_file()
        assert "rol_y_exclusiones" in target.read_text(encoding="utf-8")
