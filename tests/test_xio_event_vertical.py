import sqlite3
import tempfile
import unittest
from pathlib import Path

from flujo.rd.xio_ingest import ensure_event_schema, ingest, load_samples, sync_event


class XioEventVerticalTests(unittest.TestCase):
    def make_db(self):
        handle = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        handle.close()
        path = Path(handle.name)
        conn = sqlite3.connect(path)
        conn.executescript(
            """
            CREATE TABLE mesas_testeo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evento_ref TEXT NOT NULL,
                evento_origen TEXT NOT NULL,
                numero INTEGER,
                etiqueta TEXT,
                origen TEXT NOT NULL,
                UNIQUE(evento_ref, evento_origen, etiqueta)
            );
            CREATE TABLE muestras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                mesa_id INTEGER,
                evento_ref TEXT,
                evento_origen TEXT,
                codigo_muestra TEXT,
                sustancia_declarada TEXT NOT NULL,
                tipo_muestra TEXT,
                color TEXT,
                textura TEXT,
                logo_o_marca TEXT,
                peso_mg REAL,
                foto_ref TEXT,
                notas TEXT,
                descartada INTEGER DEFAULT 0
            );
            CREATE TABLE muestra_resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                muestra_id INTEGER NOT NULL,
                reactivo TEXT NOT NULL,
                resultado_color TEXT,
                familia_detectada TEXT,
                coincide_con_declarada INTEGER,
                adulterante_sospechado TEXT,
                limitacion TEXT NOT NULL,
                orden INTEGER
            );
            """
        )
        conn.commit()
        conn.close()
        return path

    def test_event_sync_is_idempotent_and_bounded(self):
        path = self.make_db()
        try:
            payload = {
                "clientEventId": "xio-2026-09-11-001",
                "eventName": "Noche XIO",
                "venue": "Sala Norte",
                "producer": "Productora Candidata",
                "startDate": "2026-09-11",
                "endDate": "2026-09-12",
                "djs": ["DJ A", "DJ B"],
                "triangulation": {"sources": ["flyer", "venue"]},
                "flyerRef": "xio_evidence/flyer.jpg",
                "flyerSha256": "a" * 64,
            }
            first = sync_event(payload, path)
            payload["venue"] = "Sala Norte 2"
            second = sync_event(payload, path)
            self.assertFalse(first["duplicate"])
            self.assertTrue(second["duplicate"])
            conn = sqlite3.connect(path)
            row = conn.execute(
                "SELECT COUNT(*), venue_name, djs_json FROM xio_eventos "
                "WHERE client_event_id=?", (payload["clientEventId"],)
            ).fetchone()
            conn.close()
            self.assertEqual(row[0], 1)
            self.assertEqual(row[1], "Sala Norte 2")
            self.assertIn("DJ A", row[2])
        finally:
            path.unlink(missing_ok=True)

    def test_event_ref_closes_sample_chain_and_read_projection(self):
        path = self.make_db()
        evidence = path.parent / (path.name + "-evidence")
        try:
            event = sync_event(
                {"clientEventId": "xio-chain-1", "eventName": "Evento de prueba"},
                path,
            )
            result = ingest(
                {
                    "date": "2026-09-11",
                    "eventRef": event["eventRef"],
                    "eventOrigin": event["eventOrigin"],
                    "sampleCode": "M-001",
                    "substanceDeclared": "sin dato",
                    "mesa": {"label": "Mesa XIO"},
                    "tests": [{"reagent": "Marquis", "resultColor": "morado"}],
                },
                path,
                evidence,
            )
            projection = load_samples(path, event["eventRef"])
            self.assertEqual(projection["sampleCount"], 1)
            self.assertEqual(projection["samples"][0]["sampleId"], result["sampleId"])
            self.assertEqual(projection["samples"][0]["tests"][0]["resultColor"], "morado")
        finally:
            path.unlink(missing_ok=True)
            if evidence.exists():
                evidence.rmdir()

    def test_invalid_identity_and_dates_are_rejected(self):
        path = self.make_db()
        try:
            with self.assertRaises(ValueError):
                sync_event(
                    {"clientEventId": "xio-bad-1", "eventName": "Evento", "email": "x@y"},
                    path,
                )
            with self.assertRaises(ValueError):
                sync_event(
                    {
                        "clientEventId": "xio-bad-2",
                        "eventName": "Evento",
                        "startDate": "2026-09-12",
                        "endDate": "2026-09-11",
                    },
                    path,
                )
            with self.assertRaises(ValueError):
                sync_event(
                    {"clientEventId": "xio-bad-3", "eventName": "Evento", "flyerSha256": "no"},
                    path,
                )
        finally:
            path.unlink(missing_ok=True)

    def test_schema_can_be_created_on_existing_database(self):
        path = self.make_db()
        try:
            conn = sqlite3.connect(path)
            ensure_event_schema(conn)
            ensure_event_schema(conn)
            count = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='xio_eventos'"
            ).fetchone()[0]
            conn.close()
            self.assertEqual(count, 1)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
