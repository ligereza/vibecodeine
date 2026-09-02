from cultura.mak_plataforma.copilot import (active_ordering_seed,
                                             build_gtm_map, build_suggestions,
                                             evaluate_feedback, group_suggestions,
                                             evidence_readiness,
                                             external_evidence_profile,
                                             inference_prompt,
                                             learning_profile,
                                             ordering_seed,
                                             review_profile,
                                             media_manifest, normalize_inference,
                                             inference_quality,
                                             normalize_vision,
                                             ordering_distance_profile,
                                             replay_ordering_evaluation,
                                             READINESS_SCHEMA,
                                             _vector_distance)

import json


def item(item_id, date="2026-08-08", description="", kind="story", publication=""):
    return {"id": item_id, "fecha": date, "descripcion_original": description,
            "tipo_contenido": kind, "publicacion_id": publication,
            "asset_path": "/portfolio-media/stories/a.mp4", "asset_available": True}


def test_inference_prompt_carries_saved_visual_observations_as_weak_evidence():
    source = item("a", description="visual para un show")
    source["vision_features"] = {
        "visual_terms": ["geometric grid"],
        "dominant_colors": ["violet"],
        "composition": ["central subject"],
        "motion_or_media": ["sampled frames show movement"],
    }
    payload = json.loads(inference_prompt(source, [item("b")]))
    assert payload["source"]["vision_observations"]["dominant_colors"] == ["violet"]
    assert payload["candidates"][0]["vision_observations"] == {}
    assert any("solo como señal" in rule for rule in payload["rules"])


def test_emits_multiple_relation_hypotheses_for_one_candidate():
    source = item("a", description="luz cuerpo rave", publication="p1")
    candidate = item("b", description="luz cuerpo", publication="p2")
    rows, _ = build_suggestions(source, [candidate])
    assert {row["relation_type"] for row in rows} >= {"same_date_context", "shared_concept"}


def test_feedback_changes_confidence_and_score():
    source = item("a", description="luz cuerpo")
    candidate = item("b", description="luz cuerpo")
    base = build_suggestions(source, [candidate])[0][0]
    learned = build_suggestions(source, [candidate], feedback=[
        {"source_id": "a", "target_id": "b", "action": "accept"}
    ])[0][0]
    assert learned["score"] > base["score"]
    assert learned["confidence"] == "confirmada"


def test_learning_ignores_repeated_portfolio_action_but_keeps_unpaired_signals():
    repeated = [{"source_id": "a", "target_id": "b", "action": "accept",
                 "facet": "text", "relation": "shared_concept"}] * 4
    profile = learning_profile(repeated)
    assert profile["feedback_total"] == 1
    assert profile["weights"]["text"] == 1.5


def test_discarded_or_rejected_candidates_leave_the_active_suggestion_set():
    source = item("a", description="luz cuerpo")
    discarded = item("b", description="luz cuerpo")
    rejected = item("c", description="luz cuerpo")
    rows, _ = build_suggestions(
        source, [discarded, rejected],
        selections={"b": {"decision": "descartar"}},
        feedback=[{"source_id": "a", "target_id": "c", "action": "reject"}],
    )
    assert rows == []


def test_visual_similarity_is_a_derived_channel_and_metadata_does_not_duplicate_it():
    source = item("a", description="luz cuerpo")
    visual_only = item("b", date="2026-08-07", description="otra cosa", kind="published_media")
    rows, _ = build_suggestions(source, [visual_only], visual_relations=[{
        "item_id": "b", "score": .61, "margin": .03, "eligible": True,
        "model": "MobileCLIP-S0", "model_version": "mobileclip_s0.pt",
    }])
    visual = next(row for row in rows if row["facet"] == "visual_similarity")
    assert visual["relation_type"] == "visual_similarity"
    assert visual["scope"] == "exploratory"
    assert visual["visual_score"] == .61
    assert visual["evidence"][0]["model"] == "MobileCLIP-S0"

    metadata = item("c", description="luz cuerpo")
    rows, _ = build_suggestions(source, [metadata], visual_relations=[{
        "item_id": "c", "score": .91, "margin": .1, "eligible": True,
    }])
    assert not any(row["facet"] == "visual_similarity" for row in rows)


