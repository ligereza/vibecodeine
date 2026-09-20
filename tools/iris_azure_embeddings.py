#!/usr/bin/env python3
"""Add an Azure text-feature channel to a sanitized IRIS decision session."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "cultura" / "mak_plataforma"
if str(PLATFORM) not in sys.path:
    sys.path.insert(0, str(PLATFORM))

from azure_embeddings import embed  # noqa: E402


DEFAULT_SESSION = Path(
    "/home/mak/research/azure-ml/staging/"
    "iris-autonomous-20260920-01/decisions.jsonl"
)
TRACKING_URI = (
    "azureml://brazilsouth.api.azureml.ms/mlflow/v1.0/subscriptions/"
    "6519fcfc-3807-407e-bae5-5f1f7f64e337/resourceGroups/makmak/"
    "providers/Microsoft.MachineLearningServices/workspaces/makmak-ml-workspace"
)


def _read_records(path: Path) -> list[dict]:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not records:
        raise ValueError("empty decision dataset")
    if any(row.get("status") != "final" for row in records):
        raise ValueError("all decisions must be final")
    if any(row.get("requires_approval") is not False for row in records):
        raise ValueError("pending decisions are not accepted")
    return records


def _embedding_text(row: dict) -> str:
    evidence = row.get("evidence") or {}
    reason_messages = [
        str(item.get("message", ""))
        for item in evidence.get("reasons", [])
        if isinstance(item, dict)
    ]
    parts = [
        "ruta_relativa: " + str(row.get("project_rel_root", "")),
        "tipo: " + str(row.get("project_kind", "")),
        "origen: " + str(row.get("origin_class", "")),
        "estructura: " + str(row.get("structure_class", "")),
        "evidencia: " + " | ".join(reason_messages),
        "paquetes: " + json.dumps(
            evidence.get("package_summary", {}), ensure_ascii=False, sort_keys=True
        ),
        "clusters: " + json.dumps(
            evidence.get("cluster_summary", {}), ensure_ascii=False, sort_keys=True
        ),
        "historial: " + json.dumps(
            evidence.get("history_summary", {}), ensure_ascii=False, sort_keys=True
        ),
    ]
    return "\n".join(parts)


def build_embeddings(path: Path, *, batch_size: int = 16) -> tuple[list[dict], dict]:
    records = _read_records(path)
    output = []
    requests = 0
    usage = Counter()
    dimensions = None
    for offset in range(0, len(records), batch_size):
        batch = records[offset:offset + batch_size]
        texts = [_embedding_text(row) for row in batch]
        result = embed(texts)
        if not result.get("available"):
            raise RuntimeError(str(result.get("error", "azure_embedding_unavailable")))
        requests += 1
        dimensions = int(result["dimensions"])
        for key, value in result.get("usage", {}).items():
            if isinstance(value, (int, float)):
                usage[str(key)] += value
        for source, vector in zip(batch, result["vectors"]):
            output.append({
                "schema": "mak-iris-text-embedding-v2",
                "session_id": source["session_id"],
                "project_id": source["project_id"],
                "group_key": source["group_key"],
                "decision": source["decision"],
                "decision_authority": source["decision_authority"],
                "deployment": result["deployment"],
                "dimensions": dimensions,
                "source_item_sha256": source["source_item_sha256"],
                "text_sha256": hashlib.sha256(
                    _embedding_text(source).encode("utf-8")
                ).hexdigest(),
                "embedding": vector,
                "independent_gold_label": False,
            })
    receipt = {
        "schema": "mak-iris-text-embedding-dataset-v2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(path),
        "source_dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "session_id": records[0]["session_id"],
        "rows": len(output),
        "groups": len({row["group_key"] for row in output}),
        "dimensions": dimensions,
        "requests": requests,
        "usage": dict(usage),
        "contains_input_text": False,
        "label_fields_embedded": False,
        "contains_absolute_source_paths": False,
        "contains_credentials": False,
        "physical_actions": 0,
        "compute_started": False,
    }
    return output, receipt


def write_embeddings(rows: list[dict], receipt: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "text_embeddings.jsonl"
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    data_path.write_text(text, encoding="utf-8")
    receipt["dataset_path"] = str(data_path)
    receipt["dataset_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    receipt_path = out_dir / "text_embeddings_receipt.json"
    receipt["receipt_path"] = str(receipt_path)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data_path, receipt_path


def register_mlflow(data_path: Path, receipt_path: Path, receipt: dict) -> None:
    import mlflow
    from azure_ml_mlflow_compat import patch_azureml_artifact_builder

    patch_azureml_artifact_builder()
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("mak-iris-decision-sessions")
    with mlflow.start_run(run_name=receipt["session_id"] + "-text-embeddings-label-free") as run:
        mlflow.log_params({
            "schema": receipt["schema"],
            "deployment": "text-embedding-3-small",
            "contains_input_text": "false",
            "label_fields_embedded": "false",
            "split_by": "group_key",
        })
        mlflow.log_metrics({
            "embedding_rows": receipt["rows"],
            "embedding_groups": receipt["groups"],
            "embedding_dimensions": receipt["dimensions"],
            "embedding_requests": receipt["requests"],
        })
        mlflow.log_artifact(str(data_path), artifact_path="datasets")
        receipt["mlflow_run_id"] = run.info.run_id
        receipt["artifact_uploaded"] = True
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Embed a finalized IRIS decision session")
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--register-mlflow", action="store_true")
    args = parser.parse_args(argv)
    out_dir = args.out or args.session.parent
    rows, receipt = build_embeddings(args.session, batch_size=args.batch_size)
    data_path, receipt_path = write_embeddings(rows, receipt, out_dir)
    if args.register_mlflow:
        register_mlflow(data_path, receipt_path, receipt)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
