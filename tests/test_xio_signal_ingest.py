import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path

from flujo.rd.xio_ingest import (
    load_application_events,
    sync_application_event,
)


def _event(event_id, sequence, **overrides):
    value = {
        "eventId": event_id,
        "eventRef": "event-001",
        "sourceApp": "XIO",
        "eventType": "preflight.completed",
        "channel": "instar",
        "payload": {"phase": "preflight", "status": "pass"},
        "sourceTimestamp": f"2026-09-11T10:00:{sequence:02d}Z",
        "receivedTimestamp": f"2026-09-11T10:00:{sequence + 1:02d}Z",
        "sessionId": "session-001",
        "peerId": "peer-001",
        "sequence": sequence,
        "rawHash": f"sha256:{sequence:03d}",
        "provenance": {"transport": "offline", "producer": "test"},
    }
    value.update(overrides)
    return value


def test_signal_event_is_idempotent_and_replay_ordered():
    with TemporaryDirectory(prefix="xio-signal-test-") as folder:
        db = Path(folder) / "rd.db"
        first = sync_application_event(_event("evt-002", 2), db)
        second = sync_application_event(_event("evt-001", 1), db)
        duplicate = sync_application_event(_event("evt-001", 1), db)

        assert first["duplicate"] is False
        assert second["duplicate"] is False
        assert duplicate["duplicate"] is True
        rows = load_application_events(db, "session-001")
        assert [row["event_id"] for row in rows] == ["evt-001", "evt-002"]
        assert rows[0]["payload"] == {"phase": "preflight", "status": "pass"}
        with sqlite3.connect(db) as con:
            assert con.execute(
                "SELECT COUNT(*) FROM xio_signal_events"
            ).fetchone()[0] == 2


def test_signal_event_rejects_conflicting_identity_and_sequence():
    with TemporaryDirectory(prefix="xio-signal-test-") as folder:
        db = Path(folder) / "rd.db"
        sync_application_event(_event("evt-001", 1), db)

        try:
            sync_application_event(
                _event("evt-001", 1, rawHash="sha256:changed"), db
            )
        except ValueError as exc:
            assert "contenido diferente" in str(exc)
        else:
            raise AssertionError("conflicting event_id was accepted")

        try:
            sync_application_event(_event("evt-other", 1), db)
        except ValueError as exc:
            assert "sequence" in str(exc)
        else:
            raise AssertionError("conflicting sequence was accepted")


def test_signal_event_requires_timezone_and_technical_identity():
    with TemporaryDirectory(prefix="xio-signal-test-") as folder:
        db = Path(folder) / "rd.db"
        try:
            sync_application_event(
                _event("evt-001", 1, sourceTimestamp="2026-09-11T10:00:00"),
                db,
            )
        except ValueError as exc:
            assert "zona horaria" in str(exc)
        else:
            raise AssertionError("timezone-less event was accepted")

        try:
            sync_application_event(_event("evt-\u00f1", 1), db)
        except ValueError as exc:
            assert "ASCII" in str(exc)
        else:
            raise AssertionError("non-ASCII technical id was accepted")