def test_rejected_text_channel_does_not_hide_date_channel_for_same_pair():
    source = item("a", description="luz cuerpo")
    candidate = item("b", description="luz cuerpo")
    source["artist"] = ["Ober"]
    candidate["artist"] = ["Ober"]
    rows, _ = build_suggestions(source, [candidate], feedback=[{
        "source_id": "a", "target_id": "b", "action": "reject",
        "facet": "text", "relation": "shared_concept",
    }])

    assert "text" not in {row["facet"] for row in rows}
    assert "date" in {row["facet"] for row in rows}
    assert "artist" in {row["facet"] for row in rows}


def test_same_carousel_is_a_group_not_a_relation_candidate():
    source = item("a", description="luz cuerpo", publication="post:1")
    same_carousel = item("b", description="luz cuerpo", publication="post:1")
    different_post = item("c", description="luz cuerpo", publication="post:2")
    rows, _ = build_suggestions(source, [same_carousel, different_post])
    assert "b" not in {row["item_id"] for row in rows}
    assert "c" in {row["item_id"] for row in rows}


def test_suggestion_focus_can_switch_to_concept_channel():
    source = item("a", description="luz cuerpo")
    candidate = item("b", description="luz cuerpo")
    rows, _ = build_suggestions(source, [candidate], focus_facet="concept")
    assert rows
    assert {row["facet"] for row in rows} == {"text"}


def test_gtm_map_returns_topology_positions_and_declared_features():
    source = item("a", date="2026-08-08", description="luz cuerpo rave",
                  publication="p1")
    source["classification"] = {"ownership": "client", "format": "video"}
    source["selection"] = "seleccionar"
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
    assert result["ordering"]["counts"]["work"] == 1
    assert result["ordering"]["coverage"] == 0.5
    assert result["ordering"]["missing_labels"] == ["record", "review", "discard"]
    prediction = next(row for row in result["items"] if row["item_id"] == "b")["triage_prediction"]
    assert prediction["evidence_count"] == 1
    assert prediction["confidence"] == "baja"
    assert prediction["learning_ready"] is True
    assert result["ordering"]["field"]["schema"] == "faro-ordering-field-v1"


def test_ordering_profile_uses_human_triage_and_selection_as_learning_signal():
    items = [item("a"), item("b"), item("c")]
    items[0]["classification"] = {"triage": "record"}
    items[1]["selection"] = "descartar"
    profile = build_gtm_map(items, width=3, height=3)["ordering"]

    assert profile["schema"] == "faro-ordering-learning-v1"
    assert profile["counts"] == {"work": 0, "record": 1, "review": 0, "discard": 1}
    assert profile["labeled"] == 2


def test_stable_gtm_topology_ignores_live_triage_for_repeat_review_passes():
    items = [item("a", description="luz cuerpo", publication="p1"),
             item("b", description="luz cuerpo", publication="p2")]
    first = build_gtm_map(items, stable_topology=True, width=3, height=3)
    items[0]["selection"] = "seleccionar"
    items[0]["classification"] = {"triage": "work"}
    second = build_gtm_map(items, stable_topology=True, width=3, height=3)

    first_positions = {row["item_id"]: (row["x"], row["y"])
                       for row in first["items"]}
    second_positions = {row["item_id"]: (row["x"], row["y"])
                        for row in second["items"]}
    assert first_positions == second_positions
    assert first["atlas"]["topology_id"] == second["atlas"]["topology_id"]
    assert first["atlas"]["learning_revision"] != second["atlas"]["learning_revision"]
    assert second["ordering"]["mode"] == "stable_topology_live_field"
    assert second["ordering"]["field"]["moves_geometry"] is False
    assert second["ordering"]["field"]["method"] == (
        "adaptive_pair_metric_on_stable_topology")
    assert second["ordering"]["counts"]["work"] == 1
    assert second["ordering"]["evaluation"]["automation_ready"] is False
    prediction = next(row for row in second["items"]
                      if row["item_id"] == "b")["triage_prediction"]
    assert prediction["evidence_count"] == 1
    assert prediction["information_gain"] > 0


