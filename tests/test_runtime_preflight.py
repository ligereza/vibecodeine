"""Ratchets for tools/runtime_preflight.py.

The preflight exists because an HTTP 200 was being read as proof that a
service runs the canonical source.  A detector that can only ever return 0 is
worth nothing, so most of what is pinned here is the tool's ability to FAIL:
an absent source, a decoy tree, an executed source that differs from the
declared one.

Everything that can be hermetic is hermetic -- a temporary root with its own
`flujo` adapter, a temporary binary -- so the assertions do not depend on the
MAK services being up.  The two cases that do call `build_report` only assert
the exit code, never a specific finding code, because which error fires first
depends on what happens to be running on the box.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "tools" / "runtime_preflight.py"
    spec = importlib.util.spec_from_file_location("runtime_preflight", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # @dataclass resolves annotations through sys.modules[cls.__module__], so
    # the module has to be registered before it is executed.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def _adapter_root(tmp_path: Path) -> Path:
    """Build a root whose `flujo` entry is a directory of sibling symlinks.

    This is the shape measured on the box: not a symlink, not a worktree, not
    a second repository.
    """

    root = tmp_path / "root"
    (root / "src" / "flujo" / "web").mkdir(parents=True)
    (root / "src" / "flujo" / "web" / "hub.py").write_text("# canonical\n", encoding="utf-8")
    adapter = root / MODULE.ADAPTER_NAME
    adapter.mkdir()
    (adapter / "src").symlink_to("../src")
    return root


def _report(**conditions: bool) -> dict[str, object]:
    base = {
        MODULE.CONDITION_ERROR: False,
        MODULE.CONDITION_UNKNOWN: False,
        MODULE.CONDITION_WARN: False,
        MODULE.CONDITION_ADAPTER: False,
    }
    base.update(conditions)
    return {"conditions": base}


# ---------------------------------------------------------------- failure paths


def test_empty_root_is_an_error_not_a_silent_pass(tmp_path):
    # Nothing declared exists under this root, so every Python surface must
    # report source_missing.  Before this tool, the same box answered HTTP 200
    # on all five ports, which is why a green result had to be impossible here.
    report = MODULE.build_report(tmp_path, Path(__file__))
    assert report["conditions"][MODULE.CONDITION_ERROR] >= 1
    assert MODULE.exit_code(report) == MODULE.EXIT_ERROR
    codes = {
        finding["code"]
        for surface in report["surfaces"]
        for finding in surface["findings"]
    }
    assert "source_missing" in codes


def test_decoy_tree_is_an_error_because_the_live_process_runs_elsewhere(tmp_path):
    # A tree that reproduces the relative paths with different bytes is the
    # dangerous case: the source "exists", so an existence check would pass.
    for relative in (
        "cultura/mak_plataforma/hub.py",
        "cultura/mak_research/interfaz.py",
        "cultura/mak_codex/interfaz_codex.py",
        "src/flujo/web/hub.py",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# decoy, not the canonical source\n", encoding="utf-8")

    report = MODULE.build_report(tmp_path, Path(__file__))
    assert MODULE.exit_code(report) == MODULE.EXIT_ERROR
    # The specific code depends on what is running: an ExecStart pointing
    # outside this root, a mismatch, or a missing process. Any of them is an
    # error, and none of them may be swallowed.
    codes = {
        finding["code"]
        for surface in report["surfaces"]
        for finding in surface["findings"]
        if finding["status"] == MODULE.STATUS_ERROR
    }
    assert codes, "a decoy root must produce at least one error finding"
    assert codes & {
        "exec_start_outside_root",
        "executed_source_mismatch",
        "source_changed_after_start",
        "listener_source_unverified",
        "process_missing",
    }


def test_executed_source_different_from_declared_is_an_error(tmp_path):
    root = tmp_path / "root"
    (root / "cultura").mkdir(parents=True)
    declared = root / "cultura" / "declared.py"
    executed = root / "cultura" / "executed.py"
    declared.write_text("# declared\n", encoding="utf-8")
    executed.write_text("# something else entirely\n", encoding="utf-8")

    report = MODULE.SurfaceReport("probe", "Probe", "systemd_user")
    MODULE._check_exec_paths(report, root, declared, ["/usr/bin/python3", str(executed)], "cmdline")
    assert report.status == MODULE.STATUS_ERROR
    assert [f.code for f in report.findings] == ["executed_source_mismatch"]
    assert report.conditions[MODULE.CONDITION_ERROR] is True


def test_source_inside_frozen_evidence_is_an_error(tmp_path):
    # WIN and _archive are evidence trees. Code executed from there is
    # historical material, and a green report over it would be a lie.
    root = tmp_path / "root"
    frozen = root / "_archive" / "merge" / "origins"
    frozen.mkdir(parents=True)
    historical = frozen / "hub.py"
    historical.write_text("# historical copy\n", encoding="utf-8")

    report = MODULE.SurfaceReport("probe", "Probe", "systemd_user")
    MODULE._check_exec_paths(report, root, None, ["/usr/bin/python3", str(historical)], "cmdline")
    assert [f.code for f in report.findings] == ["exec_start_historical"]
    assert report.status == MODULE.STATUS_ERROR


# ------------------------------------------------------------- adapter handling


def test_adapter_root_is_normalized_and_the_substitution_is_recorded(tmp_path):
    # `/home/mak/flujo` is a real directory, so realpath does not collapse it
    # and `root / "flujo"` would invent `<root>/flujo/flujo`.
    root = _adapter_root(tmp_path)
    normalized, recorded = MODULE.normalize_root(root / MODULE.ADAPTER_NAME)
    assert normalized == root
    assert recorded == str(root / MODULE.ADAPTER_NAME)

    plain, nothing = MODULE.normalize_root(root)
    assert plain == root
    assert nothing is None


def test_source_reached_through_the_adapter_is_flagged_not_hidden(tmp_path):
    root = _adapter_root(tmp_path)
    canonical = root / "src" / "flujo" / "web" / "hub.py"
    through_adapter = root / MODULE.ADAPTER_NAME / "src" / "flujo" / "web" / "hub.py"
    # Same inode reached by two names: the resolution is sound, the
    # declaration is not.
    assert through_adapter.resolve() == canonical.resolve()

    report = MODULE.SurfaceReport("probe", "Probe", "manual_process")
    MODULE._check_exec_paths(report, root, canonical, [str(through_adapter)], "import_probe")
    assert [f.code for f in report.findings] == ["exec_start_via_adapter"]
    assert report.status == MODULE.STATUS_OK_VIA_ADAPTER
    assert report.conditions[MODULE.CONDITION_ADAPTER] is True
    assert report.conditions[MODULE.CONDITION_ERROR] is False


def test_adapter_is_never_reported_as_a_repository_or_a_worktree():
    adapter = MODULE.adapter_report(MODULE.PHYSICAL_ROOT)
    assert adapter["role"] == "compatibility_adapter"
    assert adapter["is_symlink"] is False
    assert adapter["own_git_dir"] is False
    assert adapter["is_git_worktree"] is False
    # A symlink resolving inside its own ancestor is what allowed cyclic
    # walks; the adapter must stay free of them.
    assert adapter["recursive_symlinks"] == []
    assert adapter["broken_symlinks"] == []


# ---------------------------------------------------------------- native source


def test_native_binary_surface_is_verified_by_argv0(tmp_path):
    binary = tmp_path / "ollama"
    binary.write_bytes(b"\x7fELF fake binary")

    ok = MODULE.SurfaceReport("ollama", "Ollama", "systemd_system")
    MODULE._check_native_executable(ok, tmp_path, binary, [str(binary), "serve"])
    assert ok.findings == []
    assert ok.status == MODULE.STATUS_OK
    assert ok.data["executed_binary"] == str(binary)

    other = tmp_path / "impostor"
    other.write_bytes(b"\x7fELF another binary")
    bad = MODULE.SurfaceReport("ollama", "Ollama", "systemd_system")
    MODULE._check_native_executable(bad, tmp_path, binary, [str(other), "serve"])
    assert [f.code for f in bad.findings] == ["executed_source_mismatch"]
    assert bad.status == MODULE.STATUS_ERROR


def test_ollama_surface_declares_a_binary_and_keeps_repo_libs_as_consumers():
    # Declaring a repo library as Ollama's source left the real executable
    # unverified and turned a MAK-side edit into fake daemon drift.
    surface = next(s for s in MODULE.SURFACES if s.surface_id == "ollama")
    assert surface.source_kind == "native_binary"
    assert surface.source_declared == "/usr/local/bin/ollama"
    assert "cultura/mak_research/research_lib.py" in surface.consumer_sources


# ------------------------------------------------------------------ exit codes


def test_strict_distinguishes_warning_from_success():
    clean = _report()
    warned = _report(**{MODULE.CONDITION_WARN: True})

    # Normal mode keeps its contract: a warning is not a failure.
    assert MODULE.exit_code(clean) == MODULE.EXIT_OK
    assert MODULE.exit_code(warned) == MODULE.EXIT_OK
    # Strict mode separates them.
    assert MODULE.exit_code(clean, strict=True) == MODULE.EXIT_OK
    assert MODULE.exit_code(warned, strict=True) == MODULE.EXIT_WARN


def test_one_exit_code_per_condition_worst_first():
    assert MODULE.exit_code(_report(**{MODULE.CONDITION_ERROR: True}), strict=True) == MODULE.EXIT_ERROR
    assert MODULE.exit_code(_report(**{MODULE.CONDITION_UNKNOWN: True}), strict=True) == MODULE.EXIT_UNKNOWN
    assert MODULE.exit_code(_report(**{MODULE.CONDITION_ADAPTER: True}), strict=True) == MODULE.EXIT_ADAPTER
    # An error outranks every softer condition, in both modes.
    everything = _report(
        **{
            MODULE.CONDITION_ERROR: True,
            MODULE.CONDITION_UNKNOWN: True,
            MODULE.CONDITION_WARN: True,
            MODULE.CONDITION_ADAPTER: True,
        }
    )
    assert MODULE.exit_code(everything) == MODULE.EXIT_ERROR
    assert MODULE.exit_code(everything, strict=True) == MODULE.EXIT_ERROR
    # An unknown unit is never swallowed, with or without strict.
    unknown = _report(**{MODULE.CONDITION_UNKNOWN: True, MODULE.CONDITION_WARN: True})
    assert MODULE.exit_code(unknown) == MODULE.EXIT_UNKNOWN


def test_check_adapter_is_independent_of_strict():
    adapter_only = _report(**{MODULE.CONDITION_ADAPTER: True})
    assert MODULE.exit_code(adapter_only) == MODULE.EXIT_OK
    assert MODULE.exit_code(adapter_only, check_adapter=True) == MODULE.EXIT_ADAPTER
    assert MODULE.exit_code(adapter_only, strict=True) == MODULE.EXIT_ADAPTER

    # With a warning present, --check-adapter alone still isolates the
    # adapter, because the warning code only exists in strict mode.
    both = _report(**{MODULE.CONDITION_WARN: True, MODULE.CONDITION_ADAPTER: True})
    assert MODULE.exit_code(both, check_adapter=True) == MODULE.EXIT_ADAPTER
    assert MODULE.exit_code(both, strict=True) == MODULE.EXIT_WARN


def test_port_fallback_never_becomes_a_silent_success(monkeypatch):
    # 8765 declared, 8766 answering: probing 8766 alone would report success
    # without noticing the declared port never bound.
    #
    # This assertion first failed the moment FLUJO was redeployed on 8765:
    # the check reached the live box through _socket_open and found the
    # declared port open, so the fallback scenario stopped existing. A test
    # whose verdict depends on what happens to be running is worthless, so
    # the socket probe is pinned to the scenario under test.
    surface = next(s for s in MODULE.SURFACES if s.surface_id == "flujo_app")
    assert surface.declared_port == 8765
    assert 8766 in surface.fallback_ports

    monkeypatch.setattr(MODULE, "_socket_open", lambda port: port == 8766)
    monkeypatch.setattr(MODULE, "_probe_http",
                        lambda port, paths: {"http_path": "/", "http_status": 200, "bytes": 1})
    report = MODULE.SurfaceReport("flujo_app", "FLUJO App", "manual_process")
    report.data["pid"] = None
    report.data["source_sha256"] = "n/a"
    MODULE._port_evidence(report, surface, {8766: {"pid": None, "process": "python"}}, {})
    assert report.data["declared_port"] == 8765
    assert report.data["effective_port"] == 8766
    assert report.data["fallback_port"] == 8766
    assert "port_fallback" in [f.code for f in report.findings]
    assert report.conditions[MODULE.CONDITION_WARN] is True


# --------------------------------------------------------------- read-only-ness


def test_the_report_alters_no_file_it_inspects():
    watched = [
        MODULE.PHYSICAL_ROOT / "cultura" / "mak_plataforma" / "hub.py",
        MODULE.PHYSICAL_ROOT / "cultura" / "mak_research" / "interfaz.py",
        MODULE.PHYSICAL_ROOT / "cultura" / "mak_codex" / "interfaz_codex.py",
        MODULE.PHYSICAL_ROOT / "src" / "flujo" / "web" / "hub.py",
        MODULE.PHYSICAL_ROOT / "cultura" / "mak_plataforma" / "mak-hub.service",
        MODULE.PHYSICAL_ROOT / "cultura" / "mak_research" / "interfaz.service",
        MODULE.PHYSICAL_ROOT / "cultura" / "mak_codex" / "mak-codex.service",
    ]

    def fingerprint() -> dict[str, tuple[str, int, int]]:
        rows = {}
        for path in watched:
            if not path.is_file():
                continue
            stat = path.stat()
            rows[str(path)] = (
                hashlib.sha256(path.read_bytes()).hexdigest(),
                stat.st_mtime_ns,
                stat.st_ino,
            )
        return rows

    before = fingerprint()
    assert before, "the watched set must not be empty on the MAK box"
    report = MODULE.build_report(MODULE.PHYSICAL_ROOT, Path(__file__))
    assert fingerprint() == before
    # And the report itself must stay serializable evidence, not a side effect.
    assert json.loads(json.dumps(report, ensure_ascii=True))["schema"] == MODULE.SCHEMA
