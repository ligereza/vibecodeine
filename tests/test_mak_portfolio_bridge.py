from pathlib import Path

import json

import pytest

from cultura.mak_plataforma.contrato_archivo import (
    desde_convocatoria_seed,
    normalize_portfolio_candidate,
    portfolio_identity_graph,
    portfolio_metadata_index,
    portfolio_candidate_verdict,
    mesa_scene,
)
from cultura.mak_plataforma import hub


def test_mesa_scene_deduplicates_targets_and_keeps_relations_as_edges():
    source = {"id": "source", "tipo_contenido": "published_media",
              "fecha": "2026-08-08", "asset_path": "/source.jpg",
              "asset_available": True}
    target = {"id": "target", "tipo_contenido": "story",
              "fecha": "2026-08-08", "asset_path": "/target.mp4",
              "asset_available": True, "record_kind": "story_record"}
    scene = mesa_scene(source, [target], [
        {"item_id": "target", "facets": ["date"],
         "relation_type": "same_date_context", "feedback": "pendiente",
         "scope": "declared", "space": "evidence",
         "evidence": [{"kind": "instagram_metadata"}],
         "note": "nota de prueba"},
        {"item_id": "target", "facets": ["format"],
         "relation_type": "same_media_role", "feedback": "pendiente"},
    ])

    assert scene["schema"] == "faro-portfolio-scene-v1"
    assert [row["source_id"] for row in scene["records"]] == ["source", "target"]
    assert len(scene["relations"]) == 1
    assert scene["relations"][0]["channels"] == ["date", "format"]
    assert scene["relations"][0]["note"] == "nota de prueba"
    assert scene["relations"][0]["space"] == "evidence"
    assert scene["relations"][0]["spaces"] == ["evidence"]
    assert scene["interaction"] == {
        "camera_drag": True, "node_drag": False,
        "duplicate_targets": False, "decision_surface": "map_hud",
        "projection": "gtm", "feedback_updates_topology": False,
        "learning_surface": "live_field_over_stable_atlas",
    }


def test_mesa_scene_does_not_reintroduce_discarded_target():
    source = {"id": "source", "tipo_contenido": "published_media",
              "asset_available": True}
    discarded = {"id": "discarded", "tipo_contenido": "story",
                 "selection": "descartar", "asset_available": True}
    scene = mesa_scene(source, [discarded], [
        {"item_id": "discarded", "facets": ["date"],
         "relation_type": "same_date_context", "feedback": "pendiente"},
    ])

    assert [row["source_id"] for row in scene["records"]] == ["source"]
    assert scene["relations"] == []


def test_mesa_scene_exposes_carousel_as_one_publication_group():
    source = {"id": "source", "tipo_contenido": "published_media",
              "publicacion_id": "post:1", "medio_indice": 0,
              "medio_total": 2, "asset_available": True}
    sibling = {"id": "sibling", "tipo_contenido": "published_media",
               "publicacion_id": "post:1", "medio_indice": 1,
               "medio_total": 2, "asset_available": True}
    scene = mesa_scene(source, [sibling], [])

    group = scene["records"][0]["publication_group"]
    assert [row["source_id"] for row in scene["records"]] == ["source"]
    assert group["id"] == "post:1"
    assert group["count"] == 2
    assert [row["source_id"] for row in group["media"]] == ["source", "sibling"]


def test_mesa_scene_groups_accepted_same_work_feedback():
    source = {"id": "source", "tipo_contenido": "published_media",
              "asset_path": "/source.jpg", "asset_available": True}
    target = {"id": "target", "tipo_contenido": "published_media",
              "asset_path": "/target.jpg", "asset_available": True}
    scene = mesa_scene(source, [target], [{
        "item_id": "target", "facets": ["text"],
        "relation_type": "shared_concept", "feedback": "accept",
        "feedback_facet": "obra",
    }])

    assert scene["records"][0]["work_group"]["label"] == "misma obra"
    assert scene["records"][0]["work_group"]["count"] == 2
    assert scene["relations"][0]["feedback_facet"] == "obra"
    assert "obra" in scene["relations"][0]["channels"]


def test_mesa_scene_collapses_candidate_carousel_members_into_one_target():
    source = {"id": "source", "tipo_contenido": "story", "asset_available": True}
    first = {"id": "first", "tipo_contenido": "published_media",
             "publicacion_id": "post:2", "medio_indice": 0, "medio_total": 3,
             "asset_path": "/first.jpg", "asset_available": True}
    second = {"id": "second", "tipo_contenido": "published_media",
              "publicacion_id": "post:2", "medio_indice": 1, "medio_total": 3,
              "asset_path": "/second.jpg", "asset_available": True}
    scene = mesa_scene(source, [first, second], [
        {"item_id": "first", "facets": ["date"], "relation_type": "same_date_context"},
        {"item_id": "second", "facets": ["text"], "relation_type": "shared_concept"},
    ])

    assert [row["source_id"] for row in scene["records"]] == ["source", "first"]
    assert scene["records"][1]["publication_group"]["count"] == 2
    assert len(scene["relations"]) == 1
    assert scene["relations"][0]["member_ids"] == ["first", "second"]


def test_hub_scene_uses_existing_inbox_and_copilot_groups(monkeypatch):
    items = [{"id": "source", "tipo_contenido": "published_media",
              "asset_available": True},
             {"id": "target", "tipo_contenido": "story",
              "record_kind": "story_record", "asset_available": True}]
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: next(
        (row for row in items if row["id"] == item_id), None))
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": items})
    monkeypatch.setattr(hub, "_portfolio_apply_human_context", lambda rows: rows)
    monkeypatch.setattr(hub, "_portfolio_suggestions", lambda _item_id, **_kwargs: {
        "provider": "local_hypothesis_engine", "learning": {},
        "map": {"schema": "faro-gtm-map-v1", "engine": "elastic_latent_grid",
                "fit": {"total": 2}, "ordering": {"labeled": 2}, "items": [
                    {"item_id": "source", "x": 0.2, "y": 0.3,
                     "confidence": "high"},
                    {"item_id": "target", "x": 0.8, "y": 0.7,
                     "confidence": "medium"},
                ]},
        "suggestion_groups": [{"item_id": "target", "facets": ["date"],
                                "relation_type": "same_date_context"}],
    })

    scene = hub._portfolio_scene("source", limit=10)

    assert scene["ok"] is True
    assert scene["active_id"] == "source"
    assert [row["source_id"] for row in scene["records"]] == ["source", "target"]
    assert scene["relations"][0]["target_id"] == "target"
    assert scene["map"]["engine"] == "elastic_latent_grid"
    assert scene["learning"]["ordering"]["labeled"] == 2
    assert {row["item_id"] for row in scene["map"]["items"]} == {"source", "target"}


