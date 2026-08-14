import json

from cultura.mak_plataforma import revision_episodios


def test_episode_api_preserves_original_and_model_reading(monkeypatch, tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    fichas = {
        "items": [{
            "episodio": "demo",
            "medios": ["1.mp4"],
            "descripcion_original": ["texto del artista"],
            "observaciones_aws": [{"reading": "lectura provisional"}],
        }]
    }
    (run / "FICHAS_CURATORIA_VISUAL_RONDA1.json").write_text(
        json.dumps(fichas), encoding="utf-8")
    monkeypatch.setattr(revision_episodios, "RUN", run)
    monkeypatch.setattr(revision_episodios, "FICHAS", run / "FICHAS_CURATORIA_VISUAL_RONDA1.json")
    monkeypatch.setattr(revision_episodios, "MAPA", run / "missing-map.json")
    monkeypatch.setattr(revision_episodios, "REVIEWS", run / "episode_reviews.jsonl")

    row = revision_episodios.api()["rows"][0]
    assert row["descripcion_original"] == ["texto del artista"]
    assert row["observaciones_aws"][0]["reading"] == "lectura provisional"
    assert revision_episodios.record("demo", "revise")["ok"] is True
    assert revision_episodios.api()["pending_human"] == 0
