"""Small stdlib-only evaluator for relation, phase, series and portfolio claims."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Callable, Iterable


def _key(record: dict[str, Any], kind: str) -> tuple[str, ...]:
    if kind == "relation":
        return (record["source"], record["target"], record["relation"])
    if kind == "phase":
        return (record["item_id"], record["phase"])
    if kind == "series":
        return (record["item_id"], record["series_id"])
    raise ValueError(f"unknown kind: {kind}")


def _ranked(records: Iterable[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    ordered = sorted(enumerate(records), key=lambda pair: (pair[1].get("rank", pair[0] + 1), pair[0]))
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for _, record in ordered:
        key = _key(record, kind)
        if key not in seen:
            result.append(record)
            seen.add(key)
    return result


def _case_metrics(gold: list[dict[str, Any]], predicted: list[dict[str, Any]], kind: str, k: int) -> dict[str, Any]:
    gold_keys = {_key(record, kind) for record in gold}
    ranked = _ranked(predicted, kind)
    hits = sum(_key(record, kind) in gold_keys for record in ranked[:k])
    return {
        "gold": len(gold_keys),
        "predicted": len(ranked),
        "hits_at_k": hits,
        "precision_at_k": hits / k,
        "recall_at_k": (hits / len(gold_keys)) if gold_keys else None,
    }


def evaluate_ranked(
    cases: Iterable[str],
    gold: Iterable[dict[str, Any]],
    predicted: Iterable[dict[str, Any]],
    kind: str,
    k_values: tuple[int, ...] = (1, 3, 5),
) -> dict[str, Any]:
    """Evaluate top-k retrieval; empty predictions are the unknown baseline."""
    case_ids = list(cases)
    gold_by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    predicted_by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in gold:
        gold_by[record["case_id"]].append(record)
    for record in predicted:
        predicted_by[record["case_id"]].append(record)

    by_case: dict[str, dict[str, Any]] = {}
    for case_id in case_ids:
        by_case[case_id] = {
            f"k{k}": _case_metrics(gold_by[case_id], predicted_by[case_id], kind, k)
            for k in k_values
        }

    total_gold = sum(len({_key(record, kind) for record in records}) for records in gold_by.values())
    gold_cases = sum(bool({_key(record, kind) for record in gold_by[case_id]}) for case_id in case_ids)
    metrics: dict[str, Any] = {"kind": kind, "gold_count": total_gold, "case_count": len(case_ids), "by_case": by_case}
    for k in k_values:
        hits = sum(by_case[case_id][f"k{k}"]["hits_at_k"] for case_id in case_ids)
        metrics[f"precision_at_{k}"] = hits / (len(case_ids) * k) if case_ids else 0.0
        metrics[f"recall_at_{k}"] = hits / total_gold if total_gold else None
        covered = sum(by_case[case_id][f"k{k}"]["hits_at_k"] > 0 for case_id in case_ids if gold_by[case_id])
        metrics[f"coverage_at_{k}"] = covered / gold_cases if gold_cases else 0.0
    last_k = k_values[-1]
    metrics["recall"] = metrics[f"recall_at_{last_k}"]
    metrics["coverage"] = metrics[f"coverage_at_{last_k}"]
    return metrics


def evaluate_portfolio(
    intent: dict[str, Any],
    selected_ids: Iterable[str],
    items: Iterable[dict[str, Any]],
    gold_phases: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    item_by_id = {item["id"]: item for item in items}
    selected = [item_by_id[item_id] for item_id in selected_ids if item_id in item_by_id]
    phases_by_item: dict[str, set[str]] = defaultdict(set)
    for record in gold_phases:
        phases_by_item[record["item_id"]].add(record["phase"])

    required_phases = set(intent["required_phases"])
    covered_phases = set().union(*(phases_by_item[item["id"]] for item in selected)) if selected else set()
    phase_coverage = len(required_phases & covered_phases) / len(required_phases) if required_phases else 1.0

    formats = {item["format"] for item in selected}
    ratios = {item["aspect_ratio"] for item in selected}
    format_score = min(1.0, len(formats) / intent["min_distinct_formats"]) if intent["min_distinct_formats"] else 1.0
    ratio_score = min(1.0, len(ratios) / intent["min_distinct_ratios"]) if intent["min_distinct_ratios"] else 1.0
    diversity = (format_score + ratio_score) / 2

    required_buckets = set(intent["chronology_buckets"])
    buckets = {item["chronology"] for item in selected}
    chronology = len(required_buckets & buckets) / len(required_buckets) if required_buckets else 1.0

    works = [item["work_id"] for item in selected]
    unique_works = len(set(works))
    duplicate_count = len(works) - unique_works
    redundancy = duplicate_count / len(works) if works else 0.0
    return {
        "selected_count": len(selected),
        "coverage": {"required_phases": sorted(required_phases), "covered_phases": sorted(covered_phases), "score": phase_coverage},
        "diversity": {"formats": sorted(formats), "ratios": sorted(ratios), "score": diversity},
        "chronology": {"required_buckets": sorted(required_buckets), "covered_buckets": sorted(required_buckets & buckets), "score": chronology},
        "redundancy": {"unique_works": unique_works, "duplicate_count": duplicate_count, "rate": redundancy},
        "portfolio_score": mean((phase_coverage, diversity, chronology, 1.0 - redundancy)) if selected else 0.0,
    }


def select_portfolio(intent: dict[str, Any], items: Iterable[dict[str, Any]]) -> list[str]:
    """Greedily derive a small portfolio from observed phase hints.

    This is deliberately not a learned curator. It is an executable baseline
    planner: cover required phases first, then add items only while they add a
    missing format, ratio or chronology bucket. Reusing a work is penalized so
    a frame sequence cannot masquerade as portfolio breadth.
    """
    pool = list(items)
    selected: list[dict[str, Any]] = []

    def score(item: dict[str, Any]) -> tuple[int, int, int, int]:
        phases = {entry.get("phase_hint") for entry in selected}
        formats = {entry["format"] for entry in selected}
        ratios = {entry["aspect_ratio"] for entry in selected}
        chronology = {entry["chronology"] for entry in selected}
        phase_gain = int(item.get("phase_hint") not in phases)
        format_gain = int(item["format"] not in formats)
        ratio_gain = int(item["aspect_ratio"] not in ratios)
        chronology_gain = int(item["chronology"] not in chronology)
        repeated_work = int(item["work_id"] in {entry["work_id"] for entry in selected})
        # Phase coverage is primary; diversity follows; duplicate work loses.
        return (phase_gain * 100 + format_gain * 10 + ratio_gain * 5 + chronology_gain * 3 - repeated_work * 20,
                format_gain, ratio_gain, chronology_gain)

    for phase in intent["required_phases"]:
        choices = [item for item in pool if item.get("phase_hint") == phase and item not in selected]
        if choices:
            selected.append(max(choices, key=score))

    while True:
        formats = {entry["format"] for entry in selected}
        ratios = {entry["aspect_ratio"] for entry in selected}
        chronology = {entry["chronology"] for entry in selected}
        need_more = (
            len(formats) < intent["min_distinct_formats"]
            or len(ratios) < intent["min_distinct_ratios"]
            or len(chronology) < len(intent["chronology_buckets"])
        )
        if not need_more:
            break
        choices = [item for item in pool if item not in selected]
        if not choices:
            break
        candidate = max(choices, key=score)
        before = (len(formats), len(ratios), len(chronology))
        selected.append(candidate)
        after = (len({entry["format"] for entry in selected}), len({entry["aspect_ratio"] for entry in selected}), len({entry["chronology"] for entry in selected}))
        if after == before:
            break

    return [item["id"] for item in selected]


def evaluate_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    cases = [case["id"] for case in fixture["cases"]]
    sections: dict[str, dict[str, Any]] = {}
    for name, kind in (("relations", "relation"), ("phases", "phase"), ("series", "series")):
        gold = fixture[name]["gold"]
        candidate = fixture[name]["candidate"]
        sections[name] = {
            "baseline": evaluate_ranked(cases, gold, [], kind),
            "candidate": evaluate_ranked(cases, gold, candidate, kind),
        }
    planned_selection = select_portfolio(fixture["portfolio"]["intent"], fixture["items"])
    sections["portfolio"] = {
        "baseline": evaluate_portfolio(fixture["portfolio"]["intent"], [], fixture["items"], fixture["phases"]["gold"]),
        "candidate": evaluate_portfolio(
            fixture["portfolio"]["intent"], planned_selection, fixture["items"], fixture["phases"]["gold"]
        ),
        "selection_method": "greedy_phase_coverage",
        "selected_ids": planned_selection,
    }
    return {"schema": "mak-cycle-c08-report-v1", "sections": sections}
