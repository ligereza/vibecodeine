"""Focused guards for the non-sequential test-area index."""

from conftest import classify_test_axes, classify_test_path, topic_for_test_path
from tools.test_lane_map import _is_motor_path


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
