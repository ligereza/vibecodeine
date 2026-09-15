"""Contracts for the explicit Portafolio/IRIS corpus bridge."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.mak


ROOT = Path(__file__).resolve().parents[1]


def _load_hub():
    name = "hub_portfolio_iris_context_test"
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "cultura" / "mak_plataforma" / "hub.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _prepare(hub, tmp_path, monkeypatch):
    inbox = tmp_path / "PORTFOLIO_INBOX.json"
    inbox.write_text(json.dumps({
        "schema": "faro-portfolio-inbox-v1",
        "items": [
            {"id": "work-a.jpg", "tipo_contenido": "image",
             "asset_path": "/portfolio-media/series/a/work-a.jpg",
             "asset_available": True},
            {"id": "work-b.jpg", "tipo_contenido": "image",
             "asset_path": "/portfolio-media/series/b/work-b.jpg",
             "asset_available": True},
        ],
    }), encoding="utf-8")
    feedback = tmp_path / "copilot_feedback.jsonl"
    feedback.write_text(json.dumps({
        "source_id": "work-a.jpg", "target_id": "work-b.jpg",
        "action": "accept", "facet": "text", "relation": "shared_concept",
    }) + "\n", encoding="utf-8")
    empty = {
        "PORTFOLIO_SELECTIONS": tmp_path / "selections.jsonl",
        "PORTFOLIO_CLASSIFICATIONS": tmp_path / "classifications.jsonl",
        "PORTFOLIO_DRAFTS": tmp_path / "drafts.jsonl",
        "PORTFOLIO_VISION": tmp_path / "vision.jsonl",
        "PORTFOLIO_CONNECTIONS": tmp_path / "connections.jsonl",
        "PORTFOLIO_FEEDBACK": feedback,
    }
    monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(inbox))
    for name, path in empty.items():
        monkeypatch.setattr(hub, name, str(path))
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(tmp_path))
    hub._PORTFOLIO_INBOX_CACHE.clear()


def test_context_declares_membership_without_inventing_authorship(tmp_path, monkeypatch):
    hub = _load_hub()
    _prepare(hub, tmp_path, monkeypatch)
    monkeypatch.setenv("MAK_PORTFOLIO_ARTIST_ID", "artist-supplied")
    monkeypatch.setenv("MAK_PORTFOLIO_CORPUS_ID", "corpus-supplied")

    context = hub._portfolio_context()
    source = hub._portfolio_source_envelope(hub._portfolio_item("work-a.jpg"))

    assert context["artist_id"] == "artist-supplied"
    assert context["corpus_id"] == "corpus-supplied"
    assert context["membership"]["authorship_claim"] is False
    assert source["relative_path"] == "series/a/work-a.jpg"
    assert source["folder"] == "series/a"
    assert source["subfolders"] == ["series", "a"]


def test_research_candidates_use_confirmed_relations_and_keep_human_gate(
    tmp_path, monkeypatch,
):
    hub = _load_hub()
    _prepare(hub, tmp_path, monkeypatch)

    payload = hub._portfolio_research_candidates()

    assert payload["schema"] == "faro-portfolio-research-candidates-v1"
    assert payload["confirmed_edge_count"] == 1
    assert [row["item_id"] for row in payload["items"]] == [
        "work-a.jpg", "work-b.jpg"]
    assert all(row["research_ready"] is False for row in payload["items"])
    assert payload["policy"]["automatic_dispatch"] is False


def test_dispatch_research_links_existing_plan_and_codex_queue(
    tmp_path, monkeypatch,
):
    hub = _load_hub()
    _prepare(hub, tmp_path, monkeypatch)
    monkeypatch.setattr(hub, "_portfolio_research_job_for",
                        lambda _item_id, _question: None)
    monkeypatch.setattr(hub, "_create_research_job",
                        lambda body: {"ok": True, "id": 17,
                                      "domain": body.get("domain") or "general"})
    links = []
    monkeypatch.setattr(hub, "_link_portfolio_research_job",
                        lambda job_id, source: links.append((job_id, source)) or {
                            "id": 3, "type": "portfolio_research_source"})
    queued = []
    monkeypatch.setattr(hub, "_enqueue_portfolio_codex",
                        lambda task: queued.append(task) or {"ok": True, "queued": True,
                                                              "duplicate": False})

    research = hub._portfolio_dispatch({
        "item_id": "work-a.jpg", "depto": "research",
        "texto": "Explorar su relación cultural.",
    })
    codex = hub._portfolio_dispatch({
        "item_id": "work-a.jpg", "depto": "codex",
        "texto": "Probar una herramienta visual.",
    })

    assert research["ok"] is True
    assert research["status"] == "planned"
    assert research["dispatch"] is False
    assert research["source"]["source_id"] == "work-a.jpg"
    assert links[0][0] == 17
    assert codex["ok"] is True
    assert codex["status"] == "queued"
    assert queued[0]["source"]["relative_path"] == "series/a/work-a.jpg"


def test_research_dispatch_persists_typed_link_in_existing_registry(
    tmp_path, monkeypatch,
):
    hub = _load_hub()
    _prepare(hub, tmp_path, monkeypatch)
    registry = tmp_path / "research" / "registry.sqlite"
    monkeypatch.setattr(hub, "_research_registry_path", lambda: registry)

    result = hub._portfolio_dispatch({
        "item_id": "work-a.jpg", "depto": "research",
        "texto": "Investigar la textura y su contexto cultural.",
    })
    job = hub._research_job(result["id"])

    assert result["ok"] is True
    assert result["status"] == "planned"
    assert any(row["type"] == "portfolio_research_source"
               and row["from"] == "portfolio:item:work-a.jpg"
               for row in job["job"]["relations"])


def test_legacy_map_route_reuses_the_real_gtm_map(tmp_path, monkeypatch):
    hub = _load_hub()
    _prepare(hub, tmp_path, monkeypatch)

    class Handler:
        path = "/api/portfolio/copilot/map?width=8&height=6"
        rfile = io.BytesIO()
        headers = {}

        def _json(self, payload, code=200):
            self.payload = payload
            self.code = code

    handler = Handler()
    hub.H.do_GET(handler)

    assert handler.code == 200
    assert handler.payload["context"]["schema"] == "faro-portfolio-corpus-context-v1"
    assert handler.payload["items"]
    assert handler.payload["engine"] == "elastic_latent_grid"
