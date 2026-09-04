"""Focused guards for the non-sequential test-area index, and for the MAK
dependency boundary that the lane contract does not cover.

Both contracts live here on purpose (2026-09-02). A separate test file would
land in the `review` lane, because `context/test_lane_map.json` is generated
and must not be hand-edited, and `pytest_ignore_collect` skips non-matching
lanes on every exact-lane run -- so a new file would never execute. A new
`tools/` module would need a VIVO/MUERTO row in `CAPACIDADES_MAK.md`
(`test_tools_en_registro`), a second surface for logic only this ratchet
consumes. This file is already declared `repo_hygiene`, the lane that guards
classification, so the dependency boundary is guarded from here.
"""

import ast
import inspect
import re
import subprocess
import sys
from pathlib import Path

from conftest import classify_test_axes, classify_test_path, topic_for_test_path
from tools.test_lane_map import REPO, TEST_LANE_MAP, _is_motor_path


def test_research_layers_share_one_area_label() -> None:
    for name in (
        "tests/test_mak_research_memoria_degradation.py",
        "tests/test_mak_research_interfaz_pure.py",
        "tests/test_mak_research_interfaz_http.py",
    ):
        areas, _roles = classify_test_path(name)
        assert "research" in areas


def test_bridge_can_be_selected_by_more_than_one_common_axis() -> None:
    areas, roles = classify_test_path("tests/test_mak_portfolio_bridge.py")
    assert "portfolio" in areas
    assert "integration" in roles


def test_unknown_filename_is_visible_in_explicit_fallback() -> None:
    areas, roles = classify_test_path("tests/test_unclassified_edge.py")
    assert areas == ("misc",)
    assert roles == ("general",)


def test_lane_map_recognizes_motor_paths_from_both_checkouts() -> None:
    assert _is_motor_path("src/flujo/cli.py")
    assert _is_motor_path("flujo/src/flujo/cli.py")
    assert not _is_motor_path("cultura/mak_plataforma/hub.py")


def test_filename_topic_exposes_the_existing_subject_axis() -> None:
    assert topic_for_test_path("tests/test_mak_research_interfaz_http.py") == "research"
    assert topic_for_test_path("tests/test_cli_more_commands.py") == "cli"


def test_small_candidate_is_explicitly_routable() -> None:
    size, scope, environment = classify_test_axes(
        "tests/test_mak_research_interfaz_pure.py"
    )
    assert (size, scope, environment) == ("small", "unit", "machine_bound")


def test_physical_candidate_is_not_mislabeled_as_small() -> None:
    size, scope, environment = classify_test_axes(
        "tests/test_portfolio_production.py"
    )
    assert size == "large"
    assert scope == "system"
    assert environment == "physical"


def test_optional_dependency_is_its_own_environment_lane() -> None:
    """Probed `test_archive_toolchain.py` until 2026-09-02.

    That file left MAK for FLUJO in the separation, and the classifier reads
    the SOURCE to find the signal, so a path that no longer exists yields no
    signals and falls back to `unknown` -- the probe stopped measuring the
    property it names. `test_laser.py` replaces it: it lives here, its stem
    says nothing about optionality, and vpype is the optional dependency the
    signal comes from. A stem-named probe would have proved nothing.
    """
    _size, _scope, environment = classify_test_axes("tests/test_laser.py")
    assert environment == "optional"


def test_unknown_axes_remain_visible_for_review() -> None:
    assert classify_test_axes("tests/test_new_behavior.py") == (
        "unknown", "unknown", "unknown"
    )


# The lane classifier reads imports, not behavior. A test that reaches the
# motor through `subprocess` looks import-free to the AST, so it lands in
# `repo_hygiene` -- a lane the MAK profile runs WITHOUT typer, the one package
# of the motor's CLI stack that profile genuinely lacks (rich, pydantic and
# requests do arrive transitively; measured in CI run 33670334244). That is
# exactly how
# `test_comandos_manifiesto.py::test_the_manifest_is_not_stale_against_the_real_cli`
# reached CI MAK: green on the box, red on a clean runner, for an environment
# reason that looked like a stale manifest. Retirement: when the classifier
# records subprocess consumption and the contract can place these files itself.
_CLI_BY_SUBPROCESS = re.compile(r"""["']-m["']\s*,\s*["']flujo["']|-m\s+flujo""")
_CLI_TABLE_GENERATOR = "gen_mapa_comandos"


