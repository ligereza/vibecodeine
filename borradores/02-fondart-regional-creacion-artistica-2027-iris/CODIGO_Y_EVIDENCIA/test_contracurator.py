from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from flujo.knowledge.contracurator import (
    ContracuratorError,
    EPISODE_SCHEMA,
    SCHEMA,
    compile_contracurator_exhibition,
    record_contracurator_episode,
    validate_contracurator_exhibition,
)
from flujo.knowledge.product_view import project_archive_portfolio_view
from flujo.knowledge.project_ir import LearningStore, build_project_ir


ROOT = Path(__file__).resolve().parents[1]
REAL_ARCHIVE = ROOT / "iskvw" / "datos" / "archivo.json"


def _real_archive() -> dict:
    if not REAL_ARCHIVE.is_file():
        pytest.skip("requires the generated physical iskvw archive")
    return json.loads(REAL_ARCHIVE.read_text(encoding="utf-8"))


def _view() -> dict:
    return project_archive_portfolio_view(_real_archive(), max_items_per_format=24)


def test_real_visible_56_produces_one_falsifiable_exhibition() -> None:
    view = _view()
    original = copy.deepcopy(view)

    result = compile_contracurator_exhibition(view)

    assert result["schema"] == SCHEMA
    assert result["input"]["visible_item_count"] == 56
    assert result["status"] == "survived"
    assert validate_contracurator_exhibition(result) is True
    assert len(result["theses"]) == 3
    assert [row["assessment"]["status"] for row in result["theses"]].count("defeated") == 2
    exhibition = result["result"]["exhibition"]
    assert 8 <= len(exhibition["source_refs"]) <= 12
    assert len(exhibition["source_refs"]) == len(set(exhibition["source_refs"]))
    assert all(row["source_ref"] in exhibition["source_refs"] for row in exhibition["why_in"])
    assert all(row["relation_refs"] and row["contextual_reason"] for row in exhibition["why_in"])
    assert all(row["source_ref"] for row in exhibition["why_out"])
    assert exhibition["alternative_version"]["status"] == "abstain_not_exhibition"
    assert result["product_episode"]["schema"] == EPISODE_SCHEMA
    assert result["product_episode"]["control"]["database_write"] is False
    assert view == original


def test_typed_context_is_a_real_survival_gate() -> None:
    archive = _real_archive()
    archive["vinculos"] = [row for row in archive["vinculos"] if row["clase"] != "etiqueta"]
    view = project_archive_portfolio_view(archive, max_items_per_format=24)
    # The input remains a valid archive view after the source relations are
    # removed. The contracurator must abstain rather than use titles or routes
    # as a fallback.
    result = compile_contracurator_exhibition(view)

    assert result["status"] == "abstain"
    boundary = result["theses"][0]
    assert boundary["assessment"]["status"] == "defeated"
    assert "declared_selection_missing_typed_context" in boundary["assessment"]["rejection_reasons"]
    assert result["result"]["exhibition"] is None


def test_defeated_theses_expose_their_own_forbidden_shortcuts() -> None:
    result = compile_contracurator_exhibition(_view())
    by_id = {row["thesis_id"]: row for row in result["theses"]}

    operation = by_id["thesis:operation-as-work"]
    observed = by_id["thesis:observed-image-identity"]
    assert "typed_derivation_relation_missing" in operation["assessment"]["rejection_reasons"]
    assert operation["assessment"]["derived_as_independent_work"] is True
    assert "depends_on_name_route_or_authorship" in observed["assessment"]["rejection_reasons"]
    assert observed["assessment"]["name_route_authorship_dependency"] is True
    assert all(8 <= len(row["source_refs"]) <= 12 for row in result["theses"])


def test_episode_records_through_existing_store_only_when_project_exists(tmp_path: Path) -> None:
    exhibition = compile_contracurator_exhibition(_view())
    database = tmp_path / "learning.db"
    store = LearningStore(database)
    project = build_project_ir(
        project_id="iskvw-contracurator-test",
        title="ISKVW contracurator test",
        source_root="iskvw/datos/archivo.json",
        artifacts=[],
        domains=("curatoria",),
        purpose="test existing learning store mapping",
        state="review_required",
        evidence=[],
        unknowns=[],
        relations=[],
        source_kind="archive_view",
        source_ref="iskvw/datos/archivo.json",
    )
    store.save_project(project)

    episode_id = record_contracurator_episode(
        store, exhibition, project_id=project["project_id"],
        code_commit="a" * 40, tool_versions={"contracurator": SCHEMA},
    )
    same_id = record_contracurator_episode(
        store, exhibition, project_id=project["project_id"],
        code_commit="a" * 40, tool_versions={"contracurator": SCHEMA},
    )

    assert same_id == episode_id
    with store.connect() as con:
        row = con.execute(
            "SELECT action_json,observation_json,outcome_json,status FROM project_episodes WHERE episode_id=?",
            (episode_id,),
        ).fetchone()
    assert row is not None and row[3] == "needs_evidence"
    assert json.loads(row[0])["candidate_thesis_ids"] == [
        "thesis:declared-boundary", "thesis:operation-as-work", "thesis:observed-image-identity",
    ]
    assert json.loads(row[1])["theses"][1]["assessment"]["status"] == "defeated"
    assert json.loads(row[2])["status"] == "survived"


def test_recording_requires_existing_project_and_complete_code_provenance(tmp_path: Path) -> None:
    exhibition = compile_contracurator_exhibition(_view())
    with pytest.raises(ContracuratorError, match="code_provenance_incomplete"):
        record_contracurator_episode(
            LearningStore(tmp_path / "learning.db"), exhibition,
            project_id="missing", code_commit="a" * 40,
        )
