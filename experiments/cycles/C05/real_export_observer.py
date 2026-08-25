"""Observe one explicit Blender export witness without opening Blender.

The adapter is intentionally narrow: every input path is supplied explicitly,
the source is checked against an existing native snapshot, the marker and
script are parsed as evidence, and the GLB JSON is inspected for exported
object names.  It never scans a directory, runs a script, opens Blender, or
labels the artifact as a final artwork.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import struct
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping


CONTRACT = "mak-cycle-c05-export-witness-v1"
GLB_JSON_CHUNK = 0x4E4F534A


class InputError(ValueError):
    """Raised when an explicitly supplied evidence input is malformed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise InputError(f"{label}_not_a_file:{path}")


def _basename(value: str) -> str:
    return PureWindowsPath(value.replace("/", "\\")).name.casefold()


def _parse_script(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    names_match = re.search(r"(?m)^\s*names\s*=\s*(\[[^\n]*\])", text)
    output_match = re.search(r"(?m)^\s*OUT\s*=\s*(r?[\"'][^\n]+[\"'])", text)
    if not names_match or not output_match:
        raise InputError("export_script_missing_names_or_output")
    try:
        names = ast.literal_eval(names_match.group(1))
        output_path = ast.literal_eval(output_match.group(1))
    except (SyntaxError, ValueError) as exc:
        raise InputError("export_script_literal_parse_failed") from exc
    if not isinstance(names, list) or any(not isinstance(name, str) or not name for name in names):
        raise InputError("export_script_names_invalid")
    if not isinstance(output_path, str) or not output_path:
        raise InputError("export_script_output_invalid")
    return {"names": names, "output_path": output_path}


def _parse_marker(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    match = re.fullmatch(r"OK exported=(?P<names>\[[^\n]*\]) -> (?P<target>.+)", text)
    if not match:
        return {"status": "failed_or_unrecognised", "raw": text}
    try:
        names = ast.literal_eval(match.group("names"))
    except (SyntaxError, ValueError) as exc:
        raise InputError("export_marker_literal_parse_failed") from exc
    if not isinstance(names, list) or any(not isinstance(name, str) or not name for name in names):
        raise InputError("export_marker_names_invalid")
    return {"status": "ok", "names": names, "target": match.group("target")}


def _read_glb_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20:
        raise InputError("glb_too_short")
    magic, version, declared_length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(data):
        raise InputError("glb_header_invalid")
    offset = 12
    json_payload: bytes | None = None
    while offset < len(data):
        if offset + 8 > len(data):
            raise InputError("glb_chunk_header_truncated")
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        end = offset + chunk_length
        if end > len(data):
            raise InputError("glb_chunk_truncated")
        if chunk_type == GLB_JSON_CHUNK and json_payload is None:
            json_payload = data[offset:end].rstrip(b" \\t\\r\\n\\x00")
        offset = end
    if json_payload is None:
        raise InputError("glb_json_chunk_missing")
    try:
        parsed = json.loads(json_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError("glb_json_parse_failed") from exc
    if not isinstance(parsed, dict):
        raise InputError("glb_json_not_an_object")
    return parsed


def _snapshot_object_names(snapshot: Mapping[str, Any]) -> list[str]:
    native = snapshot.get("snapshot", {}).get("native", {})
    scenes = native.get("scenes", []) if isinstance(native, Mapping) else []
    names: list[str] = []
    for scene in scenes:
        if not isinstance(scene, Mapping):
            continue
        for obj in scene.get("objects", []):
            if isinstance(obj, Mapping) and isinstance(obj.get("name"), str):
                names.append(obj["name"])
    return names


def _check(status: bool, reason: str, **details: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "pass" if status else "fail", "reason": reason}
    if details:
        result["details"] = details
    return result


def build_observation(
    *,
    source_blend: str | Path,
    source_snapshot: str | Path,
    export_script: str | Path,
    marker: str | Path,
    output_glb: str | Path,
) -> dict[str, Any]:
    source = Path(source_blend)
    snapshot_path = Path(source_snapshot)
    script = Path(export_script)
    marker_path = Path(marker)
    output = Path(output_glb)
    for path, label in (
        (source, "source_blend"),
        (snapshot_path, "source_snapshot"),
        (script, "export_script"),
        (marker_path, "export_marker"),
        (output, "output_glb"),
    ):
        _require_file(path, label)

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if not isinstance(snapshot, Mapping):
        raise InputError("source_snapshot_not_an_object")
    script_data = _parse_script(script)
    marker_data = _parse_marker(marker_path)
    glb = _read_glb_json(output)

    source_hash = sha256_file(source)
    integrity = snapshot.get("integrity", {})
    expected_hash = integrity.get("sha256_before") or snapshot.get("source", {}).get("expected_sha256")
    source_names = _snapshot_object_names(snapshot)
    output_names = [
        node.get("name")
        for node in glb.get("nodes", [])
        if isinstance(node, Mapping) and isinstance(node.get("name"), str)
    ]
    output_mesh_names = [
        mesh.get("name")
        for mesh in glb.get("meshes", [])
        if isinstance(mesh, Mapping) and isinstance(mesh.get("name"), str)
    ]
    script_names = list(script_data["names"])
    marker_names = list(marker_data.get("names", []))
    target_names = set(script_names)
    checks = {
        "source_hash_matches_native_snapshot": _check(
            bool(expected_hash) and source_hash.casefold() == str(expected_hash).casefold(),
            "source_hash_matches_snapshot" if expected_hash else "snapshot_has_no_expected_source_hash",
            actual=source_hash,
            expected=expected_hash,
        ),
        "script_and_marker_agree": _check(
            marker_data.get("status") == "ok" and marker_names == script_names,
            "marker_confirms_script_selection" if marker_data.get("status") == "ok" else "marker_not_successful",
            script_names=script_names,
            marker_names=marker_names,
        ),
        "marker_target_matches_output": _check(
            marker_data.get("status") == "ok"
            and _basename(str(marker_data.get("target", ""))) == output.name.casefold()
            and _basename(str(script_data["output_path"])) == output.name.casefold(),
            "declared_output_basename_matches_observed_glb" if marker_data.get("status") == "ok" else "marker_not_successful",
            script_target=script_data["output_path"],
            marker_target=marker_data.get("target"),
            observed_output=output.name,
        ),
        "source_contains_exported_objects": _check(
            target_names.issubset(set(source_names)),
            "native_snapshot_contains_selected_objects",
            selected=script_names,
            source_objects=source_names,
        ),
        "output_contains_exported_objects": _check(
            target_names.issubset(set(output_names))
            and target_names.issubset(set(output_mesh_names)),
            "glb_contains_selected_nodes_and_meshes",
            selected=script_names,
            output_nodes=output_names,
            output_meshes=output_mesh_names,
        ),
        "output_is_blender_glb": _check(
            isinstance(glb.get("asset"), Mapping)
            and str(glb["asset"].get("version")) == "2.0"
            and "Blender" in str(glb["asset"].get("generator", "")),
            "glb_generator_and_version_observed",
            asset=glb.get("asset"),
        ),
        "output_after_script_and_marker": _check(
            output.stat().st_mtime_ns >= script.stat().st_mtime_ns
            and output.stat().st_mtime_ns >= marker_path.stat().st_mtime_ns,
            "filesystem_mtime_order_is_consistent",
            script_mtime_ns=script.stat().st_mtime_ns,
            marker_mtime_ns=marker_path.stat().st_mtime_ns,
            output_mtime_ns=output.stat().st_mtime_ns,
        ),
    }
    passed = all(item["status"] == "pass" for item in checks.values())
    refs = [
        f"C05/source_blend/sha256={source_hash}",
        f"C05/export_script/sha256={sha256_file(script)}",
        f"C05/export_marker/sha256={sha256_file(marker_path)}",
        f"C05/output_glb/sha256={sha256_file(output)}",
        "C02/blender_endpoint/snapshot.json#/snapshot/native/scenes/0/objects",
    ]
    return {
        "schema": CONTRACT,
        "read_policy": {
            "directory_scan": False,
            "blender_opened": False,
            "scripts_executed": False,
            "inputs_written": False,
        },
        "inputs": {
            "source_locator": "ARICA/RAYU.blend",
            "source_sha256": source_hash,
            "source_snapshot_sha256": sha256_file(snapshot_path),
            "export_script_sha256": sha256_file(script),
            "marker_sha256": sha256_file(marker_path),
            "output_sha256": sha256_file(output),
            "output_bytes": output.stat().st_size,
        },
        "witness": {
            "status": "supported" if passed else "unknown",
            "reason": "explicit_script_marker_and_glb_bind_native_objects_to_export" if passed else "export_evidence_is_incomplete_or_conflicting",
            "evidence_refs": refs,
            "checks": checks,
            "event_type": "export",
            "source_ref": "authoring:blend:ARICA/RAYU.blend",
            "target_ref": f"artifact:glb:{output.name}",
            "claim_limit": "supports an export event for this artifact; does not prove final-delivery status, artistic intent, authorship, or absence of later modification",
        },
        "artifact": {
            "name": output.name,
            "format": "glb",
            "generator": glb.get("asset", {}).get("generator") if isinstance(glb.get("asset"), Mapping) else None,
            "nodes": output_names,
            "meshes": output_mesh_names,
        },
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    root = Path("/home/mak/curatoria_inbox/ARICA")
    cycle = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-blend", default=str(root / "RAYU.blend"))
    parser.add_argument("--source-snapshot", default="../C02/blender_endpoint/snapshot.json")
    parser.add_argument("--export-script", default=str(root / "rayu_export.py"))
    parser.add_argument("--marker", default=str(root / "rayu_export_done.txt"))
    parser.add_argument("--output-glb", default=str(root / "rayu_resources.glb"))
    parser.add_argument("--output", default=str(cycle / "real_export_witness.json"))
    args = parser.parse_args(argv)
    snapshot = Path(args.source_snapshot)
    if not snapshot.is_absolute():
        snapshot = (cycle / snapshot).resolve()
    observation = build_observation(
        source_blend=args.source_blend,
        source_snapshot=snapshot,
        export_script=args.export_script,
        marker=args.marker,
        output_glb=args.output_glb,
    )
    output_path = Path(args.output)
    output_path.write_text(json.dumps(observation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "status": observation["witness"]["status"], "check_count": len(observation["witness"]["checks"])}, sort_keys=True))
    return 0 if observation["witness"]["status"] == "supported" else 2


if __name__ == "__main__":
    raise SystemExit(main())
