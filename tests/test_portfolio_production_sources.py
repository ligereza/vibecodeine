#!/usr/bin/env python3
"""No production input may live in a directory the harness deletes.

`PORTFOLIO_PRODUCTION_SOURCES` hardcoded two absolute paths into
`/home/mak/.claude/jobs/3428381a/tmp/` -- the scratch directory of an agent
session from 2026-08-23. Those files are real measurements of the archive, and
that directory is removed when the job is deleted. The chain that backs a
funding application would have begun answering `fuentes_ausentes` on cleanup
day, with nothing in the answer to say why.

They are copies now, under `data/` beside the other production inputs, and the
originals were left alone. This module keeps the class closed: an input that
points at a scratch, a cache or a temp directory is a dependency on something
nobody promised to keep.
"""
from __future__ import annotations

import json
from pathlib import Path

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

# Directory names that mean "this may be gone tomorrow".
EPHEMERAL = ("/.claude/", "/tmp/", "/var/tmp/", "/.cache/", "/scratch/")


def ephemeral_markers(path: str, repo: Path = REPO) -> list[str]:
    """Markers left in the part of the path the repository does not account for.

    `is_relative_to(repo)` cannot answer this alone, and getting it wrong is
    silent in both directions:

    * The MAK checkout is `/home/mak`, so the scratch path
      `/home/mak/.claude/jobs/<id>/tmp/x.json` sits "inside the repository" by
      prefix while being exactly the directory this module exists to reject.
      Exempting everything inside the repository disarms the guard there.
    * A worktree lives under `.claude/worktrees/`, so every repository path
      carries `/.claude/`. Matching the raw string flags the repository itself.

    Both disappear once the repository root is removed first and only the
    remainder is read. Whatever the repository lives in is as durable as the
    repository; what hangs off it is not.
    """
    candidate = Path(str(path))
    if candidate.is_relative_to(repo):
        rest = "/" + candidate.relative_to(repo).as_posix()
    else:
        rest = str(path).replace("\\", "/")
    lowered = rest.lower()
    return [marker for marker in EPHEMERAL if marker in lowered]


class TestNoInputLivesSomewhereTemporary:
    @pytest.mark.parametrize(
        "name,path", sorted(hub.PORTFOLIO_PRODUCTION_SOURCES.items())
    )
    def test_the_path_is_not_in_a_scratch_directory(self, name: str, path: str) -> None:
        offending = ephemeral_markers(path)
        assert not offending, (
            f"production input {name!r} hangs off {offending[0]!r}: {path}\n"
            "That directory is not promised to survive, and the chain reports "
            "its loss as `fuentes_ausentes` without naming the cause."
        )

    # The exact shape that was in the table until 2026-09-04, checked from
    # both places this repository is checked out. The first parameter is the
    # MAK checkout, where the scratch path is *inside* the repository by
    # prefix -- that case shipped green on 2026-09-04 and failed the moment
    # the merge reached `/home/mak`, because the guard exempted it.
    @pytest.mark.parametrize("repo", [
        Path("/home/mak"),
        Path("/home/mak/.claude/worktrees/mak-nocturno-mejoras"),
        Path("/home/runner/work/vibecodeine/vibecodeine"),
    ])
    def test_the_check_still_catches_a_scratch_path(self, repo: Path) -> None:
        scratch = "/home/mak/.claude/jobs/3428381a/tmp/declared_inputs.json"
        # Two markers match this shape -- `/.claude/` and the `/tmp/` inside
        # the job directory. Asserting the exact list would be asserting the
        # order of a constant, so require the one that carries the meaning.
        found = ephemeral_markers(scratch, repo)
        assert "/.claude/" in found, (
            f"the guard is disarmed when the checkout is {repo}: {found}"
        )

    # ...and it must still let the repository's own files through, wherever
    # the repository happens to live.
    @pytest.mark.parametrize("repo,path", [
        (Path("/home/mak"), "/home/mak/data/portfolio_practices.json"),
        (Path("/home/mak/.claude/worktrees/x"),
         "/home/mak/.claude/worktrees/x/data/portfolio_practices.json"),
    ])
    def test_it_does_not_flag_the_repository_itself(
        self, repo: Path, path: str
    ) -> None:
        assert ephemeral_markers(path, repo) == []

    def test_the_two_recovered_inputs_are_in_the_repository(self) -> None:
        for name in ("declared_inputs", "blend_targets"):
            path = Path(hub.PORTFOLIO_PRODUCTION_SOURCES[name])
            assert path.is_file(), f"{name} is missing at {path}"
            assert path.is_relative_to(REPO), (
                f"{name} resolves outside the repository: {path}"
            )

    def test_they_carry_the_content_they_are_supposed_to(self) -> None:
        # A file that exists and is empty satisfies `present` and measures
        # nothing, which is the failure mode this whole class is about.
        targets = json.loads(
            Path(hub.PORTFOLIO_PRODUCTION_SOURCES["blend_targets"]).read_text(
                encoding="utf-8")
        )
        assert isinstance(targets, list) and len(targets) >= 40, (
            f"blend_targets holds {len(targets)} entries; it held 48 when copied"
        )

        declared = json.loads(
            Path(hub.PORTFOLIO_PRODUCTION_SOURCES["declared_inputs"]).read_text(
                encoding="utf-8")
        )
        assert isinstance(declared, dict) and len(declared) >= 100, (
            f"declared_inputs holds {len(declared)} entries; it is a per-filename "
            "count of declared inputs and was far larger"
        )


class TestTheRemainingInputsAreDeclaredHonestly:
    def test_every_input_is_an_absolute_path(self, ) -> None:
        for name, path in hub.PORTFOLIO_PRODUCTION_SOURCES.items():
            assert os.path.isabs(str(path)), f"{name} is relative: {path}"

    def test_the_inputs_outside_the_repository_are_the_ones_that_must_be(
        self,
    ) -> None:
        # Two inputs are physical by nature: the portable SSD and the index
        # built from it. Everything else belongs to the repository, and a new
        # outside path should be a deliberate decision rather than a drift.
        #
        # Asked as `is_relative_to(REPO)` this was checkout-dependent: the
        # MAK checkout is `/home/mak`, so `index` at `/home/mak/labs/...`
        # reads as inside the repository there and outside it in a worktree.
        # The invariant that does not move is which trees the repository
        # actually owns.
        owned = (REPO / "data", REPO / "iskvw")
        outside = sorted(
            name for name, path in hub.PORTFOLIO_PRODUCTION_SOURCES.items()
            if not any(Path(str(path)).is_relative_to(tree) for tree in owned)
        )
        assert outside == ["index", "screen_setup_root"], (
            f"unexpected production input outside the repository: {outside}"
        )

    def test_the_sources_report_presence_without_reading_the_files(self) -> None:
        # `_portfolio_production_sources` is called to decide whether the chain
        # can run; it must not pay to open a 900 GB volume to answer.
        reported = hub._portfolio_production_sources()
        assert set(reported) == set(hub.PORTFOLIO_PRODUCTION_SOURCES)
        for name, row in reported.items():
            assert set(row) == {"path", "present"}
            assert isinstance(row["present"], bool)
