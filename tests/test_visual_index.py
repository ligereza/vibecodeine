import json

from cultura.mak_plataforma import visual_index


def _item(item_id, path, publication="", index=0, total=1):
    return {
        "id": item_id,
        "asset_path": "/portfolio-media/" + path,
        "asset_available": True,
        "publicacion_id": publication,
        "medio_indice": index,
        "medio_total": total,
        "tipo_contenido": "story" if path.endswith(".mp4") else "published_media",
    }


def test_group_portfolio_items_keeps_one_carousel_unit(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"a")
    (tmp_path / "b.jpg").write_bytes(b"b")
    units = visual_index.group_portfolio_items([
        _item("a.jpg", "a.jpg", "post:1", 0, 2),
        _item("b.jpg", "b.jpg", "post:1", 1, 2),
    ], tmp_path)

    assert len(units) == 1
    assert units[0]["is_carousel"] is True
    assert units[0]["media_count"] == 2
    assert units[0]["source_ids"] == ["a.jpg", "b.jpg"]


def test_sample_is_deterministic_and_mixed(tmp_path):
    items = []
    for index in range(4):
        name = "image-%s.jpg" % index
        (tmp_path / name).write_bytes(name.encode())
        items.append(_item(name, name))
    (tmp_path / "video.mp4").write_bytes(b"video")
    items.append(_item("video.mp4", "video.mp4"))
    (tmp_path / "carousel-a.jpg").write_bytes(b"ca")
    (tmp_path / "carousel-b.jpg").write_bytes(b"cb")
    items.extend([
        _item("carousel-a.jpg", "carousel-a.jpg", "post:2", 0, 2),
        _item("carousel-b.jpg", "carousel-b.jpg", "post:2", 1, 2),
    ])
    units = visual_index.group_portfolio_items(items, tmp_path)

    first = visual_index.select_sample(units, 3)
    second = visual_index.select_sample(units, 3)
    assert [row["unit_id"] for row in first] == [row["unit_id"] for row in second]
    assert any(row["is_carousel"] for row in first)
    assert any(row["has_video"] for row in first)


def test_visual_surface_maps_carousel_members_and_filters_abstentions(tmp_path):
    payload = {
        "schema": visual_index.VISUAL_NEIGHBORS_SCHEMA,
        "index_schema": visual_index.VISUAL_INDEX_SCHEMA,
        "model": visual_index.MODEL_NAME,
        "model_version": visual_index.MODEL_VERSION,
        "dimension": 512,
        "items": {
            "publication:source": {
                "source_id": "source-a.jpg", "source_ids": ["source-a.jpg", "source-b.jpg"],
                "neighbors": [{
                    "item_id": "target.jpg", "score": .61, "margin": .03,
                    "eligible": True, "model": visual_index.MODEL_NAME,
                }, {
                    "item_id": "weak.jpg", "score": .49, "margin": .001,
                    "eligible": False,
                }],
            },
        },
    }
    (tmp_path / "neighbors.json").write_text(json.dumps(payload), encoding="utf-8")
    surface = visual_index.read_surface(tmp_path)

    rows = visual_index.visual_relations("source-b.jpg", surface)
    assert [row["item_id"] for row in rows] == ["target.jpg"]
    assert visual_index.surface_profile(surface)["abstained_neighbors"] == 1


def test_missing_visual_surface_is_safe_fallback(tmp_path):
    surface = visual_index.read_surface(tmp_path)
    assert surface["available"] is False
    assert visual_index.visual_relations("source", surface) == []
