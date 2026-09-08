from pathlib import Path

from cultura.mak_post.pipeline import (build_post_package, load_post_spec,
                                        validate_post_package)


def test_post_requires_source_preservation_and_text_blocks():
    spec = {
        "post_id": "post-test",
        "source_document": "source.pdf",
        "source_integrity": {
            "source_order_preserved": True,
            "text_blocks_preserved_verbatim": True,
        },
        "slides": [{"text_blocks": ["source text"]}],
    }
    assert validate_post_package(spec) == []
    assert build_post_package(spec)["status"] == "candidate"


def test_post_never_accepts_missing_source_text_as_ready():
    spec = {"post_id": "post-test", "slides": [{}]}
    result = build_post_package(spec)
    assert result["status"] == "rejected"
    assert "missing:source_document" in result["errors"]


def test_recovered_chemsex_spec_is_a_valid_candidate():
    path = (Path(__file__).resolve().parents[1] / "docs" / "recovered" /
            "claude_sessions_2026-08-12" / "raw" /
            "rd_post_chemsex_spec_2026-08-11.json")
    result = build_post_package(load_post_spec(path))
    assert result["status"] == "candidate"
    assert result["public_gate"] == "human_required"
