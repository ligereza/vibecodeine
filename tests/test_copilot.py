from cultura.mak_plataforma.copilot import (build_suggestions, evaluate_feedback,
                                             learning_profile, media_manifest,
                                             normalize_inference)


def item(item_id, date="2026-08-08", description="", kind="story", publication=""):
    return {"id": item_id, "fecha": date, "descripcion_original": description,
            "tipo_contenido": kind, "publicacion_id": publication,
            "asset_path": "/portfolio-media/stories/a.mp4", "asset_available": True}


def test_emits_multiple_relation_hypotheses_for_one_candidate():
    source = item("a", description="luz cuerpo rave", publication="p1")
    candidate = item("b", description="luz cuerpo", publication="p1")
    rows, _ = build_suggestions(source, [candidate])
    assert {row["relation_type"] for row in rows} >= {"same_carousel", "same_date_context", "shared_concept"}


def test_feedback_changes_confidence_and_score():
    source = item("a", description="luz cuerpo")
    candidate = item("b", description="luz cuerpo")
    base = build_suggestions(source, [candidate])[0][0]
    learned = build_suggestions(source, [candidate], feedback=[
        {"source_id": "a", "target_id": "b", "action": "accept"}
    ])[0][0]
    assert learned["score"] > base["score"]
    assert learned["confidence"] == "confirmada"


def test_context_suppresses_redundant_facet():
    source = item("a", publication="p1")
    candidate = item("b", publication="p1")
    rows, suppressed = build_suggestions(source, [candidate], context={"facet": "publication"})
    assert rows
    assert all(row["facet"] != "publication" for row in rows)
    assert suppressed == 1


def test_board_scope_does_not_mix_explicit_artist_context():
    source = item("a", description="luz cuerpo")
    same = dict(item("b", description="luz cuerpo"), artista="Drefquila")
    other = dict(item("c", description="luz cuerpo"), artista="Ober")
    rows, suppressed = build_suggestions(
        source, [same, other], context={"facet": "artist", "value": "Drefquila"})
    assert rows
    assert {row["item_id"] for row in rows} == {"b"}
    assert suppressed >= 1


def test_learning_profile_is_bounded_and_facet_specific():
    rows = [{"facet": "artist", "action": "accept"}] * 20
    rows += [{"facet": "venue", "action": "reject"}] * 3
    profile = learning_profile(rows)
    assert profile["weights"]["artist"] == 8.0
    assert profile["weights"]["venue"] == -4.5
    assert profile["feedback_total"] == 23


def test_manifest_is_provider_neutral():
    manifest = media_manifest(item("a"))
    assert manifest["modality"] == "video"
    assert manifest["asset_available"] is True


def test_feedback_summary_is_a_real_measure():
    summary = evaluate_feedback([{"action": "accept"}, {"action": "reject"}])
    assert summary == {"counts": {"accept": 1, "correct": 0, "reject": 1, "ignore": 0},
                       "total": 2, "confirmed": 1, "rejected": 1}


def test_provider_inference_is_candidate_only_and_never_fact():
    result = normalize_inference({
        "hypotheses": [
            {"item_id": "b", "facet": "artist", "relation_type": "same_event",
             "reason": "evidence needs confirmation", "evidence": ["date"],
             "confidence": "medium"},
            {"item_id": "outside", "facet": "artist", "reason": "hallucination"},
            {"item_id": "b", "facet": "unknown", "reason": "invalid facet"},
        ],
        "unknowns": ["venue missing"],
    }, "a", ["b"])
    assert len(result["hypotheses"]) == 1
    assert result["hypotheses"][0]["status"] == "candidate"
    assert result["unknowns"] == ["venue missing"]