def test_hub_order_scene_uses_stable_map_without_relation_engine(monkeypatch):
    items = [{"id": "source", "tipo_contenido": "published_media",
              "asset_available": True, "publicacion_id": "post:source"},
             {"id": "target", "tipo_contenido": "story",
              "asset_available": True, "publicacion_id": "story:target"}]
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: next(
        (row for row in items if row["id"] == item_id), None))
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": items})
    monkeypatch.setattr(hub, "_portfolio_apply_human_context", lambda rows: rows)
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [])
    monkeypatch.setattr(hub, "_portfolio_suggestions",
                        lambda *args, **kwargs: pytest.fail(
                            "order surface must not build relation hypotheses"))
    monkeypatch.setattr(hub.copilot, "build_gtm_map", lambda *args, **kwargs: {
        "schema": "faro-gtm-map-v1", "engine": "elastic_latent_grid",
        "fit": {"total": 2}, "ordering": {"mode": "stable_topology"},
        "items": [{"item_id": "source", "x": 0.2, "y": 0.3},
                  {"item_id": "target", "x": 0.3, "y": 0.35}],
    })

    scene = hub._portfolio_scene("source", limit=10, surface="order")

    assert scene["provider"] == "gtm_order_projection"
    assert [row["source_id"] for row in scene["records"]] == ["source", "target"]
    assert scene["relations"][0]["relation_type"] == "map_neighbor"
    assert scene["relations"][0]["space"] == "topology"
    assert scene["relations"][0]["evidence"] == []


def test_portfolio_file_stays_inside_iskvw_root(tmp_path, monkeypatch):
    root = tmp_path / "iskvw"
    root.mkdir()
    (root / "editor.html").write_text("<html>", encoding="utf-8")
    (root / "datos").mkdir()
    (root / "datos" / "campo.json").write_text("{}", encoding="utf-8")
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(root))

    assert Path(hub._portfolio_file("editor.html")).name == "editor.html"
    assert Path(hub._portfolio_file("datos/campo.json")).name == "campo.json"
    assert hub._portfolio_file("../secret.txt") is None
    assert hub._portfolio_file("missing.json") is None


def test_portfolio_selection_is_idempotent_for_repeated_same_action(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox.json"
    inbox.write_text(json.dumps({"items": [{
        "id": "story-a", "tipo_contenido": "story", "asset_available": True,
    }]}), encoding="utf-8")
    selections = tmp_path / "selections.jsonl"
    classifications = tmp_path / "classifications.jsonl"
    vision = tmp_path / "vision.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(inbox))
    monkeypatch.setattr(hub, "PORTFOLIO_SELECTIONS", str(selections))
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(classifications))
    monkeypatch.setattr(hub, "PORTFOLIO_VISION", str(vision))
    monkeypatch.setattr(hub, "_ledger", None)

    first = hub._portfolio_select(
        "story-a", "descartar", decision_scope="record",
        reason_code="no_es_obra", target_id="story-a", note="registro")
    second = hub._portfolio_select(
        "story-a", "descartar", decision_scope="record",
        reason_code="no_es_obra", target_id="story-a", note="registro")

    assert first["ok"] is True
    assert second["duplicate"] is True
    assert len(selections.read_text(encoding="utf-8").splitlines()) == 1


def test_portfolio_classification_is_idempotent_but_preserves_new_axes(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox.json"
    inbox.write_text(json.dumps({"items": [{
        "id": "story-a", "tipo_contenido": "story", "asset_available": True,
    }]}), encoding="utf-8")
    classifications = tmp_path / "classifications.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(inbox))
    monkeypatch.setattr(hub, "PORTFOLIO_SELECTIONS", str(tmp_path / "selections.jsonl"))
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(classifications))
    monkeypatch.setattr(hub, "PORTFOLIO_VISION", str(tmp_path / "vision.jsonl"))
    monkeypatch.setattr(hub, "_ledger", None)

    first = hub._portfolio_classify({
        "item_id": "story-a", "fields": {"triage": "work"},
    })
    second = hub._portfolio_classify({
        "item_id": "story-a", "fields": {"triage": "work"},
    })
    third = hub._portfolio_classify({
        "item_id": "story-a", "fields": {"triage": "work", "lane": "rd"},
    })

    assert first["ok"] is True
    assert second["duplicate"] is True
    assert third["classification"] == {"triage": "work", "lane": "rd"}
    assert len(classifications.read_text(encoding="utf-8").splitlines()) == 2


def test_director_surface_exposes_system_capabilities_without_secret_values():
    surface = hub._director_capabilities()

    assert surface["schema"] == "faro-director-capabilities-v1"
    assert surface["work_schema"] == "mak-work-v1"
    assert surface["decisions"] == ["hacer", "revisar", "refutar", "archivar", "descartar"]
    assert surface["routes"]["visual"]["capability"] == "vision"
    assert all("api_key" not in json.dumps(row).lower()
               for row in surface["providers"]["providers"])


def test_director_decision_is_a_projection_until_explicit_persistence():
    result = hub._director_decision({
        "area": "rd_evidence",
        "payload": {"items": [{
            "claim": "source missing", "evidence": [], "files": [],
            "confidence": "medium", "action": "verify_source",
        }]},
    })

    assert result["ok"] is True
    assert result["persisted"] is False
    assert result["record"]["decision"] == "revisar"
    assert result["record"]["promotion"] == "none"


def test_portfolio_organism_projects_existing_data_without_duplication(monkeypatch):
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": [
        {"id": "story-a", "tipo_contenido": "story", "fecha": "2025-12-05",
         "publicacion_id": "pub-a", "descripcion_original": "Ober en vivo",
         "asset_path": "/portfolio-media/stories/a.mp4", "asset_available": True,
         "selection": "pendiente"},
        {"id": "post-b", "tipo_contenido": "published_media", "fecha": "2025-12-05",
         "publicacion_id": "pub-b", "descripcion_original": "visual",
         "asset_path": "/portfolio-media/posts/b.jpg", "asset_available": True,
         "selection": "seleccionar"},
    ]})
    monkeypatch.setattr(hub, "_portfolio_boards", lambda: {"boards": [{
        "id": "tablero-obra", "name": "Ober", "facet": "artist",
        "value": "Ober", "item_ids": ["story-a", "missing-item"],
    }]})
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [{
        "source_id": "story-a", "target_id": "post-b", "action": "accept",
        "facet": "date", "relation": "same_date_context",
        "board_id": "tablero-obra",
    }])
    monkeypatch.setattr(hub, "_portfolio_jsonl", lambda _path: [{
        "source_id": "story-a", "target_id": "post-b",
        "relation": "same_date_context",
    }])

    projection = hub._portfolio_organism_projection()

    assert projection["schema"] == "faro-portfolio-organism-v1"
    assert projection["mode"] == "projection_only"
    assert {row["id"] for row in projection["blocks"]} == {"story-a", "post-b"}
    assert projection["blocks"][0]["record_kind"] == "story_record"
    assert projection["blocks"][0]["contract"]["schema"] == "faro-portfolio-entity-v1"
    assert projection["blocks"][0]["contract"]["format"] == "registro"
    assert projection["blocks"][0]["contract"]["next_action"] == "review"
    assert projection["blocks"][0]["contract"]["owner"] == "human"
    assert projection["blocks"][0]["contract"]["consent"]["status"] == "unknown"
    assert projection["blocks"][0]["contract"]["publication"]["status"] == "private_candidate"
    assert projection["blocks"][0]["contract"]["publication"]["requires_human_gate"] is True
    assert projection["blocks"][1]["contract"]["next_action"] == "triangulate"
    assert projection["blocks"][1]["contract"]["owner"] == "MAK"
    assert projection["projection_contract"]["layers"]["archive"] == "source_of_truth"
    assert projection["publication_policy"]["requires_recorded_consent"] is True
    assert projection["publication_policy"]["requires_human_gate"] is True
    assert projection["channels"][0]["block_ids"] == ["story-a"]
    assert projection["connections"][0]["origin"] == "human"
    assert projection["connections"][0]["confidence"] == "high"
    assert projection["decisions"][0]["facet"] == "date"


