"""A small, evidence-backed comparison of routing and operating-world planning.

This module is intentionally isolated from the production router and learning
ledger.  It does not write the database, promote anything, or claim that the
current episodes contain a complete planning domain.  It makes the missing
pieces explicit while comparing two outputs on the same Project IR cases:

* a legacy one-label decision;
* a typed capability planner that can compose steps or report a capability gap.
"""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from flujo.knowledge.learning_policy import _features, _predict, fit_learning_policy
from flujo.knowledge.project_router import route_project


class OperatingWorldError(ValueError):
    """Invalid isolated experiment input."""


@dataclass(frozen=True)
class Capability:
    """A typed operator; implementation identity is not the learned target."""

    capability_id: str
    implementation_id: str
    requires: frozenset[str]
    produces: frozenset[str]
    validator: str
    source_phase: str
    cost: int = 1
    risk: int = 0

    def applicable(self, facts: frozenset[str]) -> bool:
        return self.requires <= facts


@dataclass(frozen=True)
class OperatingCase:
    case_id: str
    project_id: str
    phase: str
    objective: str
    initial_facts: frozenset[str]
    goal_facts: frozenset[str]
    expected_status: str
    composite: bool
    legacy_tools: tuple[str, ...]
    expected_missing_facts: frozenset[str]


@dataclass(frozen=True)
class ObservationCard:
    """What the current ledger can say about an observed capability."""

    phase: str
    episode_ids: tuple[str, ...]
    project_ids: tuple[str, ...]
    validators: tuple[str, ...]
    outcome_statuses: tuple[str, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class PlanResult:
    status: str
    plan: tuple[str, ...]
    achieved_facts: frozenset[str]
    missing_facts: frozenset[str]
    total_cost: int
    total_risk: int
    validator_chain: tuple[str, ...]
    evidence_basis: tuple[str, ...]


def load_cases(path: str | Path) -> tuple[OperatingCase, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping) or payload.get("schema") != "mak-operating-world-cases-v1":
        raise OperatingWorldError("cases_bad_schema")
    rows = payload.get("cases")
    if not isinstance(rows, list) or not rows:
        raise OperatingWorldError("cases_missing")
    output: list[OperatingCase] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise OperatingWorldError("case_not_mapping")
        case_id = str(row.get("case_id") or "").strip()
        if not case_id or case_id in seen:
            raise OperatingWorldError("case_duplicate_or_missing_id")
        output.append(
            OperatingCase(
                case_id=case_id,
                project_id=str(row.get("project_id") or "").strip(),
                phase=str(row.get("phase") or "unknown").strip(),
                objective=str(row.get("objective") or "").strip(),
                initial_facts=frozenset(str(item).strip() for item in row.get("initial_facts", []) if str(item).strip()),
                goal_facts=frozenset(str(item).strip() for item in row.get("goal_facts", []) if str(item).strip()),
                expected_status=str(row.get("expected_status") or "").strip(),
                composite=bool(row.get("composite")),
                legacy_tools=tuple(str(item).strip() for item in row.get("legacy_tools", []) if str(item).strip()),
                expected_missing_facts=frozenset(
                    str(item).strip() for item in row.get("expected_missing_facts", []) if str(item).strip()
                ),
            )
        )
        if not output[-1].project_id or not output[-1].objective or not output[-1].goal_facts:
            raise OperatingWorldError(f"case_incomplete: {case_id}")
        seen.add(case_id)
    return tuple(output)


def load_project_ir(database: str | Path, project_id: str) -> dict[str, Any]:
    """Read one Project IR record without creating schema or changing state."""
    path = Path(database).expanduser()
    uri = "file:" + str(path.resolve()) + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as con:
        row = con.execute("SELECT ir_json FROM project_records WHERE project_id=?", (project_id,)).fetchone()
    if not row:
        raise OperatingWorldError(f"project_missing: {project_id}")
    try:
        value = json.loads(str(row[0]))
    except json.JSONDecodeError as exc:
        raise OperatingWorldError(f"project_ir_invalid: {project_id}") from exc
    if not isinstance(value, dict):
        raise OperatingWorldError(f"project_ir_not_object: {project_id}")
    return value


def _json_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, str):
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return {}
    return dict(parsed) if isinstance(parsed, Mapping) else {}


