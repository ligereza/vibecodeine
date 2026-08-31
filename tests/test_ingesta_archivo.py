from __future__ import annotations

import json
import sqlite3
import sys
import types
from pathlib import Path

from PIL import Image

from cultura.mak_curatoria import ingesta_archivo


def _seed_asset(conn: sqlite3.Connection, source: Path, name: str,
                data: bytes = b"seed-bytes") -> str:
    """Register one file under `source` as a real assets row and return its id.

    Several projection functions store observations/candidates that carry a
    foreign key to `assets(asset_id)` (enforced: `connect()` turns on
    `PRAGMA foreign_keys=ON`), so tests that exercise them need a genuine
    row, not a made-up id string. If the caller already wrote `name` itself
    (e.g. a real PNG via Pillow), that content is left untouched; otherwise
    this writes `data` as filler content.
    """
    source.mkdir(parents=True, exist_ok=True)
    target = source / name
    if not target.is_file():
        target.write_bytes(data)
    ingesta_archivo.inventory(conn, source, full_hash_limit=1 << 20)
    row = conn.execute(
        "SELECT asset_id FROM assets WHERE relative_path=?", (name,)
    ).fetchone()
    return row["asset_id"]


def test_run_indexes_source_without_mutation_and_keeps_exact_duplicate_evidence(
        tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    Image.new("RGB", (8, 4), "black").save(source / "poster.png")
    (source / "a.txt").write_text("same bytes", encoding="utf-8")
    (source / "b.txt").write_text("same bytes", encoding="utf-8")
    before = {path.name: path.read_bytes() for path in source.iterdir()}
    out = tmp_path / "derived"

    result = ingesta_archivo.run(source, out, full_hash_mb=1,
                                 perception_limit=0, timeout=1)

    assert result["inventory"]["assets"] == 3
    assert result["inventory"]["exact_duplicate_relations"] == 1
    assert result["perception"] == {"requested": 0, "processed": 0,
                                    "failed": 0, "skipped": 0}
    assert (out / "summary.json").is_file()
    assert {path.name: path.read_bytes() for path in source.iterdir()} == before

    with sqlite3.connect(out / "archivo_index.sqlite") as conn:
        relation_count = conn.execute(
            "SELECT COUNT(*) FROM relations WHERE relation='exact_duplicate'"
        ).fetchone()[0]
        assert relation_count == 1


def test_structure_lineage_routes_to_judge_without_identity_promotion(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "left.txt").write_text("left", encoding="utf-8")
    (source / "right.txt").write_text("right", encoding="utf-8")
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        ingesta_archivo.inventory(conn, source, full_hash_limit=1024)
        root_key = ingesta_archivo.source_key(source)
        left_id = ingesta_archivo.asset_key(root_key, "left.txt")
        right_id = ingesta_archivo.asset_key(root_key, "right.txt")
        manifest = {
            "status": "OBSERVED",
            "tool": "fixture",
            "evidence_edges": [{
                "relation": "has_document_id",
                "right_id": "document:shared-fixture",
                "status": "candidate",
                "evidence": {"key": "shared-fixture"},
            }],
        }

        first = ingesta_archivo.project_structure_evidence(conn, left_id, manifest)
        second = ingesta_archivo.project_structure_evidence(conn, right_id, manifest)
        gate = ingesta_archivo.build_evidence_gate(conn, left_id)

        assert first["lineage_edges_written"] == 0
        assert second["lineage_edges_written"] == 1
        assert gate["route"] == "ROUTE_TO_JUDGE"
        assert gate["identity_resolution"].startswith("candidate_only")
        assert gate["promotion"] == "none"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Pure helpers: deterministic in, deterministic out, no DB or filesystem
# mocking needed.
# ---------------------------------------------------------------------------

def test_media_kind_classifies_every_known_family_and_falls_back_to_other():
    assert ingesta_archivo.media_kind(Path("a.PNG")) == "image"
    assert ingesta_archivo.media_kind(Path("a.mp4")) == "video"
    assert ingesta_archivo.media_kind(Path("a.pdf")) == "pdf"
    assert ingesta_archivo.media_kind(Path("a.psd")) == "structural"
    assert ingesta_archivo.media_kind(Path("a.txt")) == "other"


def test_is_within_distinguishes_child_from_sibling(tmp_path: Path):
    parent = tmp_path / "parent"
    child = parent / "child"
    sibling = tmp_path / "sibling"
    child.mkdir(parents=True)
    sibling.mkdir()
    assert ingesta_archivo.is_within(child, parent) is True
    assert ingesta_archivo.is_within(sibling, parent) is False
    assert ingesta_archivo.is_within(parent, parent) is True


def test_sample_fingerprint_reads_head_and_tail_of_a_large_file(
        tmp_path: Path, monkeypatch):
    # CHUNK is 1 MiB in production; shrink it so a "large" file (> CHUNK)
    # stays cheap to write in a test while still exercising the head+tail
    # branch instead of only the small-file path.
    monkeypatch.setattr(ingesta_archivo, "CHUNK", 8)
    path = tmp_path / "big.bin"
    path.write_bytes(b"HEADHEAD" + b"." * 100 + b"TAILTAIL")
    size = path.stat().st_size
    first = ingesta_archivo.sample_fingerprint(path, size)
    second = ingesta_archivo.sample_fingerprint(path, size)
    assert first == second
    small_path = tmp_path / "small.bin"
    small_path.write_bytes(b"tiny")
    assert ingesta_archivo.sample_fingerprint(small_path, 4) != first


def test_split_venue_and_city_separates_a_known_city_alias():
    assert ingesta_archivo.split_venue_and_city("Espacio Riesco, Santiago") == (
        "Espacio Riesco", "Santiago")
    assert ingesta_archivo.split_venue_and_city("Unknown Place") == ("Unknown Place", "")
    assert ingesta_archivo.split_venue_and_city("") == ("", "")


def test_cartel_norm_and_date_anchors_pick_high_confidence_boxes_only():
    assert ingesta_archivo._cartel_norm("Café, Éxito!") == "cafeexito"
    boxes = [
        {"text": "12.03", "confidence": 90, "y": 10},
        {"text": "12.03", "confidence": 20, "y": 10},  # low confidence, same line: skipped
        {"text": "not-a-date", "confidence": 99, "y": 10},
        {"text": "13.03", "confidence": 91, "y": 300},  # far enough to be a new anchor
    ]
    anchors = ingesta_archivo._cartel_date_anchors(boxes)
    assert [box["text"] for box in anchors] == ["12.03", "13.03"]


def test_cartel_raw_venue_lines_and_join_recognize_known_venue_fragments():
    text = "ESPACIO\nRIESCO\nrandomjunkline\n12.03"
    lines = ingesta_archivo._cartel_raw_venue_lines(text)
    assert lines == ["ESPACIO", "RIESCO"]
    joined = ingesta_archivo._cartel_join_venue_words(lines)
    assert joined[0] == "ESPACIO RIESCO"


def test_cartel_city_candidates_matches_known_aliases_only():
    assert ingesta_archivo._cartel_city_candidates("evento en Valparaiso este verano") == [
        "Valparaíso"]
    assert ingesta_archivo._cartel_city_candidates("sin ciudad reconocible") == []


def test_canonical_producer_matches_only_exact_normalized_identity(
        tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ingesta_archivo, "REPO_ROOT", tmp_path)
    catalog_dir = tmp_path / "data" / "productoras"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "acme.json").write_text(json.dumps({
        "name": "Acme", "aliases": ["Acme Producciones"],
        "venues": [], "logos": [],
    }), encoding="utf-8")

    found = ingesta_archivo.canonical_producer("acme producciones")
    assert found is not None
    assert found["record"]["name"] == "Acme"
    assert found["path"] == "data/productoras/acme.json"
    assert ingesta_archivo.canonical_producer("Nonexistent Brand") is None


