"""Regression tests for the Hub/Portafolio maintenance pass."""

from __future__ import annotations

import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cultura" / "mak_plataforma"))

import hub  # noqa: E402


def test_inbox_cache_serializes_concurrent_misses(monkeypatch, tmp_path):
    inbox = tmp_path / "inbox.json"
    inbox.write_text('{"items": []}', encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(inbox))
    monkeypatch.setattr(hub, "_PORTFOLIO_INBOX_CACHE", {})
    calls = 0
    calls_lock = threading.Lock()

    def read_once(*, compact=False):
        nonlocal calls
        with calls_lock:
            calls += 1
        time.sleep(0.02)
        return {"items": [], "compact": compact}

    monkeypatch.setattr(hub, "_portfolio_inbox_uncached", read_once)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: hub._portfolio_inbox(), range(8)))

    assert calls == 1
    assert all(result is results[0] for result in results)


def test_archive_view_cache_reuses_projection_and_invalidates_on_source_change(
    monkeypatch, tmp_path,
):
    archive_path = tmp_path / "datos" / "archivo.json"
    archive_path.parent.mkdir()
    archive_path.write_text('{"version": 1}', encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(tmp_path))
    monkeypatch.setattr(hub, "_PORTFOLIO_ARCHIVE_CACHE", None)
    monkeypatch.setattr(hub, "_read_human_decisions", None)
    monkeypatch.setattr(hub, "_triage_declarations", None)
    calls = []

    def project_view(archive, **_kwargs):
        calls.append(archive["version"])
        return {"version": archive["version"]}

    monkeypatch.setattr(hub, "_project_archive_portfolio_view", project_view)
    monkeypatch.setattr(hub, "_compile_contracurator_exhibition", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(hub, "_validate_archive_portfolio_envelope", lambda _payload: True)

    first, _ = hub._archive_portfolio_view_read_only()
    second, _ = hub._archive_portfolio_view_read_only()
    archive_path.write_text('{"version": 20}', encoding="utf-8")
    third, _ = hub._archive_portfolio_view_read_only()

    assert calls == [1, 20]
    assert first is second
    assert third["version"] == 20


def test_portfolio_read_errors_and_missing_candidates_use_machine_visible_status():
    assert hub._status_for({"error": "inbox_no_disponible"}) == 503
    assert hub._status_for({"ok": False, "error": "item_no_encontrado"}) == 404


def test_portfolio_media_route_reads_existing_files_and_returns_404_for_missing(
    monkeypatch, tmp_path,
):
    media = tmp_path / "media"
    media.mkdir()
    (media / "still.jpg").write_bytes(b"image")
    monkeypatch.setattr(hub, "PORTFOLIO_MEDIA_ROOT", str(media))

    class Handler:
        path = "/portfolio-media/still.jpg"
        do_GET = hub.H.do_GET

        def _send_bytes(self, data, ctype="application/octet-stream", code=200):
            self.response = (data, ctype, code)

        def _send(self, body, ctype="text/html; charset=utf-8", code=200):
            self.response = (body, ctype, code)

    present = Handler()
    present.do_GET()
    missing = Handler()
    missing.path = "/portfolio-media/missing.jpg"
    missing.do_GET()

    assert present.response[0] == b"image"
    assert missing.response[2] == 404


def test_archive_loader_coalesces_inflight_requests_and_drops_repeated_explanation():
    source = (ROOT / "iskvw" / "editor.html").read_text(encoding="utf-8")
    assert "cargarArchivePortfolioView.request" in source
    assert "Esta superficie consulta el Hub en modo lectura." not in source
