#!/usr/bin/env python3
"""No repository scanner may walk into the operator's cloud mounts.

`/home/mak/GoogleDrive` and `/home/mak/OneDrive` are `fuse.rclone` mounts.
Reading a file there downloads it, and on this box processes have been observed
stuck in FUSE wait (`request_wait_answer`, `fuse_lock_inode`) for hours.

`consolidate_static_duplicates.PROTECTED_TOPS` already names the four roots a
tool must stay out of: WIN, curatoria_inbox, GoogleDrive and OneDrive. That set
is the repository's decision, taken once. `build_mak_knowledge_db.ACTIVE_SKIP`
carried only WIN, so its default `--active-root /home/mak` would descend into
both mounts and hash -- which is to say download -- every file in them.

This module holds the two scanners to the same list, and is the place to add
the next one rather than discovering the same hole a third time.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.build_mak_knowledge_db import ACTIVE_SKIP, should_skip_dir
from tools.consolidate_static_duplicates import PROTECTED_TOPS

HOME = Path("/home/mak")


class TestTheProtectedSetIsTheContract:
    def test_it_still_names_the_cloud_mounts(self) -> None:
        # If this shrinks, the tests below would pass while checking less.
        assert {"GoogleDrive", "OneDrive"} <= PROTECTED_TOPS
        assert {"WIN", "curatoria_inbox"} <= PROTECTED_TOPS


class TestTheKnowledgeScannerStaysOut:
    @pytest.mark.parametrize("protected", sorted(PROTECTED_TOPS))
    def test_every_protected_root_is_skipped(self, protected: str) -> None:
        assert should_skip_dir(HOME / protected, "active"), (
            f"the knowledge scan would descend into {protected}"
        )

    @pytest.mark.parametrize("protected", sorted(PROTECTED_TOPS))
    def test_the_skip_list_names_it(self, protected: str) -> None:
        assert protected in ACTIVE_SKIP

    def test_an_ordinary_directory_is_still_scanned(self) -> None:
        # A scanner that skips everything indexes nothing.
        assert not should_skip_dir(HOME / "proyecto", "active")
        assert not should_skip_dir(HOME / "iskvw", "active")
        assert not should_skip_dir(HOME / "tools", "active")

    def test_a_directory_merely_containing_the_name_is_scanned(self) -> None:
        # The match is on the directory name, not a substring of the path.
        assert not should_skip_dir(HOME / "proyecto" / "GoogleDriveExport", "active")
        assert not should_skip_dir(HOME / "notas_OneDrive", "active")


class TestDecidingCostsNoFilesystem:
    """The decision must not touch the mount it is deciding to avoid."""

    @pytest.fixture
    def no_probe(self, monkeypatch):
        """Arm the one call the decision could make: the pyvenv.cfg stat.

        Only `Path.is_file` is replaced. Patching `exists` or `stat` wholesale
        breaks pytest's own traceback machinery, which stats source files --
        the failure mode reads as an INTERNALERROR and hides whatever the test
        was about.
        """
        import tools.build_mak_knowledge_db as scanner

        def landmine(path):
            raise AssertionError(f"the scanner stat'd {path} to decide")

        monkeypatch.setattr(scanner, "is_virtual_environment", landmine)

    @pytest.mark.parametrize("protected", sorted(PROTECTED_TOPS))
    def test_a_protected_root_is_skipped_without_being_probed(
        self, no_probe, protected: str
    ) -> None:
        # The name check used to run *after* the pyvenv.cfg stat, so deciding
        # never to read the cloud cost one round trip to the cloud.
        assert should_skip_dir(HOME / protected, "active")

    def test_the_landmine_is_armed(self, no_probe) -> None:
        # An ordinary directory still reaches the probe, so the fixture is
        # doing something and the tests above are not passing for free.
        with pytest.raises(AssertionError, match="stat'd"):
            should_skip_dir(HOME / "proyecto", "active")