def test_portfolio_organism_hides_only_the_rejected_relation_channel(monkeypatch):
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": [
        {"id": "a", "tipo_contenido": "story"},
        {"id": "b", "tipo_contenido": "story"},
    ]})
    monkeypatch.setattr(hub, "_portfolio_boards", lambda: {"boards": []})
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [{
        "source_id": "a", "target_id": "b", "action": "reject",
        "facet": "text", "relation": "shared_concept",
    }])
    monkeypatch.setattr(hub, "_portfolio_jsonl", lambda path: [
        {"source_id": "a", "target_id": "b", "relation": "same_event"},
        {"source_id": "a", "target_id": "b", "relation": "shared_concept"},
    ])

    projection = hub._portfolio_organism_projection()

    assert [row["relation"] for row in projection["connections"]] == ["same_event"]


def test_hub_scene_keeps_feedback_channels_separate_for_one_target(monkeypatch):
    items = [
        {"id": "source", "tipo_contenido": "story", "asset_available": True},
        {"id": "target", "tipo_contenido": "published_media", "asset_available": True},
    ]
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: next(
        (row for row in items if row["id"] == item_id), None))
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": items})
    monkeypatch.setattr(hub, "_portfolio_apply_human_context", lambda rows: rows)
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [
        {"source_id": "source", "target_id": "target", "action": "accept",
         "facet": "date", "relation": "same_date_context", "note": "mismo dia"},
        {"source_id": "source", "target_id": "target", "action": "reject",
         "facet": "text", "relation": "shared_concept", "note": "texto insuficiente"},
    ])
    monkeypatch.setattr(hub, "_portfolio_suggestions", lambda *args, **kwargs: {
        "provider": "local_hypothesis_engine", "learning": {},
        "map": {"schema": "faro-gtm-map-v1", "engine": "elastic_latent_grid",
                "fit": {"total": 2}, "ordering": {}, "items": []},
        "suggestion_groups": [{"item_id": "target", "facets": ["date", "text"],
                                "relation_type": "same_date_context"}],
    })

    scene = hub._portfolio_scene("source")

    relation = scene["relations"][0]
    assert relation["status"] == "accepted"
    assert {row["facet"] for row in relation["decisions"]} == {"date", "text"}
    assert {row["action"] for row in relation["decisions"]} == {"accept", "reject"}


def test_portfolio_classification_is_partial_append_only_and_private(monkeypatch, tmp_path):
    classification_path = tmp_path / "classifications.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(classification_path))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "publicacion_id": "posts.json:3", "fecha": "2026-08-09",
        "asset_path": "/portfolio-media/posts/a.jpg",
    })

    result = hub._portfolio_classify({
        "item_id": "obra-a",
        "fields": {"ownership": "client", "format": "video"},
    })

    assert result["ok"] is True
    assert result["classification"] == {"ownership": "client", "format": "video"}
    assert result["row"]["status"] == "human_draft"
    assert result["row"]["promotion"] == "none"

    second = hub._portfolio_classify({
        "item_id": "obra-a", "fields": {"ownership": "client", "format": "web"},
    })
    assert second["ok"] is True
    rows = classification_path.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 2
    assert hub._portfolio_classifications()["obra-a"]["fields"]["format"] == "web"


def test_portfolio_classification_rejects_unknown_values(monkeypatch, tmp_path):
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(tmp_path / "classifications.jsonl"))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {"id": item_id})

    result = hub._portfolio_classify({
        "item_id": "obra-a", "fields": {"purpose": "inventado"},
    })

    assert result == {
        "ok": False, "error": "valor_de_clasificacion_invalido", "field": "purpose",
    }


def test_portfolio_classification_supports_lane_and_context_without_relation(monkeypatch, tmp_path):
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(tmp_path / "classifications.jsonl"))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "publicacion_id": "post:1", "asset_path": "/obra.jpg",
    })

    first = hub._portfolio_classify({
        "item_id": "obra-a",
        "fields": {"lane": "rd", "context_kind": "artist", "context_value": "dref"},
    })
    second = hub._portfolio_classify({
        "item_id": "obra-a", "fields": {"nature": "3d"},
    })

    assert first["ok"] is True
    assert second["classification"] == {
        "lane": "rd", "context_kind": "artist", "context_value": "dref", "nature": "3d",
    }


def test_portfolio_classification_clears_stale_context_name_on_kind_change(
        monkeypatch, tmp_path):
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(tmp_path / "classifications.jsonl"))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {"id": item_id})

    hub._portfolio_classify({
        "item_id": "obra-a",
        "fields": {"context_kind": "artist", "context_value": "dref"},
    })
    changed = hub._portfolio_classify({
        "item_id": "obra-a", "fields": {"context_kind": "venue"},
    })

    assert changed["classification"] == {"context_kind": "venue"}


def test_portfolio_inbox_skips_malformed_rows_and_normalizes_numeric_ids(
        monkeypatch, tmp_path):
    inbox = tmp_path / "inbox.json"
    selections = tmp_path / "selections.jsonl"
    classifications = tmp_path / "classifications.jsonl"
    vision = tmp_path / "vision.jsonl"
    inbox.write_text(json.dumps({"items": [None, {"id": 7}, {"id": ""}]}),
                     encoding="utf-8")
    selections.write_text(json.dumps({"item_id": "7", "decision": "seleccionar"}) + "\n",
                          encoding="utf-8")
    for path in (classifications, vision):
        path.write_text("", encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(inbox))
    monkeypatch.setattr(hub, "PORTFOLIO_SELECTIONS", str(selections))
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(classifications))
    monkeypatch.setattr(hub, "PORTFOLIO_VISION", str(vision))

    payload = hub._portfolio_inbox()

    assert [row["id"] for row in payload["items"]] == ["7"]
    assert payload["items"][0]["selection"] == "seleccionar"


def test_portfolio_triangulation_and_context_reads_survive_one_bad_jsonl_line(
        monkeypatch, tmp_path):
    triangulation = tmp_path / "triangulation.json"
    reviews = tmp_path / "reviews.jsonl"
    triangulation.write_text(json.dumps({"groups": [{"key": "evento-a"}]}),
                             encoding="utf-8")
    reviews.write_text(json.dumps({"group_key": "evento-a", "artist": "Ober"})
                       + "\nnot-json\n"
                       + json.dumps({"schema": "mak-triangulation-context-link-v1",
                                    "source_id": "story-a", "group_key": "evento-a"})
                       + "\n", encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_TRIANGULATION", str(triangulation))
    monkeypatch.setattr(hub, "PORTFOLIO_TRIANGULATION_REVIEW", str(reviews))

    surface = hub._portfolio_triangulation()

    assert len(surface["human_resolutions"]) == 2
    assert hub._portfolio_context_links() == {"story-a": ["evento-a"]}
    assert len(hub._portfolio_context_link_rows()) == 1


def test_hub_batch_classification_validates_before_any_write(monkeypatch, tmp_path):
    classifications = tmp_path / "classifications.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(classifications))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id} if item_id == "obra-a" else None)

    missing = hub._portfolio_classify_batch({
        "item_ids": ["obra-a", "missing"], "fields": {"triage": "record"}})
    invalid = hub._portfolio_classify_batch({
        "item_ids": ["obra-a"], "fields": {"triage": "inventado"}})

    assert missing["error"] == "items_no_encontrados"
    assert invalid["error"] == "valor_de_clasificacion_invalido"
    assert not classifications.exists()


def test_portfolio_vision_persists_candidate_features_without_entity_resolution(monkeypatch, tmp_path):
    media_root = tmp_path / "media"
    (media_root / "posts").mkdir(parents=True)
    (media_root / "posts" / "a.jpg").write_bytes(b"not-a-real-image-for-the-provider-test")
    vision_path = tmp_path / "vision_features.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_MEDIA_ROOT", str(media_root))
    monkeypatch.setattr(hub, "PORTFOLIO_VISION", str(vision_path))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "published_media",
        "asset_path": "/portfolio-media/posts/a.jpg", "asset_available": True,
    })
    monkeypatch.setattr(hub.providers, "load_env", lambda: None)
    calls = []

    def fake_call(provider, prompt, **kwargs):
        calls.append((provider, kwargs.get("image_paths")))
        return {"visual_terms": ["violet liquid"], "artist": "must be dropped",
                "unknowns": ["event unknown"], "confidence": "medium"}

    monkeypatch.setattr(hub.providers, "call", fake_call)
    result = hub._portfolio_vision_read({"item_id": "obra-a", "provider": "aws"})
    repeated = hub._portfolio_vision_read({"item_id": "obra-a", "provider": "aws"})

    assert result["ok"] is True
    assert result["features"]["visual_terms"] == ["violet liquid"]
    assert result["evidence_kind"] == "still_image"
    assert repeated["duplicate"] is True
    assert calls[0][0] == "aws"
    assert calls[0][1][0].endswith("posts\\a.jpg")
    assert "artist" not in result["features"]
    assert vision_path.read_text(encoding="utf-8").count("faro-portfolio-vision-v1") == 1


