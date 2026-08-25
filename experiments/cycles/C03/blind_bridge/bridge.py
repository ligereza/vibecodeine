"""Blind public-to-local recovery for the isolated C03 benchmark.

This module accepts one normalized observation bundle and never opens the
evaluation fixture.  It uses only public observations plus local/native
observations.  A result is a retrieval decision, not a claim about authorship
or production history.
"""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


OBSERVATION_SCHEMA = "mak-cycle-c03-observations-v1"
EXTRACTOR_VERSION = "c03-blind-bridge-1.0"
STATUSES = {"candidate", "confirmed", "contradicted", "ambiguous", "unknown"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_EVALUATION_KEYS = {
    "truth",
    "expected",
    "gold",
    "ground_truth",
    "groundtruth",
    "oracle",
    "label",
}


class ObservationError(ValueError):
    """Raised when an observation bundle is not normalized C03 input."""


def _reject_evaluation_fields(value: Any, path: str = "observations") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key).lower() in _FORBIDDEN_EVALUATION_KEYS:
                raise ObservationError(f"evaluation field is not an observation: {path}.{key}")
            _reject_evaluation_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_evaluation_fields(nested, f"{path}[{index}]")


def _require_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise ObservationError(f"{context} must be a non-empty string")
    return value


def _require_sha(value: Any, context: str) -> str:
    value = _require_string(value, context).lower()
    if not _SHA256.fullmatch(value):
        raise ObservationError(f"{context} must be a lowercase SHA-256 digest")
    return value


