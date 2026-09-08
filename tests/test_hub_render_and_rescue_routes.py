#!/usr/bin/env python3
"""tests/test_hub_render_and_rescue_routes.py -- two GET routes with zero
witnesses anywhere in the suite before this file: /api/render (backed by
_render_estado, which merges the render bridge state with data extracted
from curatoria's fichas) and /api/research/rescue (backed by
_legacy_rescue_queue). Grepped tests/*.py for _render_estado,
_legacy_rescue_queue and both literal paths first; none appeared.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


class FakeHandler:
    def __init__(self, path):
        self.path = path
        self.rfile = io.BytesIO(b"")
        self.headers = {}
        self.calls = []

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    @property
    def last(self):
        return self.calls[-1]


def _get(path):
    handler = FakeHandler(path)
    hub.H.do_GET(handler)
    _, payload, code = handler.last
    return payload, code


class TestRenderEstadoRoute:
    def test_separates_done_pieces_from_pending_ones_across_both_shapes(
            self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "RENDER_CONFIG", str(tmp_path / "render_config.json"))
        monkeypatch.setattr(hub, "HOME", str(tmp_path))
        puente = tmp_path / "plataforma" / "puente_issues_estado.json"
        puente.parent.mkdir(parents=True)
        puente.write_text(json.dumps({"hechos": {
            # old shape: a single link directly on the issue
            "101": {"ts": "2026-08-01T00:00:00", "url": "http://x/a", "ok": True,
                    "destino": "instagram", "en_departamento": None},
            # new shape: several pieces under one issue, one done, one not
            "102": {"ts": "2026-08-02T00:00:00", "piezas": [
                {"url": "http://x/b", "ok": True, "destino": "tiktok",
                 "en_departamento": None},
                {"url": "http://x/c", "ok": False, "destino": "tiktok",
                 "en_departamento": None},
            ]},
        }}), encoding="utf-8")
        monkeypatch.setattr(hub, "PUENTE_ESTADO", str(puente))

        payload, code = _get("/api/render")

        assert code == 200
        assert len(payload["hechos"]) == 2
        assert len(payload["pendientes"]) == 1
        assert payload["pendientes"][0]["url"] == "http://x/c"
        # most recent issue (102) sorts first
        assert payload["hechos"][0]["issue"] == "102"
        assert payload["pendientes_bandeja"] == 0

    def test_missing_bridge_state_reports_an_empty_queue_not_an_error(
            self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "RENDER_CONFIG", str(tmp_path / "render_config.json"))
        monkeypatch.setattr(hub, "HOME", str(tmp_path))
        monkeypatch.setattr(hub, "PUENTE_ESTADO", str(tmp_path / "does-not-exist.json"))

        payload, code = _get("/api/render")

        assert code == 200
        assert payload["hechos"] == []
        assert payload["pendientes"] == []

    def test_counts_pending_jpg_inbox_and_ignores_other_extensions(
            self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "RENDER_CONFIG", str(tmp_path / "render_config.json"))
        monkeypatch.setattr(hub, "HOME", str(tmp_path))
        monkeypatch.setattr(hub, "PUENTE_ESTADO", str(tmp_path / "does-not-exist.json"))
        bandeja = tmp_path / "RD" / "desde_issues"
        bandeja.mkdir(parents=True)
        (bandeja / "a.JPG").write_bytes(b"")
        (bandeja / "b.jpg").write_bytes(b"")
        (bandeja / "c.txt").write_bytes(b"")

        payload, code = _get("/api/render")

        assert code == 200
        assert payload["pendientes_bandeja"] == 2


class TestLegacyRescueQueueRoute:
    def test_maps_each_decision_to_its_next_action(self, tmp_path, monkeypatch):
        review = tmp_path / "RESCUE_ADJUDICATED.json"
        review.write_text(json.dumps({
            "schema": "mak-rescue-review-v1",
            "counts": {"total": 3},
            "items": [
                {"work_id": "a", "decision": "rescue"},
                {"work_id": "b", "decision": "review"},
                {"work_id": "c", "decision": "retire_without_deleting"},
            ],
        }), encoding="utf-8")
        monkeypatch.setattr(hub, "LEGACY_RESCUE_REVIEW", str(review))

        payload, code = _get("/api/research/rescue")

        assert code == 200
        assert payload["status"] == "candidate_only"
        actions = {item["work_id"]: item["next_action"] for item in payload["items"]}
        assert actions == {
            "a": "rescatar_con_revision_humana",
            "b": "revisar_manual",
            "c": "retirar_sin_borrar",
        }
        assert payload["counts"] == {"total": 3}

    def test_unclassified_decision_falls_back_to_manual_review(self, tmp_path, monkeypatch):
        review = tmp_path / "RESCUE_ADJUDICATED.json"
        review.write_text(json.dumps({"items": [
            {"work_id": "z", "decision": "something_new"}]}), encoding="utf-8")
        monkeypatch.setattr(hub, "LEGACY_RESCUE_REVIEW", str(review))

        payload, code = _get("/api/research/rescue")

        assert payload["items"][0]["next_action"] == "revisar_manual"

    def test_missing_review_file_reports_unavailable_not_an_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "LEGACY_RESCUE_REVIEW", str(tmp_path / "missing.json"))

        payload, code = _get("/api/research/rescue")

        assert code == 200
        assert payload == {"schema": "mak-rescue-review-v1", "status": "unavailable",
                           "items": [], "counts": {"total": 0}}