def _module_constants(tree: ast.AST) -> dict[str, str]:
    """Module-level names mapped to the source text of their value.

    This exists because measuring the detector refuted it. The published
    version of the offending test called
    `subprocess.run([sys.executable, str(GENERADOR), "--check"])`, where
    neither `-m flujo` nor the generator name appears inside the call: the path
    lives in `GENERADOR = RAIZ / "tools" / "gen_mapa_comandos.py"`. A detector
    that reads only the call text reports the very case that motivated it as
    clean.
    """
    constants: dict[str, str] = {}
    for node in getattr(tree, "body", []):
        if not isinstance(node, ast.Assign) or node.value is None:
            continue
        value = ast.unparse(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                constants[target.id] = value
    return constants


def _spawns_flujo_cli(source: str, tree: ast.AST) -> list[str]:
    """Subprocess calls that reach the FLUJO CLI, scoped to the call itself.

    Scoped on purpose: `tests/test_higiene_repo.py` NAMES
    `tools/gen_mapa_comandos.py` in a data table without ever running it, and a
    whole-file substring match would call that a defect. Names the call
    references are expanded once through `_module_constants`, which is where
    the real case hid the path.
    """
    constants = _module_constants(tree)
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = ast.unparse(node.func)
        if not target.startswith(("subprocess.", "os.system", "os.popen")):
            continue
        text = ast.get_source_segment(source, node) or ast.unparse(node)
        expanded = [text]
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id in constants:
                expanded.append(constants[child.id])
        whole = "\n".join(expanded)
        if _CLI_BY_SUBPROCESS.search(whole) or _CLI_TABLE_GENERATOR in whole:
            found.append(target)
    return found


_SPAWNING_SOURCES = {
    "direct": 'import subprocess, sys\nsubprocess.run([sys.executable, "-m", "flujo", "verify"])\n',
    "through_a_module_constant": (
        "import subprocess, sys\nfrom pathlib import Path\n"
        'R = Path(".")\nG = R / "tools" / "gen_mapa_comandos.py"\n'
        'subprocess.run([sys.executable, str(G), "--check"])\n'
    ),
    "shell_string": 'import subprocess\nsubprocess.run("python -m flujo verify", shell=True)\n',
    "os_system": 'import os\nos.system("python -m flujo verify")\n',
}

_MENTIONING_SOURCES = {
    "data_table": (
        "import subprocess\n"
        'TOOLS = {"tools/gen_mapa_comandos.py": "generates the table"}\n'
        'subprocess.run(["git", "status"])\n'
    ),
    "comment": (
        "import subprocess\n"
        "# see tools/gen_mapa_comandos.py and python -m flujo --help\n"
        'subprocess.run(["git", "diff"])\n'
    ),
    "unspawned_string": (
        "import subprocess\n"
        'MSG = "run python -m flujo verify"\nsubprocess.run(["ls"])\n'
    ),
    "no_subprocess_at_all": 'GEN = "tools/gen_mapa_comandos.py"\nprint(GEN, "python -m flujo")\n',
}


def test_the_detector_finds_execution_including_indirect_paths() -> None:
    """Pin the instrument on known text, the way the idioma ratchet does.

    The first version of this detector passed its own suite and still reported
    the real offender as clean, because the path sat in a module constant. A
    guard measured only against the tree it currently guards proves nothing:
    the tree is clean by construction once the fix lands.
    """
    for name, source in _SPAWNING_SOURCES.items():
        assert _spawns_flujo_cli(source, ast.parse(source)), name


def test_the_detector_does_not_accuse_a_mention() -> None:
    """Naming the CLI is not running it, and a ratchet that cannot tell the
    difference gets disabled by whoever it accuses first."""
    for name, source in _MENTIONING_SOURCES.items():
        assert not _spawns_flujo_cli(source, ast.parse(source)), name


def test_a_hygiene_lane_test_never_spawns_the_flujo_cli() -> None:
    """`repo_hygiene` runs under the MAK profile, which has no motor CLI stack.

    A test that spawns `python -m flujo` or the command-table generator needs
    typer, so it belongs to `integration`: the lane that composes both
    physical checkouts and installs `requirements-integration.txt`.
    """
    offenders: list[str] = []
    for path, record in sorted(TEST_LANE_MAP.items()):
        if record.lane != "repo_hygiene":
            continue
        source_file = REPO / path
        if not source_file.is_file():
            continue
        source = source_file.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=str(source_file))
        except SyntaxError:
            continue
        for target in _spawns_flujo_cli(source, tree):
            offenders.append(f"{path}: {target}")
    assert not offenders, (
        "these tests are declared repo_hygiene and spawn the FLUJO CLI, which "
        "the MAK profile does not install. Their lane is integration:\n"
        + "\n".join(offenders)
    )