def observed_capability_cards(database: str | Path) -> dict[str, ObservationCard]:
    """Extract only what episodes actually expose; do not infer effects silently."""
    path = Path(database).expanduser()
    uri = "file:" + str(path.resolve()) + "?mode=ro"
    grouped: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    with sqlite3.connect(uri, uri=True) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """SELECT episode_id,project_id,phase,status,action_json,outcome_json,
                      validation_json FROM project_episodes
               WHERE status IN ('succeeded','verified')
               ORDER BY episode_id"""
        ).fetchall()
    for row in rows:
        phase = str(row["phase"] or "unknown")
        action = _json_object(row["action_json"])
        outcome = _json_object(row["outcome_json"])
        validation = _json_object(row["validation_json"])
        bucket = grouped[phase]
        bucket["episode_ids"].add(str(row["episode_id"]))
        bucket["project_ids"].add(str(row["project_id"]))
        validator = str(validation.get("validator") or "")
        if validator:
            bucket["validators"].add(validator)
        bucket["outcome_statuses"].add(str(outcome.get("status") or row["status"]))
        evidence = outcome.get("evidence")
        if isinstance(evidence, list):
            for item in evidence:
                if isinstance(item, Mapping):
                    for key in ("path", "ref", "kind"):
                        value = str(item.get(key) or "").strip()
                        if value:
                            bucket["evidence_refs"].add(value)
        selected = action.get("decision")
        if isinstance(selected, Mapping):
            selected = selected.get("selected")
        if isinstance(selected, Mapping):
            tool_id = str(selected.get("tool_id") or "").strip()
            if tool_id:
                bucket["validators"].add("implementation:" + tool_id)
    return {
        phase: ObservationCard(
            phase=phase,
            episode_ids=tuple(sorted(values["episode_ids"])),
            project_ids=tuple(sorted(values["project_ids"])),
            validators=tuple(sorted(values["validators"])),
            outcome_statuses=tuple(sorted(values["outcome_statuses"])),
            evidence_refs=tuple(sorted(values["evidence_refs"])),
        )
        for phase, values in sorted(grouped.items())
    }


def model_inventory(database: str | Path) -> dict[str, Any]:
    """Inventory model inputs and explicitly list the missing planning fields."""
    cards = observed_capability_cards(database)
    return {
        "available_from_project_ir": [
            "schema", "project_id", "title", "state", "source", "purpose",
            "domains", "artifacts", "unknowns", "evidence", "provenance",
        ],
        "available_from_verified_episodes": [
            "phase", "action", "observation", "outcome", "validation",
            "provider", "model", "cost", "source_refs", "tool_identity",
        ],
        "observed_phases": sorted(cards),
        "missing_for_general_planning": [
            "typed_goal_schema",
            "formal_preconditions",
            "formal_effects_and_negative_effects",
            "capability_inputs_and_outputs",
            "validated_cost_duration_and_risk_model",
            "causal_dependencies_between_steps",
            "failure_probability_or_recovery_model",
            "independent_plan_validators_for_unseen_compositions",
        ],
    }


def build_capability_registry(cards: Mapping[str, ObservationCard]) -> tuple[Capability, ...]:
    """Build a deliberately small typed registry from observed phase vocabulary.

    The operators are explicit benchmark contracts, while their provenance is
    checked against the real episode cards.  This prevents the experiment from
    pretending that the current JSON ledger already contains formal effects.
    """
    definitions = (
        Capability(
            "research.capture_sources", "research_job_router",
            frozenset({"source_available", "domain:research"}), frozenset({"sources_captured"}),
            "execute_research_job.capture_gate", "capture",
        ),
        Capability(
            "research.contextualize", "research_job_router",
            frozenset({"sources_captured"}), frozenset({"context_declared"}),
            "interpretive_garden_workflow.context_gate", "contextualize",
        ),
        Capability(
            "research.extract_claims", "research_job_router",
            frozenset({"context_declared"}), frozenset({"claims_extracted"}),
            "interpretive_garden_workflow.extract_gate", "extract",
        ),
        Capability(
            "research.interpret_hypothesis", "research_job_router",
            frozenset({"claims_extracted"}), frozenset({"hypothesis_scoped"}),
            "interpretive_garden_workflow.interpretation_gate", "interpret",
        ),
        Capability(
            "research.relate_claims", "research_job_router",
            frozenset({"claims_extracted"}), frozenset({"relations_linked"}),
            "interpretive_garden_workflow.relation_gate", "relate",
        ),
        Capability(
            "research.simulate", "research_simulation_consumer",
            frozenset({"hypothesis_scoped"}), frozenset({"simulation_verified"}),
            "deterministic_rerun_and_marker_check", "verified_execution",
        ),
        Capability(
            "research.publish", "publication_gate",
            frozenset({"simulation_verified", "license_approved"}), frozenset({"publication_permitted"}),
            "publication_gate_not_observed", "inferred_contract",
        ),
        Capability(
            "tennis.project_events", "tennis_shot_event_consumer",
            frozenset({"artifact:data", "domain:tennis", "annotated_notation_available"}),
            frozenset({"shot_events_validated"}), "schemas/tennis/shot_event.schema.json",
            "tennis_shot_event_projection",
        ),
        Capability(
            "source.verify_memory", "source_learning_bridge",
            frozenset({"source_bundle_available", "domain:source_memory"}),
            frozenset({"source_memory_verified"}), "flujo.knowledge.source_learning.verify_case",
            "source_learning_ingestion",
        ),
    )
    return tuple(
        capability for capability in definitions
        if capability.source_phase in cards
        or capability.source_phase in {"verified_execution", "inferred_contract"}
    )


