#!/usr/bin/env python3
"""retencion.py -- retention policy for MAK research reports.

Manages unbounded growth of ~/research/informes/ and ~/research/paneles/.
Lists report pairs (*.md + *.json with same basename), sorts by mtime,
and marks older ones for archival (never deletion). Default keeps newest 50,
older ones move to archive/ subdir.

Usage:
    python3 retencion.py --dir PATH [--keep 50] [--apply]

    Default is dry-run (lists actions). --apply actually moves files.
"""
import argparse
import json
import os
from pathlib import Path
from typing import List, Tuple


def list_reports(dir_path: str, exclude_archive: bool = True) -> List[Tuple[str, List[str]]]:
    """List all report pairs in a directory, sorted by mtime (newest first).

    Returns list of (basename, [file_paths]) tuples, where basename is the
    common name before .md/.json extension.

    Args:
        dir_path: Directory to scan (e.g., ~/research/informes).
        exclude_archive: If True, skip files in archive/ subdirectory.

    Returns:
        List of (basename, sorted_file_paths) tuples, sorted by pair mtime.
    """
    dir_path_obj = Path(dir_path)
    if not dir_path_obj.is_dir():
        return []

    # Collect all files by basename (ignoring extension).
    basenames_to_files = {}

    for file_path in dir_path_obj.iterdir():
        # Skip non-files.
        if not file_path.is_file():
            continue
        # Skip files in archive/ subdir only if we're not already scanning archive/ dir.
        if exclude_archive and dir_path_obj.name != "archive" and file_path.parent.name == "archive":
            continue

        # Extract basename (everything before the last .ext).
        stem = file_path.stem  # filename without rightmost extension
        ext = file_path.suffix  # the extension (.md, .json, etc.)

        # Only track .md and .json files; ignore others.
        if ext not in {".md", ".json"}:
            continue

        if stem not in basenames_to_files:
            basenames_to_files[stem] = []
        basenames_to_files[stem].append(str(file_path))

    # Sort file lists by mtime (newest first).
    report_pairs = []
    for stem, files in basenames_to_files.items():
        files_sorted = sorted(files, key=lambda p: os.path.getmtime(p), reverse=True)
        # Get mtime of the most recent file in the pair for sorting.
        mtime = os.path.getmtime(files_sorted[0])
        report_pairs.append((stem, files_sorted, mtime))

    # Sort all report pairs by mtime (newest first).
    report_pairs.sort(key=lambda x: x[2], reverse=True)

    return [(stem, files) for stem, files, _ in report_pairs]


def retention_plan(report_pairs: List[Tuple[str, List[str]]],
                   keep: int = 50) -> Tuple[List[Tuple[str, List[str]]],
                                            List[Tuple[str, List[str]]]]:
    """Partition report pairs into keep and archive lists.

    Args:
        report_pairs: Output of list_reports().
        keep: Number of reports (pairs) to keep. Newer reports are kept.

    Returns:
        (keep_list, archive_list) tuples of (basename, files).
    """
    keep = max(1, keep)  # Always keep at least 1.
    keep_list = report_pairs[:keep]
    archive_list = report_pairs[keep:]
    return keep_list, archive_list


def apply_retention(archive_list: List[Tuple[str, List[str]]],
                   dir_path: str) -> int:
    """Move archived reports to archive/ subdirectory.

    Creates archive/ if needed. Moves all files in archive_list to archive/.

    Args:
        archive_list: Output of retention_plan()[1].
        dir_path: Base directory (archive/ subdir created here).

    Returns:
        Number of files moved.
    """
    if not archive_list:
        return 0

    archive_dir = Path(dir_path) / "archive"
    archive_dir.mkdir(exist_ok=True)

    files_moved = 0
    for basename, file_paths in archive_list:
        for file_path in file_paths:
            src = Path(file_path)
            dst = archive_dir / src.name
            src.rename(dst)
            files_moved += 1

    return files_moved


def dry_run_summary(report_pairs: List[Tuple[str, List[str]]],
                    keep: int = 50) -> str:
    """Generate a summary of what would happen without --apply.

    Args:
        report_pairs: Output of list_reports().
        keep: Number of reports to keep.

    Returns:
        Formatted string summarizing the retention plan.
    """
    keep_list, archive_list = retention_plan(report_pairs, keep)

    lines = []
    lines.append(f"Retention Report (dry-run)")
    lines.append(f"  Total reports: {len(report_pairs)}")
    lines.append(f"  Keep (newest {keep}): {len(keep_list)}")
    lines.append(f"  Archive: {len(archive_list)}")

    if archive_list:
        files_to_archive = sum(len(files) for _, files in archive_list)
        lines.append(f"  Files to move: {files_to_archive}")
        lines.append("")
        lines.append("Reports to archive (oldest):")
        for basename, files in archive_list[-5:]:  # Show last 5 (oldest).
            files_str = " + ".join(Path(f).name for f in files)
            lines.append(f"  - {basename}: {files_str}")
        if len(archive_list) > 5:
            lines.append(f"  ... and {len(archive_list) - 5} more")
    else:
        lines.append("")
        lines.append("No reports to archive.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Retention policy for MAK research reports."
    )
    parser.add_argument("--dir", required=True,
                       help="Directory to scan (e.g., ~/research/informes)")
    parser.add_argument("--keep", type=int, default=50,
                       help="Number of reports to keep (default: 50)")
    parser.add_argument("--apply", action="store_true",
                       help="Apply retention (default is dry-run)")
    args = parser.parse_args()

    dir_path = os.path.expanduser(args.dir)

    # List all reports.
    reports = list_reports(dir_path, exclude_archive=True)

    # Show summary.
    summary = dry_run_summary(reports, args.keep)
    print(summary)

    if args.apply:
        # Apply retention.
        keep_list, archive_list = retention_plan(reports, args.keep)
        files_moved = apply_retention(archive_list, dir_path)
        print(f"\nApplied: {files_moved} files moved to archive/")
        return 0

    print("\nDry-run mode. Add --apply to move files to archive/")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