def test_distance_profile_stays_identity_without_pair_contrast():
    items = [item("a"), item("b")]
    items[0]["classification"] = {"triage": "work"}
    profile = ordering_distance_profile(items, vectors={
        "a": [1.0] + [0.0] * 31,
        "b": [0.0, 1.0] + [0.0] * 30,
    })

    assert profile["method"] == "identity"
    assert profile["metric_ready"] is False
    assert profile["weights"] == [1.0] * 32


def test_distance_profile_learns_bounded_pair_contrast_without_moving_atlas():
    items = [item("a"), item("b"), item("c"), item("d")]
    items[0]["classification"] = {"triage": "work"}
    items[1]["classification"] = {"triage": "work"}
    items[2]["classification"] = {"triage": "discard"}
    items[3]["classification"] = {"triage": "discard"}
    vectors = {
        "a": [1.0, 0.0] + [0.0] * 30,
        "b": [1.0, 0.0] + [0.0] * 30,
        "c": [0.0, 1.0] + [0.0] * 30,
        "d": [0.0, 1.0] + [0.0] * 30,
    }
    profile = ordering_distance_profile(items, vectors=vectors)

    assert profile["method"] == "pair_contrast"
    assert profile["pair_support"]["positive"] == 2
    assert profile["pair_support"]["negative"] == 4
    assert profile["weights"][0] > 1.0
    assert profile["weights"][1] > 1.0
    assert all(0.55 <= weight <= 1.8 for weight in profile["weights"])
    assert _vector_distance(vectors["a"], vectors["c"], profile["weights"]) > _vector_distance(vectors["a"], vectors["c"])


def test_ordering_seed_balances_unlabeled_records_without_assigning_labels():
    items = [item(str(index), date=f"2026-0{index % 3 + 1}-01",
                  kind="story" if index % 2 else "published_media")
             for index in range(12)]
    items[0]["classification"] = {"triage": "work"}
    items[1]["selection"] = "descartar"
    items[2]["vision_features"] = {"visual_terms": ["violet"]}

    seed = ordering_seed(items, limit=6)

    assert len(seed) == 6
    assert all(row["status"] == "human_candidate" for row in seed)
    assert all(row["review_scope"] == "record_or_review" for row in seed)
    assert {row["item_id"] for row in seed}.isdisjoint({"0", "1"})


def test_active_ordering_seed_prioritizes_uncertainty_without_splitting_carousel():
    items = [item("labeled", publication="p0"),
             item("a", publication="p1"),
             item("b", publication="p2"),
             item("c", publication="p2"),
             item("d", publication="p3")]
    items[0]["classification"] = {"triage": "work"}
    positions = []
    for index, current in enumerate(items):
        positions.append({
            "item_id": current["id"], "x": index / 5, "y": (index % 2) / 2,
            "triage_prediction": {
                "probabilities": {"work": 0.25, "record": 0.25,
                                  "review": 0.25, "discard": 0.25},
                "uncertainty": 1.0 if current["id"] == "d" else 0.7,
                "coverage_gap": 0.9 if current["id"] == "d" else 0.4,
            },
        })

    seed = active_ordering_seed(items, {"items": positions}, limit=3)

    assert seed[0]["item_id"] == "d"
    assert "labeled" not in {row["item_id"] for row in seed}
    assert len({row["publication_id"] for row in seed}) == len(seed)
    assert next(row for row in seed if row["publication_id"] == "p2")[
        "publication_media_count"] == 2
    assert all(row["selection_method"] == "active_information_gain"
               for row in seed)
    assert all(row["reason"] in {
        "zona_sin_cobertura", "frontera_ambigua", "muestra_diversa"}
        for row in seed)


