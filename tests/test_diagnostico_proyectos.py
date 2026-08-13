import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
INGESTA_SPEC = importlib.util.spec_from_file_location(
    "ingesta_archivo", ROOT / "cultura" / "mak_curatoria" / "ingesta_archivo.py")
ingesta = importlib.util.module_from_spec(INGESTA_SPEC)
INGESTA_SPEC.loader.exec_module(ingesta)
DIAG_SPEC = importlib.util.spec_from_file_location(
    "diagnostico_proyectos", ROOT / "cultura" / "mak_curatoria" / "diagnostico_proyectos.py")
diagnostico = importlib.util.module_from_spec(DIAG_SPEC)
DIAG_SPEC.loader.exec_module(diagnostico)


class DiagnosticoProyectosTests(unittest.TestCase):
    def test_video_represents_render_sequence_and_keeps_role_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            db = base / "archivo_index.sqlite"
            conn = ingesta.connect(base)
            for index, (relative, ext, kind) in enumerate([
                ("CLIENTE_A/animacion/project.blend", ".blend", "structural"),
                ("CLIENTE_A/animacion/render_0001.png", ".png", "image"),
                ("CLIENTE_A/animacion/render_0002.png", ".png", "image"),
                ("CLIENTE_A/animacion/render_0003.png", ".png", "image"),
                ("CLIENTE_A/animacion/render_0004.png", ".png", "image"),
                ("CLIENTE_A/animacion/render_0005.png", ".png", "image"),
                ("CLIENTE_A/animacion/animacion.mp4", ".mp4", "video"),
            ]):
                asset_id = "asset-%d" % index
                conn.execute(
                    """INSERT INTO assets(asset_id,source_key,relative_path,extension,media_kind,
                       bytes,mtime_ns,sample_sha256,full_sha256,hash_state,hash_error,indexed_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (asset_id, "source", relative, ext, kind, 100 + index, index,
                     None, None, "pending", None, "now"),
                )
            conn.commit()
            diagnostico.create_schema(conn)
            result = diagnostico.diagnose(conn)
            self.assertEqual(result["projects"], 1)
            family = conn.execute(
                "SELECT family_kind,strategy,representative_asset_id,member_count FROM families"
            ).fetchone()
            self.assertEqual(tuple(family), ("animation_sequence", "video_first_frames_deferred", "asset-6", 7))
            project = conn.execute("SELECT owner_status,dimensionality,strategy FROM projects").fetchone()
            self.assertEqual(project[0], "client_candidate")
            self.assertEqual(project[1], "3d")
            self.assertEqual(project[2], "diagnose_editable_and_video")
            conn.close()

    def test_backup_marker_is_storage_role_not_work_identity(self):
        self.assertEqual(
            diagnostico.role_from_path("iCloud/obra", "iCloud")[2],
            "backup_or_archive_candidate",
        )
        self.assertEqual(
            diagnostico.role_from_path("iCloud/obra", "iCloud")[0],
            "personal_candidate",
        )

    def test_organism_plan_routes_video_first_without_resolving_identity(self):
        plan = diagnostico.organism_plan({
            "family_id": "family-1",
            "project_id": "project-1",
            "family_kind": "animation_sequence",
            "strategy": "video_first_frames_deferred",
            "representative_asset_id": "asset-video",
            "representative_reason": "video_completo",
        }, "obra/render.mp4")
        self.assertEqual(plan["schema"], "mak-family-triangulation-plan-v1")
        self.assertEqual(plan["status"], "awaiting_coverage")
        self.assertTrue(plan["scope"]["process_representative_first"])
        self.assertTrue(plan["representative"]["video_first"])
        self.assertEqual(plan["work"]["schema"], "mak-work-v1")
        self.assertTrue(plan["work_contract_valid"], plan["work_contract_errors"])
        self.assertEqual(plan["work"]["identity"]["entities"]["artist"], [])
        self.assertEqual(plan["work"]["identity"]["entities"]["client"], [])
        self.assertEqual(plan["promotion"], "none")
        self.assertEqual(plan["join_policy"]["minimum_independent_evidence"], 2)
        valid, errors = diagnostico.validate_organism_plan(plan)
        self.assertTrue(valid, errors)
        invalid = dict(plan)
        invalid["promotion"] = "published"
        valid, errors = diagnostico.validate_organism_plan(invalid)
        self.assertFalse(valid)
        self.assertIn("plan_promotion_not_none", errors)

    def test_organism_plan_defers_cache_without_provider_work(self):
        plan = diagnostico.organism_plan({
            "family_id": "family-cache",
            "project_id": "project-1",
            "family_kind": "asset_family",
            "strategy": "metadata_only_deferred",
            "representative_asset_id": "asset-cache",
            "representative_reason": "metadata_unica",
        }, "cache/preview.png")
        self.assertEqual(plan["status"], "deferred")
        self.assertEqual(plan["work"]["status"], "coverage_deferred")
        self.assertEqual(plan["work"]["next_action"], "archive_metadata_only")
        required = {branch["name"] for branch in plan["branches"] if branch["required"]}
        self.assertEqual(required, {"coverage", "claim_safety"})
        self.assertFalse(plan["scope"]["process_representative_first"])

    def test_structure_branch_exposes_installed_adapter(self):
        plan = diagnostico.organism_plan({
            "family_id": "family-video", "project_id": "project-video",
            "family_kind": "video_bundle", "strategy": "inspect_video",
            "representative_asset_id": "asset-video",
            "representative_reason": "video_completo", "media_kind": "video",
        }, "clip.mp4")
        structure = [row for row in plan["execution"]["ready"]
                     if row.get("branch") == "structure"]
        self.assertEqual(len(structure), 1)
        self.assertEqual(structure[0]["adapter"], "ffprobe")
        valid, errors = diagnostico.validate_organism_plan(plan)
        self.assertTrue(valid, errors)

    def test_sidecar_names_are_non_content(self):
        self.assertTrue(diagnostico.is_non_content_path("folder/._render.mp4"))
        self.assertTrue(diagnostico.is_non_content_path(".DS_Store"))
        self.assertFalse(diagnostico.is_non_content_path("folder/render.mp4"))

    def test_coverage_gate_separates_strong_ambiguous_and_unmatched(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "source"
            derived = base / "derived"
            source.mkdir()
            (source / "REVIEWED").mkdir()
            (source / "AMBIGUOUS").mkdir()
            (source / "UNSEEN").mkdir()
            (source / "REVIEWED" / "movie.mp4").write_bytes(b"reviewed")
            (source / "AMBIGUOUS" / "same.png").write_bytes(b"ambiguous")
            (source / "UNSEEN" / "new.png").write_bytes(b"unseen")
            ingesta.run(source, derived, full_hash_mb=0, perception_limit=0, timeout=1)
            conn = sqlite3.connect(derived / "archivo_index.sqlite")
            conn.row_factory = sqlite3.Row
            diagnostico.create_schema(conn)
            diagnostico.diagnose(conn)
            prior = base / "prior.jsonl"
            prior.write_text("\n".join([
                json.dumps({"ruta_rel": "movie.mp4", "bytes": 8, "fuente": "old-fichas"}),
                json.dumps({"ruta_rel": "old/same.png", "bytes": 9, "fuente": "old-a"}),
                json.dumps({"ruta_rel": "other/same.png", "bytes": 9, "fuente": "old-b"}),
            ]) + "\n", encoding="utf-8")
            coverage = diagnostico.apply_coverage(conn, [str(prior)])
            self.assertEqual(coverage["family_status"]["already_reviewed"], 1)
            self.assertEqual(coverage["family_status"]["ambiguous"], 1)
            self.assertEqual(coverage["family_status"]["unreviewed"], 1)
            rows = conn.execute(
                """SELECT p.project_path, fc.status FROM family_coverage fc
                   JOIN families f ON f.family_id=fc.family_id
                   JOIN projects p ON p.project_id=f.project_id
                   WHERE fc.run_id=?""", (coverage["run_id"],)
            ).fetchall()
            statuses = {row["project_path"]: row["status"] for row in rows}
            self.assertEqual(statuses["REVIEWED"], "already_reviewed")
            self.assertEqual(statuses["AMBIGUOUS"], "ambiguous")
            self.assertEqual(statuses["UNSEEN"], "unreviewed")
            conn.close()


if __name__ == "__main__":
    unittest.main()
