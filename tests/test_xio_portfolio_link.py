import json

from cultura.mak_plataforma import hub


def test_xio_portfolio_link_is_human_and_idempotent(monkeypatch, tmp_path):
    review_path = tmp_path / "human_resolutions.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_TRIANGULATION_REVIEW", str(review_path))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {"id": item_id})
    monkeypatch.setattr(hub, "_portfolio_xio_evidence", lambda: {
        "available": True,
        "work": {"work_id": "xio:show:test"},
        "segments": [{"segment_id": "xio:test:cue:1"}],
    })

    result = hub._portfolio_xio_link({
        "work_id": "xio:show:test",
        "source_id": "portfolio-piece",
        "segment_id": "xio:test:cue:1",
    })

    assert result["ok"] is True
    assert result["already_linked"] is False
    assert result["resolution"]["schema"] == "mak-xio-portfolio-link-v1"
    assert result["resolution"]["promotion"] == "none"

    repeated = hub._portfolio_xio_link({
        "work_id": "xio:show:test",
        "source_id": "portfolio-piece",
        "segment_id": "xio:test:cue:1",
    })

    assert repeated["ok"] is True
    assert repeated["already_linked"] is True
    rows = [json.loads(line) for line in review_path.read_text().splitlines()]
    assert len(rows) == 1


def test_xio_portfolio_link_rejects_unknown_source(monkeypatch, tmp_path):
    monkeypatch.setattr(hub, "PORTFOLIO_TRIANGULATION_REVIEW",
                        str(tmp_path / "human_resolutions.jsonl"))
    monkeypatch.setattr(hub, "_portfolio_item", lambda _item_id: None)
    monkeypatch.setattr(hub, "_portfolio_xio_evidence", lambda: {
        "available": True, "work": {"work_id": "xio:show:test"},
        "segments": [],
    })

    result = hub._portfolio_xio_link({
        "work_id": "xio:show:test", "source_id": "missing-piece"})

    assert result == {"ok": False, "error": "item_no_encontrado"}
