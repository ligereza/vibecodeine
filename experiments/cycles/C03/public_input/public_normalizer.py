"""Closed-world normalizer for the C03 public-input experiment.

The module accepts only explicitly declared C03 forms.  It does not access the
network and does not infer identity, authorship, timestamps, URLs, media, or
publication-to-authoring relationships.
"""

from __future__ import annotations

import copy
import html.parser
import json
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "c03.public_input.normalized.v1"
CANONICAL_SCHEMA = "c03.public_input.canonical.v1"
DECLARED_JSON_WRAPPER = "c03.public_input.declared_json_export.v1"
HTML_JSON_WRAPPER = "c03.public_input.html_json_incomplete.v1"
RECORD_TYPES = ("post", "reel", "story")
PLURAL_TYPES = {"posts": "post", "reels": "reel", "stories": "story"}
CATALOG_STATUSES = ("available", "unavailable", "unknown")
COMPLETENESS_STATUSES = ("complete", "partial", "unknown", "unavailable")
FORBIDDEN_KEYS = {"generated", "RENDERS_TO"}


class NormalizationError(ValueError):
    """A source cannot be safely represented by the public-input contract."""


def _fail(message: str) -> None:
    raise NormalizationError(message)


def _copy(value: Any) -> Any:
    return copy.deepcopy(value)


def _non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{field} must be an explicit non-empty string")
    return value


def _require_archive_id(payload: Mapping[str, Any]) -> str:
    if "archive_id" not in payload:
        _fail("archive_id is required and cannot be inferred")
    return _non_empty_string(payload["archive_id"], "archive_id")


def _validate_status(value: Any, field: str, allowed: tuple[str, ...]) -> str:
    if not isinstance(value, str) or value not in allowed:
        _fail(f"{field} must be one of {', '.join(allowed)}")
    return value