# ---------------------------------------------------------------------------
# The MAK dependency boundary
# ---------------------------------------------------------------------------
#
# Audited 2026-09-02: MAK imports rich, pydantic and requests exactly zero
# times, so their transitive arrival is not load-bearing and declaring them
# would add dependencies MAK does not use. typer is absent from the MAK
# profile, which is what broke the manifest ratchet in CI run 33670334244.
# Nothing re-measured any of that, which is the defect this guard closes: the
# claim in `requirements.txt` that the split was "measured by AST" was a
# one-time hand measurement, and `tools/release_gate.py` only enforces profile
# FILE separation, never import-vs-declaration coverage.
#
# The venv is NOT the source of truth here. Installed distributions are never
# consulted: a package present only because another package happens to require
# it would otherwise read as "declared". Every answer comes from the
# requirements files, from `git ls-files`, from the interpreter's stdlib list,
# and from the three reasoned tables below.
#
# Retirement: when a profile installer verifies coverage itself.

# Import name -> distribution name, for the cases where they differ. An
# explicit table, because deriving it needs the installed metadata this guard
# refuses to trust.
_IMPORT_TO_DISTRIBUTION = {
    "PIL": "pillow",
    "yaml": "pyyaml",
    "sklearn": "scikit-learn",
    "fontTools": "fonttools",
    "cv2": "opencv-python",
    "dateutil": "python-dateutil",
    "fitz": "pymupdf",
    "serial": "pyserial",
    "OpenSSL": "pyopenssl",
    "attr": "attrs",
}

# Provided by an embedding interpreter, never installable with pip. The files
# that import these run inside Blender (`blender --python`), so declaring them
# in a requirements file would be a lie that pip could not satisfy.
_RUNTIME_PROVIDED = {
    "bpy": "Blender's embedded Python",
    "bmesh": "Blender's embedded Python",
    "mathutils": "Blender's embedded Python",
    "gpu": "Blender's embedded Python",
    "bgl": "Blender's embedded Python",
    "aud": "Blender's embedded Python",
}

# Hard requirements of a package the MAK profile DOES declare. Listed with the
# declaration that guarantees them, so the guarantee is auditable here instead
# of being inferred from whatever the venv happens to hold.
_GUARANTEED_BY_DECLARED = {
    "werkzeug": "Flask>=3.1.3 declares werkzeug>=3.1.0; xio/new/server.py "
                "imports werkzeug.utils.secure_filename directly",
}

# Optional backends whose ImportError is handled by a CALLER, which no
# single-file AST pass can see. Each entry names where the fallback lives, so
# the claim is checkable and not a blanket exemption.
_CALLER_HANDLED_OPTIONAL = {
    "pypdf": "cultura/mak_research/source_pipeline.py: _pypdf_extract() is a "
             "lazy import; extract_pdf_text() catches ImportError and returns "
             "pdf_text_backend_unavailable after the pdftotext binary fails",
}

# What the MAK profile is actually responsible for running.
_MAK_RUNTIME_PREFIXES = ("cultura/", "tools/", "xio/")

