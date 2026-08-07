import json

from cultura.mak_plataforma import revision


def test_revision_marca_decision_sin_sobrescribir(monkeypatch, tmp_path):
    root = tmp_path / "review"
    sheets = tmp_path / "sheets"
    root.mkdir()
    sheets.mkdir()
    (root / "123_mp4").mkdir()
    (root / "123_mp4" / "result.json").write_text(
        json.dumps({"status": "revise", "review": {"verdict": "revise"}}),
        encoding="utf-8")
    (sheets / "123.jpg").write_bytes(b"jpg")
    monkeypatch.setattr(revision, "ROOT", root)
    monkeypatch.setattr(revision, "SHEETS", sheets)
    monkeypatch.setattr(revision, "REVIEWS", root / "human_reviews.jsonl")

    result = revision.record("123_mp4", "accept", "verificado")
    assert result["ok"] is True
    assert revision.api()["pending_human"] == 0
    assert revision.media_path("/123.jpg") == sheets / "123.jpg"


def test_revision_rechaza_traversal_y_decision_invalida(tmp_path, monkeypatch):
    monkeypatch.setattr(revision, "ROOT", tmp_path / "review")
    monkeypatch.setattr(revision, "SHEETS", tmp_path / "sheets")
    assert revision.media_path("/../secret.jpg") is None
    assert revision.record("123_mp4", "publicar")["ok"] is False


def test_revision_no_duplica_doble_click(monkeypatch, tmp_path):
    root = tmp_path / "review"
    root.mkdir()
    monkeypatch.setattr(revision, "ROOT", root)
    monkeypatch.setattr(revision, "REVIEWS", root / "human_reviews.jsonl")
    assert revision.record("123_mp4", "reject")["ok"] is True
    result = revision.record("123_mp4", "reject")
    assert result["duplicate"] is True
    assert len((root / "human_reviews.jsonl").read_text().splitlines()) == 1