def test_portfolio_selection_does_not_persist_when_ledger_rejects(monkeypatch, tmp_path):
    selections = tmp_path / "selections.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_SELECTIONS", str(selections))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {"id": item_id})

    class RejectingLedger:
        @staticmethod
        def append_unique(*args, **kwargs):
            return False, ["invalid"], None

    monkeypatch.setattr(hub, "_ledger", RejectingLedger())
    result = hub._portfolio_select("obra-a", "seleccionar")

    assert result["ok"] is False
    assert not selections.exists()


def test_relation_feedback_does_not_persist_when_ledger_rejects(monkeypatch, tmp_path):
    feedback = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_FEEDBACK", str(feedback))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {"id": item_id})

    class RejectingLedger:
        @staticmethod
        def append_unique(*args, **kwargs):
            return False, ["invalid"], None

    monkeypatch.setattr(hub, "_ledger", RejectingLedger())
    result = hub._portfolio_feedback_record({
        "source_id": "obra-a", "target_id": "obra-b", "action": "accept",
        "facet": "date", "relation": "same_event",
    })

    assert result["ok"] is False
    assert not feedback.exists()


def test_portfolio_visual_asset_caches_one_contact_sheet_for_video(monkeypatch, tmp_path):
    media_root = tmp_path / "media"
    video_path = media_root / "stories" / "202607" / "clip.mp4"
    video_path.parent.mkdir(parents=True)
    video_path.write_bytes(b"video")

    class FakePercepcion:
        calls = []

        @classmethod
        def generar_contact_sheet(cls, source, destination, timeout=90):
            cls.calls.append((source, destination, timeout))
            Path(destination).write_bytes(b"contact-sheet")
            return True, ""

    monkeypatch.setattr(hub, "PORTFOLIO_MEDIA_ROOT", str(media_root))
    monkeypatch.setattr(hub, "PORTFOLIO_CONTACT_SHEETS",
                        str(media_root / "_contact_sheets"))
    monkeypatch.setattr(hub, "_percepcion", FakePercepcion)

    item_data = {"id": "clip.mp4", "asset_path": "/portfolio-media/stories/202607/clip.mp4"}
    first = hub._portfolio_visual_asset(item_data)
    second = hub._portfolio_visual_asset(item_data)

    assert first[1] == "/portfolio-media/_contact_sheets/clip.contact.jpg"
    assert second == first
    assert len(FakePercepcion.calls) == 1
    assert FakePercepcion.calls[0][0] == str(video_path)


def test_opportunity_seed_stays_unverified_until_primary_source_check():
    card = desde_convocatoria_seed({
        "titulo": "Fondart regional",
        "fuente": "Fondos de Cultura",
        "url": "https://fondosdecultura.cl/bases.pdf",
        "cierre": "segunda quincena de agosto",
        "personas_naturales": True,
        "areas": "visual, digital",
        "detectada": "2026-08-06",
    })

    assert card["schema"] == "faro-opportunity-card-v1"
    assert card["status"] == "unverified"
    assert card["deadline_raw"] == "segunda quincena de agosto"
    assert card["deadline_verified"] is False
    assert card["eligibility"] == "persona natural"
    assert card["areas"] == ["visual", "digital"]
    assert card["evidence"] == ["https://fondosdecultura.cl/bases.pdf"]


def test_opportunity_seed_rejects_missing_source_url():
    with pytest.raises(ValueError, match="source_url"):
        desde_convocatoria_seed({"titulo": "Sin fuente"})


def test_hub_opportunity_surface_exposes_candidates_not_raw_history(monkeypatch):
    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return [{
                "id": "opportunity:one",
                "domain": "opportunities",
                "decision": "revisar",
                "owner": "human",
                "metadata": {"opportunity_card": {
                    "schema": "faro-opportunity-card-v1",
                    "title": "Candidate one",
                    "status": "unverified",
                }},
            }, {"domain": "rd", "metadata": {}}]

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    surface = hub._oportunidades()

    assert surface["schema"] == "faro-opportunity-surface-v1"
    assert surface["counts"] == {"total": 1, "unverified": 1}
    assert surface["items"][0]["title"] == "Candidate one"
    assert surface["items"][0]["owner"] == "human"


def test_hub_contract_surface_is_small_and_does_not_require_projection_data():
    surface = hub._portfolio_contract_surface()

    assert surface["projection_contract"]["schema"] == "faro-portfolio-entity-v1"
    assert surface["projection_contract"]["required"][-2:] == ["consent", "publication"]
    assert surface["publication_policy"]["requires_human_gate"] is True


def test_portfolio_suggestions_without_map_are_lightweight_and_complete(monkeypatch):
    source = {"id": "obra-a", "descripcion_original": "vaso violeta"}
    monkeypatch.setattr(hub, "_portfolio_item", lambda _item_id: source)
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": [source]})
    monkeypatch.setattr(hub, "_portfolio_item_context", lambda _item_id: {})
    monkeypatch.setattr(hub, "_portfolio_boards", lambda: {"boards": []})
    monkeypatch.setattr(hub, "_portfolio_selections", lambda: [])
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [])
    monkeypatch.setattr(hub, "_portfolio_external_review_rows", lambda: [])
    monkeypatch.setattr(hub.copilot, "build_suggestions", lambda *args, **kwargs: ([], []))

    result = hub._portfolio_suggestions("obra-a")

    assert result["ok"] is True
    assert result["map"]["engine"] == "not_requested"
    assert result["map"]["source_position"] is None


