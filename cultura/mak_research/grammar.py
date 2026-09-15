"""Bounded representation-learning runner for the semantic-icons-v1 corpus.

The runner keeps the experiment local and typed:

    observations -> serializable programs -> inferred library -> compositions

The semantic compiler remains the authority for validating and rendering
specifications.  Library bodies are inferred from repeated fields in the
construction partition; no operation name or body is seeded for this runner.
Development and reserved material are read only after the library is frozen.
Every generation is dispatched through the existing MAK Conductor and
checkpointed so a stopped process can continue without rewriting prior output.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


RUN_SCHEMA = "mak-grammar-run-v1"
LANGUAGE = "semantic-icons-v1"
EXPERIMENT_VERSION = "semantic-icons-v1-grammar-v1"
CONDUCTOR_STAGE = "grammar_lab_generation"
STOP_FILE = "STOP"


class GrammarRunError(RuntimeError):
    """A user-actionable error in the bounded grammar runner."""


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(".%s.tmp" % path.name)
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value)).strip("-")
    return value or "candidate"


def _sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _git_revision(repository: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip() or None


def _semantic_modules(module_root: Path):
    parent = str(module_root.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    try:
        from motor_semantico import algebra
        from motor_semantico.compilador import (
            COMPOSICIONES,
            FIGURAS,
            GESTOS,
            RITMOS,
            TONOS,
            compilar,
            validar_spec,
        )
    except ImportError as exc:  # pragma: no cover - machine configuration
        raise GrammarRunError(
            "no se pudo cargar el intérprete semantic-icons-v1 desde "
            f"{module_root}: {exc}"
        ) from exc
    return {
        "algebra": algebra,
        "compilar": compilar,
        "validar_spec": validar_spec,
        "composiciones": COMPOSICIONES,
        "figuras": FIGURAS,
        "gestos": GESTOS,
        "ritmos": RITMOS,
        "tonos": TONOS,
    }


def _source_path(manifest: dict, manifest_path: Path) -> Path:
    source = Path(str(manifest["source"]["path"]))
    if source.is_absolute():
        return source.resolve()
    module_root = Path(str(manifest["adapter"]["module_root"]))
    candidate = (module_root / source).resolve()
    if candidate.exists():
        return candidate
    return (manifest_path.parent / source).resolve()


def _validate_contract(manifest_path: Path) -> dict:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GrammarRunError(f"manifiesto inválido: {manifest_path}: {exc}") from exc
    source_path = _source_path(manifest, manifest_path)
    if not source_path.is_file():
        raise GrammarRunError(f"no existe el corpus declarado: {source_path}")
    expected_sha = str(manifest["source"]["sha256"])
    actual_sha = _sha256_file(source_path)
    if actual_sha != expected_sha:
        raise GrammarRunError(
            "corpus_changed: el SHA-256 no coincide con el manifiesto "
            f"(esperado {expected_sha}, actual {actual_sha}); usa otra versión "
            "de experimento y otro directorio de salida"
        )
    try:
        rows = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GrammarRunError(f"corpus inválido: {source_path}: {exc}") from exc
    if not isinstance(rows, list):
        raise GrammarRunError("el corpus declarado no es una lista JSON")
    declared_count = int(manifest["source"].get("records", len(rows)))
    if len(rows) != declared_count:
        raise GrammarRunError(
            f"corpus_count_mismatch: manifiesto={declared_count}, actual={len(rows)}"
        )
    by_slug = {str(row.get("slug")): row for row in rows if isinstance(row, dict)}
    if len(by_slug) != len(rows):
        raise GrammarRunError("el corpus contiene slugs ausentes o duplicados")
    partitions = manifest.get("partitions") or {}
    seen: list[str] = []
    partition_rows: dict[str, list[dict]] = {}
    for name in ("construction", "development", "final_reserved"):
        slugs = [str(slug) for slug in partitions.get(name, [])]
        missing = [slug for slug in slugs if slug not in by_slug]
        if missing:
            raise GrammarRunError(f"manifest_entries_missing: {missing}")
        partition_rows[name] = [deepcopy(by_slug[slug]) for slug in slugs]
        seen.extend(slugs)
    if sorted(seen) != sorted(by_slug):
        raise GrammarRunError("las particiones no cubren exactamente el corpus")
    module_root = Path(str(manifest["adapter"]["module_root"])).resolve()
    semantic = _semantic_modules(module_root)
    validity = {}
    for row in rows:
        errors = list(semantic["validar_spec"](row))
        validity[str(row["slug"])] = {"valid": not errors, "errors": errors}
    source_revision = manifest.get("source_revision") or {}
    repository = Path(str(source_revision.get("repository") or manifest_path.parent))
    return {
        "manifest": manifest,
        "manifest_path": str(manifest_path.resolve()),
        "source_path": str(source_path),
        "source_sha256": actual_sha,
        "source_revision": deepcopy(source_revision),
        "current_git_revision": _git_revision(repository),
        "rows": rows,
        "by_slug": by_slug,
        "partitions": partition_rows,
        "validity": validity,
        "module_root": str(module_root),
        "semantic": semantic,
    }


def load_contract(manifest_path: str | os.PathLike[str]) -> dict:
    """Validate the manifest and corpus once, returning a compact run context."""
    return _validate_contract(Path(manifest_path).expanduser().resolve())


def _header_for(spec: dict) -> dict:
    return {key: deepcopy(value) for key, value in spec.items() if key != "capas"}


def direct_program(spec: dict) -> dict:
    return {
        "language": LANGUAGE,
        "program_version": EXPERIMENT_VERSION,
        "op": "icon",
        "header": _header_for(spec),
        "parts": [
            {"position": index,
             "node": {"op": "layer", "layer": deepcopy(layer)}}
            for index, layer in enumerate(spec.get("capas", []))
        ],
    }


def _repeat_groups(spec: dict) -> list[tuple[tuple[str, str], list[tuple[int, dict]]]]:
    groups: dict[tuple[str, str], list[tuple[int, dict]]] = defaultdict(list)
    for index, layer in enumerate(spec.get("capas", [])):
        figure = layer.get("figura")
        gesture = layer.get("gesto", "quieto")
        if figure and gesture:
            groups[(str(figure), str(gesture))].append((index, layer))
    return sorted(
        [(key, values) for key, values in groups.items() if len(values) >= 2],
        key=lambda item: (-len(item[1]), item[1][0][0], item[0]),
    )


def _slug_part(value: object) -> str:
    return _safe_name(str(value).lower().replace(" ", "-"))


def _cost_for_fragment(layers: list[tuple[int, dict]], name: str,
                       kind: str) -> dict:
    before = len(canonical({"positions": [i for i, _ in layers],
                            "layers": [layer for _, layer in layers]}))
    if kind == "text_layer":
        args = {"layer": layers[0][1]}
    else:
        args = {"constant_fields": ["figura", "gesto"],
                "items": [{"position": i, "layer": layer} for i, layer in layers]}
    after = len(canonical({"op": "call", "name": name, "args": args}))
    return {"before_bytes": before, "after_bytes": after,
            "library_body_bytes": 0}


def discover_library(rows: list[dict]) -> dict:
    """Infer operation bodies from repeated observed fragments.

    The operation names, matchers and bodies are assembled from input
    evidence.  The code only defines how to turn an invariant into a template;
    it does not seed a corpus-specific operation or body.
    """
    text_groups: dict[tuple[str, tuple[str, ...]], list[tuple[str, int, dict]]] = defaultdict(list)
    repeated: list[tuple[str, tuple[str, str], list[tuple[int, dict]]]] = []
    for row in rows:
        slug = str(row["slug"])
        for index, layer in enumerate(row.get("capas", [])):
            if layer.get("texto") is not None and not layer.get("figura"):
                structural_keys = tuple(sorted(key for key in layer if key != "texto"))
                text_groups[(str(layer.get("rol")), structural_keys)].append(
                    (slug, index, deepcopy(layer)))
        repeated.extend((slug, key, values) for key, values in _repeat_groups(row))

    operations: list[dict] = []
    for (role, structural_keys), examples in sorted(
            text_groups.items(), key=lambda item: (-len({x[0] for x in item[1]}), item[0])):
        source_slugs = sorted({example[0] for example in examples})
        if len(source_slugs) < 2:
            continue
        name = "text_layer_%s_v1" % _slug_part(role)
        layers = [(example[1], example[2]) for example in examples]
        constants = {key: examples[0][2].get(key) for key in structural_keys
                     if all(example[2].get(key) == examples[0][2].get(key)
                            for example in examples)}
        body = {"op": "layer", "fields": {
            **constants, "texto": "$texto",
        }}
        cost = _cost_for_fragment(layers[:1], name, "text_layer")
        cost["library_body_bytes"] = len(canonical(body))
        operations.append({
            "name": name,
            "version": 1,
            "kind": "text_layer",
            "matcher": {"kind": "text_layer", "constants": constants},
            "body": body,
            "source_examples": [{"slug": slug, "position": index}
                                 for slug, index, _ in examples],
            "support": {"records": len(examples), "distinct_slugs": len(source_slugs)},
            "declared_cost": cost,
            "uses": [],
            "expansion_contract": "expands to the observed text layer without dropping fields",
        })

    repeated_source_slugs = sorted({slug for slug, _, _ in repeated})
    if len(repeated_source_slugs) >= 2:
        name = "repeat_layer_group_v1"
        body = {
            "op": "repeat",
            "constant_fields": ["figura", "gesto"],
            "item_fields": "full_observed_layer",
            "position_field": "position",
        }
        all_layers = [(index, layer) for _, _, values in repeated for index, layer in values]
        example_calls = []
        for slug, key, values in repeated:
            example_calls.append({
                "slug": slug,
                "pattern": {"figura": key[0], "gesto": key[1]},
                "positions": [index for index, _ in values],
            })
        cost = _cost_for_fragment(all_layers[:2], name, "repeat_layer_group")
        cost["library_body_bytes"] = len(canonical(body))
        operations.append({
            "name": name,
            "version": 1,
            "kind": "repeat_layer_group",
            "matcher": {"kind": "repeated_layer_group", "minimum_count": 2,
                         "constant_fields": ["figura", "gesto"]},
            "body": body,
            "source_examples": example_calls,
            "support": {"records": len(repeated), "distinct_slugs": len(repeated_source_slugs)},
            "declared_cost": cost,
            "uses": [],
            "expansion_contract": "expands to every observed layer at its original position",
        })

    return {
        "library_version": "semantic-icons-v1-inferred-v1",
        "language": LANGUAGE,
        "source_partition": "construction",
        "discovery_method": "invariant-template-inference-from-repeated-fragments-v1",
        "operations": operations,
        "initial_vocabulary": {
            "primitive_program": "icon(header, ordered layer nodes)",
            "layer_fields": sorted({key for row in rows for layer in row.get("capas", [])
                                    for key in layer}),
            "interpreter_operations": [
                "algebra.sustituir", "algebra.transferir_estilo",
                "algebra.interpolar", "algebra.distancia",
            ],
            "discovered_operation_count_before_learning": 0,
        },
        "inference_trace": {
            "input_records": [str(row["slug"]) for row in rows],
            "text_group_count": len(text_groups),
            "repeated_group_count": len(repeated),
            "threshold": "at least two distinct construction slugs",
        },
        "limits": [
            "the closed semantic vocabulary is inherited from semantic-icons-v1",
            "development and final_reserved are not used to infer or retune operations",
            "support is frequency evidence, not open-world grammar coverage",
        ],
    }


def _operation_by_name(library: dict) -> dict[str, dict]:
    return {str(operation["name"]): operation
            for operation in library.get("operations", [])}


def _matches_constants(layer: dict, constants: dict) -> bool:
    return all(layer.get(key) == value for key, value in constants.items())


def compress_program(spec: dict, library: dict) -> dict:
    operations = _operation_by_name(library)
    layers = list(enumerate(deepcopy(spec.get("capas", []))))
    consumed: set[int] = set()
    parts: list[dict] = []
    text_ops = [op for op in operations.values() if op.get("kind") == "text_layer"]
    for index, layer in layers:
        if layer.get("texto") is None or layer.get("figura"):
            continue
        operation = next((op for op in text_ops
                          if _matches_constants(layer, op.get("matcher", {}).get("constants", {}))),
                         None)
        if operation is None:
            continue
        parts.append({"position": index, "node": {
            "op": "call", "name": operation["name"],
            "args": {"layer": deepcopy(layer)},
        }})
        consumed.add(index)

    repeat_op = next((op for op in operations.values()
                      if op.get("kind") == "repeat_layer_group"), None)
    if repeat_op is not None:
        for (figure, gesture), values in _repeat_groups(spec):
            if any(index in consumed for index, _ in values):
                continue
            parts.append({"position": min(index for index, _ in values), "node": {
                "op": "call", "name": repeat_op["name"],
                "args": {
                    "constant_fields": ["figura", "gesto"],
                    "figure": figure,
                    "gesture": gesture,
                    "items": [{"position": index, "layer": deepcopy(layer)}
                              for index, layer in values],
                },
            }})
            consumed.update(index for index, _ in values)

    parts.extend(
        {"position": index, "node": {"op": "layer", "layer": layer}}
        for index, layer in layers if index not in consumed
    )
    parts.sort(key=lambda part: int(part["position"]))
    return {
        "language": LANGUAGE,
        "program_version": EXPERIMENT_VERSION,
        "op": "icon",
        "header": _header_for(spec),
        "parts": parts,
    }


def expand_program(program: dict, library: dict) -> dict:
    operations = _operation_by_name(library)
    output = deepcopy(program.get("header") or {})
    layers: list[tuple[int, dict]] = []
    for part in program.get("parts", []):
        position = int(part["position"])
        node = part.get("node") or {}
        if node.get("op") == "layer":
            layers.append((position, deepcopy(node["layer"])))
            continue
        if node.get("op") != "call" or str(node.get("name")) not in operations:
            raise GrammarRunError(f"nodo de programa no soportado: {node}")
        operation = operations[str(node["name"])]
        args = node.get("args") or {}
        if operation.get("kind") == "text_layer":
            layers.append((position, deepcopy(args["layer"])))
        elif operation.get("kind") == "repeat_layer_group":
            for item in args.get("items", []):
                layers.append((int(item["position"]), deepcopy(item["layer"])))
        else:
            raise GrammarRunError(f"tipo de operación no expandible: {operation}")
    output["capas"] = [layer for _, layer in sorted(layers, key=lambda pair: pair[0])]
    return output


def _semantic_payload(spec: dict) -> dict:
    return {key: deepcopy(value) for key, value in spec.items()
            if key not in {"slug", "titulo", "brief"}}


def behavior_hash(spec: dict) -> str:
    return digest(_semantic_payload(spec))


def _descriptor(spec: dict, semantic: dict) -> list[int]:
    composition_names = sorted(semantic["composiciones"])
    figure_names = sorted(semantic["figuras"])
    figure_layers = [layer for layer in spec.get("capas", []) if layer.get("figura")]
    return [
        composition_names.index(spec["composicion"]),
        len(spec.get("capas", [])),
        sum(1 for layer in spec.get("capas", []) if layer.get("texto") is not None),
        sum(1 for layer in spec.get("capas", [])
            if layer.get("gesto", "quieto") != "quieto"),
        len({layer.get("figura") for layer in figure_layers}),
        len(_repeat_groups(spec)),
        sum(figure_names.index(layer["figura"]) for layer in figure_layers),
    ]


def program_stats(program: dict, target: dict, library: dict, semantic: dict) -> dict:
    expanded = expand_program(program, library)
    parts = program.get("parts", [])
    calls = [part["node"] for part in parts if part.get("node", {}).get("op") == "call"]
    direct = [part["node"] for part in parts if part.get("node", {}).get("op") == "layer"]
    return {
        "program_bytes": len(canonical(program)),
        "residue_bytes": len(canonical(direct)),
        "direct_layer_nodes": len(direct),
        "library_calls": [str(call.get("name")) for call in calls],
        "library_call_count": len(calls),
        "expanded_exact": expanded == target,
        "observation_hash": digest(expanded),
        "behavior_hash": behavior_hash(expanded),
        "descriptor": _descriptor(expanded, semantic),
    }


def _candidate_summary(candidate: dict) -> dict:
    return {key: deepcopy(candidate[key]) for key in (
        "candidate_id", "generation", "partition", "role", "source_slugs",
        "operations_used", "program_path", "svg_path", "render_status",
        "valid_input", "validation_errors", "stats",
    )}


def _make_candidate(spec: dict, *, candidate_id: str, generation: int,
                    partition: str, role: str, source_slugs: list[str],
                    operations_used: list[str], library: dict, semantic: dict,
                    output: Path, source_path: str) -> dict:
    candidate_id = _safe_name(candidate_id)
    errors = list(semantic["validar_spec"](spec))
    valid_input = not errors
    program = (compress_program(spec, library)
               if "learned" in role or role == "composed"
               else direct_program(spec))
    stats = None
    svg_path = None
    render_status = "not_rendered_invalid_input"
    render_error = None
    warnings: list[str] = []
    if valid_input:
        stats = program_stats(program, spec, library, semantic)
        expanded = expand_program(program, library)
        try:
            svg, warnings = semantic["compilar"](expanded, slug=candidate_id)
        except Exception as exc:  # compiler failure is recorded, not hidden
            render_status = "render_failed"
            render_error = str(exc)
        else:
            svg_rel = Path("svg") / f"{candidate_id}.svg"
            svg_abs = output / svg_rel
            svg_abs.parent.mkdir(parents=True, exist_ok=True)
            svg_abs.write_text(svg, encoding="utf-8")
            svg_path = svg_rel.as_posix()
            render_status = "rendered"
    calls = stats["library_calls"] if stats else []
    combined_ops = list(dict.fromkeys([*operations_used, *calls]))
    program_rel = Path("programs") / f"{candidate_id}.json"
    record = {
        "schema": "mak-grammar-candidate-v1",
        "candidate_id": candidate_id,
        "generation": generation,
        "partition": partition,
        "role": role,
        "source_slugs": list(source_slugs),
        "observation": {
            "slug": str(spec.get("slug")),
            "stable_ref": f"{source_path}#{spec.get('slug')}",
            "source_group": partition,
            "evidence_state": "validator_rejected_exception" if not valid_input
            else "validator_accepted",
        },
        "valid_input": valid_input,
        "validation_errors": errors,
        "operations_used": combined_ops,
        "program": program,
        "stats": stats,
        "svg_path": svg_path,
        "render_status": render_status,
        "render_error": render_error,
        "compiler_warnings": warnings,
    }
    _write_json(output / program_rel, record)
    record["program_path"] = program_rel.as_posix()
    return record


def _proposals_for_generation(context: dict, generation: int,
                              seed: int) -> list[dict]:
    construction = context["partitions"]["construction"]
    development = context["partitions"]["development"]
    reserved = context["partitions"]["final_reserved"]
    semantic = context["semantic"]
    algebra = semantic["algebra"]
    proposals: list[dict] = []
    if generation == 0:
        for row in construction:
            slug = str(row["slug"])
            proposals.extend([
                {"spec": row, "candidate_id": f"g00-{slug}-direct",
                 "partition": "construction", "role": "initial_direct", "ops": []},
                {"spec": row, "candidate_id": f"g00-{slug}-learned",
                 "partition": "construction", "role": "initial_learned", "ops": []},
            ])
    elif generation == 1:
        for row in development:
            slug = str(row["slug"])
            proposals.extend([
                {"spec": row, "candidate_id": f"g01-{slug}-direct",
                 "partition": "development", "role": "development_direct", "ops": []},
                {"spec": row, "candidate_id": f"g01-{slug}-learned",
                 "partition": "development", "role": "development_learned", "ops": []},
            ])
    elif generation == 2:
        for index, row in enumerate(development):
            source = str(row["slug"])
            style = construction[(index + seed) % len(construction)]
            transferred = algebra.transferir_estilo(row, style)
            transferred["slug"] = f"{source}-style-{style['slug']}"
            transferred["titulo"] = f"{row.get('titulo', source)} · composition"
            proposals.append({
                "spec": transferred,
                "candidate_id": f"g02-{source}-transfer-style",
                "partition": "development",
                "role": "composed",
                "ops": ["algebra.transferir_estilo"],
            })
            donor_figures = [layer.get("figura") for layer in style.get("capas", [])
                             if layer.get("figura")]
            target_figures = [layer.get("figura") for layer in row.get("capas", [])
                              if layer.get("figura")]
            if donor_figures and target_figures:
                substituted = algebra.sustituir(row, target_figures[0], donor_figures[0])
                substituted["slug"] = f"{source}-substitute-{donor_figures[0]}"
                substituted["titulo"] = f"{row.get('titulo', source)} · substitution"
                if not semantic["validar_spec"](substituted):
                    proposals.append({
                        "spec": substituted,
                        "candidate_id": f"g02-{source}-substitute",
                        "partition": "development",
                        "role": "composed",
                        "ops": ["algebra.sustituir"],
                    })
        # Reserved material is evaluated only after the library is frozen.
        for row in reserved:
            slug = str(row["slug"])
            proposals.extend([
                {"spec": row, "candidate_id": f"g02-heldout-{slug}-direct",
                 "partition": "final_reserved", "role": "heldout_evaluation", "ops": []},
                {"spec": row, "candidate_id": f"g02-heldout-{slug}-learned",
                 "partition": "final_reserved", "role": "heldout_evaluation_learned", "ops": []},
            ])
    return proposals


def _append_uses(library: dict, records: Iterable[dict]) -> None:
    by_name = _operation_by_name(library)
    for record in records:
        for name in record.get("operations_used", []):
            operation = by_name.get(name)
            if operation is None:
                continue
            uses = operation.setdefault("uses", [])
            if record["candidate_id"] not in uses:
                uses.append(record["candidate_id"])
            uses.sort()


def _evaluate_condition(rows: list[dict], condition: str, library: dict,
                        context: dict) -> dict:
    records = []
    for row in rows:
        valid = context["validity"][str(row["slug"])]
        program = (direct_program(row) if condition == "initial"
                   else compress_program(row, library))
        if not valid["valid"]:
            records.append({"slug": row["slug"], "valid_input": False,
                            "validation_errors": valid["errors"], "stats": None})
            continue
        stats = program_stats(program, row, library, context["semantic"])
        records.append({"slug": row["slug"], "valid_input": True, "stats": stats})
    valid_records = [record for record in records if record["valid_input"]]
    return {
        "condition": condition,
        "records": records,
        "valid_input_count": len(valid_records),
        "expanded_exact_count": sum(record["stats"]["expanded_exact"]
                                    for record in valid_records),
        "reuse_count": sum(record["stats"]["library_call_count"] > 0
                           for record in valid_records),
        "total_program_bytes": sum(record["stats"]["program_bytes"]
                                   for record in valid_records),
        "total_residue_bytes": sum(record["stats"]["residue_bytes"]
                                   for record in valid_records),
        "effective_behavior_count": len({record["stats"]["behavior_hash"]
                                         for record in valid_records}),
    }


def _partition_for_slug(context: dict, slug: str) -> str:
    for name, rows in context["partitions"].items():
        if any(str(row["slug"]) == slug for row in rows):
            return name
    return "unknown"


def _metrics(context: dict, library: dict, candidates: list[dict],
             state: dict) -> dict:
    comparison_rows = (context["partitions"]["construction"]
                       + context["partitions"]["development"])
    initial = _evaluate_condition(comparison_rows, "initial", library, context)
    expanded = _evaluate_condition(comparison_rows, "expanded", library, context)
    reserved = _evaluate_condition(context["partitions"]["final_reserved"],
                                   "expanded", library, context)
    valid_reserved = [
        row for row in context["partitions"]["final_reserved"]
        if context["validity"][str(row["slug"])]["valid"]
    ]
    library_bytes = len(canonical(library))
    return {
        "schema": "mak-grammar-metrics-v1",
        "experiment_version": EXPERIMENT_VERSION,
        "status": state["status"],
        "current_generation": state["current_generation"],
        "completed_generations": list(state["completed_generations"]),
        "contract": {
            "manifest": context["manifest_path"],
            "source": context["source_path"],
            "source_sha256": context["source_sha256"],
            "manifest_source_revision": context["source_revision"],
            "current_git_revision": context["current_git_revision"],
        },
        "observations": [
            {"slug": str(row["slug"]),
             "partition": _partition_for_slug(context, str(row["slug"])),
             "valid": context["validity"][str(row["slug"])]["valid"],
             "behavior_hash": digest(_semantic_payload(row)),
             "evidence_state": (
                 "validator_rejected_exception"
                 if not context["validity"][str(row["slug"])]["valid"]
                 else "validator_accepted"
             )}
            for row in context["rows"]
        ],
        "vocabulary_comparison": {
            "same_resources": [str(row["slug"]) for row in comparison_rows],
            "initial": {**initial, "library_bytes": 0, "operation_count": 0},
            "expanded": {
                **expanded,
                "library_bytes": library_bytes,
                "operation_count": len(library.get("operations", [])),
                "library_plus_program_bytes": (
                    library_bytes + expanded["total_program_bytes"]
                ),
            },
            "interpretation": (
                "la biblioteca conserva y reutiliza estructuras observadas; en "
                "este lote pequeño su coste compartido puede superar el ahorro "
                "sintáctico"
            ),
        },
        "final_reserved_evaluation": {
            "library_frozen_from": "construction",
            "retuning": False,
            "valid_records_expected": len(valid_reserved),
            "invalid_records_preserved": [
                row["slug"] for row in context["partitions"]["final_reserved"]
                if not context["validity"][str(row["slug"])]["valid"]
            ],
            "expanded": {
                **reserved,
                "library_bytes": library_bytes,
                "operation_count": len(library.get("operations", [])),
            },
            "limitation": (
                "no es evidencia de transferencia entre formatos ni de "
                "autoría independiente"
            ),
        },
        "candidate_count": len(candidates),
        "candidate_summaries": [_candidate_summary(candidate)
                                for candidate in candidates],
        "limits": [
            "una única interfaz ejecutable: semantic-icons-v1",
            "la reserva no participa en descubrimiento ni ajuste",
            "el descriptor numérico mide comportamiento observado y no cobertura abierta",
            "una operación reutilizada no implica significado artístico certificado",
        ],
    }


def _write_index(output: Path, context: dict, library: dict,
                 metrics: dict) -> None:
    input_rows = []
    for row in context["rows"]:
        slug = str(row["slug"])
        validity = context["validity"][slug]
        partition = _partition_for_slug(context, slug)
        state = "válida" if validity["valid"] else "excepción preservada"
        detail = "" if validity["valid"] else "; ".join(validity["errors"])
        input_rows.append(
            f"<tr><td><code>{html.escape(slug)}</code></td>"
            f"<td>{html.escape(partition)}</td><td>{state}</td>"
            f"<td>{html.escape(detail)}</td></tr>"
        )
    cards = []
    for candidate in metrics.get("candidate_summaries", []):
        if candidate.get("svg_path"):
            visual = (
                f'<img src="{html.escape(candidate["svg_path"])}" '
                f'alt="{html.escape(candidate["candidate_id"])}">'
            )
        else:
            visual = (
                '<div class="no-svg">sin SVG: entrada rechazada por '
                "el intérprete</div>"
            )
        cards.append(f"""
        <article class="card">
          <div class="visual">{visual}</div>
          <h3>{html.escape(candidate["candidate_id"])}</h3>
          <p>{html.escape(candidate["partition"])} ·
             {html.escape(candidate["role"])} · generación {candidate["generation"]}</p>
          <p>entrada: <code>{html.escape(", ".join(candidate.get("source_slugs") or ["—"]))}</code></p>
          <p>operaciones: <code>{html.escape(", ".join(
              candidate.get("operations_used") or ["—"]))}</code></p>
          <p>render: {html.escape(candidate.get("render_status") or "—")}</p>
          <details><summary>programa y medidas</summary>
            <p><a href="{html.escape(candidate["program_path"])}">
              abrir JSON del candidato</a></p>
            <pre>{html.escape(json.dumps(candidate.get("stats"),
                                          ensure_ascii=False, indent=2))}</pre>
          </details>
        </article>""")
    operations = []
    for operation in library.get("operations", []):
        operations.append(f"""
        <tr><td><code>{html.escape(operation["name"])}</code></td>
        <td>{html.escape(str(operation.get("kind")))}</td>
        <td>{operation.get("support", {}).get("distinct_slugs", 0)}</td>
        <td>{len(operation.get("uses") or [])}</td>
        <td><code>{html.escape(json.dumps(operation.get("body"),
                                             ensure_ascii=False))}</code></td></tr>""")
    status = html.escape(str(metrics.get("status")))
    checkpoint = html.escape(str(output / "checkpoint.json"))
    body = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Grammar run</title>
<style>
body{{font-family:system-ui,sans-serif;background:#101014;color:#eee;
max-width:1320px;margin:2rem auto;padding:0 1rem}}
h1,h2{{color:#f2cf65}} a{{color:#8ed8ff}}
code,pre{{font-family:ui-monospace,monospace}}
pre{{white-space:pre-wrap;background:#181820;padding:.75rem;border-radius:.5rem;
font-size:.78rem}}
.meta{{background:#181820;padding:1rem;border-radius:.6rem;line-height:1.6}}
table{{width:100%;border-collapse:collapse;margin:1rem 0}}
th,td{{border-bottom:1px solid #333;padding:.5rem;text-align:left;vertical-align:top}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}}
.card{{background:#181820;border:1px solid #333;border-radius:.6rem;padding:.8rem}}
.visual{{min-height:160px;display:grid;place-items:center;background:#0b0b0e}}
.visual img{{width:160px;height:160px}}
.no-svg{{color:#f59b9b;padding:2rem;text-align:center}}
summary{{cursor:pointer;color:#8ed8ff}}
</style></head><body>
<h1>MAK grammar · {status}</h1>
<div class="meta"><b>Corpus:</b> {html.escape(context["source_path"])}<br>
<b>SHA-256:</b> <code>{html.escape(context["source_sha256"])}</code><br>
<b>Generaciones:</b> {metrics.get("completed_generations")} ·
<b>candidatos:</b> {metrics.get("candidate_count")}<br>
<b>Biblioteca:</b> {len(library.get("operations", []))}
operaciones inferidas; la reserva queda congelada.</div>
<h2>Comparación de vocabulario</h2>
<pre>{html.escape(json.dumps(metrics.get("vocabulary_comparison"),
                             ensure_ascii=False, indent=2))}</pre>
<h2>Entradas del corpus</h2>
<table><thead><tr><th>slug</th><th>partición</th><th>estado</th>
<th>detalle</th></tr></thead><tbody>{"".join(input_rows)}</tbody></table>
<h2>Operaciones descubiertas y reutilizadas</h2>
<table><thead><tr><th>operación</th><th>tipo</th><th>soporte</th>
<th>usos</th><th>cuerpo</th></tr></thead><tbody>
{"".join(operations) or '<tr><td colspan="5">biblioteca vacía</td></tr>'}
</tbody></table>
<h2>Entradas y composiciones visibles</h2>
<section class="grid">{"".join(cards) or "<p>todavía no hay candidatos</p>"}</section>
<h2>Control</h2>
<p>Estado: <code>{status}</code>. Para inspeccionar:
<code>MAK grammar status --checkpoint {checkpoint}</code>.
Para detener entre generaciones:
<code>MAK grammar stop --checkpoint {checkpoint}</code>.
Para continuar:
<code>MAK grammar resume --checkpoint {checkpoint}</code>.</p>
</body></html>"""
    (output / "index.html").write_text(body, encoding="utf-8")


