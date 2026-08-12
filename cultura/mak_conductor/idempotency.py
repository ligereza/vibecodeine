"""Deterministic identity and byte-level evidence helpers for MAK jobs."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Mapping


SCHEMA_VERSION = "mak-conductor-v2"
_SPACE_RE = re.compile(r"\s+")


def normalize_text(value: Any) -> str:
    """Return NFC text with collapsed whitespace for stable identity keys."""
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFC", text).strip()
    return _SPACE_RE.sub(" ", text)


def canonical_json(value: Any) -> str:
    """Serialize JSON without incidental key or whitespace differences."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=str)


def _identity_value(value: Any) -> Any:
    """Normalize semantic payload fields without discarding their meaning."""
    if isinstance(value, Mapping):
        return {
            str(key): _identity_value(item)
            for key, item in value.items()
            if str(key) not in {"producer", "queued_at", "request_id"}
        }
    if isinstance(value, (list, tuple)):
        return [_identity_value(item) for item in value]
    if isinstance(value, str):
        return normalize_text(value)
    return value


def job_idempotency_key(
    stage: str,
    payload: Mapping[str, Any],
    *,
    parent_job_id: str | None = None,
    model: str = "",
    template_version: str = "",
    params: Mapping[str, Any] | None = None,
    schema_version: str = SCHEMA_VERSION,
) -> str:
    """Build a stable key from the job meaning, not its arrival time."""
    parts = [
        normalize_text(stage),
        normalize_text(schema_version),
        normalize_text(parent_job_id),
        normalize_text(model),
        normalize_text(template_version),
        canonical_json(_identity_value(payload)),
        canonical_json(_identity_value(params or {})),
    ]
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def artifact_content_hash(content: bytes | bytearray | memoryview | str) -> str:
    """Hash raw artifact bytes; text uses UTF-8 without normalization."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(bytes(content)).hexdigest()
