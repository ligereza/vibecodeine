"""Shared fixture builders for the product/portfolio compilation chain.

``tests/test_product_view.py`` imports ``_inputs``, ``_chain`` and
``_technical_context``.  They used to live inside three sibling test modules
that were removed by ``db3ab515`` ("carry only the tests this branch can run"),
which left the importing module failing at collection with
``ModuleNotFoundError``.  The builders are reproduced here unchanged so the
chain has one owner that is not itself a test module.

``_chain`` no longer reaches into a test module for ``_inputs``; it calls the
copy defined above it.
"""
from __future__ import annotations

import hashlib

from flujo.knowledge.artistic_program_evaluator import (
    evaluate_artistic_program_payload,
    fit_input_hash_for,
    program_id_for,
    stable_json,
)
from flujo.knowledge.artistic_program_hypotheses import generate_artistic_program_hypotheses
from flujo.knowledge.evidence_return import build_evidence_return
from flujo.knowledge.opportunity_constraints import compile_opportunity_constraints
from flujo.knowledge.opportunity_fit import evaluate_opportunity_fit
from flujo.knowledge.possibility_field import build_possibility_field
from flujo.knowledge.research_evidence_triangulation import triangulate_research_evidence
from flujo.knowledge.research_frontier_bridge import compile_research_frontier

__all__ = [
    "_candidate",
    "_chain",
    "_hash",
    "_inputs",
    "_opportunity",
    "_payload",
    "_practice",
    "_technical_context",
]


def _hash(value: object) -> str:
    return "sha256:" + hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()

def _practice() -> dict:
    state = {
        "schema": "mak-practice-evidence-state-v1",
        "algorithm_version": "practice-evidence-state-1",
        "tenant": "mak",
        "archive_id": "archive-fixture",
        "snapshot_id": "snapshot-fixture",
        "input_hash": "sha256:archive-input",
        "source_schema": "mak-archive-project-ir-bundle-v1",
        "units": [{
            "unit_id": "unit:one",
            "project_id": "project-one",
            "role": "project_unit",
            "status": "provisional_unit",
            "source_state": "candidate",
            "artifact_refs": ["artifact:gate", "artifact:media", "artifact:resource"],
            "member_refs": ["artifact:gate", "artifact:media", "artifact:resource"],
            "dependency_refs": [],
            "candidate_ids": [],
            "evidence_refs": ["artifact:gate", "artifact:media", "artifact:resource"],
            "evidence_for": ["fixture"],
            "evidence_against": [],
            "alternatives": [],
            "missing_evidence": [],
            "provenance_ref": "unit:unit:one",
            "provenance": {"source_rescan": False},
        }],
        "artifacts": [{
            "artifact_ref": "artifact:gate",
            "artifact_id": "artifact:gate",
            "physical_id": "physical:gate",
            "content_id": "content:one",
            "relative_path": "work/gate.bin",
            "availability": "available",
            "kind": "file",
            "role": "source",
            "evidence_refs": ["artifact:gate"],
            "unit_id": "unit:one",
        }, {
            "artifact_ref": "artifact:media",
            "artifact_id": "artifact:media",
            "physical_id": "physical:media",
            "content_id": "content:one",
            "relative_path": "work/media.bin",
            "availability": "available",
            "kind": "file",
            "role": "source",
            "evidence_refs": ["artifact:media"],
            "unit_id": "unit:one",
        }, {
            "artifact_ref": "artifact:resource",
            "artifact_id": "artifact:resource",
            "physical_id": "physical:resource",
            "content_id": "content:resource",
            "relative_path": "work/resource.bin",
            "availability": "available",
            "kind": "file",
            "role": "source",
            "evidence_refs": ["artifact:resource"],
            "unit_id": "unit:one",
        }],
        "media": [{
            "dimension": "media", "value": "audio", "status": "supported",
            "evidence_refs": ["artifact:media"], "requirement_ids": ["req:media"],
            "unit_id": "unit:one", "provenance_ref": "unit:unit:one", "source_index": 0,
        }],
        "capabilities": [], "temporality": [], "manifestations": [],
        "resources": [{
            "dimension": "resources", "value": "resource:one", "status": "supported",
            "evidence_refs": ["artifact:resource"], "requirement_ids": [],
            "unit_id": "unit:one", "provenance_ref": "unit:unit:one", "source_index": 0,
        }],
        "claims": {
            "supported": [
                {
                    "claim_id": "claim:gate", "unit_id": "unit:one", "status": "supported",
                    "statement": "explicit gate evidence", "evidence_refs": ["artifact:gate"],
                    "requirement_ids": ["req:gate"], "source_status": "supported",
                    "provenance_ref": "unit:unit:one",
                },
            ],
            "candidate": [],
            "unknown": [],
        },
        "dependencies": [],
        "ambiguous_refs": [],
        "unassigned_refs": [],
        "gaps": [],
        "abstentions": [],
        "provenance": {"producer": "fixture", "source_rescan": False},
        "reconciliation": {"duplicate_physical_refs_collapsed": False},
    }
    state["state_hash"] = _hash(state)
    return state

