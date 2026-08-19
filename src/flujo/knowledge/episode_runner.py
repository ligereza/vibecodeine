"""Turn a router decision into a bounded, auditable consumer probe.

This layer deliberately stops before arbitrary execution.  It can say that a
consumer is selected, unavailable, plan-only or abstained, and can persist the
result as an episode.  A later authorized executor may consume the command
plan; the router itself never runs it.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any, Mapping

from .project_ir import LearningStore, ProjectIRError, stable_json
from .project_router import evaluate_route


def probe_declared_consumer(
    project: Mapping[str, Any], decision: Mapping[str, Any], *,
    repo_root: str | Path,
) -> dict[str, Any]:
    """Prepare a read-only probe result without spawning a process."""
    if decision.get("decision") == "abstain":
        return {
            "status": "abstained",
            "reason": decision.get("reason", "router_abstained"),
            "command": [],
            "validation": {"status": "verified", "check": "router_state_gate"},
        }
    selected = decision.get("selected")
    if not isinstance(selected, Mapping):
        return {
            "status": "needs_evidence",
            "reason": "selected_consumer_missing",
            "command": [],
            "validation": {"status": "not_run", "check": "route_contract"},
        }
    tool_id = str(selected.get("tool_id") or "")
    if selected.get("mode") != "read_only":
        if tool_id in {"research_job_router", "research_opportunity_gate"}:
            from .project_research import build_research_plan
            plan = build_research_plan(project)
            if plan.get("decision") == "abstain":
                return {
                    "status": "abstained",
                    "reason": plan.get("reason", "research_plan_abstained"),
                    "tool_id": tool_id,
                    "command": [],
                    "plan": plan,
                    "validation": {"status": "verified", "check": "research_state_gate"},
                }
            return {
                "status": "needs_evidence",
                "reason": "research_plan_ready_no_job_created",
                "tool_id": tool_id,
                "command": [],
                "plan": plan,
                "validation": {"status": "planned", "check": "research_plan_only"},
            }
        return {
            "status": "needs_evidence",
            "reason": "consumer_is_plan_only",
            "tool_id": tool_id,
            "command": [],
            "validation": {"status": "not_run", "check": "mutating_or_plan_only_gate"},
        }
    if tool_id == "blend_scene_audit":
        blender = shutil.which("blender")
        artifacts = project.get("artifacts", [])
        source = project.get("source") if isinstance(project.get("source"), Mapping) else {}
        root = Path(str(source.get("root_ref") or ""))
        blend = None
        for artifact in artifacts if isinstance(artifacts, list) else []:
            if not isinstance(artifact, Mapping) or artifact.get("format_family") != "3d":
                continue
            candidate = root / str(artifact.get("relative_path") or "")
            if candidate.is_file():
                blend = candidate
                break
        if not blender:
            reason = "blender_not_installed"
        elif blend is None:
            reason = "blend_source_not_available"
        else:
            reason = "read_only_blender_probe_ready"
        return {
            "status": "succeeded" if reason == "read_only_blender_probe_ready" else "needs_evidence",
            "reason": reason,
            "tool_id": tool_id,
            "command": [blender, "--background", str(blend), "--python", "tools/audit_blend_scene.py"] if blender and blend else [],
            "validation": {"status": "planned" if reason != "read_only_blender_probe_ready" else "ready", "check": "bounded_command_plan"},
        }
    return {
        "status": "needs_evidence",
        "reason": "consumer_probe_not_implemented",
        "tool_id": tool_id,
        "command": [],
        "validation": {"status": "not_run", "check": "consumer_adapter_gate"},
    }


def record_probe(
    store: LearningStore, project: Mapping[str, Any], decision: Mapping[str, Any],
    probe: Mapping[str, Any], *, phase: str = "consumer_probe",
    episode_id: str | None = None,
) -> str:
    """Persist one probe result using the router's conservative classification."""
    project_id = str(project.get("project_id") or "").strip()
    if not project_id:
        raise ProjectIRError("probe_missing_project_id")
    evaluated = evaluate_route(
        decision,
        {"status": probe.get("status"), "validation": (probe.get("validation") or {}).get("status")},
    )
    plan = probe.get("plan") if isinstance(probe.get("plan"), Mapping) else None
    plan_fingerprint = hashlib.sha256(stable_json(plan).encode("utf-8")).hexdigest() if plan else ""
    return store.record_episode(
        project_id=project_id,
        objective="probe declared project consumer",
        phase=phase,
        action={"decision": decision, "command": list(probe.get("command") or []), "plan": plan},
        observation={"reason": probe.get("reason"), "tool_id": probe.get("tool_id"), "plan_fingerprint": plan_fingerprint},
        outcome={"status": probe.get("status"), "classification": evaluated, "plan_fingerprint": plan_fingerprint},
        validation=probe.get("validation") if isinstance(probe.get("validation"), Mapping) else {},
        status=evaluated["status"], provider="local", model="policy-router",
        episode_id=episode_id,
    )