def test_portfolio_relation_map_reuses_stable_atlas(monkeypatch):
    source = {"id": "obra-a", "descripcion_original": "vaso violeta"}
    calls = []
    monkeypatch.setattr(hub, "_portfolio_item", lambda _item_id: source)
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": [source]})
    monkeypatch.setattr(hub, "_portfolio_apply_human_context", lambda rows: rows)
    monkeypatch.setattr(hub, "_portfolio_item_context", lambda _item_id: {})
    monkeypatch.setattr(hub, "_portfolio_boards", lambda: {"boards": []})
    monkeypatch.setattr(hub, "_portfolio_selections", lambda: [])
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [{"action": "accept"}])
    monkeypatch.setattr(hub, "_portfolio_external_review_rows", lambda: [])
    monkeypatch.setattr(hub.copilot, "build_suggestions", lambda *args, **kwargs: ([], []))
    monkeypatch.setattr(hub.copilot, "build_gtm_map", lambda rows, **kwargs: (
        calls.append(kwargs) or {
            "schema": "faro-gtm-map-v1", "engine": "elastic_latent_grid",
            "fit": {"total": 1}, "ordering": {},
            "items": [{"item_id": "obra-a", "x": .2, "y": .4}],
        }))

    result = hub._portfolio_suggestions("obra-a", include_map=True)

    assert result["ok"] is True
    assert calls == [{"feedback": [{"action": "accept"}], "stable_topology": True}]
    assert result["map"]["source_position"]["x"] == .2


def test_hub_external_candidates_are_review_only(monkeypatch):
    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return [{
                "id": "portfolio:story-a:external",
                "domain": "portfolio",
                "decision": "revisar",
                "next_action": "human_review",
                "metadata": {"portfolio_candidate": {
                    "entity_id": "story-a",
                    "triage": {
                        "provider": "aws", "verdict": "accept",
                        "candidate_relations": {"username": ["tomas.pcaa"]},
                        "evidence_basis": ["description_original"],
                    },
                }},
                "work": {"identity": {"source_id": "story-a"}},
            }]

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "story", "fecha": "2025-12-05",
        "publicacion_id": "stories.json:1", "descripcion_original": "@tomas.pcaa",
        "asset_path": "/portfolio-media/stories/a.mp4", "asset_available": True,
    })
    surface = hub._portfolio_external_candidates("story-a")

    assert surface["schema"] == "faro-portfolio-external-candidate-surface-v1"
    assert surface["total"] == 1
    assert surface["items"][0]["candidate_relations"] == {
        "username": ["tomas.pcaa"]}
    assert surface["items"][0]["review_state"] == "pending"
    assert surface["items"][0]["item"]["asset_available"] is True
    assert surface["public_promotion"] is False


def test_hub_external_candidates_deduplicate_same_source_rows(monkeypatch):
    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            rows = []
            for suffix, evidence in (("a", "description_original"),
                                     ("b", "contact_sheet")):
                rows.append({
                    "id": "candidate-%s" % suffix,
                    "domain": "portfolio",
                    "decision": "revisar",
                    "next_action": "human_review",
                    "metadata": {"portfolio_candidate": {
                        "entity_id": "story-a",
                        "triage": {
                            "provider": "aws", "verdict": "accept",
                            "candidate_relations": {},
                            "evidence_basis": [evidence],
                        },
                    }},
                    "work": {"identity": {"source_id": "story-a"}},
                })
            return rows

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "story", "fecha": "2025-12-05",
        "publicacion_id": "stories.json:1", "descripcion_original": "registro",
        "asset_path": "/portfolio-media/stories/a.mp4", "asset_available": True,
    })

    surface = hub._portfolio_external_candidates()

    assert surface["total"] == 1
    assert surface["items"][0]["source_id"] == "story-a"
    assert surface["items"][0]["candidate_occurrences"] == 2
    assert surface["items"][0]["evidence_basis"] == [
        "description_original", "contact_sheet"]


def test_hub_external_candidates_skip_orphan_sources_and_preserve_candidate_scope(
        monkeypatch):
    rows = [
        {"id": "candidate-a", "domain": "portfolio", "metadata": {
            "portfolio_candidate": {"entity_id": "story-a", "triage": {}}}},
        {"id": "candidate-b", "domain": "portfolio", "metadata": {
            "portfolio_candidate": {"entity_id": "story-a", "triage": {}}}},
        {"id": "candidate-empty", "domain": "portfolio", "metadata": {
            "portfolio_candidate": {"entity_id": "", "triage": {}}}},
        {"id": "candidate-missing", "domain": "portfolio", "metadata": {
            "portfolio_candidate": {"entity_id": "missing", "triage": {}}}},
        {"id": "review-b", "domain": "portfolio", "metadata": {
            "external_candidate_review": {
                "candidate_id": "candidate-b", "source_id": "story-a",
                "decision": "reject", "ts": "2026-08-09T02:00:00-04:00"}}},
    ]

    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return rows

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "story", "asset_available": True
    } if item_id == "story-a" else None)

    surface = hub._portfolio_external_candidates()

    assert surface["total"] == 1
    assert surface["items"][0]["human_decision"] == "pending"
    assert surface["items"][0]["candidate_occurrences"] == 2


def test_hub_board_action_normalizes_existing_and_new_item_ids(monkeypatch, tmp_path):
    boards = tmp_path / "boards.json"
    boards.write_text(json.dumps({"boards": [{
        "id": "board-a", "name": "obra", "item_ids": ["a", "a"]
    }]}), encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_BOARDS", str(boards))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id} if item_id in {"a", "b"} else None)
    monkeypatch.setattr(hub, "_portfolio_feedback_record", lambda body: {
        "ok": True})

    result = hub._portfolio_board_action({
        "action": "add", "board_id": "board-a", "item_ids": ["b", "b", "a"]})

    assert result["board"]["item_ids"] == ["a", "b"]


def test_hub_review_queue_only_exposes_human_pending_candidates(monkeypatch):
    monkeypatch.setattr(hub, "_portfolio_external_candidates", lambda _source_id="": {
        "items": [
            {"source_id": "story-a", "ledger_id": "candidate-a",
             "review_state": "pending"},
            {"source_id": "story-b", "ledger_id": "candidate-b",
             "review_state": "accepted"},
        ]
    })

    queue = hub._portfolio_review_queue()

    assert queue["schema"] == "faro-portfolio-review-queue-v1"
    assert queue["status"] == "human_review_required"
    assert queue["total"] == 1
    assert queue["items"][0]["source_id"] == "story-a"


def test_human_accepted_external_context_reaches_copilot_without_promotion(monkeypatch):
    monkeypatch.setattr(hub, "_portfolio_external_candidates", lambda _item_id="": {
        "items": [{
            "source_id": "story-a", "provider": "aws",
            "candidate_relations": {"username": ["doncata.cl"]},
            "evidence_basis": ["description_original"],
            "human_decision": "accept", "human_note": "colab confirmada",
            "reviewed_at": "2026-08-09T00:00:00-04:00",
        }]
    })
    monkeypatch.setattr(hub, "_portfolio_triangulation", lambda: {"groups": []})

    context = hub._portfolio_item_context("story-a")

    assert context["human_evidence"]["schema"] == "faro-portfolio-human-context-v1"
    assert context["human_evidence"]["count"] == 1
    assert context["human_evidence"]["accepted"][0]["candidate_relations"] == {
        "username": ["doncata.cl"]}
    assert context["human_evidence"]["accepted"][0]["public_promotion"] is False


def test_human_context_records_stay_separate_from_candidate_groups(monkeypatch):
    monkeypatch.setattr(hub, "_portfolio_external_candidates", lambda _item_id="": {
        "items": [{
            "source_id": "story-a", "item": {"tipo_contenido": "story"},
            "context_fields": {"venue": ["Sala Metronomo"]},
            "candidate_relations": {"username": ["par4noi4rt"]},
            "evidence_basis": ["description_original"],
            "human_decision": "accept", "human_note": "venue confirmada",
            "reviewed_at": "2026-08-09T00:00:00-04:00",
        }]
    })

    records = hub._portfolio_human_context_records()

    assert records[0]["context_state"] == "human_confirmed_context"
    assert records[0]["context_fields"] == {"venue": ["Sala Metronomo"]}
    assert records[0]["next_action"] == "link manually to event or venue group"
    assert records[0]["promotion"] == "none"


def test_human_context_link_is_append_only_and_explicit(monkeypatch, tmp_path):
    review_path = tmp_path / "human_resolutions.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_TRIANGULATION_REVIEW", str(review_path))
    monkeypatch.setattr(hub, "_portfolio_triangulation", lambda: {
        "groups": [{"key": "marlon-breeze"}],
    })
    monkeypatch.setattr(hub, "_portfolio_human_context_records", lambda: [{
        "source_id": "18025062500279121.mp4",
        "context_fields": {"artist": ["Marlon Breeze"],
                            "venue": ["Sala Metronomo"]},
        "human_note": "evento confirmado por la persona",
    }])

    result = hub._portfolio_context_link({
        "source_id": "18025062500279121.mp4",
        "group_key": "marlon-breeze",
    })

    assert result["ok"] is True
    assert result["already_linked"] is False
    assert result["resolution"]["schema"] == "mak-triangulation-context-link-v1"
    assert result["resolution"]["promotion"] == "none"
    assert result["resolution"]["context_fields"]["venue"] == ["Sala Metronomo"]
    second = hub._portfolio_context_link({
        "source_id": "18025062500279121.mp4",
        "group_key": "marlon-breeze",
    })
    assert second["already_linked"] is True
    assert len(review_path.read_text(encoding="utf-8").splitlines()) == 1


