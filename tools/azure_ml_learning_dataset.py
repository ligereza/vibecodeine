#!/usr/bin/env python3
"""Export MAK learning evaluations as a sanitized Azure ML/MLflow artifact.

This is a data-lineage step, not model training and not a DeepSeek benchmark.
It exports only evaluation metadata and metrics from the local ledger; raw
prompts, documents, RD data, and credentials never leave the machine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SUBSCRIPTION_ID = "6519fcfc-3807-407e-bae5-5f1f7f64e337"
RESOURCE_GROUP = "makmak"
WORKSPACE = "makmak-ml-workspace"
TRACKING_URI = (
    "azureml://brazilsouth.api.azureml.ms/mlflow/v1.0/subscriptions/"
    + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP
    + "/providers/Microsoft.MachineLearningServices/workspaces/"
    + WORKSPACE
)
DEFAULT_DB = "/home/mak/data/mak_knowledge.db"
DEFAULT_OUT = "/home/mak/research/azure-ml/staging"


def _rows(db_path: str) -> list[dict]:
    with sqlite3.connect(db_path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT evaluation_id, target_kind, target_id, "
            "dataset_fingerprint, split_kind, status, metrics_json, "
            "baseline_policy_id, candidate_policy_id, created_at "
            "FROM learning_evaluations ORDER BY created_at, evaluation_id"
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["metrics"] = json.loads(item.pop("metrics_json") or "{}")
        except (TypeError, ValueError, json.JSONDecodeError):
            item["metrics"] = {"parse_error": True}
            item.pop("metrics_json", None)
        result.append(item)
    return result


def export_dataset(db_path: str, out_root: str) -> tuple[Path, dict]:
    rows = _rows(db_path)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = Path(out_root).expanduser() / ("learning-evaluations-" + stamp)
    target.mkdir(parents=True, exist_ok=False)
    dataset_path = target / "learning_evaluations.jsonl"
    with dataset_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    digest = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    statuses = Counter(str(row.get("status", "")) for row in rows)
    targets = Counter(str(row.get("target_kind", "")) for row in rows)
    metadata = {
        "schema": "mak-azure-ml-learning-dataset-v1",
        "source": os.path.abspath(db_path),
        "rows": len(rows),
        "statuses": dict(statuses),
        "target_kinds": dict(targets),
        "dataset_fingerprints": sorted({
            str(row.get("dataset_fingerprint"))
            for row in rows if row.get("dataset_fingerprint")
        }),
        "contains_prompts": False,
        "contains_documents": False,
        "contains_credentials": False,
        "purpose": "evaluation lineage only; no model training",
        "dataset_sha256": digest,
    }
    receipt_path = target / "receipt.json"
    receipt_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    return dataset_path, {**metadata, "receipt_path": str(receipt_path),
                          "dataset_path": str(dataset_path)}


def _patch_azureml_artifact_builder() -> str:
    """Bridge MLflow 3's builder kwargs to azureml-mlflow 1.60.0.

    The Azure plugin is otherwise usable for this workspace.  Its entry point
    predates MLflow's ``tracking_uri``/``registry_uri`` constructor kwargs.
    Keep the patch process-local and leave installed packages untouched.
    """
    from azure_ml_mlflow_compat import patch_azureml_artifact_builder
    return patch_azureml_artifact_builder()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Exporta evaluaciones sanitizadas a MLflow Azure ML")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    dataset_path, metadata = export_dataset(args.db, args.out)
    try:
        import mlflow
        mlflow.set_tracking_uri(TRACKING_URI)
        mlflow.set_experiment("mak-ml-datasets")
        with mlflow.start_run(run_name="learning-evaluations-dataset") as run:
            mlflow.log_params({
                "dataset_schema": metadata["schema"],
                "source_table": "learning_evaluations",
                "contains_prompts": "false",
                "contains_documents": "false",
                "purpose": "evaluation_lineage_only",
            })
            mlflow.log_metrics({
                "dataset_rows": metadata["rows"],
                "dataset_fingerprints": len(metadata["dataset_fingerprints"]),
            })
            metadata["artifact_builder"] = _patch_azureml_artifact_builder()
            mlflow.log_artifact(str(dataset_path), artifact_path="datasets")
            mlflow.log_params({
                "dataset_sha256": metadata["dataset_sha256"],
                "dataset_local_path": str(dataset_path),
                "artifact_upload": "uploaded",
            })
            metadata["mlflow_run_id"] = run.info.run_id
            metadata["artifact_upload"] = "uploaded"
        Path(metadata["receipt_path"]).write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(json.dumps(metadata, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001 - receipt still exists locally
        metadata["mlflow_error"] = type(exc).__name__
        Path(metadata["receipt_path"]).write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(json.dumps(metadata, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