# ---------------------------------------------------------------------------
# raster_metadata(): the Pillow-optional sensor inside ingesta_archivo.py
# itself. Same doctrine as the archive_toolchain absence tests: the
# degraded state must be a named status, not a crash or a fabricated
# metadata blob.
# ---------------------------------------------------------------------------

def test_raster_metadata_names_absence_when_pillow_is_unavailable(
        tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ingesta_archivo, "Image", None)
    result = ingesta_archivo.raster_metadata(tmp_path / "whatever.png")
    assert result == {"status": "DEFERRED_TOOL", "reason": "pillow_unavailable"}


def test_raster_metadata_observes_real_png_dimensions(tmp_path: Path):
    path = tmp_path / "poster.png"
    Image.new("RGB", (16, 9), "red").save(path)
    result = ingesta_archivo.raster_metadata(path)
    assert result["status"] == "OBSERVED"
    assert (result["width"], result["height"]) == (16, 9)
    assert result["observer"] == "Pillow"


def test_raster_metadata_retries_on_a_corrupt_image_instead_of_raising(tmp_path: Path):
    path = tmp_path / "corrupt.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"not-really-a-png")
    result = ingesta_archivo.raster_metadata(path)
    assert result["status"] == "RETRY"
    assert "reason" in result


# ---------------------------------------------------------------------------
# project_structure_evidence(): the two early, evidence-free returns that
# the lineage test above never reaches.
# ---------------------------------------------------------------------------

