from __future__ import annotations

import sqlite3
from pathlib import Path

from PIL import Image

from cultura.mak_curatoria import ingesta_archivo


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
