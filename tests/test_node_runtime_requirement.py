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


# --- console scripts of declared dependencies ------------------------------
#
# A gate that never fires where the dependency IS installed is not a gate.
# Measured on 2026-08-21: vpype is declared in pyproject.toml under the dev
# extra, .venv/bin/vpype exists and `import vpype` works, yet
# laser.verificar() returned {"vpype": False} and
# test_estado_reporta_la_cadena_real skipped with "vpype not installed".
# shutil.which only searches PATH, and pip puts console scripts next to the
# interpreter -- a directory that is NOT on PATH when the suite runs as
# ./.venv/bin/python -m pytest.


def test_a_console_script_in_this_venv_is_found():
    from flujo.knowledge.runtime_tools import resolve_console_script

    found = resolve_console_script("flujo")
    assert found is not None, "this package's own console script is missing"
    assert found.is_file()


def test_the_interpreter_symlink_does_not_hide_the_venv_bin():
    """The trap that broke the first version of this resolver.

    .venv/bin/python is a symlink to /usr/bin/python3, so
    Path(sys.executable).resolve().parent is /usr/bin and the console script is
    never seen. The unresolved dirname is the one that holds it.
    """
    import sys
    from pathlib import Path

    from flujo.knowledge.runtime_tools import resolve_console_script

    unresolved = Path(sys.executable).parent
    resolved = Path(sys.executable).resolve().parent
    found = resolve_console_script("flujo")
    assert found is not None
    if unresolved != resolved:
        # Exactly the situation that caused the bug; prove it is handled.
        assert str(found).startswith(str(unresolved)) or found.parent == resolved


def test_an_absent_tool_returns_none_not_a_guess():
    from flujo.knowledge.runtime_tools import resolve_console_script

    assert resolve_console_script("definitely-not-installed-anywhere") is None


def test_an_explicit_override_wins_but_a_broken_one_falls_through(
        tmp_path, monkeypatch):
    from flujo.knowledge.runtime_tools import resolve_console_script

    fake = tmp_path / "vpype"
    fake.write_text("#!/bin/sh\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("VPYPE_EXE", str(fake))
    assert resolve_console_script("vpype", env_var="VPYPE_EXE") == fake.resolve()
    # A configured path that does not exist must not stop the search.
    monkeypatch.setenv("VPYPE_EXE", str(tmp_path / "absent"))
    assert resolve_console_script("vpype", env_var="VPYPE_EXE") != tmp_path / "absent"


def test_the_laser_chain_reports_the_tool_it_actually_has():
    """The end of the chain: verificar() must agree with the filesystem."""
    from flujo import laser
    from flujo.knowledge.runtime_tools import resolve_console_script

    expected = resolve_console_script("vpype", env_var="VPYPE_EXE") is not None
    assert laser.verificar()["vpype"] is expected


def test_blender_honours_the_documented_env_name_and_its_legacy_alias(
        tmp_path, monkeypatch):
    """BLENDER_EXE is what MAPA.md documents; MAK_BLENDER was read only by the
    curatoria diagnostic, so setting the documented one resolved Blender in one
    place and not the other."""
    from flujo.knowledge.runtime_tools import resolve_blender

    fake = tmp_path / "blender"
    fake.write_text("#!/bin/sh\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.delenv("MAK_BLENDER", raising=False)
    monkeypatch.setenv("BLENDER_EXE", str(fake))
    assert resolve_blender(tmp_path) == fake.resolve()
    monkeypatch.delenv("BLENDER_EXE")
    monkeypatch.setenv("MAK_BLENDER", str(fake))
    assert resolve_blender(tmp_path) == fake.resolve()


def test_the_curatoria_diagnostic_reads_the_documented_name_too():
    """Same divergence, other side: it used to read only MAK_BLENDER."""
    source = (REPO / "cultura" / "mak_curatoria"
              / "diagnostico_proyectos.py").read_text(encoding="utf-8")
    assert 'os.environ.get("BLENDER_EXE"' in source, (
        "the curatoria diagnostic ignores the documented BLENDER_EXE again")
    assert 'os.environ.get("MAK_BLENDER"' in source, (
        "the legacy alias was dropped; an existing setup would break")