def _base_facts(project: Mapping[str, Any]) -> set[str]:
    facts = {"state:" + str(project.get("state") or "unknown")}
    domains = project.get("domains") if isinstance(project.get("domains"), list) else []
    facts.update("domain:" + str(value).casefold().strip() for value in domains if str(value).strip())
    artifacts = project.get("artifacts") if isinstance(project.get("artifacts"), list) else []
    facts.update(
        "artifact:" + str(item.get("format_family") or "unknown").casefold()
        for item in artifacts if isinstance(item, Mapping)
    )
    return facts


def plan_case(case: OperatingCase, project: Mapping[str, Any], capabilities: Iterable[Capability], max_steps: int = 8) -> PlanResult:
    """Breadth-first plan search with explicit no-plan output."""
    registry = tuple(capabilities)
    initial = frozenset(_base_facts(project) | set(case.initial_facts))
    queue = deque([(initial, tuple(), 0, 0, tuple(), tuple())])
    visited = {initial}
    while queue:
        facts, plan, cost, risk, validators, basis = queue.popleft()
        if case.goal_facts <= facts:
            return PlanResult("planned", plan, facts, frozenset(), cost, risk, validators, basis)
        if len(plan) >= max_steps:
            continue
        for capability in registry:
            if not capability.applicable(facts):
                continue
            produced = capability.produces - facts
            if not produced:
                continue
            next_facts = frozenset(set(facts) | set(capability.produces))
            if next_facts in visited:
                continue
            visited.add(next_facts)
            card = capability.source_phase
            queue.append((
                next_facts,
                plan + (capability.capability_id,),
                cost + capability.cost,
                risk + capability.risk,
                validators + (capability.validator,),
                basis + ("observed_phase:" + card,),
            ))
    reachable = set(initial)
    changed = True
    while changed:
        changed = False
        for capability in registry:
            if capability.requires <= reachable and not capability.produces <= reachable:
                reachable.update(capability.produces)
                changed = True
    missing = set(case.goal_facts - reachable)
    changed = True
    while changed:
        changed = False
        for capability in registry:
            if not capability.produces & missing:
                continue
            for requirement in capability.requires - reachable:
                if requirement not in missing:
                    missing.add(requirement)
                    changed = True
    return PlanResult(
        "capability_gap", tuple(), frozenset(reachable), frozenset(missing),
        0, 0, tuple(), tuple(),
    )


def validate_plan(case: OperatingCase, result: PlanResult) -> dict[str, Any]:
    """Validate against the case's goal/gap contract, never against a tool label."""
    if case.expected_status == "planned":
        passed = result.status == "planned" and case.goal_facts <= result.achieved_facts
        return {
            "status": "passed" if passed else "failed",
            "reason": "goal_reached" if passed else "goal_not_reached",
            "expected": "planned",
            "actual": result.status,
        }
    if case.expected_status == "capability_gap":
        passed = result.status == "capability_gap" and case.expected_missing_facts <= result.missing_facts
        return {
            "status": "passed" if passed else "failed",
            "reason": "gap_identified" if passed else "gap_hidden_or_wrong",
            "expected": "capability_gap",
            "actual": result.status,
        }
    raise OperatingWorldError(f"case_bad_expected_status: {case.case_id}")


