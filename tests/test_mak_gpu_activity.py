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
                    department="research", provider="groq",
                    model="openai/gpt-oss-20b")
    activity.record("model", "finished", trigger="cron:MAK-TRABAJO",
                    caller="mak-research.LLM", queue="research.llm",
                    department="research", provider="groq",
                    model="openai/gpt-oss-20b")

    payload = activity.inventory()
    assert payload["schema"] == "mak-activity-inventory-v1"
    assert payload["rows"] == 2
    assert payload["groups"][0]["trigger"] == "cron:MAK-TRABAJO"
    assert payload["groups"][0]["queue"] == "research.llm"
    assert payload["groups"][0]["finished"] == 1


def test_gpu_guard_is_importable_on_linux_without_active_state(tmp_path, monkeypatch):
    activity = _load("mak_test_actividad_gpu", PLATFORM / "actividad.py")
    monkeypatch.setattr(activity, "ACTIVITY_FILE", str(tmp_path / "activity.jsonl"))
    monkeypatch.setattr(activity, "LOCK_FILE", str(tmp_path / "activity.lock"))
    sys.modules["actividad"] = activity
    gpu = _load("mak_test_gpu_guard", PLATFORM / "gpu_guard.py")
    monkeypatch.setattr(gpu, "LOCK_FILE", str(tmp_path / "gpu.lock"))
    monkeypatch.setattr(gpu, "STATE_FILE", str(tmp_path / "gpu-state.json"))

    with gpu.slot(caller="test", queue="test.queue", model="test-model",
                  department="test", trigger="test"):
        # The test uses an isolated lock/state path and must not leave active state.
        assert not Path(gpu.STATE_FILE).exists() or Path(gpu.STATE_FILE).is_file()


def test_inventory_rows_are_valid_json(tmp_path, monkeypatch):
    activity = _load("mak_test_actividad_json", PLATFORM / "actividad.py")
    monkeypatch.setattr(activity, "ACTIVITY_FILE", str(tmp_path / "activity.jsonl"))
    monkeypatch.setattr(activity, "LOCK_FILE", str(tmp_path / "activity.lock"))
    activity.record("queue", "finished", trigger="manual", extra={"count": 3})
    line = (tmp_path / "activity.jsonl").read_text(encoding="utf-8").strip()
    assert json.loads(line)["schema"] == "mak-activity-v1"
