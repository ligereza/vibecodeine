#!/usr/bin/env python3
"""Portable checks for the MAK activity inventory and Linux GPU seam."""
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "cultura" / "mak_plataforma"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_activity_inventory_groups_execution_path(tmp_path, monkeypatch):
    activity = _load("mak_test_actividad", PLATFORM / "actividad.py")
    monkeypatch.setattr(activity, "ACTIVITY_FILE", str(tmp_path / "activity.jsonl"))
    monkeypatch.setattr(activity, "LOCK_FILE", str(tmp_path / "activity.lock"))

    activity.record("model", "started", trigger="cron:MAK-TRABAJO",
                    caller="mak-research.LLM", queue="research.llm",
                    department="research", provider="watsonx",
                    model="mistral-medium")
    activity.record("model", "finished", trigger="cron:MAK-TRABAJO",
                    caller="mak-research.LLM", queue="research.llm",
                    department="research", provider="watsonx",
                    model="mistral-medium")

    payload = activity.inventory()
    assert payload["schema"] == "mak-activity-inventory-v1"
    assert payload["rows"] == 2
    assert payload["groups"][0]["trigger"] == "cron:MAK-TRABAJO"
    assert payload["groups"][0]["queue"] == "research.llm"
    assert payload["groups"][0]["finished"] == 1


def test_gpu_guard_is_importable_on_director_windows(tmp_path, monkeypatch):
    activity = _load("mak_test_actividad_gpu", PLATFORM / "actividad.py")
    monkeypatch.setattr(activity, "ACTIVITY_FILE", str(tmp_path / "activity.jsonl"))
    monkeypatch.setattr(activity, "LOCK_FILE", str(tmp_path / "activity.lock"))
    sys.modules["actividad"] = activity
    gpu = _load("mak_test_gpu_guard", PLATFORM / "gpu_guard.py")
    monkeypatch.setattr(gpu, "LOCK_FILE", str(tmp_path / "gpu.lock"))
    monkeypatch.setattr(gpu, "STATE_FILE", str(tmp_path / "gpu-state.json"))

    with gpu.slot(caller="test", queue="test.queue", model="test-model",
                  department="test", trigger="test"):
        # Windows has no fcntl; the MAK Linux lock is intentionally a no-op here.
        assert not Path(gpu.STATE_FILE).exists() or Path(gpu.STATE_FILE).is_file()


def test_inventory_rows_are_valid_json(tmp_path, monkeypatch):
    activity = _load("mak_test_actividad_json", PLATFORM / "actividad.py")
    monkeypatch.setattr(activity, "ACTIVITY_FILE", str(tmp_path / "activity.jsonl"))
    monkeypatch.setattr(activity, "LOCK_FILE", str(tmp_path / "activity.lock"))
    activity.record("queue", "finished", trigger="manual", extra={"count": 3})
    line = (tmp_path / "activity.jsonl").read_text(encoding="utf-8").strip()
    assert json.loads(line)["schema"] == "mak-activity-v1"
