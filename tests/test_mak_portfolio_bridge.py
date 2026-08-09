from pathlib import Path

import json

import pytest

from cultura.mak_plataforma.contrato_archivo import (
    desde_convocatoria_seed,
    normalize_portfolio_candidate,
    portfolio_identity_graph,
    portfolio_metadata_index,
    portfolio_candidate_verdict,
)
from cultura.mak_plataforma import hub


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

    assert result["ok"] is True
    assert result["features"]["visual_terms"] == ["violet liquid"]
    assert calls[0][0] == "aws"
    assert calls[0][1][0].endswith("posts\\a.jpg")
    assert "artist" not in result["features"]
    assert vision_path.read_text(encoding="utf-8").count("faro-portfolio-vision-v1") == 1


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
    assert all(edge["status"] == "candidate" for edge in graph["edges"])


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
