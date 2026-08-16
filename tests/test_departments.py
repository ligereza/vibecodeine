"""Contracts for the three-area MAK hub registry."""
from __future__ import annotations

import json
import sys
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cultura" / "mak_plataforma"))

import hub  # noqa: E402
from src.flujo.departments import (catalog, cultura_opportunity_gate, rd_crosswalk,
                                   rd_cultura_relations, rd_summary)  # noqa: E402


def _json(base: str, path: str) -> tuple[int, dict]:
    request = urllib.request.Request(base + path)
    with urllib.request.urlopen(request, timeout=3) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_all_departments_have_contracts_and_handoffs():
    data = catalog(ROOT)
    assert data["schema"] == "mak-departments-v1"
    assert set(data["areas"]) == {"rd", "cultura", "iskvw"}
    assert all(item["ready"] for item in data["areas"].values())


def test_rd_summary_keeps_empty_runtime_database_separate():
    data = rd_summary(ROOT)
    assert data["databases"]["data/rd.db"]["rows"] > 0
    assert data["databases"]["data/rd_datos.db"]["rows"] == 0


def test_rd_crosswalk_is_validated_and_read_only():
    data = rd_crosswalk(ROOT)
    assert data["status"] == "review_only"
    assert data["mutation"] == "disabled"
    assert len(data["entities"]) == 4
    assert all(item["evidence"] for item in data["entities"])


def test_rd_cultura_relations_preserve_review_candidates():
    data = rd_cultura_relations(ROOT)
    assert data["status"] == "read_only_candidate_graph"
    assert data["mutation"] == "disabled"
    assert any(item["id"] == "openklub" for item in data["producers"])
    assert any(item["relation_type"] == "event_venue" and item["status"] == "review_candidate"
               for item in data["relations"])


def test_cultura_opportunity_gate_is_contract_only():
    data = cultura_opportunity_gate(ROOT)
    assert data["mode"] == "contract_check_only"
    assert data["provider_policy"]["network"] == "not_called"
    assert all(data["components"].values())


def test_hub_serves_area_catalog_and_static_surfaces():
    server = hub.Servidor(("127.0.0.1", 0), hub.H)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:%d" % server.server_address[1]
    try:
        status, payload = _json(base, "/api/departments")
        assert status == 200
        assert payload["areas"]["rd"]["ready"] is True
        status, _ = _json(base, "/api/rd/summary")
        assert status == 200
        status, payload = _json(base, "/api/rd/crosswalk")
        assert status == 200
        assert payload["status"] == "review_only"
        status, payload = _json(base, "/api/rd/cultura-relations")
        assert status == 200
        assert payload["mutation"] == "disabled"
        status, payload = _json(base, "/api/cultura/opportunity-gate")
        assert status == 200
        assert payload["provider_policy"]["network"] == "not_called"
        request = urllib.request.Request(base + "/static/iskvw/editor")
        with urllib.request.urlopen(request, timeout=3) as response:
            assert response.status == 200
            assert b"<!doctype html>" in response.read(512).lower()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
