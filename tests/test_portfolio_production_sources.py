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


class TestNoInputLivesSomewhereTemporary:
    @pytest.mark.parametrize(
        "name,path", sorted(hub.PORTFOLIO_PRODUCTION_SOURCES.items())
    )
    def test_the_path_is_not_in_a_scratch_directory(self, name: str, path: str) -> None:
        # Only paths *outside* the repository are checked. A checkout can sit
        # anywhere -- this one is a git worktree under `.claude/worktrees/`, so
        # every repository path contains `/.claude/` and a naive marker match
        # flags the repository itself. Whatever the repository lives in is as
        # durable as the repository.
        candidate = Path(str(path))
        if candidate.is_relative_to(REPO):
            return
        lowered = str(path).replace("\\", "/").lower()
        offending = [marker for marker in EPHEMERAL if marker in lowered]
        assert not offending, (
            f"production input {name!r} points outside the repository into "
            f"{offending[0]!r}: {path}\n"
            "That directory is not promised to survive, and the chain reports "
            "its loss as `fuentes_ausentes` without naming the cause."
        )

    def test_the_check_still_catches_a_scratch_path(self) -> None:
        # The exemption above must not turn the guard off. This is the exact
        # shape that was in the table until 2026-09-04.
        outside = "/home/mak/.claude/jobs/3428381a/tmp/declared_inputs.json"
        assert not Path(outside).is_relative_to(REPO)
        assert any(marker in outside.lower() for marker in EPHEMERAL)

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
        outside = sorted(
            name for name, path in hub.PORTFOLIO_PRODUCTION_SOURCES.items()
            if not Path(str(path)).is_relative_to(REPO)
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