def test_portfolio_metadata_index_groups_without_resolving_entities():
    index = portfolio_metadata_index([
        {"id": "a", "tipo_contenido": "published_media", "fecha": "2025-01-02",
         "publicacion_id": "p1", "descripcion_original": "Visuales para @ober.byg"},
        {"id": "b", "tipo_contenido": "published_media", "fecha": "2025-01-02",
         "publicacion_id": "p1", "descripcion_original": "colab @ober.byg"},
        {"id": "c", "tipo_contenido": "story", "fecha": "2025-01-03",
         "publicacion_id": "s1", "descripcion_original": "registro @tomas.pcaa"},
    ])

    assert index["grouping"] == {
        "publication_groups": 2, "carousel_groups": 1,
        "date_groups": 2, "story_records": 1}
    assert index["user_mentions"][0] == {
        "username": "ober.byg", "count": 2, "item_ids": ["a", "b"]}
    assert "artist" not in index["user_mentions"][0]
    assert "mentions_only" in index["identity_resolution"]


def test_identity_graph_separates_record_entities_and_never_parses_description():
    graph = portfolio_identity_graph([
        {"id": "story-a", "tipo_contenido": "story", "fecha": "2025-12-05",
         "publicacion_id": "story-a", "descripcion_original": "Sfera inventada",
         "artista": "DrefQuila", "venue": "Sala Metronomo",
         "productora": "Bees and Honey"},
    ], connections=[{"source_id": "story-a", "target_id": "story-b",
                     "relation": "same_date_context"}])

    assert graph["schema"] == "faro-identity-graph-v1"
    assert graph["resolution_policy"] == "explicit_metadata_only"
    labels = {node["label"] for node in graph["nodes"]}
    assert labels >= {"DrefQuila", "Sala Metronomo", "Bees and Honey"}
    assert "Sfera inventada" not in labels
    by_label = {node["label"]: node for node in graph["nodes"]
                if node["kind"] != "publication"}
    assert by_label["story-a"]["layer"] == "registro"
    assert by_label["DrefQuila"]["layer"] == "entidad"
    assert by_label["2025-12-05"]["layer"] == "context"
    assert graph["layer_counts"]["registro"] == 1
    assert graph["layer_counts"]["entidad"] == 3
    assert all(edge["status"] == "candidate" for edge in graph["edges"])


def test_identity_graph_accepts_explicit_classification_layers_and_entities():
    graph = portfolio_identity_graph([{
        "id": "work-a", "tipo_contenido": "published_media",
        "classification": {
            "semantic_layer": "obra", "record_kind": "work",
            "artist": "DrefQuila", "venue": "Sala Metronomo",
        },
    }])

    by_id = {node["id"]: node for node in graph["nodes"]}
    assert by_id["item:work-a"]["layer"] == "obra"
    assert by_id["artist:drefquila"]["layer"] == "entidad"
    assert by_id["venue:sala-metronomo"]["layer"] == "entidad"


def test_hub_metadata_index_reads_compact_source(monkeypatch):
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": [
        {"id": "a", "tipo_contenido": "story", "fecha": "2025-01-02",
         "publicacion_id": "s1", "descripcion_original": "@xuser"},
    ]})

    surface = hub._portfolio_metadata_index()

    assert surface["schema"] == "faro-portfolio-metadata-index-v1"
    assert surface["total"] == 1
    assert surface["identity_resolution"].startswith("mentions_only")


def test_hub_external_candidate_human_review_is_append_only(monkeypatch):
    candidate_row = {
        "id": "portfolio:story-a:external",
        "domain": "portfolio",
        "work": {"identity": {"source_id": "story-a"}},
        "metadata": {"portfolio_candidate": {
            "entity_id": "story-a",
            "triage": {"provider": "aws", "verdict": "accept",
                        "candidate_relations": {"username": ["tomas.pcaa"]}},
        }},
    }
    appended = []

    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return [candidate_row]

        @staticmethod
        def append_unique(item, path=None, source=None):
            appended.append((item, source))
            return True, [], {"id": item["id"]}

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    result = hub._portfolio_external_candidate_review({
        "ledger_id": "portfolio:story-a:external",
        "decision": "accept",
        "note": "username observable; revisar entidad antes de tablero",
        "context_fields": {
            "collab": ["doncata.cl", "doncata.cl"],
            "unknown": ["must not pass"],
        },
    })

    assert result["ok"] is True
    assert appended[0][0]["decision"] == "hacer"
    review = appended[0][0]["metadata"]["external_candidate_review"]
    assert review["decision"] == "accept"
    assert review["context_fields"] == {"collab": ["doncata.cl"]}
    assert review["context_state"] == "structured"
    assert review["work_id"].startswith("portfolio-review:story-a:")
    assert appended[0][0]["work"]["schema"] == "mak-work-v1"
    assert appended[0][0]["work"]["owner"] == "human"


def test_hub_external_candidate_review_disambiguates_duplicate_ledger_ids(
        monkeypatch):
    candidate_rows = []
    for source_id in ("story-a", "story-b"):
        candidate_rows.append({
            "id": "legacy-duplicate",
            "domain": "portfolio",
            "metadata": {"portfolio_candidate": {
                "entity_id": source_id,
                "triage": {"provider": "aws", "verdict": "accept"},
            }},
        })
    appended = []

    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return candidate_rows

        @staticmethod
        def append_unique(item, path=None, source=None):
            appended.append(item)
            return True, [], {"id": item["id"]}

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    ambiguous = hub._portfolio_external_candidate_review({
        "ledger_id": "legacy-duplicate",
        "decision": "revise",
    })
    assert ambiguous == {
        "ok": False,
        "error": "source_id_requerido",
        "details": {"ledger_id": "legacy-duplicate", "candidate_count": 2},
    }
    result = hub._portfolio_external_candidate_review({
        "ledger_id": "legacy-duplicate",
        "source_id": "story-b",
        "decision": "revise",
        "note": "revisar contexto de story-b",
    })

    assert result["ok"] is True
    assert appended[0]["metadata"]["external_candidate_review"]["source_id"] == "story-b"