def _validate_evidence_refs(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{field} must be a list when declared")
    for index, ref in enumerate(value):
        if not isinstance(ref, (str, Mapping)):
            _fail(f"{field}[{index}] must be a string or object")
    return _copy(value)


def _validate_origin(value: Any, field: str) -> Any:
    if isinstance(value, str):
        if not value.strip():
            _fail(f"{field} cannot be empty")
        return value
    if isinstance(value, Mapping):
        if not value:
            _fail(f"{field} cannot be empty")
        return _copy(value)
    _fail(f"{field} must be a non-empty string or object")


def _validate_completeness(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{field} must be an object when declared")
    result = _copy(dict(value))
    if "status" in result:
        _validate_status(result["status"], f"{field}.status", COMPLETENESS_STATUSES)
    return result


def _validate_hashes(value: Any, field: str) -> Any:
    if not isinstance(value, Mapping):
        _fail(f"{field} must be an object when declared")
    return _copy(dict(value))


def _copy_declared_fields(source: Mapping[str, Any], *, field: str) -> dict[str, Any]:
    """Copy public observations without copying relationship/provenance edges."""

    result: dict[str, Any] = {}
    # These are observations only.  Their absence is meaningful and is not
    # filled in by this module.
    for key in (
        "id",
        "record_id",
        "media_id",
        "caption",
        "timestamp",
        "published_at",
        "url",
        "filename",
        "kind",
        "mime",
        "width",
        "height",
        "duration",
    ):
        if key in source:
            result[key] = _copy(source[key])
    if "origin" in source:
        result["origin"] = _validate_origin(source["origin"], f"{field}.origin")
    if "evidence_refs" in source:
        result["evidence_refs"] = _validate_evidence_refs(
            source["evidence_refs"], f"{field}.evidence_refs"
        )
    if "hashes" in source:
        result["hashes"] = _validate_hashes(source["hashes"], f"{field}.hashes")
    if "completeness" in source:
        result["completeness"] = _validate_completeness(
            source["completeness"], f"{field}.completeness"
        )
    # A declared object may carry extra source metadata, but relationship keys
    # are intentionally not emitted by the normalizer.
    return result


def _normalize_media(media: Any, *, field: str) -> list[dict[str, Any]]:
    if not isinstance(media, list):
        _fail(f"{field} must be a list when declared")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(media):
        item_field = f"{field}[{index}]"
        if not isinstance(item, Mapping):
            _fail(f"{item_field} must be an object")
        if "origin" not in item:
            _fail(f"{item_field}.origin is required; media origin cannot be inferred")
        normalized.append(_copy_declared_fields(item, field=item_field))
    return normalized


def _normalize_record(item: Any, *, record_type: str, field: str) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        _fail(f"{field} must be an object")
    if record_type not in RECORD_TYPES:
        _fail(f"unknown record type: {record_type!r}")
    if "type" in item and item["type"] != record_type:
        _fail(f"{field}.type conflicts with declared record type {record_type!r}")

    record = _copy_declared_fields(item, field=field)
    record["type"] = record_type
    if "media" in item:
        record["media"] = _normalize_media(item["media"], field=f"{field}.media")
    else:
        record["media"] = []
    return record


def _extract_records(payload: Mapping[str, Any], form: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if form == "canonical":
        if "records" not in payload or not isinstance(payload["records"], list):
            _fail("canonical form requires a records list")
        for index, item in enumerate(payload["records"]):
            if not isinstance(item, Mapping) or "type" not in item:
                _fail(f"records[{index}].type is required in canonical form")
            record_type = item["type"]
            if record_type not in RECORD_TYPES:
                _fail(f"unknown record type: {record_type!r}")
            records.append(
                _normalize_record(item, record_type=record_type, field=f"records[{index}]")
            )
        return records

    for plural, record_type in PLURAL_TYPES.items():
        if plural not in payload:
            continue
        items = payload[plural]
        if not isinstance(items, list):
            _fail(f"{plural} must be a list when declared")
        for index, item in enumerate(items):
            records.append(
                _normalize_record(item, record_type=record_type, field=f"{plural}[{index}]")
            )
    return records


class _JSONScriptParser(html.parser.HTMLParser):
    """Collect application/json script bodies without executing HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._active = False
        self._chunks: list[str] = []
        self.json_scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        attributes = {key.lower(): (value or "") for key, value in attrs}
        self._active = attributes.get("type", "").lower() == "application/json"
        self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._active:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._active:
            self.json_scripts.append("".join(self._chunks))
            self._active = False
            self._chunks = []


def _parse_json(text: str, source_name: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        _fail(f"{source_name} is not interpretable JSON: {exc.msg}")
    if not isinstance(value, Mapping):
        _fail(f"{source_name} must contain a JSON object")
    return dict(value)


def parse_source_text(text: str, source_format: str) -> tuple[dict[str, Any], str]:
    """Parse JSON or an HTML document containing exactly one JSON export."""

    if source_format == "json":
        return _parse_json(text, "JSON source"), "json"
    if source_format == "html":
        parser = _JSONScriptParser()
        try:
            parser.feed(text)
            parser.close()
        except html.parser.HTMLParseError as exc:  # pragma: no cover - legacy parser path
            _fail(f"HTML is not interpretable: {exc}")
        if len(parser.json_scripts) != 1:
            _fail("HTML must contain exactly one application/json script")
        return _parse_json(parser.json_scripts[0], "HTML application/json script"), "html"
    _fail(f"unsupported source format: {source_format!r}")


def load_source(path: str | Path) -> tuple[dict[str, Any], str]:
    source_path = Path(path)
    if source_path.suffix.lower() == ".json":
        source_format = "json"
    elif source_path.suffix.lower() in {".html", ".htm"}:
        source_format = "html"
    else:
        _fail("input must have a .json, .html, or .htm suffix")
    try:
        text = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        _fail(f"cannot read input: {exc}")
    return parse_source_text(text, source_format)


def _detect_form(payload: Mapping[str, Any]) -> str:
    if payload.get("schema") == CANONICAL_SCHEMA:
        return "canonical"
    if payload.get("wrapper") == DECLARED_JSON_WRAPPER:
        return "declared_json"
    if payload.get("wrapper") == HTML_JSON_WRAPPER:
        return "html_json_incomplete"
    _fail("unknown or undeclared input type")


def normalize_payload(payload: Mapping[str, Any], *, source_format: str = "json") -> dict[str, Any]:
    """Normalize one declared public export, failing closed on ambiguity."""

    if not isinstance(payload, Mapping):
        _fail("source must be a JSON object")
    archive_id = _require_archive_id(payload)
    form = _detect_form(payload)
    records = _extract_records(payload, "canonical" if form == "canonical" else "wrapper")

    # An export being interpretable does not prove that a complete catalog is
    # locally available; preserve an omitted status as unknown.
    catalog_status = payload.get("catalog_status", "unknown")
    catalog_status = _validate_status(catalog_status, "catalog_status", CATALOG_STATUSES)
    completeness = payload.get("completeness", {"status": "unknown"})
    completeness = _validate_completeness(completeness, "completeness")

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "archive_id": archive_id,
        "catalog_status": catalog_status,
        "source_format": source_format,
        "input_form": form,
        "completeness": completeness,
        "records": records,
        "posts": [record for record in records if record["type"] == "post"],
        "reels": [record for record in records if record["type"] == "reel"],
        "stories": [record for record in records if record["type"] == "story"],
    }
    if "media" in payload:
        result["media"] = _normalize_media(payload["media"], field="media")

    # Root observations are preserved only if explicitly present.
    for key in ("origin", "evidence_refs", "hashes"):
        if key in payload:
            if key == "origin":
                result[key] = _validate_origin(payload[key], "origin")
            elif key == "evidence_refs":
                result[key] = _validate_evidence_refs(payload[key], "evidence_refs")
            else:
                result[key] = _validate_hashes(payload[key], "hashes")
    return result


def normalize_file(path: str | Path) -> dict[str, Any]:
    payload, source_format = load_source(path)
    return normalize_payload(payload, source_format=source_format)


def catalog_unavailable(archive_id: str) -> dict[str, Any]:
    """Represent the absence of a real local public export without a fixture."""

    archive_id = _non_empty_string(archive_id, "archive_id")
    empty = []
    return {
        "schema": SCHEMA,
        "archive_id": archive_id,
        "catalog_status": "unavailable",
        "source_format": "status_only",
        "input_form": "catalog_status",
        "completeness": {
            "status": "unavailable",
            "reason": "no_real_public_export_local",
        },
        "records": empty,
        "posts": empty.copy(),
        "reels": empty.copy(),
        "stories": empty.copy(),
        "media": empty.copy(),
    }


def normalize_file_to_json(path: str | Path) -> str:
    return json.dumps(normalize_file(path), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
