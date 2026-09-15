from flujo.departments import rd_crosswalk, rd_cultura_relations, rd_summary, rd_topics
from flujo.knowledge.rd_read_only_context import (
    build_rd_read_only_context,
    validate_rd_read_only_context,
)


def _context():
    return build_rd_read_only_context(
        rd_summary("/home/mak"),
        rd_topics("/home/mak"),
        rd_crosswalk("/home/mak"),
        rd_cultura_relations("/home/mak"),
        generated_at="fixture",
    )


def test_rd_context_preserves_candidate_boundaries():
    payload = _context()
    assert validate_rd_read_only_context(payload)
    assert payload["read_only"] is True
    assert payload["boundary"] == {
        "crosswalk_is_review_only": True,
        "candidate_graph_is_unconfirmed": True,
        "identity_requires_explicit_provenance": True,
        "counts_are_checkout_local": True,
        "semantic_claim": False,
    }
    assert payload["control"]["execution"] is False


def test_rd_context_keeps_local_counts_visible():
    payload = _context()
    assert payload["topics"]["topic_count"] == 5
    assert payload["crosswalk"]["entity_count"] >= 0
    assert payload["relations"]["relation_count"] >= 0


def test_rd_context_rejects_crosswalk_promotion():
    payload = _context()
    payload["crosswalk"]["status"] = "promoted"
    try:
        validate_rd_read_only_context(payload)
    except ValueError as exc:
        assert str(exc) == "rd_context_crosswalk_invalid"
    else:
        raise AssertionError("promoted crosswalk was accepted")
