#!/usr/bin/env python3
"""tests/test_node_runtime_requirement.py -- the Node minimum has one home.

Measured on 2026-08-21 on the MAK box: ``PATH`` resolved Node 18.20.4, the web
build warned that Vite wants a newer runtime, and Node 20.20.2 and 24.x installs
that satisfy ``web/package.json`` engines (``>=20.19.0``) were already present
under the local Actions runner and the codex runtime cache. The operational
status still reported ``node available`` because its inline candidate list
stopped at PATH plus one runtime, so a status row contradicted the declared
requirement and nobody was told which binary to use.

These tests pin the repaired contract: one resolver, the requirement read from
the manifest rather than copied, and every reachable candidate exposed so a
caller can pick one instead of guessing a path.
"""
from __future__ import annotations

import json
from pathlib import Path

from flujo.knowledge.runtime_tools import (
    declared_node_minimum,
    node_candidates,
    resolve_node,
)

REPO = Path(__file__).resolve().parents[1]


def test_declared_minimum_comes_from_the_web_manifest():
    manifest = json.loads((REPO / "web" / "package.json").read_text(encoding="utf-8"))
    expected = str((manifest.get("engines") or {}).get("node") or "").strip()
    assert declared_node_minimum(REPO) == expected
    assert expected, "web/package.json must keep declaring a node minimum"


def test_missing_manifest_reports_no_minimum_instead_of_guessing(tmp_path):
    assert declared_node_minimum(tmp_path) == ""


def test_candidates_are_executable_paths_without_duplicates(tmp_path):
    found = node_candidates(REPO)
    assert found == list(dict.fromkeys(found)), "candidate list repeats a path"
    for candidate in found:
        assert candidate.is_file(), candidate
    resolved = resolve_node(REPO)
    assert resolved == (found[0] if found else None)


def test_an_explicit_override_wins_and_is_never_invented(tmp_path, monkeypatch):
    fake = tmp_path / "node"
    fake.write_text("#!/bin/sh\necho v99.0.0\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("NODE_EXE", str(fake))
    found = node_candidates(REPO)
    assert found[0] == fake
    monkeypatch.setenv("NODE_EXE", str(tmp_path / "absent"))
    assert (tmp_path / "absent") not in node_candidates(REPO)


def test_status_reports_the_requirement_next_to_the_resolved_binary():
    """A status that says "available" without the minimum hid the drift."""
    from flujo.knowledge.system_status import _dependency_component

    node = _dependency_component(REPO)["evidence"]["node"]
    assert node["declared_minimum"] == declared_node_minimum(REPO)
    assert node["candidates"] == [str(path) for path in node_candidates(REPO)]
    if node["available"]:
        assert node["path"] in node["candidates"]


def test_status_no_longer_keeps_its_own_node_candidate_list():
    """The duplicate list is what let the two answers disagree."""
    source = (REPO / "src" / "flujo" / "knowledge" / "system_status.py").read_text(
        encoding="utf-8")
    assert "codex-primary-runtime" not in source, (
        "system_status hardcodes a node path again; resolution belongs to "
        "runtime_tools.node_candidates")
    assert "node_candidates(repo)" in source
