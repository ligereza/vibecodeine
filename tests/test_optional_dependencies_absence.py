"""The absence path of optional third-party dependencies.

CI failed with ``ModuleNotFoundError: No module named 'psd_tools'`` right
after the suite passed green on a machine that has it installed. Production
code already treats these packages as OPTIONAL capabilities and degrades:

    src/flujo/knowledge/archive_toolchain.py:761   `_module_version(...) is not None`
    cultura/mak_curatoria/diagnostico_proyectos.py:265,291   `find_spec("psd_tools")`

but until now nothing exercised the absence branch itself -- only its
presence. This module simulates absence with monkeypatch (blocking the
relevant ``__import__`` calls, or making ``importlib.util.find_spec`` return
None) and asserts that the result NAMES the missing capability instead of
raising, silently returning an empty-but-"observed" result, or otherwise
reading as health. Doctrine: absence is not read as health.
"""
from __future__ import annotations

import builtins
import importlib.util
from pathlib import Path

import pytest

from cultura.mak_curatoria import diagnostico_proyectos
from flujo.knowledge import archive_toolchain


def _block_import(monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    """Make `import <name>` (and its submodules) raise ImportError."""
    original_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name in names or any(name.startswith(blocked_name + ".") for blocked_name in names):
            raise ImportError("optional package absent (simulated by test)")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)