def test_project_structure_evidence_rejects_non_dict_manifest_and_blank_asset():
    conn = sqlite3.connect(":memory:")
    assert ingesta_archivo.project_structure_evidence(conn, "a1", None) == {
        "status": "NO_MANIFEST", "edges_written": 0,
        "lineage_edges_written": 0, "promotion": "none",
    }
    assert ingesta_archivo.project_structure_evidence(conn, "  ", {"status": "OBSERVED"}) == {
        "status": "NO_ASSET", "edges_written": 0,
        "lineage_edges_written": 0, "promotion": "none",
    }


# ---------------------------------------------------------------------------
# project_visual_surface_evidence(): a read-only projection of an existing
# derived visual index (`cultura/mak_plataforma/visual_index.py`).
# ---------------------------------------------------------------------------

def test_visual_surface_evidence_requires_both_asset_and_source_id(tmp_path: Path):
    conn = sqlite3.connect(":memory:")
    result = ingesta_archivo.project_visual_surface_evidence(
        conn, "", "poster.png", tmp_path)
    assert result == {"status": "NO_SOURCE_MAPPING", "neighbors_written": 0,
                       "promotion": "none"}


def test_visual_surface_evidence_defers_when_index_file_is_missing(tmp_path: Path):
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        asset_id = _seed_asset(conn, tmp_path / "source", "poster.png")
        result = ingesta_archivo.project_visual_surface_evidence(
            conn, asset_id, "poster.png", tmp_path / "no_index_here")
        assert result["status"] == "DEFERRED_SURFACE"
        assert result["neighbors_written"] == 0
    finally:
        conn.close()


def test_visual_surface_evidence_projects_eligible_and_abstained_neighbors(
        tmp_path: Path):
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        asset_id = _seed_asset(conn, tmp_path / "source", "poster.png")
        surface_dir = tmp_path / "visual_index"
        surface_dir.mkdir()
        (surface_dir / "neighbors.json").write_text(json.dumps({
            "model": "mobileclip", "model_version": "v1",
            "thresholds": {"eligible": 0.6},
            "items": {
                "unit-1": {
                    "source_id": "poster.png", "unit_id": "unit-1",
                    "neighbors": [
                        {"item_id": "unit-2", "eligible": True, "score": 0.91},
                        {"item_id": "unit-3", "eligible": False, "score": 0.40},
                    ],
                },
            },
        }), encoding="utf-8")

        result = ingesta_archivo.project_visual_surface_evidence(
            conn, asset_id, "poster.png", surface_dir, limit=16)

        assert result["status"] == "PROJECTED"
        assert result["neighbors_written"] == 2
        assert result["eligible"] == 1
        assert result["abstained"] == 1
        relations = {
            row["right_id"]: (row["relation"], row["status"])
            for row in conn.execute("SELECT relation,right_id,status FROM relations")
        }
        assert relations["visual:unit-2"] == ("visual_similarity_candidate", "candidate")
        assert relations["visual:unit-3"] == ("visual_similarity_abstained", "abstain")
    finally:
        conn.close()


def test_visual_surface_evidence_names_absence_when_visual_index_module_missing(
        tmp_path: Path, monkeypatch):
    import builtins
    original_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "cultura.mak_plataforma.visual_index":
            raise ImportError("optional module absent (simulated by test)")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        asset_id = _seed_asset(conn, tmp_path / "source", "poster.png")
        result = ingesta_archivo.project_visual_surface_evidence(
            conn, asset_id, "poster.png", tmp_path)
        assert result["status"] == "DEFERRED_TOOL"
        assert result["neighbors_written"] == 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# project_sequence_coverage()
# ---------------------------------------------------------------------------

def test_sequence_coverage_is_not_applicable_without_a_numbered_family():
    conn = sqlite3.connect(":memory:")
    result = ingesta_archivo.project_sequence_coverage(
        conn, "a1", "fam1", {"frame_count": 0, "video_count": 0}, None)
    assert result["status"] == "NOT_APPLICABLE"