# Everything else, with the reason it is out of scope. `.claude/skills` is the
# decided policy, not an oversight: `gen_vectorizar.py` imports fontTools
# unguarded, and no workflow, cron line, systemd unit, `tools/`, `cultura/`,
# `MAPA.md`, `context/comandos.json` or FLUJO source invokes it -- only two
# SKILL.md files do. It is AGENT_TOOL_ONLY. If that import ever moves into
# runtime scope, fonttools is declared nowhere and this guard fails, which is
# how the classification stays protected instead of merely written down.
_OUT_OF_SCOPE = {
    ".claude/": "agent playbooks and skill scripts: AGENT_TOOL_ONLY",
    "context-history/": "historical material, not runtime",
    "_archive/": "archived material, not runtime",
    "docs/": "documentation and recovered raw sessions, not runtime",
    "projects/": "project material and reference scripts, not service runtime",
    "iskvw/": "published-site surface, not the MAK service profile",
    "svg/": "product material, not runtime",
    "web/": "the Vite hub source, not a Python runtime",
}


def _distributions_declared_by(path: Path, seen: set[Path] | None = None) -> set[str]:
    """Requirement names a profile declares, following its `-r` includes."""
    seen = set() if seen is None else seen
    if path in seen or not path.is_file():
        return set()
    seen.add(path)
    names: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("-r "):
            names |= _distributions_declared_by(
                (path.parent / line[3:].strip()).resolve(), seen)
        elif not line.startswith("-e"):
            names.add(re.split(r"[<>=!\[;]", line)[0].strip().lower().replace("_", "-"))
    return names


def _tracked_python_files() -> list[str]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "*.py"],
                         capture_output=True, text=True, check=True).stdout
    return out.split()


def _own_module_names(files: list[str]) -> set[str]:
    """Module names MAK itself provides, from the tracked tree.

    MAK imports siblings by inserting their directory on `sys.path`, so a
    top-level name may be a tracked module rather than a distribution. Read
    from `git ls-files`, never from the disk or the venv.
    """
    names = {"conftest"}
    for rel in files:
        path = Path(rel)
        names.add(path.stem)
        names.update(path.parts[:-1])
    return names


def _is_mak_runtime_scope(rel: str) -> bool:
    """True when the MAK profile is responsible for this file's imports."""
    if any(rel.startswith(prefix) for prefix in _OUT_OF_SCOPE):
        return False
    if rel.startswith("tests/"):
        record = TEST_LANE_MAP.get(rel)
        return bool(record) and record.lane in ("mak", "repo_hygiene")
    return any(rel.startswith(prefix) for prefix in _MAK_RUNTIME_PREFIXES)


def _guarded_node_ids(tree: ast.AST) -> set[int]:
    """Nodes inside a `try` that handles ImportError (or handles everything)."""
    guarded: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        handles_import = any(
            handler.type is None
            or "ImportError" in ast.unparse(handler.type)
            or "ModuleNotFoundError" in ast.unparse(handler.type)
            for handler in node.handlers
        )
        if handles_import:
            for child in ast.walk(node):
                guarded.add(id(child))
    return guarded


def _third_party_imports(source: str, own: set[str], stdlib: set[str]):
    """Yield (import name, line, guarded) for third-party imports only."""
    tree = ast.parse(source)
    guarded = _guarded_node_ids(tree)
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module]
        for full in names:
            top = full.split(".", 1)[0]
            if top in stdlib or top in own or top.startswith("_"):
                continue
            if top == "flujo" or top == "src":
                continue  # the consumed motor, not a PyPI distribution
            yield top, node.lineno, id(node) in guarded


