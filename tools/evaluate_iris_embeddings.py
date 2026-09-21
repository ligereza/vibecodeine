#!/usr/bin/env python3
"""Evaluate IRIS text embeddings with group-held-out nearest neighbours."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

DEFAULT_INPUT = Path(
    "/home/mak/research/staging/"
    "iris-autonomous-20260920-01/text_embeddings.jsonl"
)


def _cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return -1.0
    return numerator / (left_norm * right_norm)


def evaluate(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("empty embedding dataset")
    predictions = []
    labels = sorted({str(row["decision"]) for row in rows})
    groups_by_label: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        groups_by_label[str(row["decision"])].add(str(row["group_key"]))

    for row in rows:
        pool = [candidate for candidate in rows if candidate["group_key"] != row["group_key"]]
        if not pool:
            continue
        neighbor = max(pool, key=lambda candidate: _cosine(row["embedding"], candidate["embedding"]))
        counts = Counter(str(candidate["decision"]) for candidate in pool)
        majority = sorted(counts, key=lambda label: (-counts[label], label))[0]
        predictions.append({
            "project_id": row["project_id"],
            "group_key": row["group_key"],
            "actual": row["decision"],
            "embedding_prediction": neighbor["decision"],
            "neighbor_project_id": neighbor["project_id"],
            "neighbor_group_key": neighbor["group_key"],
            "cosine_similarity": _cosine(row["embedding"], neighbor["embedding"]),
            "majority_prediction": majority,
        })

    def metrics(key: str) -> dict:
        correct = sum(row[key] == row["actual"] for row in predictions)
        recalls = {}
        for label in labels:
            subset = [row for row in predictions if row["actual"] == label]
            recalls[label] = (
                sum(row[key] == label for row in subset) / len(subset)
                if subset else None
            )
        measured = [value for value in recalls.values() if value is not None]
        return {
            "accuracy": correct / len(predictions) if predictions else None,
            "macro_recall": sum(measured) / len(measured) if measured else None,
            "per_class_recall": recalls,
        }

    unsupported = sorted(
        label for label, groups in groups_by_label.items() if len(groups) < 2
    )
    return {
        "schema": "mak-iris-embedding-evaluation-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evaluation": "leave-one-group-out-1nn",
        "split_key": "group_key",
        "rows": len(rows),
        "groups": len({row["group_key"] for row in rows}),
        "labels": labels,
        "groups_by_label": {key: len(value) for key, value in sorted(groups_by_label.items())},
        "embedding_1nn": metrics("embedding_prediction"),
        "majority_baseline": metrics("majority_prediction"),
        "training_ready": not unsupported,
        "unsupported_labels": unsupported,
        "decision": "hold_training" if unsupported else "eligible_for_training_trial",
        "reason": (
            "one_or_more_labels_lack_an_independent_group"
            if unsupported else "all_labels_have_independent_group_support"
        ),
        "predictions": predictions,
        "model_registered": False,
        "compute_started": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate IRIS embeddings without group leakage")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = evaluate(rows)
    report["source"] = str(args.input)
    out = args.out or args.input.with_name("embedding_evaluation.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "rows", "groups", "embedding_1nn", "majority_baseline",
        "training_ready", "unsupported_labels", "decision",
    )}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
