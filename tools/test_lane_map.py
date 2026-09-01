"""Deterministic AST import map for bounded pytest execution lanes.

The classifier is read-only. It records imports, not a test's complete
behavior; unresolved sources remain in ``review`` and never break collection.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
LANES = ("flujo", "mak", "integration", "repo_hygiene", "review")
_TREE_ONLY_WORDS = ("git", "repo", "tree", "docs", "readme", "handoff")


@dataclass(frozen=True)
class LaneRecord:
    lane: str
    imports: tuple[str, ...]
    reason: str


def _imports_and_text(path: Path) -> tuple[tuple[str, ...], str]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError):
        return (), ""
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return tuple(sorted(imported)), source.lower()


def _is_motor(name: str) -> bool:
    return name == "flujo" or name.startswith("flujo.") or name.startswith("src.flujo.")


def _is_local_box_import(name: str) -> bool:
    top = name.split(".", 1)[0]
    if _is_motor(name) or top in {"__future__", "tests"}:
        return False
    return (REPO / f"{top}.py").is_file() or (REPO / top).is_dir()


def classify(path: Path) -> LaneRecord:
    """Classify one test from AST imports, then bounded tree/git/docs signals."""
    imported, source = _imports_and_text(path)
    motor = any(_is_motor(name) for name in imported)
    box = any(_is_local_box_import(name) for name in imported)
    if motor and box:
        return LaneRecord("integration", imported, "imports motor and box layer")
    if motor:
        return LaneRecord("flujo", imported, "imports motor")
    if box:
        return LaneRecord("mak", imported, "imports box layer")
    stem = path.stem.lower()
    if any(word in stem or word in source for word in _TREE_ONLY_WORDS):
        return LaneRecord("repo_hygiene", imported, "no local import; tree/git/docs signal")
    return LaneRecord("review", imported, "mapping incomplete")


def build_test_lane_map(paths: Iterable[Path] | None = None) -> dict[str, LaneRecord]:
    """Make the in-process persisted map in one AST pass per test module."""
    selected = sorted(paths if paths is not None else TESTS.glob("test_*.py"))
    return {str(path.resolve().relative_to(REPO)): classify(path) for path in selected}


TEST_LANE_MAP = build_test_lane_map()


def lane_for_test_path(path: str | Path) -> str:
    """Return a declared lane or ``review``; do not raise during collection."""
    try:
        key = str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        return "review"
    return TEST_LANE_MAP.get(key, LaneRecord("review", (), "outside map")).lane


def sethash(paths: Iterable[str]) -> str:
    return hashlib.sha256("\n".join(sorted(paths)).encode()).hexdigest()


def report() -> dict[str, object]:
    grouped: dict[str, list[str]] = {lane: [] for lane in LANES}
    uncovered: dict[str, str] = {}
    for path, record in TEST_LANE_MAP.items():
        grouped[record.lane].append(path)
        if record.lane == "review":
            uncovered[path] = record.reason
    return {"schema": "mak-test-lane-map-v1", "lanes": {
        lane: {"N": len(paths), "SETHASH": sethash(paths), "paths": sorted(paths)}
        for lane, paths in grouped.items()}, "not_covered": uncovered, "total": len(TEST_LANE_MAP)}


def lanes_for_changed_paths(paths: Iterable[str]) -> tuple[str, ...]:
    """Select conservative lanes from ``git diff --name-only`` input paths."""
    selected: set[str] = set()
    for raw in paths:
        path = raw.strip().replace("\\", "/")
        if not path:
            continue
        if path in TEST_LANE_MAP:
            selected.add(TEST_LANE_MAP[path].lane)
        elif path.startswith("src/flujo/"):
            selected.add("flujo")
        elif path.startswith(("tools/", "cultura/")) or path.endswith(".py"):
            selected.add("mak")
        elif any(word in path.lower() for word in _TREE_ONLY_WORDS):
            selected.add("repo_hygiene")
        else:
            selected.add("review")
    return tuple(lane for lane in LANES if lane in selected)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument(
        "--select-changed", action="store_true",
        help="read git diff --name-only paths from stdin and print selected lanes",
    )
    args = parser.parse_args()
    if args.select_changed:
        print(" ".join(lanes_for_changed_paths(sys.stdin)))
        return 0
    data = report()
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for lane, value in data["lanes"].items():
            print(f"{lane}: N={value['N']} SETHASH={value['SETHASH']}")
        print("not_covered=" + ", ".join(sorted(data["not_covered"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