def test_ordering_seed_does_not_fallback_to_media_without_a_visible_asset():
    items = [item("missing"), item("visible")]
    items[0]["asset_available"] = False
    seed = ordering_seed(items, limit=2)

    assert [row["item_id"] for row in seed] == ["visible"]


def test_ordering_seed_does_not_split_a_carousel_after_one_member_is_labeled():
    labeled = item("labeled", publication="post:1")
    labeled["classification"] = {"triage": "work"}
    sibling = item("sibling", publication="post:1")
    separate = item("separate", publication="post:2")

    seed = ordering_seed([labeled, sibling, separate], limit=4)

    assert "sibling" not in {row["item_id"] for row in seed}
    assert "separate" in {row["item_id"] for row in seed}


def test_ordering_evaluation_separates_active_learning_from_automation():
    items = [item(str(index), description="grupo %s" % (index % 2),
                  publication="p%s" % index) for index in range(8)]
    for index, current in enumerate(items):
        current["classification"] = {
            "triage": "work" if index % 2 else "record"}

    evaluation = build_gtm_map(
        items, stable_topology=True, width=3, height=3)["ordering"]["evaluation"]

    assert evaluation["evaluated"] == 8
    assert evaluation["active_learning_ready"] is True
    assert evaluation["automation_ready"] is False
    assert evaluation["missing_classes"] == ["review", "discard"]
    assert evaluation["automation_gate"]["minimum_labels"] == 100