def test_sequence_coverage_stays_unresolved_without_an_observed_structure():
    conn = sqlite3.connect(":memory:")
    result = ingesta_archivo.project_sequence_coverage(
        conn, "a1", "fam1", {"frame_count": 40, "video_count": 1}, {"status": "RETRY"})
    assert result == {"status": "UNRESOLVED", "reason": "video_structure_not_observed",
                       "expected_frames": 40, "promotion": "none"}


def test_sequence_coverage_flags_sufficient_and_insufficient_video_frames(tmp_path: Path):
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        asset_id = _seed_asset(conn, tmp_path / "source", "reel.mp4")
        structure = {"status": "OBSERVED", "metadata": {
            "streams": [{"nb_frames": "48", "r_frame_rate": "24/1"}],
            "format": {"duration": "2.0"},
        }}
        covers = ingesta_archivo.project_sequence_coverage(
            conn, asset_id, "fam1", {"frame_count": 40, "video_count": 1}, structure)
        assert covers["status"] == "PROJECTED"
        assert covers["relation"] == "video_covers_sequence_candidate"
        assert covers["observed_frames"] == 48

        short = ingesta_archivo.project_sequence_coverage(
            conn, asset_id, "fam1", {"frame_count": 100, "video_count": 1}, structure)
        assert short["relation"] == "video_sequence_coverage_insufficient"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# build_evidence_gate(): the two branches the lineage test above never
# reaches (no evidence at all, and an unresolved identity candidate).
# ---------------------------------------------------------------------------

def test_evidence_gate_defers_a_blank_asset_id():
    conn = sqlite3.connect(":memory:")
    gate = ingesta_archivo.build_evidence_gate(conn, "")
    assert gate["route"] == "DEFERRED"
    assert gate["reason"] == "asset_missing"


def test_evidence_gate_defers_an_asset_with_zero_evidence_branches(tmp_path: Path):
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        asset_id = _seed_asset(conn, tmp_path / "source", "lonely.txt")
        gate = ingesta_archivo.build_evidence_gate(conn, asset_id)
        assert gate["route"] == "DEFERRED"
        assert gate["reason"] == "insufficient_independent_evidence_branches"
        assert gate["active_branches"] == []
    finally:
        conn.close()


def test_evidence_gate_abstains_on_an_unresolved_identity_candidate(tmp_path: Path):
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        asset_id = _seed_asset(conn, tmp_path / "source", "flyer.png")
        ingesta_archivo.store_candidate(
            conn, asset_id, "productora_cruda", "Acme", {"pipeline": "test"})
        gate = ingesta_archivo.build_evidence_gate(conn, asset_id)
        assert gate["route"] == "ABSTAIN"
        assert gate["reason"] == "identity_quorum_not_proven"
        assert gate["identity_candidate_count"] == 1
        assert gate["identity_candidate_kinds"] == ["productora_cruda"]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# run_perception(): both success and per-item failure, with a fake
# `percepcion.construir_ficha` standing in for the real OCR/vision pipeline
# (never invoked in this test suite). `escribir_ficha` is the real,
# side-effect-free file writer.
# ---------------------------------------------------------------------------

def _install_fake_perception_module(monkeypatch):
    from cultura.mak_curatoria.percepcion import escribir_ficha

    def fake_build_record(entry, tmp_dir, file_timeout, meta_ig=None):
        if "bad" in entry["ruta_rel"]:
            return {"ruta_rel": entry["ruta_rel"], "error": "ocr_timeout",
                    "ocr_texto": "", "vision": {}}
        return {"ruta_rel": entry["ruta_rel"], "error": None,
                "ocr_texto": "flyer text", "vision": {"objetos": []}}

    fake_module = types.ModuleType("percepcion")
    fake_module.construir_ficha = fake_build_record
    fake_module.escribir_ficha = escribir_ficha
    monkeypatch.setitem(sys.modules, "percepcion", fake_module)


def test_run_perception_returns_zero_immediately_when_limit_is_not_positive(tmp_path: Path):
    conn = sqlite3.connect(":memory:")
    result = ingesta_archivo.run_perception(
        conn, tmp_path, tmp_path / "out", limit=0, timeout=5)
    assert result == {"requested": 0, "processed": 0, "failed": 0, "skipped": 0}