def _undeclared_imports(rel: str, source: str, declared: set[str],
                        own: set[str], stdlib: set[str]) -> list[str]:
    """Offending imports in one file, applying the whole policy."""
    offenders: list[str] = []
    for top, line, guarded in _third_party_imports(source, own, stdlib):
        distribution = _IMPORT_TO_DISTRIBUTION.get(
            top, top.lower().replace("_", "-"))
        if distribution in declared:
            continue
        if top in _RUNTIME_PROVIDED or top in _GUARANTEED_BY_DECLARED:
            continue
        if top in _CALLER_HANDLED_OPTIONAL:
            continue
        if guarded:
            continue  # optional backend with its own ImportError fallback
        offenders.append(f"{rel}:{line} imports {top} ({distribution})")
    return offenders


_MAK_PROFILE = REPO / "requirements-mak.txt"
_STDLIB = frozenset(sys.stdlib_module_names)

# Synthetic sources. Each one names the property it pins, so a future edit
# cannot quietly change what the guard means.
_SYNTHETIC = {
    "missing_direct_import": (
        "cultura/mak_probe/render.py",
        "from fontTools.ttLib import TTFont\n",
        True,
    ),
    "declared_package": ("cultura/mak_probe/api.py", "import flask\n", False),
    "stdlib": ("cultura/mak_probe/io.py", "import json, subprocess\n", False),
    "own_module": ("cultura/mak_probe/use.py", "import research_lib\n", False),
    "guarded_optional": (
        "cultura/mak_probe/opt.py",
        "try:\n    import pdfplumber\nexcept ImportError:\n    pdfplumber = None\n",
        False,
    ),
    "unguarded_optional": (
        "cultura/mak_probe/opt2.py", "import pdfplumber\n", True,
    ),
    "installed_but_undeclared": (
        "cultura/mak_probe/pretty.py", "import rich\n", True,
    ),
    "mentions_only": (
        "cultura/mak_probe/table.py",
        'TOOLS = {"fontTools": "vectorizes RD text"}\n'
        "# import fontTools would belong to the RD skill, not here\n"
        'DOC = "import rich"\n',
        False,
    ),
}


def test_every_synthetic_dependency_case_lands_where_the_policy_says():
    """One assertion per contract rule, on text this repo does not contain.

    Measuring a guard only against the tree it guards proves nothing: that tree
    is clean by construction the moment the policy is written.
    """
    declared = _distributions_declared_by(_MAK_PROFILE)
    own = _own_module_names(_tracked_python_files())
    for name, (rel, source, should_offend) in _SYNTHETIC.items():
        offenders = _undeclared_imports(rel, source, declared, own, _STDLIB)
        assert bool(offenders) is should_offend, (name, offenders)


def test_a_flujo_import_is_out_of_scope_in_its_own_lane():
    """`integration` installs the FLUJO profile, so its imports are declared
    there. Two such tests import `typer.testing` unguarded, and they are
    correct: `pytest_ignore_collect` keeps them out of the MAK-profile runs."""
    assert not _is_mak_runtime_scope("tests/test_autonomia_cli.py")
    assert not _is_mak_runtime_scope("tests/test_knowledge_dossiers.py")
    for rel in ("tests/test_autonomia_cli.py", "tests/test_knowledge_dossiers.py"):
        assert TEST_LANE_MAP[rel].lane == "integration"
    assert _is_mak_runtime_scope("tests/test_test_taxonomy.py")


def test_agent_skills_are_out_of_scope_and_the_policy_is_the_reason():
    """AGENT_TOOL_ONLY, decided 2026-09-02 with the entrypoint evidence.

    The guard still protects the classification: the same import inside runtime
    scope IS an offence, so the skill cannot become a silent runtime
    dependency by being moved.
    """
    vectorizer = ".claude/skills/entregas-rd/generadores/gen_vectorizar.py"
    assert (REPO / vectorizer).is_file(), "the audited script must still exist"
    assert not _is_mak_runtime_scope(vectorizer)
    assert ".claude/" in _OUT_OF_SCOPE
    declared = _distributions_declared_by(_MAK_PROFILE)
    own = _own_module_names(_tracked_python_files())
    assert "fonttools" not in declared
    assert _undeclared_imports("cultura/mak_probe/x.py",
                               "from fontTools.ttLib import TTFont\n",
                               declared, own, _STDLIB)