def test_replay_ordering_evaluation_holds_out_each_human_answer_and_abstains():
    items = [item(str(index), description=f"grupo {index // 2}")
             for index in range(8)]
    labels = ["work", "work", "record", "record",
              "review", "review", "discard", "discard"]
    vectors = {}
    for index, (current, label) in enumerate(zip(items, labels)):
        current["classification"] = {"triage": label}
        vectors[current["id"]] = [float(index // 2), float(index % 2)]

    replay = replay_ordering_evaluation(items, vector_by_id=vectors)

    assert replay["schema"] == "faro-ordering-replay-v1"
    assert replay["evaluated"] == 8
    assert replay["committed"] + replay["abstained"] == 8
    assert replay["support"] == {
        "work": 2, "record": 2, "review": 2, "discard": 2,
    }
    assert replay["source_counts"] == {"triage": 8, "selection": 0}
    assert replay["metrics_by_source"]["selection"]["evaluated"] == 0
    assert replay["promotion"] == "none"
    assert all(case["item_id"] not in case["neighbors"]
               for case in replay["cases"])


def test_replay_ordering_evaluation_can_return_metrics_without_case_payload():
    items = [item("a"), item("b"), item("c")]
    for current, label in zip(items, ("work", "record", "review")):
        current["classification"] = {"triage": label}

    replay = replay_ordering_evaluation(items, include_cases=False)

    assert replay["cases"] == []
    assert replay["evaluated"] == 3
    assert 0.0 <= replay["abstention_rate"] <= 1.0


def test_replay_ordering_evaluation_keeps_selection_separate_from_triage():
    items = [item("triage"), item("selected"), item("discarded")]
    items[0]["classification"] = {"triage": "record"}
    items[1]["selection"] = "seleccionar"
    items[2]["selection"] = "descartar"

    replay = replay_ordering_evaluation(items)

    assert replay["source_counts"] == {"triage": 1, "selection": 2}
    assert replay["metrics_by_source"]["triage"]["evaluated"] == 1
    assert replay["metrics_by_source"]["selection"]["support"] == {
        "work": 1, "record": 0, "review": 0, "discard": 1,
    }


def test_external_evidence_profile_counts_yield_without_promotion():
    profile = external_evidence_profile([
        {"item_id": "a", "provider": "watsonx",
         "inference": {"hypotheses": [{"item_id": "b"}], "unknowns": ["date"]}},
        {"item_id": "a", "provider": "aws", "inference": {"hypotheses": []}},
    ], [
        {"item_id": "a", "confidence": "high", "evidence_kind": "still_image"},
    ])

    assert profile["external_unique_items"] == 1
    assert profile["cross_provider_items"] == 1
    assert profile["normalized_hypotheses"] == 1
    assert profile["unknowns"] == 1
    assert profile["promotion"] == "none"


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


def test_gtm_map_reports_when_large_archive_fit_is_sampled():
    items = [item(str(index), description=f"concepto-{index}")
             for index in range(1100)]
    result = build_gtm_map(items, width=4, height=3)

    assert result["fit"]["total"] == 1100
    assert result["fit"]["sampled"] is True
    assert result["count"] == 1100


def test_context_suppresses_redundant_facet():
    source = item("a", publication="p1")
    candidate = item("b", publication="p1")
    rows, suppressed = build_suggestions(source, [candidate], context={"facet": "publication"})
    assert rows == []
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


def test_explicit_entity_relations_are_separate_from_text_hypotheses():
    source = item("a", description="luz cuerpo", date="2026-08-08")
    source["artista"] = "Drefquila"
    source["venue"] = "Sala Metronomo"
    candidate = item("b", description="luz cuerpo", date="2026-08-09")
    candidate["artista"] = "Drefquila"
    candidate["venue"] = "Sala Metronomo"
    rows, _ = build_suggestions(source, [candidate])

    artist = next(row for row in rows if row["relation_type"] == "same_artist")
    assert artist["scope"] == "declared"
    assert artist["space"] == "evidence"
    assert artist["evidence"][0]["kind"] == "declared_metadata"
    assert artist["evidence"][0]["values"] == ["Drefquila"]
    assert artist["score"] > next(row for row in rows
                                   if row["relation_type"] == "shared_concept")["score"]
    concept = next(row for row in rows if row["relation_type"] == "shared_concept")
    assert concept["space"] == "resonance"


def test_group_suggestions_keeps_multiple_channels_on_one_candidate():
    rows, _ = build_suggestions(
        dict(item("a", description="luz cuerpo", publication="p1"),
             artista="Drefquila"),
        [dict(item("b", description="luz cuerpo", publication="p2"),
              artista="Drefquila")])

    groups = group_suggestions(rows)

    assert len(groups) == 1
    assert groups[0]["item_id"] == "b"
    assert groups[0]["relation_count"] >= 3
    assert {relation["facet"] for relation in groups[0]["relations"]} >= {
        "date", "artist", "text"}
    assert groups[0]["scope"] == "declared"
    assert groups[0]["space"] == "evidence"
    assert set(groups[0]["spaces"]) == {"evidence", "resonance"}


def test_learning_profile_is_bounded_and_facet_specific():
    rows = [{"facet": "artist", "action": "accept"}] * 20
    rows += [{"facet": "venue", "action": "reject"}] * 3
    profile = learning_profile(rows)
    assert profile["weights"]["artist"] == 8.0
    assert profile["weights"]["venue"] == -4.5
    assert profile["feedback_total"] == 23


def test_review_profile_preserves_decisions_and_human_context():
    profile = review_profile([
        {"source_id": "paper-a", "decision": "accept",
         "context_fields": {"process": ["croquera", "croquera"]}},
        {"source_id": "shared-b", "decision": "reject",
         "context_fields": {}},
        {"source_id": "story-c", "decision": "revise",
         "context_fields": {"event": ["festival"]}},
    ])

    assert profile["decision_counts"] == {"accept": 1, "revise": 1, "reject": 1}
    assert profile["decision_total"] == 3
    assert profile["by_facet"]["process"]["accept"] == 1
    assert profile["by_facet"]["candidate"]["reject"] == 1
    assert profile["context_signals"]["process"]["croquera"]["accept"] == 1
    assert profile["reviewed_sources"] == ["paper-a", "shared-b", "story-c"]


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


def test_inference_quality_revises_empty_provider_output():
    assert inference_quality({"hypotheses": [], "unknowns": ["date"]}) == {
        "verdict": "revise",
        "reason": "no_evidenced_hypotheses",
        "valid_hypotheses": 0,
        "missing_evidence": [],
        "promotion": "none",
    }


def test_inference_quality_keeps_only_evidenced_hypotheses_ready_for_human_gate():
    quality = inference_quality({"hypotheses": [
        {"item_id": "b", "evidence": ["fecha"], "facet": "date"},
        {"item_id": "c", "evidence": [], "facet": "artist"},
    ]})
    assert quality["verdict"] == "revise"
    assert quality["valid_hypotheses"] == 1
    assert quality["missing_evidence"] == ["c"]
    assert quality["promotion"] == "none"


# ---------------------------------------------------------------------------
# Evidence readiness: what a record has and lacks before a human labels it
# ---------------------------------------------------------------------------
#
# Added 2026-09-02 from a measurement, not a hunch. Of 7044 records, 116 are
# labelled and 6928 are not, and the ordering model predicts none of them with
# high confidence (alta=0, media=4156, baja=2772), so every case is still a
# human look. The frontier rows already carried has_description / has_vision /
# review_scope and the interface read none of them: the operator decided
# without seeing what the case contained, and `review` -- the label that means
# "not decidable yet" -- was used once in 116 decisions.


def _record(**overrides):
    row = {
        "source_id": "x.jpg", "asset_available": True, "asset_path": "/p/x.jpg",
        "description": "una pieza", "date": "2021-10-03",
        "classification": {}, "work_group": None,
    }
    row.update(overrides)
    return row


def _status(report, channel):
    return next(row["status"] for row in report["channels"]
                if row["channel"] == channel)


def test_readiness_separates_not_measured_from_measured_absent():
    """`unknown` and `absent` are different claims and must not collapse.

    The perception index covered 100 of 7044 records, so a missing vision row
    is almost always "not indexed", not "this record has no perception".
    Reading that absence as a finding is how a gap becomes a fact.
    """
    outside = evidence_readiness(_record(), vision=None,
                                         vision_indexed=["other.jpg"])
    assert _status(outside, "perception") == "unknown"
    assert "perception" in outside["unmeasured"]
    assert "perception" not in outside["missing"]

    indexed = evidence_readiness(_record(), vision=None,
                                         vision_indexed=["x.jpg"])
    assert _status(indexed, "perception") == "absent"
    assert "perception" in indexed["missing"]

    seen = evidence_readiness(
        _record(), vision={"features": {"a": 1}, "confidence": "low"},
        vision_indexed=["x.jpg"])
    assert _status(seen, "perception") == "present"


def test_readiness_abstains_when_the_minimum_is_missing():
    """No asset or no description means the label has nothing to rest on."""
    blind = evidence_readiness(_record(asset_available=False,
                                               description=""))
    assert blind["decision"] == "abstain"
    assert blind["blocking"] == ["asset", "description"]
    assert "review" in blind["next_action"]
    assert "review" in blind["labels"]


def test_readiness_never_promotes_and_keeps_the_human_as_owner():
    """A readout is not a decision. It says what is there, nothing more."""
    for report in (evidence_readiness(_record()),
                   evidence_readiness(_record(asset_available=False))):
        assert report["promotion"] == "none"
        assert report["owner"] == "human"
        assert report["producer"] == "local_readiness_report"
        assert report["next_action"].strip()
        assert report["schema"] == READINESS_SCHEMA


def test_readiness_reports_reservations_without_blocking_the_label():
    """Missing enrichment is declared, not resolved, and does not stop a
    defensible label from being possible."""
    report = evidence_readiness(_record(), relations=[{"item_id": "y"}])
    assert report["decision"] == "decidable_con_reservas"
    assert report["blocking"] == []
    assert set(report["missing"]) == {"classification", "work_group"}
    assert _status(report, "relations") == "present"
    assert "relacion" in next(row["detail"] for row in report["channels"]
                              if row["channel"] == "relations")


def test_readiness_survives_a_record_it_cannot_read():
    """Fail closed: an unusable record reports unknowns, never invented values."""
    report = evidence_readiness(None)
    assert report["decision"] == "abstain"
    assert report["item_id"] == ""
    assert all(row["status"] in ("present", "absent", "unknown")
               for row in report["channels"])
