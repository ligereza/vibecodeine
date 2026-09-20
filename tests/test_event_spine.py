from __future__ import annotations

import json

import pytest

from cultura.mak_plataforma.event_spine import (
    EventCrosswalk,
    EventSpineError,
    JsonLineEventSpine,
    new_event_id,
)


def _crosswalk(**changes):
    values = {
        "event_id": "evt_12345678",
        "rd_event_ref": "rd:fecha-01",
        "vj_event_key": "vj:show-01",
        "producer_refs": ("producer:uno", "producer:coproductora"),
        "venue_ref": "venue:galpon",
        "venue_revision_ref": "venue:galpon@2026-09-20",
        "sources": ("jobs/fecha-01.json", "foh/context.json#show-01"),
        "relation_status": "reviewed",
    }
    values.update(changes)
    return EventCrosswalk(**values)


def test_round_trip_keeps_event_producer_and_venue_distinct():
    value = _crosswalk()
    restored = EventCrosswalk.from_dict(value.to_dict())

    assert restored == value
    assert restored.event_id not in restored.producer_refs
    assert restored.venue_ref != restored.venue_revision_ref


def test_event_identity_is_opaque_and_not_derived_from_producer():
    first, second = new_event_id(), new_event_id()

    assert first.startswith("evt_") and second.startswith("evt_")
    assert first != second
    with pytest.raises(EventSpineError, match="opaque"):
        _crosswalk(event_id="producer:uno:2026-09-20")


def test_crosswalk_requires_a_domain_reference_and_sources():
    with pytest.raises(EventSpineError, match="rd_event_ref or vj_event_key"):
        _crosswalk(rd_event_ref=None, vj_event_key=None)
    with pytest.raises(EventSpineError, match="sources"):
        _crosswalk(sources=())
    with pytest.raises(EventSpineError, match="venue_revision_ref"):
        _crosswalk(venue_ref=None)


def test_ledger_is_idempotent_and_rejects_identity_rewrite(tmp_path):
    ledger = JsonLineEventSpine(tmp_path / "event_spine.jsonl")

    assert ledger.append(_crosswalk()) is True
    assert ledger.append(_crosswalk()) is False
    assert ledger.read() == [_crosswalk()]

    with pytest.raises(EventSpineError, match="conflicting event_id"):
        ledger.append(_crosswalk(relation_status="observed"))


def test_ledger_detects_tampering(tmp_path):
    path = tmp_path / "event_spine.jsonl"
    ledger = JsonLineEventSpine(path)
    ledger.append(_crosswalk())
    record = json.loads(path.read_text(encoding="utf-8"))
    record["crosswalk"]["producer_refs"] = ["producer:otro"]
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    with pytest.raises(EventSpineError, match="ledger hash"):
        ledger.read()
