
import base64
import hashlib
import sqlite3
import tempfile
from pathlib import Path

from flujo.rd.xio_ingest import ingest, load_samples


def _schema(connection):
    connection.executescript(
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
            limitacion TEXT NOT NULL DEFAULT 'presuntivo: senal de presencia, no identidad ni pureza ni dosis',
            orden INTEGER
        );
        """
    )


def test_load_samples_returns_event_chain_without_photo_bytes():
    with tempfile.TemporaryDirectory(prefix="xio-read-test-") as folder:
        db = Path(folder) / "rd.db"
        with sqlite3.connect(db) as connection:
            _schema(connection)
        ingest(
            {
                "schema": "xio-flujo-rd-v1",
                "date": "2026-09-11",
                "eventRef": "event-read-001",
                "eventOrigin": "app",
                "sampleCode": "M-READ-001",
                "substanceDeclared": "sin declarar",
                "sampleType": "tableta",
                "color": "azul",
                "mesa": {"label": "XIO / mesa móvil", "number": 1},
                "captures": [{
                    "id": "cap-read-001",
                    "kind": "photo",
                    "capturedAt": 1789120800000,
                    "sha256": "a" * 64,
                    "photoRef": "sha256:" + "a" * 64,
                    "silhouetteRef": "svg:cap-read-001",
                    "geometrySignature": "geom-read",
                    "contourPointCount": 12,
                }],
                "tests": [{
                    "reagent": "Marquis",
                    "order": 1,
                    "resultColor": "amarillo",
                    "matchesDeclared": None,
                }],
            },
            db,
            Path(folder) / "evidence",
        )
        result = load_samples(db, "event-read-001")
        assert result["sampleCount"] == 1
        sample = result["samples"][0]
        assert sample["sampleCode"] == "M-READ-001"
        assert sample["captures"][0]["geometrySignature"] == "geom-read"
        assert sample["tests"][0]["resultColor"] == "amarillo"
        assert "photoBase64" not in sample["captures"][0]


def test_load_samples_filters_by_exact_sample_code():
    with tempfile.TemporaryDirectory(prefix="xio-read-filter-") as folder:
        db = Path(folder) / "rd.db"
        with sqlite3.connect(db) as connection:
            _schema(connection)
        for code in ("M-001", "M-002"):
            ingest(
                {
                    "date": "2026-09-11",
                    "eventRef": "event-read-002",
                    "sampleCode": code,
                    "substanceDeclared": "sin declarar",
                    "mesa": {"label": "XIO / mesa móvil", "number": 1},
                    "tests": [],
                },
                db,
                Path(folder) / "evidence",
            )
        result = load_samples(db, "event-read-002", "M-002")
        assert [item["sampleCode"] for item in result["samples"]] == ["M-002"]

def test_ingest_accepts_gateway_envelope_and_upserts_evidence():
    with tempfile.TemporaryDirectory(prefix="xio-ingest-test-") as folder:
        db = Path(folder) / "rd.db"
        evidence = Path(folder) / "evidence"
        raw = b"xio-photo"
        digest = hashlib.sha256(raw).hexdigest()
        payload = {
            "schema": "xio-flujo-rd-v1",
            "date": "2026-09-11",
            "eventRef": "event-gateway-001",
            "eventOrigin": "app",
            "sampleCode": "M-GATEWAY-001",
            "substanceDeclared": "MDMA",
            "sampleType": "cristal",
            "color": "azul",
            "texture": "propuesta XIO",
            "logoOrMark": "marca observada",
            "mesa": {"label": "XIO / mesa móvil", "number": 1},
            "notes": "captura de prueba",
            "captures": [{
                "id": "cap-gateway-001",
                "kind": "photo",
                "capturedAt": 1789120800000,
                "sha256": digest,
                "silhouetteRef": "svg:cap-gateway-001",
                "silhouettePreviewRef": "png:cap-gateway-001",
                "reliefRef": "svg:cap-gateway-001.relief",
                "geometrySignature": "geom-gateway",
                "reliefSignature": "relief-gateway",
                "silhouetteConfidence": 0.91,
                "reliefConfidence": 0.82,
                "circularity": 0.73,
                "solidity": 0.88,
                "symmetry": 0.67,
                "contourPointCount": 24,
                "photoBase64": base64.b64encode(raw).decode("ascii"),
            }],
            "tests": [
                {
                    "reagent": "Marquis",
                    "order": 1,
                    "resultColor": "morado",
                    "matchesDeclared": True,
                },
                {
                    "reagent": "Mecke",
                    "order": 2,
                    "resultColor": "verde",
                    "matchesDeclared": None,
                },
            ],
        }
        with sqlite3.connect(db) as connection:
            _schema(connection)

        first = ingest(payload, db, evidence)
        payload["notes"] = "captura corregida"
        payload["tests"][0]["resultColor"] = "morado oscuro"
        second = ingest(payload, db, evidence)

        assert first["duplicate"] is False
        assert second["duplicate"] is True
        assert second["sampleId"] == first["sampleId"]
        assert second["captureCount"] == 1
        assert len(second["resultIds"]) == 2
        assert (evidence / (digest + ".jpg")).is_file()
        with sqlite3.connect(db) as connection:
            assert connection.execute("SELECT COUNT(*) FROM muestras").fetchone()[0] == 1
            assert connection.execute("SELECT COUNT(*) FROM muestra_capturas").fetchone()[0] == 1
            assert connection.execute("SELECT COUNT(*) FROM muestra_resultados").fetchone()[0] == 2
            capture = connection.execute(
                "SELECT geometry_signature, relief_signature, silhouette_confidence "
                "FROM muestra_capturas"
            ).fetchone()
            result = connection.execute(
                "SELECT resultado_color FROM muestra_resultados "
                "WHERE reactivo = ? AND orden = ?",
                ("Marquis", 1),
            ).fetchone()
        assert capture == ("geom-gateway", "relief-gateway", 0.91)
        assert result == ("morado oscuro",)

        read = load_samples(db, "event-gateway-001")
        sample = read["samples"][0]
        assert sample["notes"].startswith("captura corregida")
        assert sample["captures"][0]["photoRef"].startswith("xio_evidence/")
        assert "photoBase64" not in sample["captures"][0]
        assert [test["reagent"] for test in sample["tests"]] == ["Marquis", "Mecke"]