def test_run_perception_marks_success_and_failure_as_distinct_job_states(
        tmp_path: Path, monkeypatch):
    _install_fake_perception_module(monkeypatch)
    source = tmp_path / "source"
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        source.mkdir()
        Image.new("RGB", (4, 4), "white").save(source / "good.png")
        Image.new("RGB", (4, 4), "white").save(source / "bad.png")
        ingesta_archivo.inventory(conn, source, full_hash_limit=1 << 20)

        result = ingesta_archivo.run_perception(
            conn, source, out, limit=10, timeout=5)

        assert result["processed"] == 1
        assert result["failed"] == 1
        jobs = {
            row["asset_id"]: (row["status"], row["last_error"])
            for row in conn.execute(
                "SELECT j.asset_id,j.status,j.last_error FROM jobs j "
                "WHERE j.stage='perception'")
        }
        good_id = conn.execute(
            "SELECT asset_id FROM assets WHERE relative_path='good.png'").fetchone()[0]
        bad_id = conn.execute(
            "SELECT asset_id FROM assets WHERE relative_path='bad.png'").fetchone()[0]
        assert jobs[good_id] == ("done", None)
        assert jobs[bad_id] == ("retry", "ocr_timeout")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# project_candidates(): the cheap early return, plus the full projection
# path with a fake `extraccion_db.procesar` (the real ficha->candidate
# pipeline has its own dedicated test module) feeding a crafted
# `candidatos_db.jsonl` through this function's own routing logic.
# ---------------------------------------------------------------------------

def test_project_candidates_reports_missing_perception_output_without_guessing(
        tmp_path: Path):
    conn = sqlite3.connect(":memory:")
    result = ingesta_archivo.project_candidates(conn, tmp_path / "derived")
    assert result == {"candidates": 0, "reason": "no_perception_output"}