def _new_state(context: dict, output: Path, generations: int, seed: int,
               max_candidates: int, run_id: str) -> dict:
    return {
        "schema": RUN_SCHEMA,
        "experiment_version": EXPERIMENT_VERSION,
        "run_id": run_id,
        "created_at": _now(),
        "updated_at": _now(),
        "status": "running",
        "manifest_path": context["manifest_path"],
        "source_path": context["source_path"],
        "source_sha256": context["source_sha256"],
        "source_revision": context["source_revision"],
        "current_git_revision": context["current_git_revision"],
        "seed": int(seed),
        "requested_generations": int(generations),
        "max_candidates": int(max_candidates),
        "output_dir": str(output),
        "current_generation": -1,
        "next_generation": 0,
        "completed_generations": [],
        "candidate_count": 0,
        "candidate_summaries": [],
        "conductor_stage": CONDUCTOR_STAGE,
        "conductor_db": str(output / "conductor.db"),
        "conductor_jobs": {},
        "library_ref": str(output / "library.json"),
        "metrics_ref": str(output / "metrics.json"),
        "index_ref": str(output / "index.html"),
        "checkpoint_ref": str(output / "checkpoint.json"),
    }


def _persist(output: Path, state: dict, library: dict, context: dict,
             candidates: list[dict]) -> None:
    state["updated_at"] = _now()
    state["candidate_count"] = len(candidates)
    state["candidate_summaries"] = [
        _candidate_summary(candidate) for candidate in candidates
    ]
    _write_json(output / "library.json", library)
    metrics = _metrics(context, library, candidates, state)
    _write_json(output / "metrics.json", metrics)
    _write_index(output, context, library, metrics)
    _write_json(output / "checkpoint.json", state)