def test_hub_external_candidate_reviews_do_not_bleed_across_duplicate_ids(
        monkeypatch):
    rows = [
        {"id": "legacy-duplicate", "domain": "portfolio",
         "metadata": {"portfolio_candidate": {
             "entity_id": "story-a", "triage": {}}}},
        {"id": "legacy-duplicate", "domain": "portfolio",
         "metadata": {"portfolio_candidate": {
             "entity_id": "story-b", "triage": {}}}},
        {"id": "review-a", "domain": "portfolio",
         "metadata": {"external_candidate_review": {
             "candidate_id": "legacy-duplicate", "source_id": "story-a",
             "decision": "accept", "ts": "2026-08-09T01:00:00-04:00"}}},
    ]

    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return rows

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "story", "asset_available": True,
    })
    surface = hub._portfolio_external_candidates()
    by_source = {item["source_id"]: item for item in surface["items"]}

    assert by_source["story-a"]["human_decision"] == "accept"
    assert by_source["story-b"]["human_decision"] == "pending"


def test_hub_promotes_accepted_context_into_future_copilot_items(monkeypatch):
    monkeypatch.setattr(hub, "_portfolio_human_context_records", lambda: [{
        "source_id": "paper-a",
        "context_fields": {"process": ["croquera"], "artist": ["issvk"]},
    }])
    original = {"id": "paper-a", "artist": ["issvk"]}
    enriched = hub._portfolio_apply_human_context([original])

    assert enriched[0]["process"] == ["croquera"]
    assert enriched[0]["artist"] == ["issvk"]
    assert enriched[0]["human_context"] == {
        "process": ["croquera"], "artist": ["issvk"]}
    assert "process" not in original


def test_hub_learning_surface_exposes_candidate_review_memory(monkeypatch):
    rows = [
        {"metadata": {"external_candidate_review": {
            "candidate_id": "legacy", "source_id": "paper-a",
            "decision": "accept", "context_fields": {
                "process": ["croquera"]}, "ts": "2026-08-09T01:00:00-04:00"}}},
        {"metadata": {"external_candidate_review": {
            "candidate_id": "legacy", "source_id": "paper-a",
            "decision": "accept", "context_fields": {
                "process": ["croquera", "papel"]}, "ts": "2026-08-09T02:00:00-04:00"}}},
    ]

    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return rows

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [])
    monkeypatch.setattr(hub, "_portfolio_selections", lambda: {})
    monkeypatch.setattr(hub, "_portfolio_boards", lambda: {"boards": []})
    surface = hub._portfolio_learning()

    review = surface["candidate_reviews"]
    assert review["decision_total"] == 1
    assert review["context_signals"]["process"]["croquera"]["accept"] == 1
    assert review["context_signals"]["process"]["papel"]["accept"] == 1


def test_hub_learning_surface_uses_stable_atlas_and_active_seed(monkeypatch):
    items = [{"id": "a", "tipo_contenido": "story", "asset_available": True},
             {"id": "b", "tipo_contenido": "published_media",
              "asset_available": True}]
    calls = []
    atlas = {
        "atlas": {"schema": "faro-portfolio-atlas-v1",
                  "topology_id": "topology-test"},
        "ordering": {"counts": {"work": 0, "record": 0,
                                "review": 0, "discard": 0}},
        "items": [{"item_id": "a", "x": 0.1, "y": 0.2},
                  {"item_id": "b", "x": 0.8, "y": 0.7}],
    }
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [])
    monkeypatch.setattr(hub, "_portfolio_external_review_rows", lambda: [])
    monkeypatch.setattr(hub, "_portfolio_selections", lambda: {})
    monkeypatch.setattr(hub, "_portfolio_boards", lambda: {"boards": []})
    monkeypatch.setattr(hub, "_portfolio_inbox", lambda: {"items": items})
    monkeypatch.setattr(hub, "_portfolio_apply_human_context", lambda rows: rows)
    monkeypatch.setattr(hub, "_portfolio_jsonl", lambda _path: [])
    monkeypatch.setattr(hub, "_portfolio_vision", lambda: {})
    monkeypatch.setattr(hub.copilot, "build_gtm_map", lambda rows, **kwargs: (
        calls.append((rows, kwargs)) or atlas))
    monkeypatch.setattr(hub.copilot, "active_ordering_seed",
                        lambda rows, surface: [{
                            "item_id": rows[0]["id"],
                            "selection_method": "active_information_gain",
                            "topology_id": surface["atlas"]["topology_id"],
                        }])

    surface = hub._portfolio_learning()

    assert calls[0][1] == {"feedback": [], "stable_topology": True}
    assert surface["ordering"]["atlas"]["topology_id"] == "topology-test"
    assert surface["ordering"]["human_seed"][0][
        "selection_method"] == "active_information_gain"


def test_hub_decision_index_keeps_candidate_relation_and_selection_threads(
        monkeypatch):
    rows = [{"metadata": {"external_candidate_review": {
        "candidate_id": "legacy", "source_id": "paper-a",
        "decision": "accept", "context_fields": {},
        "work_id": "portfolio-review:paper-a:1", "ts": "2026-08-09"}}}]

    class FakeLedger:
        @staticmethod
        def read_items(_path, limit=None):
            return rows

    monkeypatch.setattr(hub, "_ledger", FakeLedger())
    monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [{
        "source_id": "paper-a", "target_id": "paper-b", "action": "accept",
        "facet": "process", "work": {"work_id": "portfolio-relation:1"},
    }])
    monkeypatch.setattr(hub, "_portfolio_selections", lambda: {
        "paper-a": {"item_id": "paper-a", "decision": "seleccionar",
                     "work": {"work_id": "portfolio:paper-a"}}
    })

    index = hub._portfolio_decision_index()

    assert index["schema"] == "faro-portfolio-decision-index-v1"
    assert index["counts"] == {
        "candidate_reviews": 1, "relation_feedback": 1, "selections": 1}
    assert index["candidate_reviews"][0]["work_id"] == "portfolio-review:paper-a:1"
    assert index["relation_feedback"][0]["work_id"] == "portfolio-relation:1"
    assert index["selections"][0]["work_id"] == "portfolio:paper-a"


