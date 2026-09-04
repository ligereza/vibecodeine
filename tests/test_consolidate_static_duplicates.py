#!/usr/bin/env python3
"""The safety gate of `tools/consolidate_static_duplicates.py`, which had none.

The tool moves files out of the live tree and into an archive. `check_path` is
the whole of what keeps it away from WIN, curatoria_inbox, GoogleDrive,
OneDrive and the flujo Git checkout, and nothing tested it.

It read the path as written. `Path` normalises a `.` but never a `..` -- it
cannot, because with a symlink in the way the two are not the same place -- so
the gate accepted:

    /home/mak/proyecto/../WIN/a.txt     read as top component "proyecto"
    /home/mak/../etc/passwd             read as inside MAK

Both are asserted below against the fixed version, along with the case that
already worked (`./WIN`) so the fix is not credited for it.

`check_path` is pure and touches no disk, so most of this runs against literal
paths under the real `/home/mak` without creating anything there. The symlink
cases build their own tree under tmp_path and repoint the module's ROOT.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import consolidate_static_duplicates as tool
from tools.consolidate_static_duplicates import (
    GIT_TOPS,
    PROTECTED_TOPS,
    ROOT,
    check_path,
    validate_file,
)


class TestTraversalCannotWalkOutOfMak:
    @pytest.mark.parametrize(
        "path",
        [
            "/home/mak/../etc/passwd",
            "/home/mak/a/../../etc/passwd",
            "/home/mak/./../../etc/shadow",
        ],
    )
    def test_dot_dot_out_of_the_tree_is_refused(self, path: str) -> None:
        with pytest.raises(RuntimeError, match="path outside MAK"):
            check_path(Path(path))

    @pytest.mark.parametrize("protected", sorted(PROTECTED_TOPS))
    def test_dot_dot_back_into_a_protected_root_is_refused(self, protected: str) -> None:
        with pytest.raises(RuntimeError, match="protected root"):
            check_path(Path(f"/home/mak/proyecto/../{protected}/archivo.txt"))

    @pytest.mark.parametrize("git_top", sorted(GIT_TOPS))
    def test_dot_dot_back_into_a_git_root_is_refused(self, git_top: str) -> None:
        with pytest.raises(RuntimeError, match="Git root"):
            check_path(Path(f"/home/mak/a/b/../../{git_top}/src/x.py"))

    def test_the_error_says_where_the_path_actually_lands(self) -> None:
        # An operator handed "proyecto/../WIN" needs to be told it means WIN.
        with pytest.raises(RuntimeError) as caught:
            check_path(Path("/home/mak/proyecto/../WIN/a.txt"))
        assert "resuelve a" in str(caught.value)
        assert "/home/mak/WIN/a.txt" in str(caught.value)


class TestTheGateStillRefusesWhatItAlwaysDid:
    """Guards against the fix being credited for cases that already worked."""

    @pytest.mark.parametrize("protected", sorted(PROTECTED_TOPS))
    def test_a_protected_root_is_refused(self, protected: str) -> None:
        with pytest.raises(RuntimeError, match="protected root"):
            check_path(ROOT / protected / "archivo.txt")

    @pytest.mark.parametrize("git_top", sorted(GIT_TOPS))
    def test_a_git_root_is_refused(self, git_top: str) -> None:
        with pytest.raises(RuntimeError, match="Git root"):
            check_path(ROOT / git_top / "src" / "x.py")

    def test_git_internals_anywhere_are_refused(self) -> None:
        with pytest.raises(RuntimeError, match="Git internals"):
            check_path(ROOT / "proyecto" / ".git" / "config")

    def test_a_path_outside_mak_is_refused(self) -> None:
        with pytest.raises(RuntimeError, match="path outside MAK"):
            check_path(Path("/etc/passwd"))

    def test_a_single_dot_was_already_normalised(self) -> None:
        with pytest.raises(RuntimeError, match="protected root"):
            check_path(Path("/home/mak/./WIN/a.txt"))


class TestTheGateStillLetsRealWorkThrough:
    """A gate that refuses everything is not a gate, it is a wall."""

    @pytest.mark.parametrize(
        "relative",
        ["proyecto/a.txt", "iskvw/piel/x.svg", "docs/nota.md", "a/b/c/d/e.bin"],
    )
    def test_an_ordinary_path_under_mak_passes(self, relative: str) -> None:
        check_path(ROOT / relative)

    def test_a_directory_named_like_a_protected_root_deeper_down_passes(self) -> None:
        # Only the top component is protected; "proyecto/WIN" is not WIN.
        check_path(ROOT / "proyecto" / "WIN" / "a.txt")

    def test_a_name_that_merely_contains_git_passes(self) -> None:
        check_path(ROOT / "proyecto" / "gitflow" / "notas.md")


class TestSymlinksCannotSmugglePathsIn:
    @pytest.fixture
    def fake_root(self, tmp_path: Path, monkeypatch) -> Path:
        root = tmp_path / "mak"
        (root / "proyecto").mkdir(parents=True)
        (root / "WIN").mkdir()
        (root / "WIN" / "privado.txt").write_text("no tocar", encoding="utf-8")
        monkeypatch.setattr(tool, "ROOT", root)
        return root

    def test_a_symlinked_directory_into_a_protected_root_is_refused(
        self, fake_root: Path
    ) -> None:
        alias = fake_root / "proyecto" / "atajo"
        alias.symlink_to(fake_root / "WIN", target_is_directory=True)
        with pytest.raises(RuntimeError, match="protected root"):
            check_path(alias / "privado.txt")

    def test_a_symlink_pointing_out_of_the_tree_is_refused(
        self, fake_root: Path, tmp_path: Path
    ) -> None:
        outside = tmp_path / "fuera"
        outside.mkdir()
        alias = fake_root / "proyecto" / "salida"
        alias.symlink_to(outside, target_is_directory=True)
        with pytest.raises(RuntimeError, match="path outside MAK"):
            check_path(alias / "algo.txt")

    def test_a_real_directory_under_the_root_still_passes(self, fake_root: Path) -> None:
        check_path(fake_root / "proyecto" / "obra.txt")


class TestValidateFile:
    @pytest.fixture
    def fake_root(self, tmp_path: Path, monkeypatch) -> Path:
        root = tmp_path / "mak"
        root.mkdir()
        monkeypatch.setattr(tool, "ROOT", root)
        return root

    def test_a_regular_file_passes(self, fake_root: Path) -> None:
        target = fake_root / "obra.txt"
        target.write_text("contenido", encoding="utf-8")
        validate_file(target)

    def test_a_symlink_to_a_regular_file_is_refused(self, fake_root: Path) -> None:
        # Archiving a symlink would retire the link and leave the file, or
        # worse, retire something the link only pointed at.
        target = fake_root / "obra.txt"
        target.write_text("contenido", encoding="utf-8")
        alias = fake_root / "alias.txt"
        alias.symlink_to(target)
        with pytest.raises(RuntimeError, match="expected regular file"):
            validate_file(alias)

    def test_a_directory_is_refused(self, fake_root: Path) -> None:
        folder = fake_root / "carpeta"
        folder.mkdir()
        with pytest.raises(RuntimeError, match="expected regular file"):
            validate_file(folder)

    def test_a_missing_file_is_refused(self, fake_root: Path) -> None:
        with pytest.raises(RuntimeError, match="expected regular file"):
            validate_file(fake_root / "no_existe.txt")

    def test_it_applies_the_path_gate_before_looking_at_the_file(
        self, fake_root: Path
    ) -> None:
        protected = fake_root / "WIN"
        protected.mkdir()
        target = protected / "privado.txt"
        target.write_text("no tocar", encoding="utf-8")
        with pytest.raises(RuntimeError, match="protected root"):
            validate_file(target)
