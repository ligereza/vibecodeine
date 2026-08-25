"""Materialize one export witness into an isolated evidence graph.

The bridge accepts only the C05 witness contract.  It does not inspect the
filesystem or reconstruct missing facts.  A witness that is incomplete,
contradictory, or lacks evidence references produces an explicit unknown and
zero export edges.
"""

from __future__ import annotations

from typing import Any, Mapping


CONTRACT = "mak-cycle-c06-export-graph-v1"
REQUIRED_CHECKS = (
    "source_hash_matches_native_snapshot",
    "script_and_marker_agree",
    "marker_target_matches_output",
    "source_contains_exported_objects",
    "output_contains_exported_objects",
    "output_is_blender_glb",
    "output_after_script_and_marker",
)


def _refs(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _valid_witness(witness: Any) -> tuple[bool, str, list[str]]:
    if not isinstance(witness, Mapping):
        return False, "witness_is_not_an_object", []
    if witness.get("schema") != "mak-cycle-c05-export-witness-v1":
        return False, "unsupported_witness_schema", []
    record = witness.get("witness")
    if not isinstance(record, Mapping):
        return False, "witness_record_missing", []
    refs = _refs(record.get("evidence_refs"))
    if record.get("status") != "supported":
        return False, "witness_status_is_not_supported", refs
    if record.get("event_type") != "export":
        return False, "witness_event_type_is_not_export", refs
    if not isinstance(record.get("source_ref"), str) or not record["source_ref"]:
        return False, "witness_source_ref_missing", refs
    if not isinstance(record.get("target_ref"), str) or not record["target_ref"]:
        return False, "witness_target_ref_missing", refs
    if not refs:
        return False, "witness_evidence_refs_missing", refs
    checks = record.get("checks")
    if not isinstance(checks, Mapping):
        return False, "witness_checks_missing", refs
    missing = [name for name in REQUIRED_CHECKS if name not in checks]
    if missing:
        return False, "witness_checks_missing_required:" + ",".join(missing), refs
    failed = [name for name in REQUIRED_CHECKS if not isinstance(checks[name], Mapping) or checks[name].get("status") != "pass"]
    if failed:
        return False, "witness_checks_failed:" + ",".join(failed), refs
    return True, "complete_supported_export_witness", refs


def materialize(witness: Mapping[str, Any]) -> dict[str, Any]:
    valid, reason, refs = _valid_witness(witness)
    record = witness.get("witness") if isinstance(witness, Mapping) else {}
    record = record if isinstance(record, Mapping) else {}
    source_ref = record.get("source_ref")
    target_ref = record.get("target_ref")
    edge = None
    if valid:
        edge = {
            "relation": "EXPORTS_TO",
            "status": "supported",
            "source_ref": source_ref,
            "target_ref": target_ref,
            "evidence_refs": refs,
            "claim_limit": "export event only; no final-delivery, artistic-intent, authorship, or post-publication claim",
        }
    nodes = []
    if isinstance(source_ref, str) and source_ref:
        nodes.append({"id": source_ref, "kind": "authoring"})
    if isinstance(target_ref, str) and target_ref:
        nodes.append({"id": target_ref, "kind": "artifact"})
    return {
        "schema": CONTRACT,
        "decision_policy": {
            "filesystem_scan": False,
            "hidden_truth": False,
            "status_override": False,
            "unknown_on_missing_or_conflicting_witness": True,
        },
        "claim": {
            "status": "supported" if valid else "unknown",
            "reason": reason,
            "evidence_refs": refs,
        },
        "nodes": nodes,
        "edges": [] if edge is None else [edge],
    }
