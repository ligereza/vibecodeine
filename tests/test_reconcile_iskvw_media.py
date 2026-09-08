"""Tests for the read-only archive/media reconciliation contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.reconcile_iskvw_media import ReconciliationError, reconcile


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    archive = tmp_path / "archivo.json"
    archive.write_text(json.dumps({"piezas": [
        {"id": "00abc-123456789", "medio": {"src": "posts/123456789.jpg"}},
        {"id": "987654321", "medio": {"src": "reels/987654321.mp4"}},
        {"id": "obra-sin-media-id"},
    ]}), encoding="utf-8")
    media = tmp_path / "media"
    (media / "posts" / "202401").mkdir(parents=True)
    (media / "reels" / "202402").mkdir(parents=True)
    (media / "_contact_sheets").mkdir()
    (media / "posts" / "202401" / "123456789.jpg").write_bytes(b"post")
    (media / "_contact_sheets" / "123456789.contact.jpg").write_bytes(b"sheet")
    (media / "reels" / "202402" / "987654321.mp4").write_bytes(b"reel")
    (media / "posts" / "202401" / "not-an-id.jpg").write_bytes(b"ignore")
    return archive, media


def test_reconcile_separates_primary_and_contact_sheet(tmp_path: Path) -> None:
    archive, media = _fixture(tmp_path)
    before_archive = archive.read_bytes()
    report = reconcile(archive, media)
    assert report["schema"] == "mak-iskvw-media-reconciliation-v1"
    assert report["read_only"] is True
    summary = report["summary"]
    assert summary["archive_numeric_ids"] == 2
    assert summary["archive_records_with_numeric_id"] == 2
    assert summary["archive_records_without_numeric_id"] == 1
    assert summary["ids_with_one_surface"] == 1
    assert summary["ids_with_cross_surface_collision"] == 1
    assert summary["orphan_ids"] == 0
    assert report["cross_surface_collisions"][0]["id"] == "123456789"
    assert archive.read_bytes() == before_archive


def test_contact_suffix_is_the_same_id_but_not_the_same_surface(tmp_path: Path) -> None:
    archive, media = _fixture(tmp_path)
    report = reconcile(archive, media)
    rows = report["matches"]["123456789"]
    assert {row["surface"] for row in rows} == {"posts", "_contact_sheets"}
    assert any(row["derivative"] for row in rows)
    assert report["matches"]["987654321"][0]["yyyymm"] == "202402"


def test_missing_sources_fail_closed(tmp_path: Path) -> None:
    archive, media = _fixture(tmp_path)
    with pytest.raises(ReconciliationError, match="media_root_missing"):
        reconcile(archive, tmp_path / "gone")
    with pytest.raises(ReconciliationError, match="archive_unreadable"):
        reconcile(tmp_path / "gone.json", media)


def test_the_medium_src_wins_over_the_composite_record_id(tmp_path: Path) -> None:
    """The regression that made the first run return zero matches.

    Reading ``piezas[].id`` directly found nothing, because the real archive
    stores a composite id (twelve hex characters, a dash, then the media id) and
    the media id also lives in ``medio.src``. The fixture in ``_fixture`` only
    exercises that by accident: its composite tail is nine digits, one short of
    the ten the suffix pattern requires, so the fallback fails for the wrong
    reason. Here the two disagree on purpose, so precedence is pinned rather
    than inferred.
    """
    archive = tmp_path / "archivo.json"
    archive.write_text(json.dumps({"piezas": [
        {"id": "00dfbf29763b-99999999999999999",
         "medio": {"src": "posts/17963390141716156.mp4"}},
    ]}), encoding="utf-8")
    media = tmp_path / "media"
    (media / "posts").mkdir(parents=True)
    (media / "posts" / "17963390141716156.mp4").write_bytes(b"work")
    (media / "posts" / "99999999999999999.mp4").write_bytes(b"decoy")

    report = reconcile(archive, media)
    assert report["summary"]["archive_numeric_ids"] == 1
    assert list(report["matches"]) == ["17963390141716156"], (
        "the composite record id was preferred over medio.src")
    assert report["summary"]["orphan_ids"] == 0


def test_a_real_composite_id_alone_still_resolves(tmp_path: Path) -> None:
    """When medio.src is absent, the composite tail is the only key left.

    Measured on the live archive: 1807 of 2034 pieces carry no ``medio.src`` at
    all, so this path is not a corner case -- it is the majority.
    """
    archive = tmp_path / "archivo.json"
    archive.write_text(json.dumps({"piezas": [
        {"id": "00dfbf29763b-17963390141716156"},
    ]}), encoding="utf-8")
    media = tmp_path / "media"
    (media / "stories" / "202409").mkdir(parents=True)
    (media / "stories" / "202409" / "17963390141716156.jpg").write_bytes(b"story")

    report = reconcile(archive, media)
    assert report["summary"]["archive_records_with_numeric_id"] == 1
    assert report["matches"]["17963390141716156"][0]["surface"] == "stories"
    assert report["matches"]["17963390141716156"][0]["yyyymm"] == "202409"


def test_a_record_with_no_media_id_abstains_instead_of_being_coerced(
        tmp_path: Path) -> None:
    """216 live records are named by hand and have no media id at all.

    Those are the only pieces in the archive that carry a human title, a date
    and the author's own sentence, so guessing an id for them would attach the
    strongest records to the wrong file.
    """
    archive = tmp_path / "archivo.json"
    archive.write_text(json.dumps({"piezas": [
        {"id": "vola", "titulo": "VOLA", "medio": {"src": "assets/works/vola-vaso.svg"}},
        {"id": "obra-2026", "titulo": "otra"},
    ]}), encoding="utf-8")
    media = tmp_path / "media"
    (media / "posts").mkdir(parents=True)

    report = reconcile(archive, media)
    assert report["summary"]["archive_records_without_numeric_id"] == 2
    assert report["summary"]["archive_numeric_ids"] == 0
    assert report["matches"] == {}
    assert report["summary"]["orphan_ids"] == 0, (
        "a record with no id is not an orphan id; it never had one")


def test_the_report_is_the_only_thing_written(tmp_path: Path) -> None:
    from tools.reconcile_iskvw_media import main

    archive, media = _fixture(tmp_path)
    before = {path: path.read_bytes() for path in sorted(media.rglob("*"))
              if path.is_file()}
    before[archive] = archive.read_bytes()
    out = tmp_path / "nested" / "report.json"

    assert main(["--archive", str(archive), "--media-root", str(media),
                 "--output", str(out)]) == 0
    assert out.is_file()
    assert json.loads(out.read_text(encoding="utf-8"))["schema"] == (
        "mak-iskvw-media-reconciliation-v1")
    for path, content in before.items():
        assert path.read_bytes() == content, f"{path} was modified"
