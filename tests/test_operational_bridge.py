import json
import sqlite3

from flujo.knowledge.operational_bridge import refresh_operational_bridge


def _rd(path):
    with sqlite3.connect(path) as con:
        con.executescript(
            """
            CREATE TABLE productoras (slug TEXT PRIMARY KEY, nombre TEXT, confirmado INTEGER, aliases TEXT);
            CREATE TABLE venues (id INTEGER PRIMARY KEY, nombre TEXT);
            CREATE TABLE productora_eventos (id INTEGER PRIMARY KEY, productora_slug TEXT, nombre TEXT, fecha TEXT, venue INTEGER, estado TEXT, fuente TEXT);
            INSERT INTO productoras VALUES ('demo-prod','Demo Producer',1,'[]');
            INSERT INTO venues VALUES (4,'Demo Venue');
            INSERT INTO productora_eventos VALUES (9,'demo-prod','Demo Event','2026-09-01',4,'observed','issue://9');
            """
        )


def _fondart(path):
    with sqlite3.connect(path) as con:
        con.executescript(
            """
            CREATE TABLE fondart_applications (application_id TEXT PRIMARY KEY, capture_id TEXT, source_folio TEXT, reported_year INTEGER, area_or_modality TEXT, project_title TEXT, responsible TEXT, amount_raw TEXT, amount_clp INTEGER, selected_status TEXT, partial INTEGER, source_url TEXT, source_text TEXT);
            INSERT INTO fondart_applications VALUES ('fa-1','cap-1','folio-1',2026,'Digital','Demo Garden','Demo Producer','$100',100,'selected',0,'https://example.test/fondart','long source text omitted from projection');
            """
        )


def _intake(path):
    with sqlite3.connect(path) as con:
        con.executescript(
            """
            CREATE TABLE intake_projects (run_id TEXT, project_id TEXT, title TEXT, status TEXT);
            CREATE TABLE fund_targets (run_id TEXT, fund_id TEXT, name TEXT, status TEXT, requirements_json TEXT, evidence_json TEXT);
            CREATE TABLE application_packages (run_id TEXT, application_id TEXT, project_id TEXT, fund_id TEXT, status TEXT, title TEXT, sections_json TEXT, evidence_json TEXT, gaps_json TEXT, outputs_json TEXT);
            CREATE TABLE mak_links (link_id INTEGER, run_id TEXT, project_id TEXT, relation TEXT, mak_path TEXT, artifact_id INTEGER, entity_kind TEXT, confidence TEXT, evidence_json TEXT);
            INSERT INTO intake_projects VALUES ('run-1','project-1','Demo Garden','candidate');
            INSERT INTO fund_targets VALUES ('run-1','fondart','Fondart','active','{}','{}');
            INSERT INTO application_packages VALUES ('run-1','app-1','project-1','fondart','draft','Demo Garden','{}','{}','{}','{}');
            INSERT INTO mak_links VALUES (1,'run-1','project-1','uses_tool','/home/mak/flujo/tools/demo.py',42,'tool','high','{"source":"fixture"}');
            """
        )


def test_bridge_materializes_operational_records_and_exact_links(tmp_path):
    rd = tmp_path / "rd.db"
    fondart = tmp_path / "fondart.sqlite"
    intake = tmp_path / "intake.sqlite"
    target = tmp_path / "master.db"
    _rd(rd)
    _fondart(fondart)
    _intake(intake)

    result = refresh_operational_bridge(target, rd, intake, fondart)

    assert result["source_rows_copied"] == 0
    with sqlite3.connect(target) as con:
        assert con.execute("SELECT COUNT(*) FROM operational_records").fetchone()[0] == 7
        assert con.execute("SELECT COUNT(*) FROM operational_links").fetchone()[0] == 4
        assert con.execute("SELECT COUNT(*) FROM operational_curation_links").fetchone()[0] == 1
        assert con.execute("SELECT venue_name FROM operational_records WHERE record_id='rd_event:9'").fetchone()[0] == 'Demo Venue'
        payload = con.execute("SELECT payload_json FROM operational_records WHERE record_id='fondart_application:fa-1'").fetchone()[0]
        assert 'long source text omitted' not in payload


def test_bridge_refresh_is_idempotent_and_replaces_derived_rows(tmp_path):
    rd = tmp_path / "rd.db"
    fondart = tmp_path / "fondart.sqlite"
    intake = tmp_path / "intake.sqlite"
    target = tmp_path / "master.db"
    _rd(rd)
    _fondart(fondart)
    _intake(intake)
    refresh_operational_bridge(target, rd, intake, fondart)
    refresh_operational_bridge(target, rd, intake, fondart)
    with sqlite3.connect(target) as con:
        assert con.execute("SELECT COUNT(*) FROM operational_records").fetchone()[0] == 7
        assert con.execute("SELECT COUNT(*) FROM operational_runs").fetchone()[0] == 1