def test_hub_selection_persists_live_pass_metadata(monkeypatch, tmp_path):
    selections = tmp_path / "selections.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_SELECTIONS", str(selections))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "published_media",
        "asset_path": "/portfolio-media/posts/a.jpg",
        "publicacion_id": "posts.json:1",
    })
    monkeypatch.setattr(hub, "_ledger", None)

    result = hub._portfolio_select("paper-a", "seleccionar",
                                   session_id="estudio-test", pass_size=10)

    row = json.loads(selections.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert row["session_id"] == "estudio-test"
    assert row["pass_size"] == 10
    assert row["work"]["session_id"] == "estudio-test"


def test_hub_discard_records_non_work_reason_without_deleting_media(monkeypatch, tmp_path):
    selections = tmp_path / "selections.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_SELECTIONS", str(selections))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "story",
        "asset_path": "/portfolio-media/stories/a.jpg",
        "publicacion_id": "stories.json:1",
    })
    monkeypatch.setattr(hub, "_ledger", None)

    result = hub._portfolio_select(
        "story-a", "descartar", session_id="estudio-test", pass_size=10,
        decision_scope="record", reason_code="no_es_obra",
        target_id="story-a")

    row = json.loads(selections.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert row["decision"] == "descartar"
    assert row["decision_scope"] == "record"
    assert row["reason_code"] == "no_es_obra"
    assert row["target_id"] == "story-a"


def test_hub_batch_ordering_persists_triage_without_creating_relations(monkeypatch, tmp_path):
    classifications = tmp_path / "classifications.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_CLASSIFICATIONS", str(classifications))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "tipo_contenido": "published_media",
        "asset_path": "/portfolio-media/%s.jpg" % item_id,
    })

    result = hub._portfolio_classify_batch({
        "item_ids": ["obra-a", "obra-b"],
        "fields": {"triage": "record"},
    })

    rows = [json.loads(line) for line in classifications.read_text(
        encoding="utf-8").splitlines()]
    assert result["ok"] is True
    assert result["schema"] == "faro-portfolio-batch-classification-v1"
    assert result["count"] == 2
    assert {row["fields"]["triage"] for row in rows} == {"record"}


def test_relation_feedback_persists_human_note(monkeypatch, tmp_path):
    feedback_path = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_FEEDBACK", str(feedback_path))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {
        "id": item_id, "asset_path": "/portfolio-media/%s.jpg" % item_id,
    })
    monkeypatch.setattr(hub, "_ledger", None)

    result = hub._portfolio_feedback_record({
        "source_id": "obra-a", "target_id": "obra-b", "action": "accept",
        "facet": "date", "relation": "same_event",
        "note": "mismo evento, la fecha coincide con mi registro",
    })

    row = json.loads(feedback_path.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert row["note"] == "mismo evento, la fecha coincide con mi registro"
    duplicate = hub._portfolio_feedback_record({
        "source_id": "obra-a", "target_id": "obra-b", "action": "accept",
        "facet": "date", "relation": "same_event",
        "note": "mismo evento, la fecha coincide con mi registro",
    })
    assert duplicate["duplicate"] is True
    assert len(feedback_path.read_text(encoding="utf-8").splitlines()) == 1


def test_connection_is_idempotent(monkeypatch, tmp_path):
    connections = tmp_path / "connections.jsonl"
    monkeypatch.setattr(hub, "PORTFOLIO_CONNECTIONS", str(connections))
    monkeypatch.setattr(hub, "_portfolio_item", lambda item_id: {"id": item_id})

    first = hub._portfolio_connect({
        "source_id": "obra-a", "target_id": "obra-b", "relation": "same_event"})
    second = hub._portfolio_connect({
        "source_id": "obra-a", "target_id": "obra-b", "relation": "same_event"})

    assert first["ok"] is True
    assert second["duplicate"] is True
    assert len(connections.read_text(encoding="utf-8").splitlines()) == 1


def test_hub_legacy_report_index_keeps_quarantine_and_pairing_distinct(
        tmp_path, monkeypatch):
    run = tmp_path / "faro-report-metadata-20260809"
    run.mkdir()
    rows = [
        {"work_id": "legacy-report:a", "duplicate_family_size": 3,
         "sfera_quarantine": False, "metadata_quality": "legacy_unknown",
         "path": "a.md", "basename": "a.md", "paired_stem": "a",
         "paired_files": ["a.md", "a.json"], "timestamp_from_name": "20260809"},
        {"work_id": "legacy-report:b", "duplicate_family_size": 1,
         "sfera_quarantine": False, "metadata_quality": "legacy_unknown",
         "path": "b.md", "basename": "b.md", "paired_stem": "b",
         "paired_files": ["b.md"], "timestamp_from_name": "20260809"},
        {"work_id": "legacy-report:c", "duplicate_family_size": 2,
         "sfera_quarantine": True, "metadata_quality": "legacy_unknown",
         "path": "c.md", "basename": "c.md", "paired_stem": "c",
         "paired_files": ["c.md", "c.json"], "timestamp_from_name": "20260809"},
    ]
    (run / "reports.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    (run / "SUMMARY.json").write_text(json.dumps({
        "root": "/home/mak/research/informes",
        "external_review": {"provider": "watsonx", "sample_items": 20,
                             "status": "quarantined_raw"},
    }), encoding="utf-8")
    monkeypatch.setattr(hub, "LEGACY_REPORT_RUNS", str(tmp_path))

    index = hub._legacy_report_index(limit=10)

    assert index["counts"] == {
        "paired_family": 1, "orphan_candidate": 1, "quarantine": 1}
    assert index["external_review"]["status"] == "quarantined_raw"
    assert index["items"][0]["duplicate_status"] == "not_proven"
    assert hub._legacy_report_index(classification="quarantine")["returned"] == 1


def test_external_portfolio_candidate_accepts_only_source_observed_relation():
    source = {
        "id": "post-a",
        "tipo_contenido": "published_media",
        "fecha": "2025-12-05",
        "descripcion_original": "Visuales para @ober.byg en Sala Metronomo",
        "selection": "pendiente",
    }
    row = {
        "item_id": "post-a",
        "record_kind": "media_candidate",
        "candidate_relations": {
            "artist": [{"name": "ober.byg", "status": "candidate"}],
            "venue": "Sala Metronomo",
            "evidence_basis": "description_original",
        },
    }

    assert portfolio_candidate_verdict(row, source) == "accept"
    candidate = normalize_portfolio_candidate(row, source, provider="aws")
    assert candidate["status"] == "candidate_external"
    assert candidate["triage"]["provider"] == "aws"
    assert candidate["triage"]["candidate_relations"] == {
        "username": ["ober.byg"], "venue": ["Sala Metronomo"]}
    assert candidate["publication"]["requires_human_gate"] is True


def test_external_portfolio_candidate_revises_generic_or_unobserved_relations():
    source = {
        "id": "story-a", "tipo_contenido": "story",
        "fecha": "2025-12-05", "descripcion_original": "registro sin nombre",
    }
    generic = {
        "item_id": "story-a", "record_kind": "story_record",
        "candidate_relations": {"artist": "candidate", "evidence_basis": "description"},
    }
    hallucinated = {
        "item_id": "story-a", "record_kind": "story_record",
        "candidate_relations": {
            "artist": "artista inventado", "evidence_basis": "description"},
    }

    assert portfolio_candidate_verdict(generic, source) == "revise"
    assert portfolio_candidate_verdict(hallucinated, source) == "revise"


def test_external_portfolio_candidate_does_not_accept_date_alone():
    source = {
        "id": "post-a", "tipo_contenido": "published_media",
        "fecha": "2025-12-05", "descripcion_original": "registro",
    }
    row = {
        "item_id": "post-a", "record_kind": "media_candidate",
        "candidate_relations": {"date": "2025-12-05", "evidence_basis": "description"},
    }

    assert portfolio_candidate_verdict(row, source) == "revise"


def test_external_portfolio_candidate_rejects_identity_or_kind_mismatch():
    source = {"id": "story-a", "tipo_contenido": "story"}
    row = {"item_id": "other", "record_kind": "media_candidate",
           "candidate_relations": {}}

    assert portfolio_candidate_verdict(row, source) == "reject"