def _load_state(checkpoint: Path) -> dict:
    try:
        state = json.loads(checkpoint.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GrammarRunError(f"checkpoint inválido: {checkpoint}: {exc}") from exc
    if state.get("schema") != RUN_SCHEMA:
        raise GrammarRunError("checkpoint de otra versión de MAK grammar")
    return state


def _load_candidates(output: Path, state: dict) -> list[dict]:
    candidates = []
    for summary in state.get("candidate_summaries", []):
        path = output / str(summary["program_path"])
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise GrammarRunError(f"candidato perdido o inválido: {path}: {exc}") from exc
        candidate["program_path"] = str(summary["program_path"])
        candidates.append(candidate)
    return candidates


def _conductor_parts(output: Path):
    del output
    configured_root = os.environ.get("MAK_REPO_ROOT", "").strip()
    candidates = [Path(configured_root).expanduser()] if configured_root else []
    candidates.append(Path(__file__).resolve().parents[2])
    root = next(
        (candidate / "cultura" for candidate in candidates
         if (candidate / "cultura" / "mak_conductor").is_dir()),
        None,
    )
    if root is None:
        raise GrammarRunError(
            "no se encontró el Conductor de MAK; configura MAK_REPO_ROOT "
            "con la raíz del checkout"
        )
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from mak_conductor.conductor import Conductor
        from mak_conductor.gpu_arbiter import GpuArbiter
        from mak_conductor.queue_store import QueueStore
    except ImportError as exc:  # pragma: no cover - machine configuration
        raise GrammarRunError(f"no se pudo cargar el Conductor de MAK: {exc}") from exc
    return Conductor, GpuArbiter, QueueStore


def _dispatch_generation(output: Path, state: dict, context: dict,
                         library: dict, candidates: list[dict],
                         generation: int) -> list[dict]:
    Conductor, GpuArbiter, QueueStore = _conductor_parts(output)
    store = QueueStore(Path(state["conductor_db"]))
    key = f"{state['run_id']}:generation:{generation}"
    job = store.enqueue(
        CONDUCTOR_STAGE,
        {"run_id": state["run_id"], "generation": generation,
         "experiment_version": EXPERIMENT_VERSION, "seed": state["seed"]},
        idempotency_key=key, template_version=EXPERIMENT_VERSION,
    )
    job_id = str(job["job_id"])
    state["conductor_jobs"][str(generation)] = {
        "job_id": job_id, "status": str(job.get("status")),
        "idempotency_key": key,
    }

    def handler(_job: dict) -> dict:
        proposals = _proposals_for_generation(context, generation, state["seed"])
        remaining = max(0, int(state["max_candidates"]) - len(candidates))
        selected = proposals[:remaining]
        made = []
        for proposal in selected:
            record = _make_candidate(
                proposal["spec"], candidate_id=proposal["candidate_id"],
                generation=generation, partition=proposal["partition"],
                role=proposal["role"],
                source_slugs=[str(proposal["spec"].get("slug"))],
                operations_used=proposal["ops"], library=library,
                semantic=context["semantic"], output=output,
                source_path=context["source_path"],
            )
            made.append(record)
        summary = [_candidate_summary(record) for record in made]
        return {
            "validated": True,
            "generation": generation,
            "candidate_summaries": summary,
            "proposals_seen": len(proposals),
            "candidates_written": len(made),
            "artifacts": [{
                "kind": "grammar_generation_summary",
                "content": json.dumps(summary, ensure_ascii=False),
            }],
        }

    conductor = Conductor(
        store, GpuArbiter(output / "conductor-gpu.lock", capacity_mb=4096),
        worker_id=f"grammar-{state['run_id']}-{os.getpid()}",
        lease_seconds=60.0,
    )
    result = conductor.dispatch_once(handler, stages=[CONDUCTOR_STAGE],
                                     job_id=job_id)
    final_job = store.get_job(job_id) or {}
    state["conductor_jobs"][str(generation)]["status"] = str(
        final_job.get("status") or (result or {}).get("status")
    )
    if final_job.get("status") == "COMPLETED" and result is None:
        result = store.get_result(job_id) or {}
    if (final_job.get("status") != "COMPLETED"
            or not result or not result.get("validated")):
        raise GrammarRunError(
            f"Conductor no completó la generación {generation}: "
            f"{result or final_job}"
        )
    for summary in result.get("candidate_summaries") or []:
        path = output / str(summary["program_path"])
        candidate = json.loads(path.read_text(encoding="utf-8"))
        candidate["program_path"] = str(summary["program_path"])
        candidates.append(candidate)
    return candidates


def _stop_requested(output: Path) -> bool:
    return (output / STOP_FILE).is_file()


def _continue(context: dict, state: dict, library: dict,
              candidates: list[dict], *,
              stop_after_generation: int | None = None) -> dict:
    output = Path(state["output_dir"])
    start = int(state.get("next_generation", 0))
    total = int(state["requested_generations"])
    if state.get("status") == "completed" or start >= total:
        state["status"] = "completed"
        _persist(output, state, library, context, candidates)
        return {
            "ok": True, "status": state["status"],
            "checkpoint": str(output / "checkpoint.json"),
            "index": str(output / "index.html"),
            "candidate_count": len(candidates),
        }
    for generation in range(start, total):
        if _stop_requested(output):
            state["status"] = "stopped"
            _persist(output, state, library, context, candidates)
            return {
                "ok": True, "status": "stopped",
                "next_generation": generation,
                "checkpoint": str(output / "checkpoint.json"),
            }
        candidates = _dispatch_generation(
            output, state, context, library, candidates, generation
        )
        _append_uses(library, candidates)
        state["current_generation"] = generation
        state["next_generation"] = generation + 1
        state["completed_generations"] = sorted(
            set(state["completed_generations"] + [generation])
        )
        state["status"] = "running"
        _persist(output, state, library, context, candidates)
        if stop_after_generation == generation:
            state["status"] = "stopped"
            _persist(output, state, library, context, candidates)
            return {
                "ok": True, "status": "stopped",
                "next_generation": generation + 1,
                "checkpoint": str(output / "checkpoint.json"),
                "candidate_count": len(candidates),
            }
    state["status"] = "completed"
    _persist(output, state, library, context, candidates)
    return {
        "ok": True, "status": "completed",
        "checkpoint": str(output / "checkpoint.json"),
        "index": str(output / "index.html"),
        "candidate_count": len(candidates),
        "completed_generations": state["completed_generations"],
    }


def run_experiment(*, corpus: str | os.PathLike[str], generations: int,
                   seed: int, max_candidates: int,
                   output: str | os.PathLike[str],
                   run_id: str | None = None,
                   stop_after_generation: int | None = None) -> dict:
    """Run a new experiment, refusing to overwrite an existing run."""
    if generations < 1 or generations > 3:
        raise GrammarRunError("--generations debe estar entre 1 y 3")
    if max_candidates < 1 or max_candidates > 200:
        raise GrammarRunError("--max-candidates debe estar entre 1 y 200")
    if (stop_after_generation is not None
            and not 0 <= stop_after_generation < generations):
        raise GrammarRunError(
            "--stop-after-generation debe ser una generación del run"
        )
    context = load_contract(corpus)
    output_path = Path(output).expanduser().resolve()
    checkpoint = output_path / "checkpoint.json"
    if checkpoint.exists():
        raise GrammarRunError(
            f"el run ya existe en {output_path}; usa MAK grammar resume "
            f"--checkpoint {checkpoint} o elige otro directorio"
        )
    output_path.mkdir(parents=True, exist_ok=True)
    for dirname in ("svg", "programs"):
        (output_path / dirname).mkdir(exist_ok=True)
    run_id = run_id or (
        f"grammar-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    library = discover_library(context["partitions"]["construction"])
    state = _new_state(
        context, output_path, generations, seed, max_candidates, run_id
    )
    candidates: list[dict] = []
    _persist(output_path, state, library, context, candidates)
    return _continue(
        context, state, library, candidates,
        stop_after_generation=stop_after_generation,
    )


def resume_experiment(checkpoint: str | os.PathLike[str]) -> dict:
    """Continue the exact run represented by a checkpoint."""
    checkpoint_path = Path(checkpoint).expanduser().resolve()
    state = _load_state(checkpoint_path)
    output = Path(state["output_dir"]).expanduser().resolve()
    stop_file = output / STOP_FILE
    if stop_file.exists():
        stop_file.unlink()
    context = load_contract(state["manifest_path"])
    if context["source_sha256"] != state.get("source_sha256"):
        raise GrammarRunError(
            "corpus_changed: el checkpoint no puede continuar este corpus"
        )
    try:
        library = json.loads(
            (output / "library.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
        raise GrammarRunError(
            f"biblioteca ausente o inválida: {output / 'library.json'}: {exc}"
        ) from exc
    candidates = _load_candidates(output, state)
    state["status"] = "running"
    return _continue(context, state, library, candidates)


def status_experiment(checkpoint: str | os.PathLike[str]) -> dict:
    checkpoint_path = Path(checkpoint).expanduser().resolve()
    state = _load_state(checkpoint_path)
    return {
        "ok": True,
        "status": state.get("status"),
        "run_id": state.get("run_id"),
        "current_generation": state.get("current_generation"),
        "next_generation": state.get("next_generation"),
        "requested_generations": state.get("requested_generations"),
        "completed_generations": state.get("completed_generations", []),
        "candidate_count": state.get("candidate_count", 0),
        "output_dir": state.get("output_dir"),
        "index": state.get("index_ref"),
        "conductor_jobs": state.get("conductor_jobs", {}),
    }


def stop_experiment(checkpoint: str | os.PathLike[str]) -> dict:
    checkpoint_path = Path(checkpoint).expanduser().resolve()
    state = _load_state(checkpoint_path)
    output = Path(state["output_dir"]).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    stop_file = output / STOP_FILE
    stop_file.write_text(
        "stop requested at %s; resume with MAK grammar resume "
        "--checkpoint checkpoint.json\n" % _now(),
        encoding="utf-8",
    )
    state["status"] = "stop_requested"
    state["updated_at"] = _now()
    _write_json(checkpoint_path, state)
    return {
        "ok": True,
        "status": "stop_requested",
        "stop_file": str(stop_file),
        "checkpoint": str(checkpoint_path),
    }