def test_bridge_projects_xio_and_rd_lineage_without_text_identity_joins(tmp_path):
    rd = tmp_path / "rd.db"
    fondart = tmp_path / "fondart.sqlite"
    intake = tmp_path / "intake.sqlite"
    target = tmp_path / "master.db"
    _rd(rd)
    with sqlite3.connect(rd) as con:
        con.executescript(
            """
            CREATE TABLE testeo_eventos_fuente (event_id TEXT PRIMARY KEY, event_label_candidate TEXT, date_iso_candidate TEXT, link_review_status TEXT, producer_name_candidate TEXT, venue_name_candidate TEXT);
            CREATE TABLE testeo_filas_fuente (test_id TEXT PRIMARY KEY, event_id TEXT, substance_raw TEXT, row_status TEXT);
            CREATE TABLE testeo_observaciones_fuente (observation_id TEXT PRIMARY KEY, test_id TEXT, event_id TEXT, reagent_raw TEXT, result_raw TEXT, observation_status TEXT);
            CREATE TABLE xio_eventos (id INTEGER PRIMARY KEY, client_event_id TEXT, event_name TEXT, venue_name TEXT, producer_name TEXT, start_date TEXT, djs_json TEXT, triangulation_json TEXT, review_status TEXT, sync_status TEXT);
            CREATE TABLE mesas_testeo (id INTEGER PRIMARY KEY, evento_ref TEXT, evento_origen TEXT, etiqueta TEXT);
            CREATE TABLE muestras (id INTEGER PRIMARY KEY, fecha TEXT, mesa_id INTEGER, evento_ref TEXT, evento_origen TEXT, codigo_muestra TEXT, sustancia_declarada TEXT, descartada INTEGER);
            CREATE TABLE muestra_capturas (id INTEGER PRIMARY KEY, muestra_id INTEGER, capture_key TEXT, kind TEXT, geometry_signature TEXT, photo_ref TEXT);
            CREATE TABLE muestra_resultados (id INTEGER PRIMARY KEY, muestra_id INTEGER, reactivo TEXT, resultado_color TEXT);
            CREATE TABLE xio_signal_events (event_id TEXT PRIMARY KEY, event_ref TEXT, event_type TEXT, source_timestamp TEXT, payload_json TEXT, provenance_json TEXT);
            INSERT INTO testeo_eventos_fuente VALUES ('hist-1','Candidate','2025-07-26','pending_human_link','Do not promote','Do not promote');
            INSERT INTO testeo_filas_fuente VALUES ('row-1','hist-1','MDMA','observed');
            INSERT INTO testeo_observaciones_fuente VALUES ('obs-1','row-1','hist-1','Marquis','yellow','observed');
            INSERT INTO xio_eventos VALUES (1,'xio-1','XIO Demo','Text Venue','Text Producer','2026-09-10','[{"name":"DJ"}]','{"venue":"flyer"}','pending_human_review','synced');
            INSERT INTO mesas_testeo VALUES (1,'xio-1','xio_app','mesa 1');
            INSERT INTO muestras VALUES (1,'2026-09-10',1,'xio-1','xio_app','M-1','declared',0);
            INSERT INTO muestra_capturas VALUES (1,1,'cap-1','photo','geom-v1','sha256:abc');
            INSERT INTO muestra_resultados VALUES (1,1,'Marquis','purple');
            INSERT INTO xio_signal_events VALUES ('sig-1','xio-1','capture','2026-09-10T01:02:03Z','{"ok":true}','{"source":"xio"}');
            """
        )
    _fondart(fondart)
    _intake(intake)

    result = refresh_operational_bridge(target, rd, intake, fondart)

    assert result["record_count"] == 16
    with sqlite3.connect(target) as con:
        event = con.execute(
            "SELECT producer_name, venue_name, payload_json FROM operational_records WHERE record_id='xio_event:xio-1'"
        ).fetchone()
        assert event[:2] == ("Text Producer", "Text Venue")
        assert json.loads(event[2])["djs"] == [{"name": "DJ"}]
        domains = {row[0] for row in con.execute("SELECT domain FROM operational_records")}
        assert {"rd_test_event", "rd_test_row", "rd_test_observation", "xio_sample_capture", "xio_sample_result", "xio_signal_event"} <= domains
        links = set(con.execute("SELECT source_record_id, relation, target_record_id FROM operational_links"))
        assert ("xio_sample:1", "context_of", "xio_event:xio-1") in links
        assert ("xio_sample_capture:1", "capture_of", "xio_sample:1") in links
        assert ("xio_signal_event:sig-1", "context_of", "xio_event:xio-1") in links
        assert con.execute("SELECT producer_name, venue_name FROM operational_records WHERE record_id='rd_test_event:hist-1'").fetchone() == (None, None)


def test_bridge_replaces_stale_snapshot_by_logical_scope(tmp_path):
    rd = tmp_path / "rd.db"
    fondart = tmp_path / "fondart.sqlite"
    intake = tmp_path / "intake.sqlite"
    target = tmp_path / "master.db"
    _rd(rd)
    _fondart(fondart)
    _intake(intake)
    refresh_operational_bridge(target, rd, intake, fondart)
    with sqlite3.connect(target) as con:
        con.execute(
            "UPDATE operational_records SET source_path=? WHERE record_id='fondart_application:fa-1'",
            ("/home/mak/research/corpus/retired-v5/sources.sqlite",),
        )
        con.commit()
    refresh_operational_bridge(target, rd, intake, fondart)
    with sqlite3.connect(target) as con:
        assert con.execute("SELECT source_path FROM operational_records WHERE record_id='fondart_application:fa-1'").fetchone()[0] == str(fondart.resolve())
        assert con.execute("SELECT COUNT(*) FROM operational_records WHERE domain='fondart_application'").fetchone()[0] == 1
