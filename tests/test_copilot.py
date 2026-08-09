from cultura.mak_plataforma.copilot import (build_gtm_map, build_suggestions,
                                             evaluate_feedback, learning_profile,
                                             media_manifest, normalize_inference,
                                             normalize_vision)


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


def test_gtm_map_returns_topology_positions_and_declared_features():
    source = item("a", date="2026-08-08", description="luz cuerpo rave",
                  publication="p1")
    source["classification"] = {"ownership": "client", "format": "video"}
    candidate = item("b", date="2026-08-09", description="mar cuerpo",
                     publication="p2", kind="published_media")
    result = build_gtm_map([source, candidate], width=4, height=3)

    assert result["schema"] == "faro-gtm-map-v1"
    assert result["engine"] == "elastic_latent_grid"
    assert result["grid"] == {"width": 4, "height": 3}
    assert {row["item_id"] for row in result["items"]} == {"a", "b"}
    assert all(0 <= row["x"] <= 1 and 0 <= row["y"] <= 1
               for row in result["items"])
    assert "video" in next(row for row in result["items"]
                            if row["item_id"] == "a")["features"]


def test_gtm_map_keeps_varied_archive_from_collapsing_to_one_point():
    items = [item(str(index), date=f"2026-07-{index + 1:02d}",
                  description=f"concepto-{index} venue-{index % 5} artista-{index % 7}",
                  publication=f"publication-{index % 4}")
             for index in range(24)]
    result = build_gtm_map(items, width=6, height=4)
    xs = [row["x"] for row in result["items"]]
    ys = [row["y"] for row in result["items"]]

    assert max(xs) - min(xs) > 0.05
    assert max(ys) - min(ys) > 0.05


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


def test_visual_normalizer_keeps_observations_and_drops_entity_claims():
    result = normalize_vision({
        "features": {
            "visual_terms": ["violet liquid", "violet liquid"],
            "dominant_colors": ["#7b20d4"],
            "composition": ["centered vessel"],
            "motion_or_media": ["still image"],
            "artist": "invented name",
        },
        "unknowns": ["event unknown"], "confidence": "medium",
    }, "obra-a", "aws", ["posts/a.jpg"])

    assert result["schema"] == "faro-portfolio-vision-v1"
    assert result["features"]["visual_terms"] == ["violet liquid"]
    assert "artist" not in result["features"]
    assert result["unknowns"] == ["event unknown"]
    assert result["promotion"] == "none"


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
