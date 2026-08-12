"""Tests for the append-only human decision-draft workflow."""

import json
import threading
import urllib.error
import urllib.request

from cultura.mak_plataforma import contrato_archivo, hub


def _install_portfolio_files(monkeypatch, tmp_path):
    items = [
        {
            "id": "a",
            "tipo_contenido": "video",
            "fecha": "2026-01-01",
            "asset_path": "/media/a.mp4",
            "asset_available": True,
            "descripcion_original": "source a",
        },
        {
            "id": "b",
            "tipo_contenido": "video",
            "fecha": "2026-01-02",
            "asset_path": "/media/b.mp4",
            "asset_available": True,
            "descripcion_original": "source b",
        },
    ]
    inbox = tmp_path / "inbox.json"
    inbox.write_text(json.dumps({"items": items}), encoding="utf-8")
    paths = {
        "PORTFOLIO_INBOX": inbox,
        "PORTFOLIO_SELECTIONS": tmp_path / "selections.jsonl",
        "PORTFOLIO_CLASSIFICATIONS": tmp_path / "classifications.jsonl",
        "PORTFOLIO_DRAFTS": tmp_path / "drafts.jsonl",
        "PORTFOLIO_FEEDBACK": tmp_path / "feedback.jsonl",
        "PORTFOLIO_CONNECTIONS": tmp_path / "connections.jsonl",
        "COMMON_LEDGER": tmp_path / "ledger.jsonl",
    }
    for name, path in paths.items():
        monkeypatch.setattr(hub, name, str(path))
    monkeypatch.setattr(hub, "_ledger", None)
    return items, paths


def _draft_body():
    return {
        "item_id": "a",
        "session_id": "test-session",
        "action": "discard",
        "fields": {
            "triage": "discard",
            "lane": "rd",
            "purpose": "expression",
            "context_kind": "event",
            "context_value": "test event",
        },
        "context_fields": {"event": ["test event"]},
        "relations": [{
            "target_id": "b",
            "decision": "accept",
            "facet": "obra",
            "relation": "same_work",
            "note": "same source context",
        }],
        "note": "human note",
    }


def _http_json(url, payload=None):
    data = None
    headers = {}
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def test_draft_keeps_complete_content_without_changing_current_state(
        monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)

    result = hub._portfolio_draft(_draft_body())

    assert result["ok"] is True
    assert result["draft"]["status"] == "saved"
    assert result["draft"]["fields"]["context_value"] == "test event"
    assert result["draft"]["context_fields"] == {"event": ["test event"]}
    assert result["draft"]["relations"][0]["target_id"] == "b"
    assert not (tmp_path / "selections.jsonl").exists()
    assert not (tmp_path / "classifications.jsonl").exists()
    assert hub._portfolio_item("a")["selection"] == "pendiente"


def test_related_piece_uses_the_same_complete_draft_shape(
        monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)
    body = _draft_body()
    body["item_id"] = "b"
    body["relations"][0]["target_id"] = "a"

    result = hub._portfolio_draft(body)

    assert result["ok"] is True
    assert result["draft"]["item_id"] == "b"
    assert result["draft"]["fields"]["context_kind"] == "event"
    assert result["draft"]["context_fields"] == {"event": ["test event"]}
    assert result["draft"]["relations"][0]["target_id"] == "a"
    assert hub._portfolio_item("b")["selection"] == "pendiente"


def test_commit_requires_explicit_confirmation(monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)
    draft = hub._portfolio_draft(_draft_body())["draft"]

    result = hub._portfolio_commit({**_draft_body(), "draft_id": draft["draft_id"]})

    assert result == {"ok": False, "error": "human_confirmation_required"}
    assert not (tmp_path / "selections.jsonl").exists()
    assert not (tmp_path / "classifications.jsonl").exists()
    assert not (tmp_path / "feedback.jsonl").exists()


def test_cancel_appends_terminal_event_without_applying_or_erasing_history(
        monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)
    body = _draft_body()
    saved = hub._portfolio_draft(body)["draft"]

    cancelled = hub._portfolio_draft({**body, "cancel": True})

    assert cancelled["ok"] is True
    assert cancelled["draft"]["status"] == "cancelled"
    assert hub._portfolio_item("a")["selection"] == "pendiente"
    assert not (tmp_path / "selections.jsonl").exists()
    assert [row["status"] for row in hub._portfolio_draft_history("a")] == [
        saved["status"], "cancelled"
    ]


def test_confirmed_commit_applies_all_parts_and_is_idempotent(
        monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)
    body = _draft_body()
    draft = hub._portfolio_draft(body)["draft"]
    commit_body = {**body, "draft_id": draft["draft_id"], "confirmed": True}

    result = hub._portfolio_commit(commit_body)
    duplicate = hub._portfolio_commit(commit_body)
    item = hub._portfolio_item("a")

    assert result["ok"] is True
    assert duplicate["duplicate"] is True
    assert item["selection"] == "descartar"
    assert item["classification"]["triage"] == "discard"
    assert hub._portfolio_feedback()[-1]["action"] == "accept"
    assert hub._portfolio_drafts()["a"]["status"] == "committed"
    assert len(hub._portfolio_selection_history("a")) == 1
    assert len(hub._portfolio_classification_history("a")) == 2
    assert len(hub._portfolio_feedback()) == 1


