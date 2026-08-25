"""Evaluation for C03, kept outside the blind recovery module."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


TRUTH_SCHEMA = "mak-cycle-c03-truth-v1"
POSITIVE_STATUSES = {"candidate", "confirmed"}


class TruthError(ValueError):
    """Raised when the separate evaluation fixture is malformed."""


def load_truth(path: str | Path) -> dict[str, Any]:
    truth_path = Path(path)
    try:
        payload = json.loads(truth_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TruthError(f"cannot read evaluation truth: {truth_path}") from exc
    if not isinstance(payload, Mapping) or payload.get("schema") != TRUTH_SCHEMA:
        raise TruthError("unsupported truth schema")
    if not isinstance(payload.get("cases"), list):
        raise TruthError("truth cases must be a list")
    return dict(payload)


def evaluate(recovery: Mapping[str, Any], truth: Mapping[str, Any]) -> dict[str, Any]:
    """Score recovery output after recovery has finished.

    The truth fixture is deliberately a separate argument to this evaluator;
    it is not accepted by or imported into the recovery functions.
    """

    by_query = {item["query_id"]: item for item in recovery.get("results", [])}
    rows: list[dict[str, Any]] = []
    tp = fp = abstentions = contradicted = 0
    for case in truth["cases"]:
        query_id = case["query_id"]
        prediction = by_query.get(query_id)
        if prediction is None:
            raise TruthError(f"recovery omitted truth query {query_id}")
        predicted_positive = prediction["status"] in POSITIVE_STATUSES and prediction["local_id"] is not None
        expected_local_id = case.get("expected_local_id")
        if predicted_positive and expected_local_id is not None and prediction["local_id"] == expected_local_id:
            outcome = "tp"
            tp += 1
        elif predicted_positive:
            outcome = "fp"
            fp += 1
        else:
            outcome = "abstention"
            abstentions += 1
            if prediction["status"] == "contradicted":
                contradicted += 1
        rows.append(
            {
                "query_id": query_id,
                "predicted_status": prediction["status"],
                "predicted_local_id": prediction["local_id"],
                "expected_local_id": expected_local_id,
                "expected_status": case.get("expected_status"),
                "outcome": outcome,
            }
        )
    total = len(rows)
    linkable = sum(1 for case in truth["cases"] if case.get("expected_local_id") is not None)
    decisions = tp + fp
    return {
        "metrics": {
            "tp": tp,
            "fp": fp,
            "abstentions": abstentions,
            "contradicted": contradicted,
            "total_cases": total,
            "decision_coverage": decisions / total if total else 0.0,
            "coverage": tp / linkable if linkable else 0.0,
            "linkable_cases": linkable,
        },
        "cases": rows,
        "orphan_local_ids": list(truth.get("orphan_local_ids", [])),
    }