def _opportunity(*, source_status: str = "current_verified", confirmed: bool = True) -> dict:
    package = {
        "schema": "mak-opportunity-document-package-v1",
        "opportunity_id": "opportunity:fixture",
        "title": "Fixture opportunity",
        "source": {
            "ref": "fixture:bases.pdf", "content": "bases-v1", "version": "v1",
            "validity": {"status": source_status, "confirmed": confirmed},
        },
        "requirements": [
            {"id": "req:gate", "kind": "hard_gate", "field": "eligibility", "evidence_refs": ["pdf:gate"]},
            {"id": "req:media", "kind": "criterion", "field": "media", "evidence_refs": ["pdf:media"]},
        ],
        "evidence": [
            {"evidence_id": "pdf:gate", "kind": "hard_gate", "field": "eligibility", "value": True, "locator": {"page": 1}},
            {"evidence_id": "pdf:media", "kind": "criterion", "field": "media", "value": "audio", "weight": 1, "locator": {"page": 2}},
        ],
    }
    return compile_opportunity_constraints(package)

def _candidate(opportunity: dict, practice: dict, fit: dict, **changes: object) -> dict:
    identity = fit["practice_identity"]
    program = {
        "program_id": "pending",
        "basis": "opportunity_conditioned",
        "status": "candidate",
        "unit_ids": ["unit:one"],
        "requirement_ids": ["req:gate", "req:media"],
        "supported_claim_ids": ["claim:gate"],
        "candidate_claim_ids": [],
        "evidence_refs": ["artifact:gate", "artifact:media", "artifact:resource"],
        "counterevidence_refs": [],
        "missing_requirement_ids": [],
        "research_action_ids": [],
        "resource_refs": ["resource:one"],
        "alternatives": [],
        "generation_reasons": ["explicit_bindings"],
        "risk_flags": [],
        "provenance": {
            "opportunity_id": opportunity["opportunity_id"],
            "opportunity_input_hash": opportunity["input_hash"],
            "practice_identity": identity,
            "practice_state_hash": practice["state_hash"],
            "fit_input_hash": fit_input_hash_for(fit),
            "source_rescan": False,
            "claims_promoted": 0,
        },
    }
    program.update(changes)
    program["program_id"] = program_id_for(
        program, opportunity_id=opportunity["opportunity_id"], practice_identity=identity
    )
    return program

def _payload(opportunity: dict, practice: dict, fit: dict, programs: list[dict]) -> dict:
    return {
        "schema": "mak-artistic-program-candidates-v1",
        "algorithm_version": "artistic-program-generator-fixture-1",
        "opportunity_id": opportunity["opportunity_id"],
        "candidates": sorted(programs, key=lambda row: row["program_id"]),
    }

def _inputs(*, source_status: str = "current_verified", confirmed: bool = True):
    opportunity = _opportunity(source_status=source_status, confirmed=confirmed)
    practice = _practice()
    fit = evaluate_opportunity_fit(opportunity, practice)
    return opportunity, practice, fit

def _chain(*, source_status: str = "current_verified", confirmed: bool = True) -> tuple[dict, ...]:
    opportunity, practice, fit = _inputs(source_status=source_status, confirmed=confirmed)
    programs = generate_artistic_program_hypotheses(opportunity, practice, fit)
    evaluations = evaluate_artistic_program_payload(opportunity, practice, fit, programs)
    possibility = build_possibility_field(programs, evaluations)
    frontier = compile_research_frontier(possibility, fit, opportunity)
    triangulation = triangulate_research_evidence(frontier, [])
    evidence_return = build_evidence_return(
        opportunity, practice, fit, frontier, triangulation
    )
    return opportunity, practice, fit, programs, possibility, frontier, evidence_return

def _technical_context() -> dict:
    return {
        "schema": "mak-project-context-v1",
        "context_id": "tool-context:surface",
        "title": "Technical archive observations",
        "entities": [
            {
                "entity_id": "artifact:one",
                "kind": "physical_artifact",
                "display_name": "native.psd",
            },
            {
                "entity_id": "artifact:two",
                "kind": "physical_artifact",
                "display_name": "logo.png",
            },
        ],
        "sources": [
            {
                "source_id": "tool-observation:surface",
                "source_type": "technical_tool_observation",
                "independence_group": "tool:archive-toolchain",
                "locator": "artifact:one",
                "claim": "technical_observation:surface_match_retrieval",
                "status": "observed",
                "metadata": {
                    "relative_path": "private/native.psd",
                    "facts": {"target_ref": "artifact:two"},
                },
            },
        ],
        "relations": [
            {
                "subject": "artifact:one",
                "predicate": "technical_surface_match_candidate",
                "object": "artifact:two",
                "status": "candidate",
                "source_ids": ["tool-observation:surface"],
                "metadata": {
                    "signals": ["perceptual_surface_similarity"],
                    "relative_path": "private/native.psd",
                    "truth_promotion": False,
                },
            },
        ],
        "projects": [],
        "provenance": {
            "archive_id": "archive:generic",
            "snapshot_id": "snapshot:one",
            "input_hash": "sha256:technical-input",
            "source_schema": "mak-archive-tool-observations-v1",
        },
    }
