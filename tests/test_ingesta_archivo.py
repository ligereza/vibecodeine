import importlib.util
import sqlite3
import tempfile
import unittest
import json
from pathlib import Path


MODULE = Path(__file__).parents[1] / "cultura" / "mak_curatoria" / "ingesta_archivo.py"
SPEC = importlib.util.spec_from_file_location("ingesta_archivo", MODULE)
ingesta_archivo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ingesta_archivo)


class IngestaArchivoTests(unittest.TestCase):
    def test_indexes_without_writing_source_and_marks_exact_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            out = base / "derived"
            root.mkdir()
            original = b"same bytes, different original filename"
            (root / "uno.psd").write_bytes(original)
            (root / "dos.ai").write_bytes(original)
            (root / "grande.mov").write_bytes(b"x" * 128)

            result = ingesta_archivo.run(root, out, full_hash_mb=1,
                                         perception_limit=0, timeout=1)

            self.assertEqual((root / "uno.psd").read_bytes(), original)
            self.assertEqual(result["inventory"]["assets"], 3)
            self.assertTrue((out / "archivo_index.sqlite").is_file())
            with sqlite3.connect(out / "archivo_index.sqlite") as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0], 1)
                self.assertEqual(conn.execute(
                    "SELECT COUNT(*) FROM jobs WHERE stage='extract_structure' AND status='ready'"
                ).fetchone()[0], 2)
                asset_id = conn.execute(
                    "SELECT asset_id FROM assets WHERE relative_path='uno.psd'"
                ).fetchone()[0]
                conn.execute("UPDATE jobs SET status='done' WHERE asset_id=? AND stage='extract_structure'",
                             (asset_id,))
                conn.commit()
            # A later inventory must not requeue completed durable work.
            ingesta_archivo.run(root, out, full_hash_mb=1,
                                perception_limit=0, timeout=1)
            with sqlite3.connect(out / "archivo_index.sqlite") as conn:
                self.assertEqual(conn.execute(
                    "SELECT status FROM jobs WHERE asset_id=? AND stage='extract_structure'", (asset_id,)
                ).fetchone()[0], "done")

    def test_refuses_derived_output_inside_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "source"
            root.mkdir()
            with self.assertRaises(ValueError):
                ingesta_archivo.run(root, root / "derived", 1, 0, 1)

    def test_projects_structure_edges_and_exact_lineage_as_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root, out = base / "source", base / "derived"
            root.mkdir()
            (root / "main.psd").write_bytes(b"main")
            (root / "autosave.psd").write_bytes(b"autosave")
            ingesta_archivo.run(root, out, full_hash_mb=1,
                                perception_limit=0, timeout=1)
            conn = sqlite3.connect(out / "archivo_index.sqlite")
            conn.row_factory = sqlite3.Row
            ids = [row["asset_id"] for row in conn.execute(
                "SELECT asset_id FROM assets ORDER BY relative_path")]
            for index, asset_id in enumerate(ids):
                projection = ingesta_archivo.project_structure_evidence(
                    conn, asset_id, {
                        "status": "OBSERVED", "tool": "test",
                        "evidence_edges": [
                            {
                                "relation": "has_document_id",
                                "right_id": "xmp:document_id:shared",
                                "status": "candidate", "evidence": {"fixture": True},
                            },
                            {
                                "relation": "embedded_date_candidate",
                                "right_id": "xmp:create_date:2025-01-0%d" % (index + 1),
                                "status": "candidate", "evidence": {"fixture": True},
                            },
                        ],
                    })
                self.assertEqual(projection["status"], "PROJECTED")
            conn.commit()
            rows = conn.execute(
                "SELECT relation,status FROM relations ORDER BY relation"
            ).fetchall()
            self.assertEqual([row["relation"] for row in rows].count("has_document_id"), 2)
            self.assertEqual([row["relation"] for row in rows].count(
                "same_embedded_lineage_key"), 1)
            self.assertEqual([row["relation"] for row in rows].count(
                "lineage_context_divergence_candidate"), 1)
            self.assertTrue(all(row["status"] == "candidate" for row in rows))
            conn.close()

    def test_projects_visual_neighbors_and_preserves_abstentions(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root, out = base / "source", base / "derived"
            root.mkdir()
            (root / "representative.png").write_bytes(b"pixel")
            ingesta_archivo.run(root, out, full_hash_mb=1,
                                perception_limit=0, timeout=1)
            surface = base / "neighbors.json"
            surface.write_text(__import__("json").dumps({
                "schema": "faro-portfolio-visual-neighbors-v1",
                "model": "MobileCLIP-S0", "model_version": "test",
                "thresholds": {"min_score": .5, "min_margin": .01},
                "items": {"publication:test": {
                    "source_id": "portfolio-source.png",
                    "source_ids": ["portfolio-source.png"],
                    "neighbors": [
                        {"item_id": "near.png", "eligible": True,
                         "score": .8, "margin": .1},
                        {"item_id": "weak.png", "eligible": False,
                         "score": .49, "margin": .001,
                         "abstention_reason": "score_insuficiente"},
                    ],
                }},
            }), encoding="utf-8")
            conn = sqlite3.connect(out / "archivo_index.sqlite")
            conn.row_factory = sqlite3.Row
            asset_id = conn.execute(
                "SELECT asset_id FROM assets WHERE relative_path='representative.png'"
            ).fetchone()[0]
            result = ingesta_archivo.project_visual_surface_evidence(
                conn, asset_id, "portfolio-source.png", surface.parent)
            conn.commit()
            self.assertEqual(result["status"], "PROJECTED")
            self.assertEqual(result["eligible"], 1)
            self.assertEqual(result["abstained"], 1)
            rows = conn.execute(
                "SELECT relation,status FROM relations WHERE left_id=?",
                (asset_id,)).fetchall()
            self.assertEqual({row["relation"] for row in rows}, {
                "visual_similarity_candidate", "visual_similarity_abstained"})
            self.assertEqual({row["status"] for row in rows}, {"candidate", "abstain"})
            conn.close()

    def test_sequence_coverage_is_candidate_and_unresolved_is_not_negative(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root, out = base / "source", base / "derived"
            root.mkdir()
            (root / "render.mp4").write_bytes(b"video")
            ingesta_archivo.run(root, out, full_hash_mb=1,
                                perception_limit=0, timeout=1)
            conn = sqlite3.connect(out / "archivo_index.sqlite")
            conn.row_factory = sqlite3.Row
            asset_id = conn.execute(
                "SELECT asset_id FROM assets WHERE relative_path='render.mp4'"
            ).fetchone()[0]
            covered = ingesta_archivo.project_sequence_coverage(
                conn, asset_id, "family-seq",
                {"frame_count": 10, "video_count": 1},
                {"status": "OBSERVED", "metadata": {
                    "streams": [{"nb_frames": "12", "r_frame_rate": "30/1"}],
                    "format": {"duration": "0.4"},
                }})
            self.assertEqual(covered["relation"], "video_covers_sequence_candidate")
            unresolved = ingesta_archivo.project_sequence_coverage(
                conn, asset_id, "family-empty",
                {"frame_count": 10, "video_count": 1},
                {"status": "OBSERVED", "metadata": {"streams": []}})
            self.assertEqual(unresolved["status"], "UNRESOLVED")
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM relations WHERE relation='video_covers_sequence_candidate'"
            ).fetchone()[0], 1)
            conn.close()

    def test_evidence_gate_routes_without_resolving_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root, out = base / "source", base / "derived"
            root.mkdir()
            (root / "representative.png").write_bytes(b"pixel")
            ingesta_archivo.run(root, out, full_hash_mb=1,
                                perception_limit=0, timeout=1)
            conn = sqlite3.connect(out / "archivo_index.sqlite")
            conn.row_factory = sqlite3.Row
            asset_id = conn.execute(
                "SELECT asset_id FROM assets WHERE relative_path='representative.png'"
            ).fetchone()[0]
            ingesta_archivo.store_observation(
                conn, asset_id, "structure", "manifest", {"status": "OBSERVED"})
            first = ingesta_archivo.build_evidence_gate(conn, asset_id)
            self.assertEqual(first["route"], "DEFERRED")
            ingesta_archivo.store_relation(
                conn, asset_id, "video_covers_sequence_candidate", "family:one",
                {"fixture": True}, None, "candidate")
            second = ingesta_archivo.build_evidence_gate(conn, asset_id)
            self.assertEqual(second["route"], "ROUTE_TO_JUDGE")
            ingesta_archivo.store_relation(
                conn, asset_id, "lineage_context_divergence_candidate", "asset:two",
                {"fixture": True}, None, "candidate")
            third = ingesta_archivo.build_evidence_gate(conn, asset_id)
            self.assertEqual(third["route"], "ABSTAIN")
            self.assertEqual(third["reason"], "evidence_conflict_requires_judge")
            conn.close()

    def test_composite_cartel_splits_date_modules_and_keeps_logo_states(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root, out = base / "source", base / "derived"
            root.mkdir()
            image = root / "cartel.png"
            # Sensor is patched: this fixture tests the projection contract,
            # not OCR quality or a model response.
            image.write_bytes(b"not-a-real-image")
            ingesta_archivo.run(root, out, full_hash_mb=1,
                                perception_limit=0, timeout=1)
            conn = sqlite3.connect(out / "archivo_index.sqlite")
            conn.row_factory = sqlite3.Row
            asset_id = conn.execute("SELECT asset_id FROM assets").fetchone()[0]
            ingesta_archivo.Image = type("FakeImage", (), {})
            # Exercise only the new candidate tables through the same storage
            # primitives when the optional raster sensor is unavailable.
            ingesta_archivo._ensure_composite_schema(conn)
            conn.execute("INSERT INTO cartel_modules VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         ("module-1", asset_id, 1, 0, 0, 10, 10, "crop.png",
                          "05.06 DAME", json.dumps({"fixture": True}), "observed", ingesta_archivo.now()))
            ingesta_archivo.store_cartel_module_candidate(
                conn, "module-1", "logo_catalog", "dame_primary",
                {"fixture": True}, 1.0, "catalog_missing_asset")
            ingesta_archivo.store_cartel_module_candidate(
                conn, "module-1", "logo_local_asset", "knowledge/logos/descargas/dame.png",
                {"fixture": True}, None, "candidate")
            conn.commit()
            rows = conn.execute("SELECT kind,status FROM cartel_module_candidates").fetchall()
            self.assertEqual({tuple(row) for row in rows}, {
                ("logo_catalog", "catalog_missing_asset"),
                ("logo_local_asset", "candidate"),
            })
            conn.close()


if __name__ == "__main__":
    unittest.main()
