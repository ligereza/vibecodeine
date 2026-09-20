"""Event identity spine shared by IRIS, RD, VJ and XIO.

The event is a dated occurrence.  A producer, venue and venue revision are
separate entities.  This module stores only the cross-domain relation; it does
not copy RD samples, VJ logs or private evidence between authorities.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "mak-event-crosswalk-v1"
RELATION_STATUSES = frozenset({"declared", "observed", "reviewed"})
_EVENT_ID = re.compile(r"^evt_[A-Za-z0-9][A-Za-z0-9._~-]*$")
_FIELDS = frozenset({
    "event_id", "rd_event_ref", "vj_event_key", "producer_refs",
    "venue_ref", "venue_revision_ref", "sources", "relation_status",
})


class EventSpineError(ValueError):
    """The crosswalk or its append-only ledger violates the contract."""


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EventSpineError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, field)


def _text_tuple(value: Any, field: str, *, required: bool = False) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or isinstance(value, (str, bytes)):
        raise EventSpineError(f"{field} must be a list of strings")
    result = tuple(_required_text(item, field) for item in value)
    if required and not result:
        raise EventSpineError(f"{field} must not be empty")
    if len(set(result)) != len(result):
        raise EventSpineError(f"{field} contains duplicates")
    return result


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def new_event_id() -> str:
    """Create an opaque identifier; no producer, venue or date is inferred."""
    return "evt_" + uuid.uuid4().hex


@dataclass(frozen=True)
class EventCrosswalk:
    event_id: str
    rd_event_ref: str | None
    vj_event_key: str | None
    producer_refs: tuple[str, ...]
    venue_ref: str | None
    venue_revision_ref: str | None
    sources: tuple[str, ...]
    relation_status: str

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, str) or not _EVENT_ID.fullmatch(self.event_id):
            raise EventSpineError("event_id must be an opaque evt_ identifier")
        rd_event_ref = _optional_text(self.rd_event_ref, "rd_event_ref")
        vj_event_key = _optional_text(self.vj_event_key, "vj_event_key")
        if self.rd_event_ref is None and self.vj_event_key is None:
            raise EventSpineError("crosswalk needs rd_event_ref or vj_event_key")
        producer_refs = _text_tuple(self.producer_refs, "producer_refs")
        venue = _optional_text(self.venue_ref, "venue_ref")
        revision = _optional_text(self.venue_revision_ref, "venue_revision_ref")
        if revision is not None and venue is None:
            raise EventSpineError("venue_revision_ref requires venue_ref")
        sources = _text_tuple(self.sources, "sources", required=True)
        if self.relation_status not in RELATION_STATUSES:
            raise EventSpineError("invalid relation_status")
        object.__setattr__(self, "rd_event_ref", rd_event_ref)
        object.__setattr__(self, "vj_event_key", vj_event_key)
        object.__setattr__(self, "producer_refs", producer_refs)
        object.__setattr__(self, "venue_ref", venue)
        object.__setattr__(self, "venue_revision_ref", revision)
        object.__setattr__(self, "sources", sources)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "EventCrosswalk":
        if not isinstance(raw, Mapping):
            raise EventSpineError("crosswalk must be an object")
        if set(raw) != _FIELDS:
            missing, extra = _FIELDS - set(raw), set(raw) - _FIELDS
            raise EventSpineError(f"crosswalk fields mismatch: missing={sorted(missing)} extra={sorted(extra)}")
        return cls(
            event_id=_required_text(raw["event_id"], "event_id"),
            rd_event_ref=_optional_text(raw["rd_event_ref"], "rd_event_ref"),
            vj_event_key=_optional_text(raw["vj_event_key"], "vj_event_key"),
            producer_refs=_text_tuple(raw["producer_refs"], "producer_refs"),
            venue_ref=_optional_text(raw["venue_ref"], "venue_ref"),
            venue_revision_ref=_optional_text(raw["venue_revision_ref"], "venue_revision_ref"),
            sources=_text_tuple(raw["sources"], "sources", required=True),
            relation_status=_required_text(raw["relation_status"], "relation_status"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "rd_event_ref": self.rd_event_ref,
            "vj_event_key": self.vj_event_key,
            "producer_refs": list(self.producer_refs),
            "venue_ref": self.venue_ref,
            "venue_revision_ref": self.venue_revision_ref,
            "sources": list(self.sources),
            "relation_status": self.relation_status,
        }

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(_canonical(self.to_dict())).hexdigest()


class JsonLineEventSpine:
    """Small append-only, hash-chained crosswalk ledger.

    Re-appending an identical event is idempotent.  Reusing an ``event_id``
    with different content fails rather than silently changing history.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")

    @staticmethod
    def _record_hash(record: Mapping[str, Any]) -> str:
        payload = {key: value for key, value in record.items() if key != "record_hash"}
        return hashlib.sha256(_canonical(payload)).hexdigest()

    def _read_unlocked(self) -> list[EventCrosswalk]:
        if not self.path.exists():
            return []
        rows: list[EventCrosswalk] = []
        previous_hash = "0" * 64
        seen: dict[str, str] = {}
        with self.path.open("r", encoding="utf-8") as handle:
            for sequence, line in enumerate(handle, start=1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise EventSpineError(f"invalid JSON at sequence {sequence}") from exc
                expected = {"schema", "sequence", "previous_hash", "crosswalk", "record_hash"}
                if not isinstance(record, dict) or set(record) != expected:
                    raise EventSpineError(f"invalid ledger record at sequence {sequence}")
                if record["schema"] != SCHEMA or record["sequence"] != sequence:
                    raise EventSpineError(f"invalid ledger sequence {sequence}")
                if record["previous_hash"] != previous_hash:
                    raise EventSpineError(f"broken ledger chain at sequence {sequence}")
                if record["record_hash"] != self._record_hash(record):
                    raise EventSpineError(f"invalid ledger hash at sequence {sequence}")
                crosswalk = EventCrosswalk.from_dict(record["crosswalk"])
                existing = seen.get(crosswalk.event_id)
                if existing is not None and existing != crosswalk.fingerprint:
                    raise EventSpineError(f"conflicting event_id {crosswalk.event_id}")
                if existing is None:
                    rows.append(crosswalk)
                    seen[crosswalk.event_id] = crosswalk.fingerprint
                previous_hash = record["record_hash"]
        return rows

    def read(self) -> list[EventCrosswalk]:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
            try:
                return self._read_unlocked()
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def append(self, crosswalk: EventCrosswalk) -> bool:
        if not isinstance(crosswalk, EventCrosswalk):
            raise EventSpineError("append requires EventCrosswalk")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                existing = self._read_unlocked()
                for current in existing:
                    if current.event_id == crosswalk.event_id:
                        if current.fingerprint == crosswalk.fingerprint:
                            return False
                        raise EventSpineError(f"conflicting event_id {crosswalk.event_id}")
                previous_hash = "0" * 64
                if self.path.exists() and self.path.stat().st_size:
                    with self.path.open("rb") as handle:
                        last = handle.readlines()[-1]
                    previous_hash = json.loads(last)["record_hash"]
                record: dict[str, Any] = {
                    "schema": SCHEMA,
                    "sequence": len(existing) + 1,
                    "previous_hash": previous_hash,
                    "crosswalk": crosswalk.to_dict(),
                }
                record["record_hash"] = self._record_hash(record)
                with self.path.open("ab") as handle:
                    handle.write(_canonical(record) + b"\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                return True
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
