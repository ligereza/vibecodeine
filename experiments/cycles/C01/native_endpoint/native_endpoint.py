"""Synthetic, read-only native provenance endpoint for cycle C01.

The extractor consumes only the JSON fixture format defined in this directory.
It never opens or probes a native source file.  Input-to-activity edges point
from the technical input to the activity; generated edges point from an
activity to its concrete output.  Lineage edges point backwards from an
output version to its declared predecessor.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping
import json


SCHEMA = "mak-cycle-c01-edge-v1"
EXTRACTOR_VERSION = "native-endpoint-synthetic-v1"
NODE_KINDS = frozenset({"publication", "deliverable", "authoring", "component", "source", "activity"})
EDGE_RELATIONS = frozenset({"uses", "generated", "derived_from", "specializes", "candidate_match", "contains"})
EDGE_STATUSES = frozenset({"confirmed", "supported", "candidate", "contradicted", "unknown"})
ACTIVITY_STATES = frozenset({"planned", "started", "completed", "failed", "unknown"})


class FixtureError(ValueError):
    """Raised when a synthetic fixture violates the endpoint contract."""


@dataclass(frozen=True)
class Node:
    kind: str
    id: str
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "id": self.id, **dict(self.attributes)}


@dataclass(frozen=True)
class Edge:
    archive_id: str
    source_kind: str
    source_id: str
    target_kind: str
    target_id: str
    relation: str
    status: str
    evidence_refs: tuple[str, ...]
    score: float | None = None
    extractor_version: str = EXTRACTOR_VERSION

    def as_contract(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "archive_id": self.archive_id,
            "source": {"kind": self.source_kind, "id": self.source_id},
            "target": {"kind": self.target_kind, "id": self.target_id},
            "relation": self.relation,
            "status": self.status,
            "evidence_refs": list(self.evidence_refs),
            "score": self.score,
            "extractor_version": self.extractor_version,
        }

    @property
    def ref(self) -> str:
        return f"{self.source_id}>{self.relation}>{self.target_id}"


@dataclass
class ProvenanceGraph:
    archive_id: str
    case_id: str
    nodes: dict[str, Node]
    edges: list[Edge]

    def nodes_of_kind(self, kind: str) -> list[Node]:
        return [node for node in self.nodes.values() if node.kind == kind]


@dataclass(frozen=True)
class MediatedLink:
    authoring_id: str
    deliverable_id: str
    activity_ids: tuple[str, ...]
    relation_path: tuple[str, ...]
    edge_refs: tuple[str, ...]
    technical_inputs: tuple[str, ...]
    lineage_relations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "authoring_id": self.authoring_id,
            "deliverable_id": self.deliverable_id,
            "activity_ids": list(self.activity_ids),
            "relation_path": list(self.relation_path),
            "edge_refs": list(self.edge_refs),
            "technical_inputs": list(self.technical_inputs),
            "lineage_relations": list(self.lineage_relations),
        }


@dataclass(frozen=True)
class DirectJoinResult:
    edges: tuple[Edge, ...]
    unanchored_deliverable_ids: tuple[str, ...]


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load a synthetic fixture; this is the only file-reading entrypoint."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise FixtureError("fixture root must be an object")
    return payload


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise FixtureError(f"{label} must be a non-empty string")
    return value


def _refs(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(ref, str) or not ref for ref in value):
        raise FixtureError(f"{label} must contain at least one non-empty evidence reference")
    return tuple(value)


def _edge_status_for_uses(activity_status: str) -> str:
    return "supported" if activity_status in {"started", "completed", "failed"} else "unknown"


def _edge_status_for_generated(activity_status: str) -> str:
    if activity_status == "completed":
        return "supported"
    if activity_status == "failed":
        return "contradicted"
    return "unknown"


def _make_edge(
    archive_id: str,
    source: Node,
    target: Node,
    relation: str,
    status: str,
    evidence_refs: Iterable[str],
) -> Edge:
    if relation not in EDGE_RELATIONS:
        raise FixtureError(f"unsupported relation: {relation}")
    if status not in EDGE_STATUSES:
        raise FixtureError(f"unsupported edge status: {status}")
    refs = tuple(evidence_refs)
    if status != "unknown" and not refs:
        raise FixtureError(f"non-unknown edge needs evidence: {source.id}>{relation}>{target.id}")
    return Edge(
        archive_id=archive_id,
        source_kind=source.kind,
        source_id=source.id,
        target_kind=target.kind,
        target_id=target.id,
        relation=relation,
        status=status,
        evidence_refs=refs,
    )


def extract_graph(fixture: Mapping[str, Any]) -> ProvenanceGraph:
    """Extract the technical graph from synthetic declarations only."""

    if fixture.get("schema") != "mak-native-fixture-v1":
        raise FixtureError("unsupported fixture schema")
    archive_id = _text(fixture.get("archive_id"), "archive_id")
    case_id = _text(fixture.get("case_id"), "case_id")
    nodes: dict[str, Node] = {}

    raw_nodes = fixture.get("nodes")
    if not isinstance(raw_nodes, list):
        raise FixtureError("nodes must be a list")
    for raw_node in raw_nodes:
        if not isinstance(raw_node, dict):
            raise FixtureError("each node must be an object")
        kind = _text(raw_node.get("kind"), "node.kind")
        node_id = _text(raw_node.get("id"), "node.id")
        if kind not in NODE_KINDS:
            raise FixtureError(f"unsupported node kind: {kind}")
        if node_id in nodes:
            raise FixtureError(f"duplicate node id: {node_id}")
        attributes = {key: value for key, value in raw_node.items() if key not in {"kind", "id"}}
        nodes[node_id] = Node(kind=kind, id=node_id, attributes=attributes)

    graph = ProvenanceGraph(archive_id=archive_id, case_id=case_id, nodes=nodes, edges=[])
    raw_activities = fixture.get("activities")
    if not isinstance(raw_activities, list):
        raise FixtureError("activities must be a list")

    for raw_activity in raw_activities:
        if not isinstance(raw_activity, dict):
            raise FixtureError("each activity must be an object")
        activity_id = _text(raw_activity.get("id"), "activity.id")
        if activity_id in graph.nodes:
            raise FixtureError(f"duplicate activity id: {activity_id}")
        activity_type = _text(raw_activity.get("activity_type"), f"activity[{activity_id}].activity_type")
        status = _text(raw_activity.get("status"), f"activity[{activity_id}].status")
        if status not in ACTIVITY_STATES:
            raise FixtureError(f"unsupported activity status: {status}")
        state_history = raw_activity.get("state_history")
        if not isinstance(state_history, list) or not state_history:
            raise FixtureError(f"activity[{activity_id}] needs an explicit state history")
        states = []
        for state in state_history:
            if not isinstance(state, dict) or state.get("state") not in ACTIVITY_STATES:
                raise FixtureError(f"invalid state history for activity[{activity_id}]")
            _refs([state.get("evidence_ref")], f"activity[{activity_id}].state evidence")
            states.append(state["state"])
        if states[-1] != status:
            raise FixtureError(f"activity[{activity_id}] final state does not equal status")
        observation_refs = _refs(raw_activity.get("observation_refs"), f"activity[{activity_id}].observation_refs")
        activity = Node(
            kind="activity",
            id=activity_id,
            attributes={
                "activity_type": activity_type,
                "status": status,
                "state_history": state_history,
                "observation_refs": list(observation_refs),
                "read_only": True,
            },
        )
        graph.nodes[activity_id] = activity

        input_ids = raw_activity.get("uses", [])
        output_ids = raw_activity.get("generated", [])
        if not isinstance(input_ids, list) or not isinstance(output_ids, list):
            raise FixtureError(f"activity[{activity_id}] uses/generated must be lists")
        for input_id in input_ids:
            input_id = _text(input_id, f"activity[{activity_id}].uses id")
            if input_id not in graph.nodes:
                raise FixtureError(f"activity[{activity_id}] references unknown input {input_id}")
            graph.edges.append(
                _make_edge(
                    archive_id,
                    graph.nodes[input_id],
                    activity,
                    "uses",
                    _edge_status_for_uses(status),
                    observation_refs,
                )
            )
        for output_id in output_ids:
            output_id = _text(output_id, f"activity[{activity_id}].generated id")
            if output_id not in graph.nodes:
                raise FixtureError(f"activity[{activity_id}] references unknown output {output_id}")
            graph.edges.append(
                _make_edge(
                    archive_id,
                    activity,
                    graph.nodes[output_id],
                    "generated",
                    _edge_status_for_generated(status),
                    observation_refs,
                )
            )

    raw_lineage = fixture.get("lineage", [])
    if not isinstance(raw_lineage, list):
        raise FixtureError("lineage must be a list")
    for raw_edge in raw_lineage:
        if not isinstance(raw_edge, dict):
            raise FixtureError("each lineage item must be an object")
        source_id = _text(raw_edge.get("source_id"), "lineage.source_id")
        target_id = _text(raw_edge.get("target_id"), "lineage.target_id")
        relation = _text(raw_edge.get("relation"), "lineage.relation")
        status = _text(raw_edge.get("status"), "lineage.status")
        if source_id not in graph.nodes or target_id not in graph.nodes:
            raise FixtureError("lineage references an unknown node")
        refs = () if status == "unknown" else _refs(raw_edge.get("evidence_refs"), "lineage.evidence_refs")
        graph.edges.append(_make_edge(archive_id, graph.nodes[source_id], graph.nodes[target_id], relation, status, refs))

    return graph


def direct_authoring_deliverable_join(graph: ProvenanceGraph) -> DirectJoinResult:
    """Make the intentionally weak baseline from an explicit declared field.

    Filename, extension, timestamps and archive_id are deliberately ignored.
    """

    edges: list[Edge] = []
    unanchored: list[str] = []
    for deliverable in graph.nodes_of_kind("deliverable"):
        if deliverable.attributes.get("identifiable", True) is False:
            unanchored.append(deliverable.id)
            continue
        declared_authoring_id = deliverable.attributes.get("declared_authoring_id")
        if not declared_authoring_id:
            unanchored.append(deliverable.id)
            continue
        authoring = graph.nodes.get(declared_authoring_id)
        if authoring is None or authoring.kind != "authoring":
            unanchored.append(deliverable.id)
            continue
        evidence_ref = f"fixture:{graph.case_id}:deliverable:{deliverable.id}:declared_authoring_id"
        edges.append(
            _make_edge(
                graph.archive_id,
                authoring,
                deliverable,
                "candidate_match",
                "candidate",
                (evidence_ref,),
            )
        )
    return DirectJoinResult(edges=tuple(edges), unanchored_deliverable_ids=tuple(unanchored))


def mediated_authoring_deliverable_links(graph: ProvenanceGraph) -> tuple[MediatedLink, ...]:
    """Follow declared uses/generated activity paths and attach lineage context."""

    uses_from: dict[str, list[Edge]] = defaultdict(list)
    generated_from: dict[str, list[Edge]] = defaultdict(list)
    lineage_from_output: dict[str, list[Edge]] = defaultdict(list)
    for edge in graph.edges:
        if edge.relation == "uses":
            uses_from[edge.source_id].append(edge)
        elif edge.relation == "generated":
            generated_from[edge.source_id].append(edge)
        elif edge.relation in {"derived_from", "specializes"}:
            lineage_from_output[edge.source_id].append(edge)

    links: list[MediatedLink] = []
    for authoring in graph.nodes_of_kind("authoring"):
        queue = deque([(authoring.id, tuple(), tuple(), tuple())])
        visited: set[tuple[str, tuple[str, ...]]] = set()
        while queue:
            current_id, activities, path_edges, technical_inputs = queue.popleft()
            state_key = (current_id, activities)
            if state_key in visited:
                continue
            visited.add(state_key)
            current_node = graph.nodes[current_id]
            if current_node.kind == "activity":
                for generated in generated_from.get(current_id, []):
                    output = graph.nodes[generated.target_id]
                    if output.kind != "deliverable" or output.attributes.get("identifiable", True) is False:
                        continue
                    lineage = lineage_from_output.get(output.id, [])
                    lineage_relations = tuple(edge.relation for edge in lineage)
                    links.append(
                        MediatedLink(
                            authoring_id=authoring.id,
                            deliverable_id=output.id,
                            activity_ids=activities,
                            relation_path=tuple(["uses"] * len(activities) + ["generated"] + list(lineage_relations)),
                            edge_refs=tuple(path_edges + (generated.ref,) + tuple(edge.ref for edge in lineage)),
                            technical_inputs=tuple(sorted(set(technical_inputs))),
                            lineage_relations=lineage_relations,
                        )
                    )
            for uses in uses_from.get(current_id, []):
                target = graph.nodes[uses.target_id]
                if target.kind == "activity":
                    next_activities = activities + (target.id,)
                    next_inputs = technical_inputs + tuple(
                        node_id for node_id, node in graph.nodes.items() if node.kind in {"source", "component"} and any(
                            edge.source_id == node_id and edge.target_id in next_activities for edge in graph.edges if edge.relation == "uses"
                        )
                    )
                    queue.append((target.id, next_activities, path_edges + (uses.ref,), next_inputs))
    unique: dict[tuple[str, str, tuple[str, ...]], MediatedLink] = {}
    for link in links:
        unique[(link.authoring_id, link.deliverable_id, link.activity_ids)] = link
    return tuple(unique.values())


def compare_models(fixture: Mapping[str, Any]) -> dict[str, Any]:
    graph = extract_graph(fixture)
    direct = direct_authoring_deliverable_join(graph)
    mediated = mediated_authoring_deliverable_links(graph)
    return {
        "case_id": graph.case_id,
        "archive_id": graph.archive_id,
        "nodes": [node.as_dict() for node in graph.nodes.values()],
        "edges": [edge.as_contract() for edge in graph.edges],
        "direct_join": {
            "edges": [edge.as_contract() for edge in direct.edges],
            "unanchored_deliverable_ids": list(direct.unanchored_deliverable_ids),
        },
        "mediated_links": [link.as_dict() for link in mediated],
        "activity_states": {
            node.id: node.attributes["status"] for node in graph.nodes_of_kind("activity")
        },
    }


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    payload = load_fixture(path)
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise FixtureError("case bundle must contain a non-empty cases list")
    return cases


__all__ = [
    "EDGE_RELATIONS",
    "EDGE_STATUSES",
    "EXTRACTOR_VERSION",
    "FixtureError",
    "SCHEMA",
    "compare_models",
    "direct_authoring_deliverable_join",
    "extract_graph",
    "load_cases",
    "load_fixture",
    "mediated_authoring_deliverable_links",
]