def _string_list(value: Any, context: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ObservationError(f"{context} must be a list of non-empty strings")
    return list(value)


def _technical(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ObservationError(f"{context} must be an object")
    width = value.get("width")
    height = value.get("height")
    if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        raise ObservationError(f"{context} requires positive integer width and height")
    result: dict[str, Any] = {"width": width, "height": height}
    for key in ("duration_ms", "mime"):
        if key in value:
            if key == "duration_ms" and (not isinstance(value[key], int) or value[key] < 0):
                raise ObservationError(f"{context}.duration_ms must be a non-negative integer")
            if key == "mime" and not isinstance(value[key], str):
                raise ObservationError(f"{context}.mime must be a string")
            result[key] = value[key]
    return result


def _normalize_public(raw: Any, index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ObservationError(f"public_observations[{index}] must be an object")
    context = f"public_observations[{index}]"
    item = {
        "id": _require_string(raw.get("id"), f"{context}.id"),
        "publication_id": _require_string(raw.get("publication_id"), f"{context}.publication_id"),
        "media_kind": _require_string(raw.get("media_kind"), f"{context}.media_kind"),
        "sha256": _require_sha(raw.get("sha256"), f"{context}.sha256"),
        "technical": _technical(raw.get("technical"), f"{context}.technical"),
        "evidence_refs": _string_list(raw.get("evidence_refs"), f"{context}.evidence_refs"),
    }
    if "media_index" in raw:
        if not isinstance(raw["media_index"], int) or raw["media_index"] < 0:
            raise ObservationError(f"{context}.media_index must be a non-negative integer")
        item["media_index"] = raw["media_index"]
    if "bridge_observation_key" in raw:
        item["bridge_observation_key"] = _require_string(
            raw["bridge_observation_key"], f"{context}.bridge_observation_key"
        )
    return item


def _normalize_local(raw: Any, index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ObservationError(f"local_native_observations[{index}] must be an object")
    context = f"local_native_observations[{index}]"
    native_raw = raw.get("native", {})
    if not isinstance(native_raw, Mapping):
        raise ObservationError(f"{context}.native must be an object")
    native: dict[str, Any] = {
        "evidence_refs": _string_list(native_raw.get("evidence_refs"), f"{context}.native.evidence_refs"),
        "conflicts_with_public_ids": _string_list(
            native_raw.get("conflicts_with_public_ids"),
            f"{context}.native.conflicts_with_public_ids",
        ),
    }
    if "observed_export_key" in native_raw:
        native["observed_export_key"] = _require_string(
            native_raw["observed_export_key"], f"{context}.native.observed_export_key"
        )
    return {
        "id": _require_string(raw.get("id"), f"{context}.id"),
        "media_kind": _require_string(raw.get("media_kind"), f"{context}.media_kind"),
        "sha256": _require_sha(raw.get("sha256"), f"{context}.sha256"),
        "technical": _technical(raw.get("technical"), f"{context}.technical"),
        "evidence_refs": _string_list(raw.get("evidence_refs"), f"{context}.evidence_refs"),
        "native": native,
    }


def normalize_observations(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return only public/local normalized observations."""

    if not isinstance(raw, Mapping):
        raise ObservationError("observation bundle must be an object")
    _reject_evaluation_fields(raw)
    if raw.get("schema") != OBSERVATION_SCHEMA:
        raise ObservationError("unsupported observation schema")
    archive_id = _require_string(raw.get("archive_id"), "archive_id")
    catalog_status = raw.get("catalog_status")
    if catalog_status not in {"available", "unavailable"}:
        raise ObservationError("catalog_status must be available or unavailable")
    public = raw.get("public_observations")
    local = raw.get("local_native_observations")
    if not isinstance(public, list) or not isinstance(local, list):
        raise ObservationError("public_observations and local_native_observations must be lists")
    normalized = {
        "schema": OBSERVATION_SCHEMA,
        "archive_id": archive_id,
        "catalog_status": catalog_status,
        "public_observations": [_normalize_public(item, i) for i, item in enumerate(public)],
        "local_native_observations": [_normalize_local(item, i) for i, item in enumerate(local)],
    }
    if "catalog_request_id" in raw:
        normalized["catalog_request_id"] = _require_string(raw["catalog_request_id"], "catalog_request_id")
    ids = [item["id"] for item in normalized["public_observations"]]
    local_ids = [item["id"] for item in normalized["local_native_observations"]]
    if len(ids) != len(set(ids)) or len(local_ids) != len(set(local_ids)):
        raise ObservationError("observation ids must be unique within each side")
    return normalized


def load_observations(path: str | Path) -> dict[str, Any]:
    """Load and normalize an observations-only JSON file."""

    observation_path = Path(path)
    try:
        raw = json.loads(observation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ObservationError(f"cannot read observations: {observation_path}") from exc
    return normalize_observations(raw)


def _technical_compatible(public: Mapping[str, Any], local: Mapping[str, Any]) -> bool:
    if public["media_kind"] != local["media_kind"]:
        return False
    left = public["technical"]
    right = local["technical"]
    if left["width"] != right["width"] or left["height"] != right["height"]:
        return False
    if "duration_ms" in left and "duration_ms" in right:
        return left["duration_ms"] == right["duration_ms"]
    return True


def _evidence(public: Mapping[str, Any], local: Mapping[str, Any] | None = None) -> list[str]:
    refs = list(public["evidence_refs"])
    if local is not None:
        refs.extend(local["evidence_refs"])
        refs.extend(local["native"]["evidence_refs"])
    return list(dict.fromkeys(refs))


def _result(
    public: Mapping[str, Any],
    status: str,
    method: str,
    local: Mapping[str, Any] | None = None,
    candidates: Sequence[Mapping[str, Any]] = (),
    reason: str = "",
) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"unsupported result status: {status}")
    return {
        "query_id": public["id"],
        "publication_id": public["publication_id"],
        "local_id": None if local is None else local["id"],
        "status": status,
        "method": method,
        "candidate_local_ids": [item["id"] for item in candidates],
        "evidence_refs": _evidence(public, local),
        "reason": reason,
    }


def _catalog_unknown(observations: Mapping[str, Any]) -> dict[str, Any]:
    query_id = observations.get("catalog_request_id", "public-catalog")
    return {
        "query_id": query_id,
        "publication_id": None,
        "local_id": None,
        "status": "unknown",
        "method": "catalog_unavailable",
        "candidate_local_ids": [],
        "evidence_refs": ["observation:catalog_status=unavailable"],
        "reason": "public_catalog_unavailable",
    }


def _finish(observations: Mapping[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    selected = {result["local_id"] for result in results if result["local_id"] is not None}
    local_ids = [item["id"] for item in observations["local_native_observations"]]
    return {
        "schema": "mak-cycle-c03-recovery-v1",
        "extractor_version": EXTRACTOR_VERSION,
        "archive_id": observations["archive_id"],
        "catalog_status": observations["catalog_status"],
        "results": results,
        "orphan_local_ids": [local_id for local_id in local_ids if local_id not in selected],
    }


def recover_direct(observations: Mapping[str, Any]) -> dict[str, Any]:
    """Run the direct baseline using observations only."""

    observations = normalize_observations(observations)
    if observations["catalog_status"] == "unavailable":
        return _finish(observations, [_catalog_unknown(observations)])
    locals_ = observations["local_native_observations"]
    results: list[dict[str, Any]] = []
    for public in observations["public_observations"]:
        exact = [
            local
            for local in locals_
            if local["media_kind"] == public["media_kind"] and local["sha256"] == public["sha256"]
        ]
        if len(exact) == 1:
            results.append(_result(public, "confirmed", "direct_exact_sha256", exact[0], exact))
            continue
        if len(exact) > 1:
            results.append(
                _result(public, "ambiguous", "direct_exact_sha256", None, sorted(exact, key=lambda item: item["id"]), "duplicate_exact_hash")
            )
            continue
        technical = [local for local in locals_ if _technical_compatible(public, local)]
        technical.sort(key=lambda item: item["id"])
        if len(technical) == 1:
            results.append(_result(public, "candidate", "direct_technical", technical[0], technical, "technical_only"))
        elif len(technical) > 1:
            results.append(
                _result(public, "candidate", "direct_first_technical", technical[0], technical, "first_candidate_baseline")
            )
        else:
            results.append(_result(public, "unknown", "direct_no_candidate", None, (), "no_observed_local_match"))
    return _finish(observations, results)


def recover_mediated(observations: Mapping[str, Any]) -> dict[str, Any]:
    """Run the conservative native-observation bridge using observations only."""

    observations = normalize_observations(observations)
    if observations["catalog_status"] == "unavailable":
        return _finish(observations, [_catalog_unknown(observations)])
    locals_ = observations["local_native_observations"]
    results: list[dict[str, Any]] = []
    for public in observations["public_observations"]:
        conflicts = [
            local
            for local in locals_
            if public["id"] in local["native"]["conflicts_with_public_ids"]
        ]
        if conflicts:
            results.append(
                _result(public, "contradicted", "explicit_native_conflict", conflicts[0], conflicts, "explicit_conflict_observation")
            )
            continue
        exact = [
            local
            for local in locals_
            if local["media_kind"] == public["media_kind"] and local["sha256"] == public["sha256"]
        ]
        if len(exact) == 1:
            results.append(_result(public, "confirmed", "mediated_exact_sha256", exact[0], exact))
            continue
        if len(exact) > 1:
            results.append(
                _result(public, "ambiguous", "mediated_exact_sha256", None, sorted(exact, key=lambda item: item["id"]), "duplicate_exact_hash")
            )
            continue
        technical = [local for local in locals_ if _technical_compatible(public, local)]
        technical.sort(key=lambda item: item["id"])
        bridge_key = public.get("bridge_observation_key")
        bridged = [
            local
            for local in technical
            if bridge_key is not None and local["native"].get("observed_export_key") == bridge_key
        ]
        if len(bridged) == 1:
            results.append(
                _result(public, "confirmed", "mediated_native_observation", bridged[0], bridged, "compatible_explicit_bridge")
            )
        elif len(bridged) > 1:
            results.append(
                _result(public, "ambiguous", "mediated_native_observation", None, bridged, "duplicate_bridge_observation")
            )
        elif len(technical) == 1:
            results.append(_result(public, "candidate", "mediated_technical_only", technical[0], technical, "no_native_bridge"))
        elif len(technical) > 1:
            results.append(
                _result(public, "ambiguous", "mediated_technical_only", None, technical, "multiple_technical_candidates")
            )
        else:
            results.append(_result(public, "unknown", "mediated_no_candidate", None, (), "no_observed_local_match"))
    return _finish(observations, results)


def recover(observations: Mapping[str, Any]) -> dict[str, Any]:
    """Default recovery entry point; it is intentionally observation-only."""

    return recover_mediated(observations)


def _assert_observation_only_signature() -> bool:
    return len(inspect.signature(recover).parameters) == 1
