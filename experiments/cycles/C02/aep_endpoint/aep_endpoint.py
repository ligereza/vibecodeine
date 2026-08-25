"""Isolated, read-only C02 endpoint for an After Effects project.

The native project is read through ``flujo.substrate.aepfile``.  Local path
resolution is deliberately narrower than a directory scan: for each declared
Windows path the adapter probes one explicitly mapped basename, or an explicit
candidate list supplied by a caller/test.  Existence and basename agreement
produce a candidate only.  They never establish that a file is an output.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence


CONTRACT = "mak-cycle-c02-aep-observation-v1"
ADAPTER_VERSION = "aep-endpoint-1.0"
EXPECTED_SHA256 = "99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460"
PUBLIC_CATALOG_STATUS = "unavailable"
PUBLIC_JOIN_STATUS = "unknown"
MISSING_EVIDENCE = "MISSING_EVIDENCE"


def _load_flujo_api() -> Any:
    """Import the existing API without importing After Effects or extra code."""

    try:
        from flujo.substrate.aepfile import read_references
    except ModuleNotFoundError as exc:  # pragma: no cover - CLI setup failure
        raise RuntimeError(
            "flujo_api_unavailable: set PYTHONPATH=/home/mak/flujo/src"
        ) from exc
    return read_references


def sha256_file(path: Path) -> str:
    """Hash exactly one input file, in bounded chunks, without writing it."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _windows_basename(declared_path: str) -> str:
    return PureWindowsPath(declared_path).name


def _probe(path: Path, basename: str) -> dict[str, Any]:
    """Record only direct filesystem evidence for one explicitly named path."""

    return {
        "path": str(path),
        "basename": path.name,
        "basename_matches": path.name == basename,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }


def _candidate_probes(
    declared_path: str,
    target_is_folder: bool,
    local_root: Path,
    explicit_candidates: Iterable[str | Path] | None,
) -> list[dict[str, Any]]:
    basename = _windows_basename(declared_path)
    if explicit_candidates is None:
        # C:\ARICA\name is mapped to local_root/name.  A declared C:\ARICA
        # folder is mapped to local_root itself.  Neither branch enumerates the
        # local root or follows children.
        target = local_root if target_is_folder else local_root / basename
        return [_probe(target, basename if not target_is_folder else target.name)]

    probes = []
    for raw_path in explicit_candidates:
        path = Path(raw_path)
        if path.name == basename:
            probes.append(_probe(path, basename))
    return probes


