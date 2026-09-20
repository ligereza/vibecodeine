from __future__ import annotations

import json
import os
from pathlib import Path

from cultura.mak_plataforma import azure_services
from tools import azure_ml_learning_dataset


def _receipt(root: Path, name: str, payload: object) -> Path:
    directory = root / name
    directory.mkdir(parents=True)
    path = directory / "receipt.json"
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid_receipt(**overrides: object) -> dict:
    payload = {
        "schema": "mak-azure-ml-learning-dataset-v1",
        "source": "/home/mak/private/prompts.sqlite",
        "receipt_path": "/home/mak/private/receipt.json",
        "dataset_path": "/home/mak/private/dataset.jsonl",
        "rows": 4,
        "statuses": {"accepted": 3, "rejected": 1},
        "target_kinds": {"tool": 4},
        "dataset_fingerprints": ["fp-a", "fp-b"],
        "dataset_sha256": "A" * 64,
        "mlflow_run_id": "run-123",
        "artifact_upload": "uploaded",
        "artifact_builder": "azureml",
        "prompt": "must never leave the machine",
    }
    payload.update(overrides)
    return payload


def test_lineage_absence_is_explicit_and_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_AZURE_ML_STAGING_ROOT", str(tmp_path))
    assert azure_services.machine_learning_lineage() == {
        "schema": "mak-azure-ml-learning-lineage-v1",
        "available": False,
        "status": "absent",
    }


def test_lineage_projects_allowlist_without_local_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_AZURE_ML_STAGING_ROOT", str(tmp_path))
    _receipt(tmp_path, "learning-evaluations-1", _valid_receipt())

    lineage = azure_services.machine_learning_lineage()

    assert lineage["available"] is True
    assert lineage["status"] == "present"
    assert lineage["rows"] == 4
    assert lineage["fingerprint_count"] == 2
    assert lineage["dataset_sha256"] == "a" * 64
    assert lineage["mlflow_run_id"] == "run-123"
    serialized = json.dumps(lineage)
    for forbidden in ("source", "dataset_path", "receipt_path", "prompt", str(tmp_path)):
        assert forbidden not in serialized


def test_lineage_selects_newest_receipt_deterministically(tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_AZURE_ML_STAGING_ROOT", str(tmp_path))
    older = _receipt(tmp_path, "older", _valid_receipt(dataset_sha256="1" * 64))
    newer = _receipt(tmp_path, "newer", _valid_receipt(dataset_sha256="2" * 64))
    os.utime(older, (100, 100))
    os.utime(newer, (200, 200))

    assert azure_services.machine_learning_lineage()["dataset_sha256"] == "2" * 64


def test_lineage_invalid_receipt_degrades_cleanly(tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_AZURE_ML_STAGING_ROOT", str(tmp_path))
    _receipt(tmp_path, "broken", "not-json")

    assert azure_services.machine_learning_lineage() == {
        "schema": "mak-azure-ml-learning-lineage-v1",
        "available": False,
        "status": "invalid",
    }


def test_snapshot_includes_lineage_without_an_azure_call(tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_AZURE_ML_STAGING_ROOT", str(tmp_path))
    _receipt(tmp_path, "learning-evaluations-1", _valid_receipt())
    monkeypatch.setattr(azure_services, "_resource_inventory", lambda: [])

    payload = azure_services.snapshot()

    assert payload["machine_learning_lineage"]["status"] == "present"
    assert payload["services"]


def test_producer_uses_the_same_configurable_staging_root(tmp_path, monkeypatch):
    monkeypatch.setenv("MAK_AZURE_ML_STAGING_ROOT", str(tmp_path))
    assert azure_ml_learning_dataset.staging_root() == str(tmp_path)
