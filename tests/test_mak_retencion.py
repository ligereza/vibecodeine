"""Tests for cultura/mak_research/retencion.py -- retention policy."""
import os
import sys
import time
from pathlib import Path

import pytest

# Add cultura dir to path so we can import retencion.
sys.path.insert(0, str(Path(__file__).parent.parent / "cultura" / "mak_research"))

from retencion import (
    list_reports,
    retention_plan,
    apply_retention,
    dry_run_summary,
)


class TestListReports:
    """Tests for list_reports()."""

    def test_empty_directory(self, tmp_path):
        """Empty directory should return empty list."""
        result = list_reports(str(tmp_path))
        assert result == []

    def test_nonexistent_directory(self):
        """Nonexistent directory should return empty list."""
        result = list_reports("/nonexistent/path/does/not/exist")
        assert result == []

    def test_single_report_pair(self, tmp_path):
        """Single report pair (.md + .json) should be listed together."""
        # Create a report pair.
        (tmp_path / "2026-07-17T10-00-00-tema-slug.md").write_text("# Report")
        (tmp_path / "2026-07-17T10-00-00-tema-slug.json").write_text("{}")

        result = list_reports(str(tmp_path))
        assert len(result) == 1
        basename, files = result[0]
        assert basename == "2026-07-17T10-00-00-tema-slug"
        assert len(files) == 2  # Both .md and .json.
        assert any(f.endswith(".md") for f in files)
        assert any(f.endswith(".json") for f in files)

    def test_multiple_reports_sorted_by_mtime(self, tmp_path):
        """Multiple reports should be sorted by mtime (newest first)."""
        # Create 3 reports with different mtimes.
        old_file = tmp_path / "2026-07-17T10-00-00-old.md"
        new_file = tmp_path / "2026-07-17T11-00-00-new.md"
        mid_file = tmp_path / "2026-07-17T10-30-00-mid.md"

        for f in [old_file, new_file, mid_file]:
            f.write_text("# Report")

        # Adjust mtimes: old is oldest, new is newest.
        t_old = time.time() - 3600  # 1 hour ago.
        t_mid = time.time() - 1800  # 30 min ago.
        t_new = time.time()

        os.utime(old_file, (t_old, t_old))
        os.utime(mid_file, (t_mid, t_mid))
        os.utime(new_file, (t_new, t_new))

        result = list_reports(str(tmp_path))
        assert len(result) == 3
        # Should be sorted newest first.
        assert result[0][0] == "2026-07-17T11-00-00-new"
        assert result[1][0] == "2026-07-17T10-30-00-mid"
        assert result[2][0] == "2026-07-17T10-00-00-old"

    def test_ignore_non_md_json_files(self, tmp_path):
        """Files other than .md/.json should be ignored."""
        (tmp_path / "2026-07-17T10-00-00-tema.md").write_text("# Report")
        (tmp_path / "2026-07-17T10-00-00-tema.json").write_text("{}")
        (tmp_path / "2026-07-17T10-00-00-tema.txt").write_text("ignored")
        (tmp_path / "other.log").write_text("also ignored")

        result = list_reports(str(tmp_path))
        assert len(result) == 1
        basename, files = result[0]
        assert basename == "2026-07-17T10-00-00-tema"
        assert len(files) == 2  # Only .md and .json.

    def test_exclude_archive_directory(self, tmp_path):
        """Files in archive/ subdirectory should be excluded."""
        # Create a report in the main dir.
        (tmp_path / "2026-07-17T10-00-00-main.md").write_text("# Report")
        (tmp_path / "2026-07-17T10-00-00-main.json").write_text("{}")

        # Create a report in archive/ subdir.
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "2026-07-17T09-00-00-archived.md").write_text("# Old Report")
        (archive_dir / "2026-07-17T09-00-00-archived.json").write_text("{}")

        result = list_reports(str(tmp_path), exclude_archive=True)
        assert len(result) == 1
        assert result[0][0] == "2026-07-17T10-00-00-main"

    def test_list_archive_subdirectory_directly(self, tmp_path):
        """Calling list_reports on archive/ subdir should list archived reports."""
        # Create archive/ subdir with reports.
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "2026-07-17T09-00-00-archived.md").write_text("# Old Report")
        (archive_dir / "2026-07-17T09-00-00-archived.json").write_text("{}")

        # Call list_reports on the archive/ directory itself.
        result = list_reports(str(archive_dir))
        assert len(result) == 1
        assert result[0][0] == "2026-07-17T09-00-00-archived"


