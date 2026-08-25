"""Closed, stdlib-only evidence evaluator for C04.

The evaluator consumes facts already observed by other bounded adapters:
native AEP declarations, local media observations, and an optional explicit
export event.  It never opens an AEP, scans a directory, hashes a file,
loads a model, or treats an expected-outcome file as a decision input.

Status meanings used by this experiment:

* observed: a fact was directly recorded in an input observation;
* supported: the requested relation follows from the declared evidence;
* candidate: a bounded basename match exists, but identity is ambiguous or
  only suggestive;
* unknown: the input does not establish the relation;
* contradicted: an exact identity assertion conflicts with a recorded hash.
"""

from __future__ import annotations

import json
from pathlib import PureWindowsPath
from typing import Any, Mapping, Sequence


CONTRACT = "mak-cycle-c04-evidence-evaluator-v1"
STATUSES = {"observed", "supported", "candidate", "unknown", "contradicted"}
FORBIDDEN_RELATIONS = {"generated", "RENDERS_TO"}


class InputError(ValueError):
    """Raised when the declared observation contract is malformed."""


def _as_object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise InputError(f"{label} must be an object")
    return value


def _as_refs(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise InputError(f"{label} must be a list of non-empty strings")
    return list(value)


def _norm_path(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    # PureWindowsPath handles the native declaration; replacing separators
    # also makes comparison deterministic for the synthetic local adapter.
    return str(PureWindowsPath(value.replace("/", "\\"))).casefold()


def _basename(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return ""
    return PureWindowsPath(value.replace("/", "\\")).name.casefold()


def _status_claim(
    status: str,
    *,
    reason: str,
    evidence_refs: Sequence[str] = (),
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in STATUSES:
        raise InputError(f"invalid evaluator status: {status}")
    result: dict[str, Any] = {
        "status": status,
        "reason": reason,
        "evidence_refs": list(evidence_refs),
    }
    if details:
        result["details"] = dict(details)
    return result


def _validate_input(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], list[Mapping[str, Any]], Mapping[str, Any] | None]:
    if payload.get("schema") != "mak-cycle-c04-evidence-input-v1":
        raise InputError("schema must be mak-cycle-c04-evidence-input-v1")
    native = _as_object(payload.get("native_aep"), "native_aep")
    local = _as_object(payload.get("local_media_observation"), "local_media_observation")
    declarations = native.get("declarations")
    observations = local.get("observations")
    if not isinstance(declarations, list) or any(not isinstance(item, Mapping) for item in declarations):
        raise InputError("native_aep.declarations must be a list of objects")
    if not isinstance(observations, list) or any(not isinstance(item, Mapping) for item in observations):
        raise InputError("local_media_observation.observations must be a list of objects")
    _as_refs(native.get("evidence_refs"), "native_aep.evidence_refs")
    _as_refs(local.get("evidence_refs"), "local_media_observation.evidence_refs")
    for index, declaration in enumerate(declarations):
        if not isinstance(declaration.get("declared_path"), str) or not declaration["declared_path"]:
            raise InputError(f"declarations[{index}].declared_path is required")
        _as_refs(declaration.get("evidence_refs"), f"declarations[{index}].evidence_refs")
    for index, observation in enumerate(observations):
        if not isinstance(observation.get("path"), str) or not observation["path"]:
            raise InputError(f"observations[{index}].path is required")
        if not isinstance(observation.get("exists"), bool):
            raise InputError(f"observations[{index}].exists must be boolean")
        _as_refs(observation.get("evidence_refs"), f"observations[{index}].evidence_refs")
    event_value = payload.get("export_event")
    event = None if event_value is None else _as_object(event_value, "export_event")
    return native, list(declarations), event if event is None else dict(event)


def _identifier_matches(reference: str, declaration: Mapping[str, Any]) -> bool:
    return reference in {
        str(declaration.get("declaration_id", "")),
        str(declaration.get("declared_path", "")),
    } or _norm_path(reference) == _norm_path(declaration.get("declared_path"))


def _observation_matches(reference: str, observation: Mapping[str, Any]) -> bool:
    return reference in {
        str(observation.get("observation_id", "")),
        str(observation.get("path", "")),
    } or _norm_path(reference) == _norm_path(observation.get("path"))


def _choose_link(
    declaration: Mapping[str, Any] | None,
    observations: list[Mapping[str, Any]],
) -> tuple[str, Mapping[str, Any] | None, str, list[str]]:
    """Return uses status, selected observation, reason and supporting refs."""

    existing = [item for item in observations if item.get("exists") and item.get("is_file", True)]
    if declaration is None:
        return "unknown", None, "no_native_declaration_for_local_observation", []

    declared_path = _norm_path(declaration.get("declared_path"))
    declared_base = _basename(declaration.get("declared_path"))
    exact = [item for item in existing if _norm_path(item.get("declared_path")) == declared_path]
    if len(exact) == 1:
        observation = exact[0]
        expected_hash = declaration.get("sha256")
        actual_hash = observation.get("sha256")
        refs = list(declaration.get("evidence_refs") or []) + list(observation.get("evidence_refs") or [])
        if expected_hash and actual_hash and str(expected_hash).casefold() != str(actual_hash).casefold():
            return "contradicted", observation, "declared_hash_differs_from_local_observation", refs
        return "supported", observation, "native_fullpath_declaration_and_local_existence", refs
    if len(exact) > 1:
        return "candidate", None, "multiple_exactly_mapped_local_observations", [
            ref for item in exact for ref in item.get("evidence_refs", [])
        ]

    basename_matches = [item for item in existing if _basename(item.get("path")) == declared_base]
    if len(basename_matches) > 1:
        return "candidate", None, "basename_match_is_ambiguous", [
            ref for item in basename_matches for ref in item.get("evidence_refs", [])
        ]
    if len(basename_matches) == 1:
        item = basename_matches[0]
        return "candidate", item, "basename_match_without_declared_path_mapping", list(item.get("evidence_refs") or [])
    return "unknown", None, "declared_path_has_no_existing_local_observation", list(declaration.get("evidence_refs") or [])


def _event_claims(
    native: Mapping[str, Any],
    declarations: list[Mapping[str, Any]],
    observations: list[Mapping[str, Any]],
    event: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate an export witness without inventing a relation."""

    unknown = _status_claim(
        "unknown",
        reason="no_explicit_export_event_with_evidence_refs",
        evidence_refs=[],
    )
    if event is None:
        return unknown, []

    refs = _as_refs(event.get("evidence_refs"), "export_event.evidence_refs")
    event_type = event.get("event_type")
    source_ref = event.get("source_ref")
    output_ref = event.get("output_ref")
    source = next((item for item in declarations if isinstance(source_ref, str) and _identifier_matches(source_ref, item)), None)
    output = next((item for item in observations if isinstance(output_ref, str) and _observation_matches(output_ref, item)), None)
    if event_type != "export" or not refs or source is None or output is None or not output.get("exists"):
        return _status_claim(
            "unknown",
            reason="export_event_is_incomplete_or_does_not_bind_observed_source_and_output",
            evidence_refs=refs,
        ), []

    event_refs = refs + list(source.get("evidence_refs") or []) + list(output.get("evidence_refs") or [])
    claims = _status_claim(
        "supported",
        reason="explicit_export_event_binds_native_declaration_to_existing_output",
        evidence_refs=event_refs,
        details={"event_id": event.get("event_id", ""), "source_ref": source_ref, "output_ref": output_ref},
    )
    relations = [
        {
            "relation": relation,
            "status": "supported",
            "source_ref": source_ref,
            "target_ref": output_ref,
            "evidence_refs": event_refs,
            "claim_limit": "explicit event supports this export relation; it does not establish artistic or authorial causality",
        }
        for relation in ("generated", "RENDERS_TO")
    ]
    return claims, relations


def evaluate(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate only declared observations; expected outcomes are not accepted."""

    native, declarations, event = _validate_input(payload)
    local = _as_object(payload["local_media_observation"], "local_media_observation")
    observations = list(local["observations"])
    native_refs = list(native.get("evidence_refs") or [])
    local_refs = list(local.get("evidence_refs") or [])

    declaration = declarations[0] if len(declarations) == 1 else None
    uses_status, selected, uses_reason, uses_refs = _choose_link(declaration, observations)
    if selected is None and declaration is not None and uses_status == "candidate":
        selected = None

    existing_refs = [
        ref for item in observations if item.get("exists") for ref in item.get("evidence_refs", [])
    ]
    dimensions = None
    for item in observations:
        if isinstance(item.get("dimensions"), Mapping):
            dimensions = item
            break
    if dimensions is not None:
        dimensions_claim = _status_claim(
            "observed",
            reason="dimensions_copied_from_local_media_observation_without_normalization",
            evidence_refs=list(dimensions.get("evidence_refs") or []) + local_refs,
            details={"dimensions": dict(dimensions["dimensions"])},
        )
    else:
        dimensions_claim = _status_claim("unknown", reason="no_dimensions_in_local_media_observation")

    event_claim, relations = _event_claims(native, declarations, observations, event)
    output_role = {
        "status": event_claim["status"],
        "reason": event_claim["reason"],
        "evidence_refs": event_claim["evidence_refs"],
    }
    claims = {
        "native_declaration": _status_claim(
            "observed" if declarations else "unknown",
            reason="native_aep_declaration_recorded" if declarations else "no_native_declaration_recorded",
            evidence_refs=native_refs + [ref for item in declarations for ref in item.get("evidence_refs", [])],
            details={"declaration_count": len(declarations)},
        ),
        "local_media": _status_claim(
            "observed" if any(item.get("exists") for item in observations) else "unknown",
            reason="local_media_existence_recorded" if any(item.get("exists") for item in observations) else "no_existing_local_media",
            evidence_refs=local_refs + existing_refs,
            details={"observation_count": len(observations)},
        ),
        "uses": _status_claim(uses_status, reason=uses_reason, evidence_refs=uses_refs),
        "dimensions": dimensions_claim,
        "output_role": output_role,
    }
    return {
        "schema": CONTRACT,
        "case_id": payload.get("case_id", "unspecified"),
        "decision_policy": {
            "inputs": ["native_aep", "local_media_observation", "export_event"],
            "uses_gpu": False,
            "uses_embeddings": False,
            "uses_hidden_truth": False,
            "directory_scan": False,
            "causality_from_coexistence": False,
        },
        "claims": claims,
        "relations": relations,
        "selected_observation_id": selected.get("observation_id") if selected else None,
    }


def evaluate_json(text: str) -> dict[str, Any]:
    value = json.loads(text)
    return evaluate(_as_object(value, "input"))
