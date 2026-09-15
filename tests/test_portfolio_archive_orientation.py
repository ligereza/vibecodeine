import pytest

from flujo.knowledge.portfolio_archive_orientation import (
    build_archive_orientation,
    validate_archive_orientation,
)


pytestmark = pytest.mark.flujo


def _archive():
    formats = []
    for format_id in ("declared-works", "documented-record", "observed-field", "practice-context"):
        formats.append({
            "format_id": format_id,
            "purpose": f"purpose {format_id}",
            "selection_rule": [f"rule={format_id}"],
            "item_ids": [f"{format_id}:1"],
            "omitted_count": 2 if format_id == "observed-field" else 0,
        })
    return {
        "schema": "mak-archive-portfolio-view-v1",
        "status": "draft_only",
        "source": {"path_hint": "iskvw/datos/archivo.json", "input_hash": "sha256:archive"},
        "formats": formats,
        "selection": {
            "selected_item_count": 4,
            "declared_work_count": 1,
            "documented_record_count": 1,
            "observed_field_count": 1,
            "practice_context_count": 1,
        },
        "reconciliation": {"source_piece_count": 8, "source_link_count": 5, "projected_link_count": 3, "omitted_piece_count": 4},
        "provenance": {
            "filename_is_not_authorship": True,
            "observed_text_is_not_author_statement": True,
            "unselected_source_items_remain_in_input": True,
        },
    }


def test_archive_orientation_keeps_four_epistemic_axes():
    result = build_archive_orientation(_archive())

    assert validate_archive_orientation(result) is True
    assert [axis["format_id"] for axis in result["axes"]] == [
        "declared-works", "documented-record", "observed-field", "practice-context"
    ]
    assert result["axes"][0]["role"] == "source_declared_work"
    assert result["axes"][3]["role"] == "code_technical_context_not_artwork"
    assert result["boundary"]["semantic_claim"] is False
    assert result["control"]["promotion"] == "none"


def test_archive_orientation_rejects_boundary_tamper():
    result = build_archive_orientation(_archive())
    result["boundary"]["semantic_claim"] = True

    with pytest.raises(ValueError, match="boundary"):
        validate_archive_orientation(result)