class TestRetentionPlan:
    """Tests for retention_plan()."""

    def test_keep_newest_reports(self):
        """retention_plan should keep the newest N reports."""
        # Create 5 fake report pairs.
        reports = [
            ("report-1", ["report-1.md", "report-1.json"]),
            ("report-2", ["report-2.md", "report-2.json"]),
            ("report-3", ["report-3.md", "report-3.json"]),
            ("report-4", ["report-4.md", "report-4.json"]),
            ("report-5", ["report-5.md", "report-5.json"]),
        ]

        keep_list, archive_list = retention_plan(reports, keep=3)
        assert len(keep_list) == 3
        assert len(archive_list) == 2
        # First 3 should be kept (newest).
        assert keep_list[0][0] == "report-1"
        assert keep_list[1][0] == "report-2"
        assert keep_list[2][0] == "report-3"
        # Last 2 should be archived.
        assert archive_list[0][0] == "report-4"
        assert archive_list[1][0] == "report-5"

    def test_keep_larger_than_count(self):
        """If keep > report count, all should be kept."""
        reports = [
            ("report-1", ["report-1.md", "report-1.json"]),
            ("report-2", ["report-2.md", "report-2.json"]),
        ]

        keep_list, archive_list = retention_plan(reports, keep=10)
        assert len(keep_list) == 2
        assert len(archive_list) == 0

    def test_keep_minimum_one(self):
        """Even if keep=0, at least 1 report should be kept."""
        reports = [
            ("report-1", ["report-1.md", "report-1.json"]),
            ("report-2", ["report-2.md", "report-2.json"]),
        ]

        keep_list, archive_list = retention_plan(reports, keep=0)
        assert len(keep_list) == 1
        assert len(archive_list) == 1


class TestApplyRetention:
    """Tests for apply_retention()."""

    def test_no_files_to_archive(self, tmp_path):
        """With empty archive_list, apply_retention should move nothing."""
        files_moved = apply_retention([], str(tmp_path))
        assert files_moved == 0
        # archive/ subdir should not be created.
        assert not (tmp_path / "archive").exists()

    def test_apply_moves_files_to_archive(self, tmp_path):
        """apply_retention should move all files in archive_list to archive/."""
        # Create files to archive.
        (tmp_path / "report-1.md").write_text("# Report 1")
        (tmp_path / "report-1.json").write_text("{}")
        (tmp_path / "report-2.md").write_text("# Report 2")
        (tmp_path / "report-2.json").write_text("{}")

        archive_list = [
            ("report-1", [str(tmp_path / "report-1.md"),
                         str(tmp_path / "report-1.json")]),
            ("report-2", [str(tmp_path / "report-2.md"),
                         str(tmp_path / "report-2.json")]),
        ]

        files_moved = apply_retention(archive_list, str(tmp_path))
        assert files_moved == 4

        # Files should no longer be in tmp_path.
        assert not (tmp_path / "report-1.md").exists()
        assert not (tmp_path / "report-1.json").exists()
        assert not (tmp_path / "report-2.md").exists()
        assert not (tmp_path / "report-2.json").exists()

        # Files should be in archive/.
        archive_dir = tmp_path / "archive"
        assert archive_dir.exists()
        assert (archive_dir / "report-1.md").exists()
        assert (archive_dir / "report-1.json").exists()
        assert (archive_dir / "report-2.md").exists()
        assert (archive_dir / "report-2.json").exists()

    def test_apply_is_idempotent(self, tmp_path):
        """A second full retention run should not re-process archived files."""
        # Create a file and archive it.
        (tmp_path / "report-1.md").write_text("# Report 1")
        (tmp_path / "report-1.json").write_text("{}")

        archive_list = [
            ("report-1", [str(tmp_path / "report-1.md"),
                         str(tmp_path / "report-1.json")]),
        ]

        files_moved_1 = apply_retention(archive_list, str(tmp_path))
        assert files_moved_1 == 2

        # List reports in main dir again: no files should be found.
        reports = list_reports(str(tmp_path), exclude_archive=True)
        assert len(reports) == 0

        # List reports in archive/ dir: archived files should be there.
        archive_reports = list_reports(str(tmp_path / "archive"))
        assert len(archive_reports) == 1