def _block_find_spec(monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    """Make `importlib.util.find_spec(<name>)` report absence for `names`."""
    original_find_spec = importlib.util.find_spec

    def patched(name, *args, **kwargs):
        if name in names:
            return None
        return original_find_spec(name, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "find_spec", patched)


# ---------------------------------------------------------------------------
# archive_toolchain.py: per-tool observers each guard their own import and
# must report "unavailable" with a named reason, never raise or fabricate
# facts.
# ---------------------------------------------------------------------------

def test_mutagen_absence_is_named_not_raised(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _block_import(monkeypatch, "mutagen")
    result = archive_toolchain._mutagen(tmp_path / "clip.mp3", {}, 10)
    assert result["status"] == "unavailable"
    assert result["method"] == {"tool": "mutagen"}
    assert result["facts"] == {"reason": "package_missing"}


def test_imagehash_absence_degrades_image_features_observer(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # PIL/Pillow is a required dependency of this repo and stays importable;
    # only ImageHash is blocked, which is the actually-optional half of the
    # "Pillow+ImageHash" pair used by _image().
    _block_import(monkeypatch, "imagehash")
    result = archive_toolchain._image(tmp_path / "poster.png", {}, 10)
    assert result["status"] == "unavailable"
    assert result["method"] == {"tool": "Pillow+ImageHash"}
    assert result["facts"] == {"reason": "package_missing"}


def test_pypdf_absence_is_named_not_raised(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _block_import(monkeypatch, "pypdf")
    result = archive_toolchain._pdf(tmp_path / "brief.pdf", {}, 10)
    assert result["status"] == "unavailable"
    assert result["method"] == {"tool": "pypdf"}
    assert result["facts"] == {"reason": "package_missing"}


def test_hachoir_absence_is_named_not_raised(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _block_import(monkeypatch, "hachoir")
    result = archive_toolchain._hachoir(tmp_path / "clip.mov", {}, 10)
    assert result["status"] == "unavailable"
    assert result["method"] == {"tool": "hachoir"}
    assert result["facts"] == {"reason": "package_missing"}


def test_surface_signature_returns_none_instead_of_fabricating_a_hash(
        monkeypatch: pytest.MonkeyPatch):
    # _surface_signature() is the one function in this file that degrades by
    # returning bare None on ImportError, rather than an {"status": ...}
    # observation dict like its siblings. That is safe ONLY because every
    # caller treats None as "skip this candidate" and the surrounding
    # native_structure observation still carries psd-tools' own status, and
    # separately _tool_inventory() names imagehash's absence at the top
    # level. The behaviour this test locks down: no phash/dhash/ahash keys
    # ever get fabricated when ImageHash is missing.
    _block_import(monkeypatch, "imagehash")
    result = archive_toolchain._surface_signature(image=None)
    assert result is None


def test_tool_inventory_reports_every_absent_optional_module_as_unavailable(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """The doctrine check: absence must not read as health anywhere in the map."""
    _block_import(monkeypatch, "imagehash", "pypdf", "mutagen", "hachoir", "psd_tools")
    inventory = archive_toolchain._tool_inventory()
    for name in ("imagehash", "pypdf", "mutagen", "hachoir", "psd_tools"):
        assert inventory[name] == {"available": False, "version": None}, (
            "%s must report available=False/version=None when the module "
            "cannot be imported, not a stale or fabricated value" % name
        )


def test_psd_observer_degrades_when_psd_tools_absent(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Companion to test_native_psd_degrades_explicitly_when_optional_package_is_missing
    # in test_archive_toolchain.py (which already covers this one function).
    # Kept here too so every optional-dependency absence path lives in one
    # place and the doctrine check above (_tool_inventory) sits next to the
    # per-observer one it summarizes.
    _block_import(monkeypatch, "psd_tools")
    result = archive_toolchain._psd(tmp_path / "layout.psd", {}, 10)
    assert result["status"] == "unavailable"
    assert result["facts"] == {"format": "psd", "reason": "package_missing"}


# ---------------------------------------------------------------------------
# diagnostico_proyectos.py: structure_adapter_for_path() must never claim a
# package is installed when it isn't -- the fallback reader names ARE the
# capability decision (see its own docstring).
# ---------------------------------------------------------------------------

def test_structure_adapter_falls_back_to_xmp_window_when_psd_tools_absent(
        monkeypatch: pytest.MonkeyPatch):
    _block_find_spec(monkeypatch, "psd_tools")
    assert diagnostico_proyectos.structure_adapter_for_path("layout.psd") == "xmp_window"
    assert diagnostico_proyectos.structure_adapter_for_path("layout.psb") == "xmp_window"


def test_structure_adapter_prefers_psd_tools_reader_when_present():
    pytest.importorskip("psd_tools", reason="psd-tools is optional and not installed here")
    assert (diagnostico_proyectos.structure_adapter_for_path("layout.psd")
            == "psd-tools+xmp_window")


def test_structure_adapter_falls_back_to_empty_reader_when_pillow_absent(
        monkeypatch: pytest.MonkeyPatch):
    # Pillow is a hard dependency of this repo (pyproject.toml [project]),
    # so this path is defensive rather than reachable on a real install --
    # but the function still branches on find_spec("PIL"), so the absence
    # branch is real code that must be proven, not just present.
    _block_find_spec(monkeypatch, "PIL")
    assert diagnostico_proyectos.structure_adapter_for_path("poster.png") == ""


def test_structure_adapter_uses_pillow_reader_when_present():
    assert diagnostico_proyectos.structure_adapter_for_path("poster.png") == "Pillow"


def test_structure_adapter_ai_reader_falls_back_when_both_tools_absent(
        monkeypatch: pytest.MonkeyPatch):
    # .ai is claimed by the earlier ADOBE_METADATA_EXTENSIONS branch (it
    # always returns "xmp_window" there, since only .psd/.psb qualify for
    # the psd-tools reader name) -- so the later `.ai`/`.eps` branch that
    # also checks psd_tools is dead code for ".ai" specifically. Documented
    # here rather than "fixed" silently: see the report for this task.
    monkeypatch.setattr("shutil.which", lambda name: None)
    _block_find_spec(monkeypatch, "psd_tools")
    assert diagnostico_proyectos.structure_adapter_for_path("legacy.eps") == "stat"
    assert diagnostico_proyectos.structure_adapter_for_path("legacy.ai") == "xmp_window"