def test_project_candidates_routes_event_producer_venue_and_logo_evidence(
        tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ingesta_archivo, "REPO_ROOT", tmp_path / "repo")
    catalog_dir = tmp_path / "repo" / "data" / "productoras"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "acme.json").write_text(json.dumps({
        "name": "Acme",
        "venues": [{"nombre": "Espacio Riesco", "venue_id": "v1", "estado": "activo"}],
        "logos": [{"id": "logoA", "estado": "encontrado", "archivo": "logo.svg",
                   "raster": "", "fuente": "catalog", "obtenido": "2020"}],
    }), encoding="utf-8")

    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        asset_id = _seed_asset(conn, tmp_path / "source", "poster.png")

        records_dir = out / "perception" / "fichas"
        records_dir.mkdir(parents=True)
        (records_dir / "fichas.jsonl").write_text("")  # existence gate only

        def fake_procesar(records_path, outdir, **_source_kwargs):
            outdir = Path(outdir)
            outdir.mkdir(parents=True, exist_ok=True)
            row = {
                "ruta_rel": "poster.png", "obra_id": "obra1", "calidad_senal": "alta",
                "fecha_cruda": "12.03", "productora_cruda": "Acme Prod",
                "productora_canonica": "Acme", "match_ratio": 0.9,
                "venue_crudo": "Espacio Riesco, Santiago",
            }
            (outdir / "candidatos_db.jsonl").write_text(
                json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
            return {"status": "fake", "candidatos": 1}

        fake_module = types.ModuleType("extraccion_db")
        fake_module.procesar = fake_procesar
        monkeypatch.setitem(sys.modules, "extraccion_db", fake_module)

        result = ingesta_archivo.project_candidates(conn, out)

        assert result["candidates"] > 0
        kinds = {row["kind"]: row["value"] for row in conn.execute(
            "SELECT kind,value FROM candidates WHERE asset_id=?", (asset_id,))}
        assert kinds["fecha_cruda"] == "12.03"
        assert kinds["productora_cruda"] == "Acme Prod"
        assert kinds["city"] == "Santiago"
        assert kinds["venue_reference"] == "v1"
        assert kinds["logo_reference"] == "logoA"

        relations = {row["relation"] for row in conn.execute(
            "SELECT relation FROM relations WHERE left_id=?", (asset_id,))}
        assert "has_candidate_venue" in relations
        assert "has_catalogued_logo" in relations

        jobs = {row["stage"]: row["status"] for row in conn.execute(
            "SELECT stage,status FROM jobs WHERE asset_id=?", (asset_id,))}
        assert jobs["resolve_producer"] == "done"
        assert jobs["resolve_logo"] == "done"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# project_composite_cartel(): the two cheap early returns, plus one full
# pass with a fake `_cartel_tsv` standing in for real tesseract output.
# ---------------------------------------------------------------------------

def test_composite_cartel_reports_asset_not_found_and_non_image_kind(tmp_path: Path):
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        assert ingesta_archivo.project_composite_cartel(
            conn, tmp_path, out, "missing-asset")["status"] == "ASSET_NOT_FOUND"

        asset_id = _seed_asset(conn, tmp_path / "source", "notes.txt")
        assert ingesta_archivo.project_composite_cartel(
            conn, tmp_path / "source", out, asset_id)["status"] == "NOT_AN_IMAGE"
    finally:
        conn.close()


def test_composite_cartel_projects_one_module_per_synthetic_date_anchor(
        tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ingesta_archivo, "REPO_ROOT", tmp_path / "repo")

    def fake_cartel_tsv(path, timeout):
        return [
            {"text": "12.03", "confidence": 90, "x": 10, "y": 50, "width": 40, "height": 10},
            {"text": "13.03", "confidence": 90, "x": 10, "y": 250, "width": 40, "height": 10},
        ]

    monkeypatch.setattr(ingesta_archivo, "_cartel_tsv", fake_cartel_tsv)

    source = tmp_path / "source"
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        source.mkdir()
        Image.new("RGB", (300, 500), "white").save(source / "cartel.png")
        asset_id = _seed_asset(conn, source, "cartel.png")

        result = ingesta_archivo.project_composite_cartel(conn, source, out, asset_id)

        assert result["status"] == "PROJECTED"
        assert result["date_anchors"] == 2
        assert result["modules"] == 2
        assert len(result["module_ids"]) == 2

        module_candidates = conn.execute(
            "SELECT kind,value,status FROM cartel_module_candidates "
            "WHERE module_id IN (SELECT module_id FROM cartel_modules WHERE asset_id=?)",
            (asset_id,),
        ).fetchall()
        dates = [row["value"] for row in module_candidates if row["kind"] == "date"]
        venues = [row for row in module_candidates if row["kind"] == "venue"]
        assert sorted(dates) == ["12.03", "13.03"]
        assert all(row["value"] == "unknown" and row["status"] == "unresolved"
                   for row in venues)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# project_folder_brand_queue()
# ---------------------------------------------------------------------------

def test_folder_brand_queue_is_unresolved_not_negative_without_any_signal(
        tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ingesta_archivo, "REPO_ROOT", tmp_path / "repo")
    source = tmp_path / "source"
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        _seed_asset(conn, source, "unrelated.txt")
        result = ingesta_archivo.project_folder_brand_queue(
            conn, source, out, ["Ghost Brand"])
        assert result == {"status": "PROJECTED", "brands": 1,
                           "path": str(out / "brand_research_queue.json"),
                           "promotion": "none"}
        payload = json.loads((out / "brand_research_queue.json").read_text(encoding="utf-8"))
        assert payload["brands"][0]["status"] == "unresolved_not_negative"
        assert payload["brands"][0]["folder_history"]["hits"] == 0
    finally:
        conn.close()


def test_folder_brand_queue_finds_a_folder_history_hit_from_the_path_itself(
        tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ingesta_archivo, "REPO_ROOT", tmp_path / "repo")
    source = tmp_path / "source"
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        _seed_asset(conn, source, "KLANG afiche.png")
        result = ingesta_archivo.project_folder_brand_queue(conn, source, out, ["KLANG"])
        assert result["brands"] == 1
        payload = json.loads((out / "brand_research_queue.json").read_text(encoding="utf-8"))
        brand_row = payload["brands"][0]
        assert brand_row["status"] == "candidate_research"
        assert brand_row["folder_history"]["hits"] >= 1
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# summary() / scan_folder_identity_history()
# ---------------------------------------------------------------------------

def test_summary_groups_assets_jobs_and_relations_after_inventory(tmp_path: Path):
    source = tmp_path / "source"
    out = tmp_path / "derived"
    conn = ingesta_archivo.connect(out)
    try:
        (source).mkdir()
        (source / "a.txt").write_text("same", encoding="utf-8")
        (source / "b.txt").write_text("same", encoding="utf-8")
        ingesta_archivo.inventory(conn, source, full_hash_limit=1 << 20)
        result = ingesta_archivo.summary(conn)
        assert result["schema"] == ingesta_archivo.SCHEMA
        assert result["assets_by_kind"] == {"other": 2}
        assert result["relations"] == {"exact_duplicate": 1}
    finally:
        conn.close()
