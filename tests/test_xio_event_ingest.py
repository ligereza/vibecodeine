import json
import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path

from flujo.rd.xio_ingest import sync_event


def _event(**overrides):
    value = {
        "clientEventId": "xio-event-20260911",
        "eventName": "Noche XIO",
        "venue": "Recinto Norte",
        "producer": "Productora Sur",
        "startDate": "2026-09-20",
        "endDate": "2026-09-21",
        "djs": ["DJ A", "DJ B"],
        "triangulation": {
            "sources": ["flyer", "producer"],
            "status": "pendiente_revision_humana",
        },
        "flyerRef": "flyers/xio-event.png",
        "flyerSha256": "a" * 64,
        "source": "xio_app",
        "reviewStatus": "pendiente_revision_humana",
    }
    value.update(overrides)
    return value


def test_event_sync_preserves_context_and_is_idempotent():
    with TemporaryDirectory(prefix="xio-event-test-") as folder:
        db = Path(folder) / "rd.db"
        first = sync_event(_event(), db)
        second = sync_event(
            _event(
                eventName="Noche XIO corregida",
                djs=["DJ A", "DJ C"],
                reviewStatus="en_revision",
            ),
            db,
        )

        assert first["duplicate"] is False
        assert second["duplicate"] is True
        assert second["eventId"] == first["eventId"]
        with sqlite3.connect(db) as con:
            assert con.execute(
                "SELECT COUNT(*) FROM xio_eventos"
            ).fetchone()[0] == 1
            row = con.execute(
                "SELECT event_name, venue_name, producer_name, start_date, "
                "end_date, djs_json, triangulation_json, flyer_ref, "
                "flyer_sha256, source, review_status, sync_status "
                "FROM xio_eventos"
            ).fetchone()

        assert row[:5] == (
            "Noche XIO corregida",
            "Recinto Norte",
            "Productora Sur",
            "2026-09-20",
            "2026-09-21",
        )
        assert json.loads(row[5]) == ["DJ A", "DJ C"]
        assert json.loads(row[6]) == _event()["triangulation"]
        assert row[7:] == (
            "flyers/xio-event.png",
            "a" * 64,
            "xio_app",
            "en_revision",
            "synced",
        )


def test_event_sync_rejects_invalid_context_and_identity_fields():
    with TemporaryDirectory(prefix="xio-event-test-") as folder:
        db = Path(folder) / "rd.db"
        cases = [
            (_event(endDate="2026-09-19"), "endDate"),
            (_event(flyerSha256="not-a-sha256"), "flyerSha256"),
            (_event(email="not-an-event-field"), "identidad"),
        ]
        for payload, expected in cases:
            try:
                sync_event(payload, db)
            except ValueError as exc:
                assert expected in str(exc)
            else:
                raise AssertionError(f"invalid event accepted: {expected}")

