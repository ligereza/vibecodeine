#!/usr/bin/env python3
"""Compile final delegated IRIS decisions into a sanitized ML dataset.

The source queue remains untouched. Decisions are final for the virtual
curation layer, but they do not authorize filesystem changes, publication,
authorship claims, or use as an independent evaluation gold set.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "mak-iris-autonomous-decision-dataset-v1"
ALLOWED_DECISIONS = {
    "KEEP_CANONICAL",
    "KEEP_DERIVATIVE",
    "PRESERVE_ECOSYSTEM",
    "QUARANTINE_COPY",
    "REVIEW_EXCEPTION",
}
DEFAULT_QUEUE = Path(
    "/home/mak/curatoria_inbox/DIMENSIONES DEL ORDEN/"
    "review_exception_feedback_queue.json"
)
DEFAULT_DECISIONS = Path(
    "/home/mak/knowledge/learning_cases/"
    "iris_autonomous_decisions_2026-09-20.json"
)
DEFAULT_OUT = Path("/home/mak/research/staging")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def compile_session(queue_path: Path, decisions_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    session = json.loads(decisions_path.read_text(encoding="utf-8"))

    if session.get("status") != "final" or session.get("requires_approval") is not False:
        raise ValueError("session decisions must be final and require no approval")
    if session.get("decision_authority") != "operator_delegated":
        raise ValueError("decision authority must be operator_delegated")

    queue_by_id = {int(item["project_id"]): item for item in queue.get("items", [])}
    records: list[dict[str, Any]] = []
    seen: set[int] = set()
    for decision in session.get("decisions", []):
        project_id = int(decision["project_id"])
        if project_id in seen:
            raise ValueError(f"duplicate project decision: {project_id}")
        seen.add(project_id)
        if decision.get("decision") not in ALLOWED_DECISIONS:
            raise ValueError(f"invalid decision for project {project_id}")
        if not 0.0 <= float(decision.get("confidence", -1)) <= 1.0:
            raise ValueError(f"invalid confidence for project {project_id}")
        item = queue_by_id.get(project_id)
        if item is None:
            raise ValueError(f"project is absent from source queue: {project_id}")
        if int(item.get("scan_id", -1)) != int(session["source"]["scan_id"]):
            raise ValueError(f"scan mismatch for project {project_id}")
        evidence = json.loads(item.get("evidence_json") or "{}")
        reasons = json.loads(item.get("reason_json") or "[]")
        records.append({
            "schema": "mak-iris-autonomous-decision-v1",
            "session_id": session["session_id"],
            "decision_authority": session["decision_authority"],
            "decision_maker": session["decision_maker"],
            "status": "final",
            "requires_approval": False,
            "project_id": project_id,
            "project_rel_root": item.get("project_rel_root"),
            "project_kind": item.get("project_kind"),
            "origin_class": item.get("origin_class"),
            "structure_class": item.get("structure_class"),
            "total_bytes": item.get("total_bytes"),
            "source_prediction": item.get("predicted_decision"),
            "source_confidence": item.get("confidence"),
            "decision": decision["decision"],
            "decision_confidence": float(decision["confidence"]),
            "reason": decision["reason"],
            "group_key": decision["group_key"],
            "purpose": session["purpose"],
            "evidence": {
                "reasons": reasons,
                "cluster_summary": evidence.get("cluster_summary", {}),
                "history_summary": evidence.get("history_summary", {}),
                "package_summary": evidence.get("package_summary", {}),
                "virtual_index": evidence.get("virtual_index", {}),
            },
            "source_item_sha256": _sha256(item),
            "physical_actions": 0,
            "publication_authorized": False,
            "independent_gold_label": False,
        })

    records.sort(key=lambda row: int(row["project_id"]))
    queue_hash = hashlib.sha256(queue_path.read_bytes()).hexdigest()
    decisions_hash = hashlib.sha256(decisions_path.read_bytes()).hexdigest()
    receipt = {
        "schema": SCHEMA,
        "session_id": session["session_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "decision_authority": session["decision_authority"],
        "decision_maker": session["decision_maker"],
        "status": "final",
        "requires_approval": False,
        "row_count": len(records),
        "group_count": len({row["group_key"] for row in records}),
        "decision_counts": dict(sorted(Counter(
            row["decision"] for row in records
        ).items())),
        "source_queue_sha256": queue_hash,
        "decision_manifest_sha256": decisions_hash,
        "contains_absolute_source_paths": False,
        "contains_prompts": False,
        "contains_credentials": False,
        "physical_actions": 0,
        "evaluation_policy": {
            "split_by": "group_key",
            "self_labels_are_independent_gold": False,
            "promotion_requires_separate_evidence": True,
        },
        "execution": "local_only",
    }
    return records, receipt


def write_session(records: list[dict[str, Any]], receipt: dict[str, Any],
                  out_root: Path) -> tuple[Path, Path]:
    target = out_root / str(receipt["session_id"])
    target.mkdir(parents=True, exist_ok=True)
    dataset_path = target / "decisions.jsonl"
    dataset_text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
        for row in records
    )
    dataset_path.write_text(dataset_text, encoding="utf-8")
    receipt["dataset_sha256"] = hashlib.sha256(dataset_text.encode("utf-8")).hexdigest()
    receipt["dataset_path"] = str(dataset_path)
    receipt_path = target / "receipt.json"
    receipt["receipt_path"] = str(receipt_path)
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return dataset_path, receipt_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile final delegated IRIS decisions for ML"
    )
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    records, receipt = compile_session(args.queue, args.decisions)
    dataset_path, receipt_path = write_session(records, receipt, args.out)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
