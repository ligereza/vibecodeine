from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))
import hub as mak_hub  # noqa: E402

from flujo.web.hub import HubRequestHandler, _project_mak_lineage  # noqa: E402


class _MakHandler:
    path = "/api/azure/lineage"

    def __init__(self):
        self.calls = []

    def _json(self, payload, code=200):
        self.calls.append((payload, code))


def _handler(root: Path) -> HubRequestHandler:
    handler = HubRequestHandler.__new__(HubRequestHandler)
    handler.root = root
    return handler


class _Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def _organismo():
    return {"salud": {"servicios": {}, "productos": {}}, "memoria": {}}


def _lineage():
    return {
        "schema": "mak-azure-ml-learning-lineage-v1",
        "available": True,
        "status": "present",
        "rows": 4,
        "fingerprint_count": 2,
        "statuses": {"accepted": 4},
        "target_kinds": {"tool": 4},
        "dataset_sha256": "a" * 64,
        "mlflow_run_id": "run-123",
        "artifact_upload": "uploaded",
        "source": "/private/prompts.sqlite",
        "prompt": "never forward",
        "unknown": "must disappear",
    }


def test_mak_lineage_route_calls_only_local_adapter(monkeypatch):
    calls = []
    monkeypatch.setattr(mak_hub, "_azure_ml_lineage", lambda: calls.append(True) or _lineage())
    monkeypatch.setattr(mak_hub, "_azure_services_snapshot", lambda: pytest.fail("snapshot called"))
    handler = _MakHandler()

    mak_hub.H.do_GET(handler)

    assert calls == [True]
    assert handler.calls[0][1] == 200
    assert handler.calls[0][0]["status"] == "present"


def test_mak_lineage_route_degrades_without_adapter(monkeypatch):
    monkeypatch.setattr(mak_hub, "_azure_ml_lineage", None)
    handler = _MakHandler()

    mak_hub.H.do_GET(handler)

    assert handler.calls[0][0] == {
        "schema": "mak-azure-ml-learning-lineage-v1",
        "available": False,
        "status": "unavailable",
    }


def test_flujo_lineage_projection_is_allowlisted():
    projected = _project_mak_lineage(_lineage())

    assert projected["rows"] == 4
    assert "source" not in projected
    assert "prompt" not in projected
    assert "unknown" not in projected
    assert projected["dataset_sha256"] == "a" * 64


def test_get_mak_keeps_box_available_when_lineage_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("FLUJO_MAK_URL", "http://mak.test:8900")
    monkeypatch.setenv("FLUJO_MAK_COMMON_LEDGER", str(tmp_path / "common.jsonl"))
    monkeypatch.setenv("FLUJO_MAK_BATCH_LEDGER", str(tmp_path / "batch.jsonl"))

    def fake_urlopen(url, timeout):
        if url.endswith("/api/organismo"):
            return _Response(_organismo())
        raise OSError("lineage offline")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    out = _handler(tmp_path)._get_mak()

    assert out["disponible"] is True
    assert out["azure_ml_lineage"]["status"] == "unavailable"


def test_get_mak_forwards_only_safe_lineage_fields(monkeypatch, tmp_path):
    monkeypatch.setenv("FLUJO_MAK_URL", "http://mak.test:8900")
    monkeypatch.setenv("FLUJO_MAK_COMMON_LEDGER", str(tmp_path / "common.jsonl"))
    monkeypatch.setenv("FLUJO_MAK_BATCH_LEDGER", str(tmp_path / "batch.jsonl"))

    def fake_urlopen(url, timeout):
        return _Response(_organismo() if url.endswith("/api/organismo") else _lineage())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    lineage = _handler(tmp_path)._get_mak()["azure_ml_lineage"]

    assert lineage["status"] == "present"
    assert "source" not in lineage
    assert "prompt" not in lineage
    assert "unknown" not in lineage


def test_mak_panel_has_one_existing_timer_and_lineage_surface():
    source = Path(__file__).parents[1].joinpath("web/src/components/MakPanel.tsx").read_text()
    assert "Azure ML · lineage" in source
    assert source.count("setInterval(") == 1
    assert "fetch('/api/mak')" in source
