"""Deterministic adversarial fixtures; no filesystem or third-party package access."""

from __future__ import annotations


def _relation(case_id: str, source: str, target: str, relation: str, rank: int | None = None) -> dict[str, object]:
    value: dict[str, object] = {"case_id": case_id, "source": source, "target": target, "relation": relation}
    if rank is not None:
        value["rank"] = rank
    return value


def _membership(case_id: str, item_id: str, label: str, field: str, rank: int | None = None) -> dict[str, object]:
    value: dict[str, object] = {"case_id": case_id, "item_id": item_id, field: label}
    if rank is not None:
        value["rank"] = rank
    return value


def build_fixture() -> dict[str, object]:
    cases = [
        {"id": "frames_one_work", "adversarial": "2048 frames from one work"},
        {"id": "export_without_project", "adversarial": "export with no project"},
        {"id": "project_without_export", "adversarial": "project with no export"},
        {"id": "post_without_project", "adversarial": "post with no project"},
        {"id": "same_work_formats_ratios", "adversarial": "same work in formats and proportions"},
        {"id": "third_party_similar", "adversarial": "similar third-party asset"},
        {"id": "similar_names", "adversarial": "similar names without relation"},
    ]
    items: list[dict[str, object]] = []
    gold_relations: list[dict[str, object]] = []
    candidate_relations: list[dict[str, object]] = []
    gold_phases: list[dict[str, object]] = []
    candidate_phases: list[dict[str, object]] = []
    gold_series: list[dict[str, object]] = []
    candidate_series: list[dict[str, object]] = []

    for number in range(1, 2049):
        item_id = f"frame-lumen-{number:04d}"
        items.append({"id": item_id, "case_id": "frames_one_work", "work_id": "work-lumen", "format": "png", "aspect_ratio": "16:9", "chronology": "early", "phase_hint": "capture"})
        gold_relations.append(_relation("frames_one_work", item_id, "work-lumen", "FRAME_OF"))
        gold_phases.append(_membership("frames_one_work", item_id, "capture", "phase"))
    for rank in range(1, 6):
        candidate_relations.append(_relation("frames_one_work", f"frame-lumen-{rank:04d}", "work-lumen", "FRAME_OF", rank))
        candidate_phases.append(_membership("frames_one_work", f"frame-lumen-{rank:04d}", "capture", "phase", rank))

    base_items = [
        ("export-ghost", "export_without_project", "ghost-export", "glb", "3:2", "mid", "export"),
        ("project-silent", "project_without_export", "silent-project", "blend", "4:3", "mid", "authoring"),
        ("post-orphan", "post_without_project", "orphan-post", "jpg", "1:1", "late", "post"),
        ("orchid-wide", "same_work_formats_ratios", "work-orchid", "png", "16:9", "early", "export"),
        ("orchid-vertical", "same_work_formats_ratios", "work-orchid", "mp4", "9:16", "mid", "post"),
        ("orchid-square", "same_work_formats_ratios", "work-orchid", "jpg", "1:1", "late", "post"),
        ("orchid-poster", "same_work_formats_ratios", "work-orchid", "webp", "4:5", "late", "post"),
        ("echo-third-party", "third_party_similar", "work-echo", "png", "16:9", "mid", "post"),
        ("project-orchid-v2", "similar_names", "work-name-v2", "blend", "4:3", "mid", "authoring"),
        ("project-orchid-final", "similar_names", "work-name-final", "blend", "4:3", "late", "authoring"),
    ]
    for item_id, case_id, work_id, fmt, ratio, chronology, phase in base_items:
        items.append({"id": item_id, "case_id": case_id, "work_id": work_id, "format": fmt, "aspect_ratio": ratio, "chronology": chronology, "phase_hint": phase})
        gold_phases.append(_membership(case_id, item_id, phase, "phase"))

    for item_id in ("orchid-wide", "orchid-vertical", "orchid-square", "orchid-poster"):
        gold_relations.append(_relation("same_work_formats_ratios", item_id, "work-orchid", "SAME_WORK"))
        gold_series.append(_membership("same_work_formats_ratios", item_id, "orchid-series", "series_id"))
    candidate_relations.extend([
        _relation("same_work_formats_ratios", "orchid-wide", "work-orchid", "SAME_WORK", 1),
        _relation("same_work_formats_ratios", "orchid-vertical", "work-orchid", "SAME_WORK", 2),
        _relation("same_work_formats_ratios", "orchid-square", "work-orchid", "SAME_WORK", 3),
        _relation("same_work_formats_ratios", "echo-third-party", "work-orchid", "SAME_WORK", 4),
    ])
    candidate_series.extend([
        _membership("same_work_formats_ratios", "orchid-wide", "orchid-series", "series_id", 1),
        _membership("same_work_formats_ratios", "orchid-vertical", "orchid-series", "series_id", 2),
        _membership("same_work_formats_ratios", "orchid-square", "orchid-series", "series_id", 3),
        _membership("same_work_formats_ratios", "echo-third-party", "orchid-series", "series_id", 4),
    ])
    candidate_relations.extend([
        _relation("export_without_project", "export-ghost", "project-ghost", "EXPORT_OF", 1),
        _relation("project_without_export", "project-silent", "export-silent", "EXPORTS", 1),
        _relation("post_without_project", "post-orphan", "project-orphan", "POST_OF", 1),
        _relation("third_party_similar", "echo-third-party", "work-orchid", "SAME_WORK", 1),
        _relation("similar_names", "project-orchid-v2", "project-orchid-final", "SAME_WORK", 1),
    ])
    candidate_phases.extend([
        _membership("export_without_project", "export-ghost", "export", "phase", 1),
        _membership("project_without_export", "project-silent", "authoring", "phase", 1),
        _membership("post_without_project", "post-orphan", "post", "phase", 1),
        _membership("same_work_formats_ratios", "orchid-wide", "export", "phase", 1),
        _membership("same_work_formats_ratios", "orchid-vertical", "post", "phase", 2),
        _membership("same_work_formats_ratios", "orchid-square", "post", "phase", 3),
    ])
    return {
        "schema": "mak-cycle-c08-fixture-v1",
        "cases": cases,
        "items": items,
        "relations": {"gold": gold_relations, "candidate": candidate_relations},
        "phases": {"gold": gold_phases, "candidate": candidate_phases},
        "series": {"gold": gold_series, "candidate": candidate_series},
        "portfolio": {
            "intent": {"required_phases": ["capture", "authoring", "export", "post"], "min_distinct_formats": 4, "min_distinct_ratios": 3, "chronology_buckets": ["early", "mid", "late"]},
            "candidate_selection": [
                "frame-lumen-0001", "frame-lumen-0002", "frame-lumen-0003", "frame-lumen-0004",
                "project-silent", "export-ghost", "post-orphan", "orchid-wide", "orchid-vertical", "orchid-square", "echo-third-party",
            ],
        },
    }