def resolve_declared_path(
    record: Mapping[str, Any],
    local_root: str | Path,
    explicit_candidates: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    """Resolve one declaration to a local candidate without deciding output.

    ``explicit_candidates`` exists for callers that already possess a bounded
    candidate list.  It is not a permission to discover files by scanning.
    """

    declared_path = str(record["declared_path"])
    target_is_folder = bool(record.get("target_is_folder"))
    basename = _windows_basename(declared_path)
    probes = _candidate_probes(
        declared_path,
        target_is_folder,
        Path(local_root),
        explicit_candidates,
    )
    existing = [probe for probe in probes if probe["exists"]]
    existing_files = [probe for probe in existing if probe["is_file"]]
    existing_dirs = [probe for probe in existing if probe["is_dir"]]

    if len(existing) > 1:
        resolution_status = "ambiguous"
        classification = "candidate"
        cause = None
    elif len(existing) == 1:
        resolution_status = "candidate"
        classification = "candidate"
        cause = None
    else:
        resolution_status = "unknown"
        classification = "unknown"
        cause = MISSING_EVIDENCE

    if target_is_folder and existing_dirs:
        local_kind = "folder"
    elif existing_files:
        local_kind = "file"
    elif existing_dirs:
        local_kind = "folder_mismatch_for_file_declaration"
    else:
        local_kind = "absent"

    return {
        "observation_status": "observed",
        "aep_record": dict(record),
        "declared_path": declared_path,
        "declared_basename": basename,
        "declared_target_is_folder": target_is_folder,
        "local_resolution": {
            "status": resolution_status,
            "classification": classification,
            "cause": cause,
            "local_kind": local_kind,
            "candidate_count": len(existing),
            "candidate_paths": [probe["path"] for probe in existing],
            "evidence": {
                "existence_checked": True,
                "basename_checked": True,
                "probes": probes,
            },
        },
        "output_claim": {
            "status": "unknown",
            "reason": "existence_and_basename_do_not_prove_output_role",
        },
    }


def build_observation(
    input_path: str | Path,
    local_root: str | Path,
    expected_sha256: str = EXPECTED_SHA256,
) -> dict[str, Any]:
    """Read the AEP with the existing API and build a JSON-safe observation."""

    source = Path(input_path)
    root = Path(local_root)
    actual_sha256 = sha256_file(source)
    read_references = _load_flujo_api()
    parsed = read_references(source)

    references = [
        resolve_declared_path(record, root)
        for record in parsed.declared
    ]
    return {
        "schema": CONTRACT,
        "adapter_version": ADAPTER_VERSION,
        "read_policy": {
            "after_effects_opened": False,
            "input_written": False,
            "renders_requested": False,
            "recursive_local_scan": False,
        },
        "input": {
            "path": str(source),
            "expected_sha256": expected_sha256,
            "actual_sha256": actual_sha256,
            "hash_status": "PASS" if actual_sha256 == expected_sha256 else "FAIL",
        },
        "aep_reader": {
            "contract": "mak-aepfile-v1",
            "completeness": parsed.completeness,
            "error": parsed.error,
            "truncated": parsed.truncated,
            "chunks_seen": parsed.chunks_seen,
            "header": None
            if parsed.header is None
            else {
                "declared_size": parsed.header.declared_size,
                "form": parsed.header.form,
                "trailing_bytes": parsed.header.trailing_bytes,
            },
            "declared_reference_count": len(parsed.declared),
        },
        "local_resolution": {
            "root": str(root),
            "method": "explicit_basename_probe",
            "references": references,
            "ambiguous_count": sum(
                item["local_resolution"]["status"] == "ambiguous"
                for item in references
            ),
            "candidate_count": sum(
                item["local_resolution"]["classification"] == "candidate"
                for item in references
            ),
            "unknown_count": sum(
                item["local_resolution"]["classification"] == "unknown"
                for item in references
            ),
        },
        "public_catalog": {
            "status": PUBLIC_CATALOG_STATUS,
            "real_local_catalog_available": False,
            "join": {
                "status": PUBLIC_JOIN_STATUS,
                "cause": MISSING_EVIDENCE,
                "verifiable": False,
                "reason": "no_real_local_social_catalog",
            },
        },
    }


def write_observation(observation: Mapping[str, Any], output_path: str | Path) -> None:
    Path(output_path).write_text(
        json.dumps(observation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="/home/mak/curatoria_inbox/ARICA/ARICA.aep",
        help="one AEP input; it is never modified",
    )
    parser.add_argument(
        "--local-root",
        default="/home/mak/curatoria_inbox/ARICA",
        help="one explicit local root for basename probes; it is not scanned",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).with_name("observation.json")),
    )
    args = parser.parse_args(argv)
    observation = build_observation(args.input, args.local_root)
    write_observation(observation, args.output)
    print(
        json.dumps(
            {
                "output": str(Path(args.output)),
                "hash_status": observation["input"]["hash_status"],
                "declared_reference_count": observation["aep_reader"][
                    "declared_reference_count"
                ],
                "candidate_count": observation["local_resolution"]["candidate_count"],
                "ambiguous_count": observation["local_resolution"]["ambiguous_count"],
                "unknown_count": observation["local_resolution"]["unknown_count"],
                "public_join_status": observation["public_catalog"]["join"]["status"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if observation["input"]["hash_status"] == "PASS" and not observation["aep_reader"]["error"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