def test_the_contract_never_consults_installed_distributions():
    """The venv is not the contract.

    Measured on the contract FUNCTIONS, not on this file's text: the first
    version of this check greped its own forbidden-word list and failed. `rich`
    is installed in the box venv and the guard still calls it undeclared, which
    is the whole point -- a package present because something else required it
    is not a declaration.
    """
    logic = "".join(inspect.getsource(fn) for fn in (
        _distributions_declared_by, _own_module_names, _tracked_python_files,
        _is_mak_runtime_scope, _guarded_node_ids, _third_party_imports,
        _undeclared_imports,
    ))
    for forbidden in ("packages_" + "distributions", "importlib" + ".metadata",
                      "pkg_" + "resources", "find_" + "distributions"):
        assert forbidden not in logic, forbidden
    declared = _distributions_declared_by(_MAK_PROFILE)
    for absent in ("rich", "pydantic", "requests", "typer"):
        assert absent not in declared, absent
    own = _own_module_names(_tracked_python_files())
    assert _undeclared_imports("cultura/mak_probe/pretty.py", "import rich\n",
                               declared, own, _STDLIB)


def test_the_mak_runtime_declares_every_dependency_it_imports():
    """The ratchet. A new direct third-party import in MAK runtime scope must
    be declared in `requirements-mak.txt`, guarded by its own ImportError
    fallback, or classified in one of the three reasoned tables above."""
    declared = _distributions_declared_by(_MAK_PROFILE)
    assert declared, "the MAK profile parsed empty: the guard measured nothing"
    files = _tracked_python_files()
    assert files, "git ls-files returned nothing: the guard measured nothing"
    own = _own_module_names(files)
    scoped = [rel for rel in files if _is_mak_runtime_scope(rel)]
    assert len(scoped) > 100, (
        "MAK runtime scope collapsed to %d files; a zero-ish scope reports "
        "'nothing missing' forever" % len(scoped))
    offenders: list[str] = []
    for rel in scoped:
        try:
            source = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            offenders.extend(
                _undeclared_imports(rel, source, declared, own, _STDLIB))
        except SyntaxError:
            continue
    assert not offenders, (
        "direct third-party imports in MAK runtime scope that "
        "requirements-mak.txt does not declare. Declare the distribution, "
        "guard the import with its own ImportError fallback, or classify it in "
        "_RUNTIME_PROVIDED / _GUARANTEED_BY_DECLARED / "
        "_CALLER_HANDLED_OPTIONAL with the reason:\n  "
        + "\n  ".join(offenders))


# A test file the generated contract does not know is routed to `review`, and
# `pytest_ignore_collect` makes the default `-m mak` run skip it entirely. The
# file docstring above records that as the reason both contracts live here
# rather than in a new module.
#
# What it did not record is that the drift is silent. `tools.test_lane_map`'s
# `report()` iterates the contract, so a file absent from it is absent from the
# report too: `review: N=0` and `not_covered=` are answers about the contract,
# not about the tests directory. Measured 2026-09-04: 234 test files on disk,
# 219 in the contract, and `-m mak` collected 2202 of 3561 cases.
#
# `tools/release_gate.py` asks a different question -- whether tests declared
# for the *other* branch's lane are present -- and while doing so it records
# both `own_tests_declared` and `test_files_tracked` in the same row without
# ever comparing them. The two numbers that reveal this gap were already being
# collected; the subtraction was not.
#
# Do NOT close the gap by re-running the classifier over the tree. Measured
# 2026-09-04, before and after fixing `_is_local_box_import` to resolve bare
# imports against the directories tests actually put on sys.path:
#
#   before   `mak` 172 -> 64, 154 files move, 108 leave the default run
#   after    `mak` 172 -> 128, 69 leave
#
# The fix was worth making and does not make regeneration safe. Of the 69 that
# still move, 55 import nothing outside the standard library: they exercise the
# tree through files, subprocesses and git rather than by importing it, so the
# AST has nothing to classify them by and they fall to `repo_hygiene` on a
# text signal. No amount of extra sys.path roots recovers them, because the
# information is not in the source.
#
# That is what `reconciled_at_utc` records: a pass that knew what a test
# exercises without being told by an import. Regeneration must reproduce that
# pass. An AST-only regeneration cannot, by construction.
#
# The pin is an upper bound, not an equality, so regenerating the contract --
# which lowers the count -- passes, and adding another unrouted file without
# regenerating fails. `tests/test_render_flyer_mak.py` was already in this
# state before the rest, so the number is not one session's debt.
# Each raise is a deliberate deferral, not an exemption: the number IS the
# debt, and it stays in the diff where a reviewer sees it. 15 -> 16 on
# 2026-09-04 for tests/test_venue_geometria_scd.py, then 17 for
# tests/test_compute_effort_residuals.py.
_UNROUTED_TEST_FILES_CEILING = 17


