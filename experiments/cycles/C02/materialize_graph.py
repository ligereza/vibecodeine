"""Materialize the two C02 native observations as a conservative graph.

This is an experiment-only adapter. It turns native declarations into
candidate/supporting ``uses`` edges and keeps public/output uncertainty as
first-class data. It never infers ``generated`` or ``RENDERS_TO``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT = "mak-cycle-c02-native-graph-v1"
ARCHIVE_ID = "archive-arica-001"
FORBIDDEN_RELATIONS = {"generated", "RENDERS_TO", "renders_to"}


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _node(nodes: dict[str, dict[str, Any]], node_id: str, kind: str, **fields: Any) -> str:
    nodes.setdefault(node_id, {"id": node_id, "kind": kind, "archive_id": ARCHIVE_ID, **fields})
    return node_id


def materialize(blender: Mapping[str, Any], aep: Mapping[str, Any]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    capabilities: list[dict[str, Any]] = []
    output_role_unknowns: list[dict[str, Any]] = []

    blend_source = "authoring:blend:ARICA/RAYU.blend"
    aep_source = "authoring:aep:ARICA/ARICA.aep"
    _node(nodes, blend_source, "authoring", format="blend", locator="ARICA/RAYU.blend")
    _node(nodes, aep_source, "authoring", format="aep", locator="ARICA/ARICA.aep")

    native = blender.get("snapshot", {}).get("native", {})
    for scene_index, scene in enumerate(native.get("scenes", [])):
        scene_name = str(scene.get("name") or f"scene-{scene_index}")
        render = scene.get("render", {})
        capabilities.append({
            "authoring_id": blend_source,
            "capability": "render",
            "scene": scene_name,
            "status": "observed",
            "settings": {
                "engine": render.get("engine"),
                "resolution_x": render.get("resolution_x"),
                "resolution_y": render.get("resolution_y"),
                "resolution_percentage": render.get("resolution_percentage"),
                "file_format": render.get("file_format"),
                "filepath_declared": render.get("filepath"),
            },
            "evidence_refs": [f"blender_endpoint/snapshot.json#/snapshot/native/scenes/{scene_index}/render"],
            "claim_limit": "configured capability; no render event or output proven",
        })

    for dependency_index, dependency in enumerate(native.get("dependencies", [])):
        declared = str(dependency.get("path") or f"dependency-{dependency_index}")
        component_id = _stable_id("component:blend-image", declared)
        _node(nodes, component_id, "component", source_kind="blender_image", declared_path=declared)
        edges.append({
            "source": {"kind": "authoring", "id": blend_source},
            "target": {"kind": "component", "id": component_id},
            "relation": "uses",
            "status": "supported",
            "evidence_refs": [f"blender_endpoint/snapshot.json#/snapshot/native/dependencies/{dependency_index}"],
            "extractor_version": blender.get("extractor", {}).get("id", "unknown"),
            "claim_limit": "native dependency declaration; external availability is not inferred",
        })

    references = aep.get("local_resolution", {}).get("references", [])
    for reference_index, reference in enumerate(references):
        declared = str(reference.get("declared_path") or f"reference-{reference_index}")
        resolution = reference.get("local_resolution", {})
        for candidate_path in resolution.get("candidate_paths", []):
            target_id = _stable_id("artifact:candidate", str(candidate_path))
            target_kind = "directory" if resolution.get("local_kind") == "folder" else "deliverable_candidate"
            _node(nodes, target_id, target_kind, locator=str(candidate_path), basename=reference.get("declared_basename"))
            edges.append({
                "source": {"kind": "authoring", "id": aep_source},
                "target": {"kind": target_kind, "id": target_id},
                "relation": "uses",
                "status": "candidate",
                "evidence_refs": [
                    f"aep_endpoint/observation.json#/local_resolution/references/{reference_index}",
                    f"aep://byte-offset/{reference.get('aep_record', {}).get('byte_offset')}",
                ],
                "extractor_version": aep.get("adapter_version", "unknown"),
                "claim_limit": "basename/existence candidate only; output role unknown",
            })
        if reference.get("output_claim", {}).get("status") == "unknown":
            output_role_unknowns.append({
                "declared_path": declared,
                "evidence_ref": f"aep_endpoint/observation.json#/local_resolution/references/{reference_index}/output_claim",
                "reason": reference.get("output_claim", {}).get("reason"),
            })
        if resolution.get("status") in {"unknown", "ambiguous"}:
            unknowns.append({
                "type": "local_reference_resolution",
                "declared_path": declared,
                "status": resolution.get("status"),
                "evidence_ref": f"aep_endpoint/observation.json#/local_resolution/references/{reference_index}/local_resolution",
            })

    public = aep.get("public_catalog", {}).get("join", {})
    unknowns.append({
        "type": "public_join",
        "status": public.get("status", "unknown"),
        "reason": public.get("reason", "missing evidence"),
        "evidence_ref": "aep_endpoint/observation.json#/public_catalog/join",
    })

    return {
        "schema": CONTRACT,
        "archive_id": ARCHIVE_ID,
        "inputs": {
            "blender": blender.get("source", {}),
            "aep": aep.get("input", {}),
        },
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": edges,
        "capabilities": capabilities,
        "unknowns": unknowns,
        "output_role_unknowns": output_role_unknowns,
        "safety": {
            "forbidden_relations_absent": not any(edge.get("relation") in FORBIDDEN_RELATIONS for edge in edges),
            "public_catalog_available": public.get("status") == "available",
            "learning_or_inference_performed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", type=Path, default=Path(__file__).parent / "blender_endpoint/snapshot.json")
    parser.add_argument("--aep", type=Path, default=Path(__file__).parent / "aep_endpoint/observation.json")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "native_graph.json")
    args = parser.parse_args(argv)
    blender = json.loads(args.blender.read_text(encoding="utf-8"))
    aep = json.loads(args.aep.read_text(encoding="utf-8"))
    payload = materialize(blender, aep)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": CONTRACT,
        "output": str(args.output),
        "node_count": len(payload["nodes"]),
        "edge_count": len(payload["edges"]),
        "unknown_count": len(payload["unknowns"]),
        "output_role_unknown_count": len(payload["output_role_unknowns"]),
        "forbidden_relations_absent": payload["safety"]["forbidden_relations_absent"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
