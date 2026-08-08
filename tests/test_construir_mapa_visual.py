from tools.construir_mapa_visual import build


def test_artist_first_does_not_turn_concepts_into_events():
    result = build({"media": [
        {"media": "a.mp4", "nota_humana": "visual para Drefquila", "descripcion_original": ""},
        {"media": "b.mp4", "nota_humana": "zootropo", "descripcion_original": ""},
        {"media": "c.mp4", "nota_humana": "colab con tomas.pca", "descripcion_original": ""},
    ]}, {"event_candidates": [{"id": "dia-musica-chilena", "status": "candidate"}]})
    ids = {row["id"] for row in result["entities"]}
    assert ids == {"drefquila", "zootropo", "tomas-pca"}
    assert result["event_candidates"][0]["status"] == "candidate"
    assert all("sin episodio" in rule for rule in result["rules"] if "sin episodio" in rule)