def _unrouted_test_files() -> list[str]:
    on_disk = {
        str(path.relative_to(REPO))
        for path in (REPO / "tests").rglob("test_*.py")
    }
    return sorted(on_disk - set(TEST_LANE_MAP))


def test_the_lane_contract_knows_about_the_tests_on_disk() -> None:
    unrouted = _unrouted_test_files()
    assert len(unrouted) <= _UNROUTED_TEST_FILES_CEILING, (
        "%d test files are absent from context/test_lane_map.json, above the "
        "declared ceiling of %d. They are routed to `review`, so the default "
        "`-m mak` run never executes them -- green in a full run and invisible "
        "in the one an operator makes. The contract is generated and must not "
        "be hand-edited; regenerate it, then lower the ceiling.\n  %s"
        % (len(unrouted), _UNROUTED_TEST_FILES_CEILING, "\n  ".join(unrouted))
    )


def test_the_unrouted_count_is_measured_not_assumed() -> None:
    # A ceiling nobody can reach is not a ratchet. If the contract is ever
    # regenerated to completeness this fails, and the ceiling should drop to 0.
    on_disk = {
        str(path.relative_to(REPO))
        for path in (REPO / "tests").rglob("test_*.py")
    }
    assert on_disk, "no test files found: the measurement is meaningless"
    assert TEST_LANE_MAP, "the lane contract is empty"
    assert len(_unrouted_test_files()) < len(on_disk), (
        "the contract knows none of the tests on disk"
    )


def test_a_bare_import_of_a_subdirectory_module_reads_as_a_box_import() -> None:
    """`import coherence` means `cultura/mak_plataforma/coherence.py`.

    Resolving against the repository root alone said no, which dropped the
    importing test out of the `mak` lane. Measured across the 108
    `sys.path.insert` calls under tests/: the directories they name are the
    ones `_BOX_IMPORT_ROOTS` now carries.
    """
    from tools.test_lane_map import _BOX_IMPORT_ROOTS, _is_local_box_import

    assert (REPO / "cultura" / "mak_plataforma" / "coherence.py").is_file(), (
        "the module this case is built on has moved; pick another"
    )
    assert _is_local_box_import("coherence")
    assert "cultura/mak_plataforma" in _BOX_IMPORT_ROOTS


def test_every_declared_box_import_root_exists() -> None:
    from tools.test_lane_map import _BOX_IMPORT_ROOTS

    for relative in _BOX_IMPORT_ROOTS:
        if not relative:
            continue
        assert (REPO / relative).is_dir(), (
            f"{relative} is declared as an import root and is not a directory; "
            "a root that cannot match makes the classifier quietly stricter"
        )


def test_the_motor_is_still_not_a_box_import() -> None:
    # Widening the roots must not swallow the MAK/FLUJO boundary the lanes
    # exist to keep.
    from tools.test_lane_map import _is_local_box_import

    assert not _is_local_box_import("flujo")
    assert not _is_local_box_import("flujo.knowledge.replay")
    assert not _is_local_box_import("src.flujo.cli")


def test_a_third_party_name_is_not_a_box_import() -> None:
    from tools.test_lane_map import _is_local_box_import

    for name in ("pytest", "flask", "PIL", "requests"):
        assert not _is_local_box_import(name), (
            f"{name} resolved as local; a root is matching too broadly"
        )