def legacy_decision(database: str | Path, case: OperatingCase, project: Mapping[str, Any]) -> dict[str, Any]:
    """Run the current router and learner without mutating either surface."""
    routed = route_project(project)
    selected = routed.get("selected") if isinstance(routed.get("selected"), Mapping) else {}
    route_tool = str(selected.get("tool_id") or "")
    fit = fit_learning_policy(database)
    learner_tool = ""
    learner_confidence = 0.0
    if fit.get("status") == "candidate" and isinstance(fit.get("model"), Mapping):
        features = _features(project, {"phase": case.phase})
        learner_tool, learner_confidence = _predict(fit["model"], features)
    direct_pass = (
        case.expected_status == "planned"
        and not case.composite
        and route_tool in set(case.legacy_tools)
    ) or (
        case.expected_status == "capability_gap" and routed.get("decision") == "abstain"
    )
    learner_pass = (
        case.expected_status == "planned"
        and not case.composite
        and learner_tool in set(case.legacy_tools)
    ) or (
        case.expected_status == "capability_gap" and not learner_tool
    )
    router_gap_explained = (
        case.expected_status == "capability_gap"
        and routed.get("decision") == "abstain"
        and routed.get("reason") == "no_declared_consumer"
    )
    return {
        "router_decision": routed.get("decision"),
        "router_reason": routed.get("reason"),
        "router_tool": route_tool or None,
        "learner_tool": learner_tool or None,
        "learner_confidence": learner_confidence,
        "can_express_composite_plan": False,
        "router_contract_passed": direct_pass,
        "router_gap_explained": router_gap_explained,
        "learner_contract_passed": learner_pass,
    }


def run_comparison(database: str | Path, cases: Iterable[OperatingCase], capability_registry: Iterable[Capability]) -> dict[str, Any]:
    """Compare both conceptions over identical cases."""
    cards = observed_capability_cards(database)
    registry = tuple(capability_registry)
    rows = []
    for case in cases:
        project = load_project_ir(database, case.project_id)
        plan = plan_case(case, project, registry)
        rows.append({
            "case_id": case.case_id,
            "project_id": case.project_id,
            "objective": case.objective,
            "composite": case.composite,
            "expected_status": case.expected_status,
            "world_model": {
                "status": plan.status,
                "plan": list(plan.plan),
                "missing_facts": sorted(plan.missing_facts),
                "achieved_facts": sorted(plan.achieved_facts),
                "total_cost": plan.total_cost,
                "total_risk": plan.total_risk,
                "validator_chain": list(plan.validator_chain),
                "evidence_basis": list(plan.evidence_basis),
                "validation": validate_plan(case, plan),
            },
            "legacy": legacy_decision(database, case, project),
            "project_ir_facts": sorted(_base_facts(project)),
        })
    world_passed = sum(row["world_model"]["validation"]["status"] == "passed" for row in rows)
    router_passed = sum(bool(row["legacy"]["router_contract_passed"]) for row in rows)
    learner_passed = sum(bool(row["legacy"]["learner_contract_passed"]) for row in rows)
    router_explained_gaps = sum(bool(row["legacy"]["router_gap_explained"]) for row in rows)
    gaps = sum(row["expected_status"] == "capability_gap" for row in rows)
    return {
        "schema": "mak-operating-world-comparison-v1",
        "database": Path(database).name,
        "observed_capability_phases": sorted(cards),
        "capability_registry": [
            {
                "capability_id": item.capability_id,
                "implementation_id": item.implementation_id,
                "requires": sorted(item.requires),
                "produces": sorted(item.produces),
                "source_phase": item.source_phase,
                "validator": item.validator,
                "observed_phase_available": item.source_phase in cards,
            }
            for item in registry
        ],
        "summary": {
            "case_count": len(rows),
            "expected_capability_gaps": gaps,
            "world_model_passed": world_passed,
            "router_contract_passed": router_passed,
            "router_explained_gaps": router_explained_gaps,
            "learner_contract_passed": learner_passed,
            "world_model_rate": world_passed / len(rows) if rows else 0.0,
            "router_contract_rate": router_passed / len(rows) if rows else 0.0,
            "learner_contract_rate": learner_passed / len(rows) if rows else 0.0,
        },
        "cases": rows,
    }
