"""Evaluate C07's generated candidates on the exact C07 fixture cases."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from evaluator import evaluate_ranked


ROOT = Path(__file__).resolve().parent
C07_GRAPH = ROOT.parent / "C07" / "graph.json"


def _artifact(graph: dict[str, Any], suffix: str) -> str:
    matches = [item["id"] for item in graph["artifacts"] if item["path"].endswith(suffix)]
    if len(matches) != 1:
        raise AssertionError(f"expected one artifact ending {suffix!r}, got {matches!r}")
    return matches[0]


def _record(case_id: str, source: str, target: str, relation: str, rank: int) -> dict[str, Any]:
    return {"case_id": case_id, "source": source, "target": target, "relation": relation, "rank": rank}


def gold_for_case(case_id: str, graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Gold is fixture truth, not a claim about the real archive."""
    if case_id == "frames_plus_export":
        frame_one = _artifact(graph, "aurora/aurora_frame_0001.png")
        frame_two = _artifact(graph, "aurora/aurora_frame_0002.png")
        export = _artifact(graph, "aurora/aurora_export.png")
        project = _artifact(graph, "aurora/aurora_project.blend")
        post = _artifact(graph, "published/aurora_public_post.jpg")
        return [
            _record(case_id, frame_one, frame_two, "same_series_candidate", 1),
            _record(case_id, frame_one, export, "component_of", 2),
            _record(case_id, frame_two, export, "component_of", 3),
            _record(case_id, export, project, "version_of", 4),
            _record(case_id, export, post, "published_as", 5),
        ]
    if case_id == "same_work_different_proportions":
        first = _artifact(graph, "study/study_4x5.png")
        second = _artifact(graph, "study/study_16x9.png")
        return [_record(case_id, first, second, "manifestation_of", 1)]
    return []


def predicted_for_case(case_id: str, graph: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [item for item in graph["relation_candidates"] if item["target_id"] is not None]
    ordered = sorted(candidates, key=lambda item: (-item["score"], item["id"]))
    return [
        _record(case_id, item["source_id"], item["target_id"], item["relation"], index)
        for index, item in enumerate(ordered, 1)
    ]


def evaluate_c07_graph(path: str | Path = C07_GRAPH) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    graphs = payload["cases"]
    cases = sorted(graphs)
    gold: list[dict[str, Any]] = []
    predicted: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    pending_by_case: dict[str, int] = {}
    for case_id in cases:
        graph = graphs[case_id]
        gold.extend(gold_for_case(case_id, graph))
        predicted.extend(predicted_for_case(case_id, graph))
        status_counts.update(item["status"] for item in graph["relation_candidates"])
        pending_by_case[case_id] = sum(item["status"] != "supported" for item in graph["relation_candidates"])
    relation_eval = evaluate_ranked(cases, gold, predicted, "relation")
    baseline = evaluate_ranked(cases, gold, [], "relation")
    return {
        "schema": "mak-cycle-c08-c07-integration-v1",
        "source": str(Path(path)),
        "same_cases": cases,
        "baseline": baseline,
        "candidate": relation_eval,
        "status_counts": dict(sorted(status_counts.items())),
        "pending_or_unresolved_by_case": pending_by_case,
        "gold_relation_count": len(gold),
        "predicted_relation_count": len(predicted),
    }