def test_relation_undo_requires_internal_path_and_restores_candidate(
        monkeypatch, tmp_path):
    items, _ = _install_portfolio_files(monkeypatch, tmp_path)
    body = _draft_body()
    draft = hub._portfolio_draft(body)["draft"]
    hub._portfolio_commit({**body, "draft_id": draft["draft_id"], "confirmed": True})

    direct = hub._portfolio_feedback_record({
        "source_id": "a", "target_id": "b", "action": "undo",
        "facet": "obra", "relation": "same_work",
    })
    undone = hub._portfolio_undo({
        "item_id": "a", "target_id": "b", "facet": "obra",
        "relation": "same_work", "scope": "relation", "confirmed": True,
    })
    source = hub._portfolio_item("a")
    scene = contrato_archivo.mesa_scene(
        source, [hub._portfolio_item(item["id"]) for item in items], [{
            "item_id": "b", "facets": ["obra"],
            "relation_type": "same_work",
            "feedback_channels": hub._portfolio_feedback(),
        }], limit=4)

    assert direct == {"ok": False, "error": "human_confirmation_required"}
    assert undone["ok"] is True
    assert undone["results"]["relation"]["feedback"]["action"] == "undo"
    assert scene["relations"][0]["status"] == "candidate"
    assert hub._portfolio_drafts()["a"]["status"] == "undone"


def test_undo_restores_previous_selection_and_classification_without_deleting(
        monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)
    body = _draft_body()
    draft = hub._portfolio_draft(body)["draft"]
    hub._portfolio_commit({**body, "draft_id": draft["draft_id"], "confirmed": True})

    undone = hub._portfolio_undo({
        "item_id": "a", "scope": "all", "confirmed": True,
    })
    repeated = hub._portfolio_undo({
        "item_id": "a", "scope": "all", "confirmed": True,
    })
    item = hub._portfolio_item("a")

    assert undone["ok"] is True
    assert item["selection"] == "deseleccionar"
    assert item["classification"] == {}
    assert repeated == {"ok": False, "error": "nothing_to_undo"}
    assert len(hub._portfolio_selection_history("a")) == 2
    assert len(hub._portfolio_classification_history("a")) == 3
    assert hub._portfolio_drafts()["a"]["status"] == "undone"


def test_partial_commit_can_retry_failed_relation_without_repeating_history(
        monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)
    body = _draft_body()
    draft = hub._portfolio_draft(body)["draft"]
    original = hub._portfolio_feedback_record
    calls = {"count": 0}

    def fail_once(payload, internal=False):
        calls["count"] += 1
        if calls["count"] == 1:
            return {"ok": False, "error": "temporary_feedback_failure"}
        return original(payload, internal=internal)

    monkeypatch.setattr(hub, "_portfolio_feedback_record", fail_once)
    first = hub._portfolio_commit({
        **body, "draft_id": draft["draft_id"], "confirmed": True,
    })
    second = hub._portfolio_commit({
        **body, "draft_id": draft["draft_id"], "confirmed": True,
    })

    assert first["ok"] is False
    assert first["partial"] is True
    assert second["ok"] is True
    assert second.get("duplicate") is not True
    assert hub._portfolio_drafts()["a"]["status"] == "committed"
    assert len(hub._portfolio_selection_history("a")) == 1
    assert len(hub._portfolio_feedback()) == 1


def test_http_route_enforces_gate_and_preserves_audit(monkeypatch, tmp_path):
    _install_portfolio_files(monkeypatch, tmp_path)
    server = hub.Servidor(("127.0.0.1", 0), hub.H)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    root = "http://127.0.0.1:%d" % server.server_port
    try:
        body = _draft_body()
        status, saved = _http_json(root + "/api/portfolio/draft", body)
        assert status == 200
        assert saved["draft"]["status"] == "saved"

        commit = {**body, "draft_id": saved["draft"]["draft_id"]}
        status, denied = _http_json(root + "/api/portfolio/commit", commit)
        assert status == 200
        assert denied == {"ok": False, "error": "human_confirmation_required"}
        assert hub._portfolio_item("a")["selection"] == "pendiente"

        status, committed = _http_json(
            root + "/api/portfolio/commit", {**commit, "confirmed": True})
        assert status == 200
        assert committed["ok"] is True
        assert committed["item"]["selection"] == "descartar"

        status, undone = _http_json(root + "/api/portfolio/undo", {
            "item_id": "a", "scope": "all", "confirmed": True,
        })
        assert status == 200
        assert undone["ok"] is True
        assert undone["item"]["selection"] == "deseleccionar"

        status, audit = _http_json(root + "/api/portfolio/audit?source_id=a")
        assert status == 200
        assert audit["ok"] is True
        assert audit["counts"]["selection_history"]["total"] == 2
        assert audit["counts"]["draft_history"]["total"] >= 3
    finally:
        server.shutdown()
        thread.join(timeout=3)
