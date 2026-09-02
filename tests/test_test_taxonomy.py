"""Focused guards for the non-sequential test-area index."""

import ast
import re

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
