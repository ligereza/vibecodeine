"""The knowledge scanner must not walk into installed dependency trees.

Measured on the live database: 1463 of the 8273 rows in
``classification_queue`` -- 17.7% of the entire queue -- came from ONE directory,
``/home/mak/curatoria_inbox/3d/NEW/env``, a Windows virtualenv copied onto this
box. ``ACTIVE_SKIP`` held ``venvs``, ``.venvs`` and ``venv-providers`` and missed
both ``env`` and the Windows layout ``env/Lib/site-packages``.

The scanner had no test at all, which is how a name list stayed the whole rule.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def scanner():
    spec = importlib.util.spec_from_file_location(
        "mak_knowledge_builder", REPO / "tools" / "build_mak_knowledge_db.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_directory_python_marked_as_an_environment_is_skipped(scanner, tmp_path):
    env = tmp_path / "env"
    env.mkdir()
    (env / "pyvenv.cfg").write_text("home = /usr/bin\n", encoding="utf-8")
    assert scanner.is_virtual_environment(env)
    assert scanner.should_skip_dir(env, "active")
    assert scanner.should_skip_dir(env, "historical")


def test_the_name_list_alone_would_have_missed_it(scanner, tmp_path):
    """The regression, stated as the reason this rule is not a name.

    ``env`` is the name the real virtualenv used. If a future edit deletes the
    definition and goes back to the list, this fails.
    """
    assert "env" not in scanner.ACTIVE_SKIP
    assert "Lib" not in scanner.ACTIVE_SKIP
    env = tmp_path / "env"
    env.mkdir()
    (env / "pyvenv.cfg").write_text("home = /usr/bin\n", encoding="utf-8")
    assert scanner.should_skip_dir(env, "active"), (
        "the scanner is back to matching names instead of testing for pyvenv.cfg")


def test_an_install_target_is_skipped_even_without_the_marker_above(scanner, tmp_path):
    """Reached when the environment root sits above the scan root."""
    for name in ("site-packages", "dist-packages"):
        target = tmp_path / "lib" / name
        target.mkdir(parents=True)
        assert scanner.should_skip_dir(target, "active")


def test_an_ordinary_directory_is_still_walked(scanner, tmp_path):
    ordinary = tmp_path / "tools"
    ordinary.mkdir()
    assert not scanner.is_virtual_environment(ordinary)
    assert not scanner.should_skip_dir(ordinary, "active")


def test_the_repository_own_venv_is_skipped(scanner):
    venv = REPO / ".venv"
    if not (venv / "pyvenv.cfg").is_file():
        pytest.skip("this checkout has no .venv")
    assert scanner.is_virtual_environment(venv)
    assert scanner.should_skip_dir(venv, "active")