class TestDryRunSummary:
    """Tests for dry_run_summary()."""

    def test_summary_format_empty(self):
        """Summary of empty report list should show 0 to archive."""
        summary = dry_run_summary([], keep=50)
        assert "Total reports: 0" in summary
        assert "Archive: 0" in summary
        assert "No reports to archive" in summary

    def test_summary_format_with_reports(self):
        """Summary should show counts and list oldest reports."""
        reports = [
            ("report-1", ["report-1.md", "report-1.json"]),
            ("report-2", ["report-2.md", "report-2.json"]),
            ("report-3", ["report-3.md", "report-3.json"]),
            ("report-4", ["report-4.md", "report-4.json"]),
        ]

        summary = dry_run_summary(reports, keep=2)
        assert "Total reports: 4" in summary
        assert "Keep (newest 2): 2" in summary
        assert "Archive: 2" in summary
        assert "Files to move: 4" in summary


class TestEndToEnd:
    """End-to-end tests combining all functions."""

    def test_full_retention_flow(self, tmp_path):
        """Full flow: create reports, list, plan, and apply retention."""
        # Create 5 reports.
        for i in range(1, 6):
            basename = f"2026-07-17T{10+i:02d}-00-00-tema-{i}"
            (tmp_path / f"{basename}.md").write_text(f"# Report {i}")
            (tmp_path / f"{basename}.json").write_text("{}")
            # Stagger mtimes so they sort properly.
            t = time.time() - (5 - i) * 600  # 10min apart.
            for ext in [".md", ".json"]:
                os.utime(tmp_path / f"{basename}{ext}", (t, t))

        # List reports.
        reports = list_reports(str(tmp_path))
        assert len(reports) == 5

        # Plan to keep 2.
        keep_list, archive_list = retention_plan(reports, keep=2)
        assert len(keep_list) == 2
        assert len(archive_list) == 3

        # Apply retention.
        files_moved = apply_retention(archive_list, str(tmp_path))
        assert files_moved == 6  # 3 reports * 2 files each.

        # Verify: 2 reports remain in main dir, 3 in archive/ (or 4 if partial files).
        main_reports = list_reports(str(tmp_path))
        assert len(main_reports) == 2

        # Verify archive/ subdir exists and has the archived reports.
        archive_dir = tmp_path / "archive"
        assert archive_dir.exists()
        archive_reports = list_reports(str(archive_dir))
        assert len(archive_reports) == 3

    def test_pair_integrity_maintained(self, tmp_path):
        """Both .md and .json of a report should move together."""
        # Create reports with explicit mtimes so report-1 is newer.
        (tmp_path / "report-1.md").write_text("# Report 1")
        (tmp_path / "report-1.json").write_text('{"meta": 1}')
        (tmp_path / "report-2.md").write_text("# Report 2")
        (tmp_path / "report-2.json").write_text('{"meta": 2}')

        # Set mtimes: report-2 is older, report-1 is newer.
        t_old = time.time() - 3600
        t_new = time.time()
        os.utime(tmp_path / "report-2.md", (t_old, t_old))
        os.utime(tmp_path / "report-2.json", (t_old, t_old))
        os.utime(tmp_path / "report-1.md", (t_new, t_new))
        os.utime(tmp_path / "report-1.json", (t_new, t_new))

        reports = list_reports(str(tmp_path))
        keep_list, archive_list = retention_plan(reports, keep=1)

        # Archive the older report.
        apply_retention(archive_list, str(tmp_path))

        # Verify pair integrity: the archived pair (report-2) is complete in archive/.
        archive_dir = tmp_path / "archive"
        assert (archive_dir / "report-2.md").exists()
        assert (archive_dir / "report-2.json").exists()

        # And the kept pair (report-1) is complete in main dir.
        assert (tmp_path / "report-1.md").exists()
        assert (tmp_path / "report-1.json").exists()
